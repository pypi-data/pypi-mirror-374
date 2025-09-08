from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

try:  # Optional scikit-learn import for API compatibility
    from sklearn.base import BaseEstimator, RegressorMixin  # type: ignore
    from sklearn.metrics import r2_score as _sk_r2_score  # type: ignore
except Exception:  # Fallbacks if sklearn isn't installed at runtime
    class BaseEstimator:  # minimal stub
        def get_params(self, deep: bool = True):
            # Return non-private, non-callable attributes
            params = {}
            for k, v in self.__dict__.items():
                if k.endswith("_"):
                    continue
                if not k.startswith("_") and not callable(v):
                    params[k] = v
            return params

        def set_params(self, **params):
            for k, v in params.items():
                setattr(self, k, v)
            return self

    class RegressorMixin:
        pass

    def _sk_r2_score(y_true, y_pred):
            y_true = np.asarray(y_true)
            y_pred = np.asarray(y_pred)
            u = ((y_true - y_pred) ** 2).sum()
            v = ((y_true - y_true.mean()) ** 2).sum()
            return 1.0 - (u / v if v != 0 else np.nan)

from .nn import PSANNNet
from .conv import PSANNConv1dNet, PSANNConv2dNet, PSANNConv3dNet
from .utils import choose_device, seed_all


class PSANNRegressor(BaseEstimator, RegressorMixin):
    """Sklearn-style regressor wrapper around a PSANN network (PyTorch).

    Parameters mirror the README's proposed API.
    """

    def __init__(
        self,
        *,
        hidden_layers: int = 2,
        hidden_width: int = 64,
        epochs: int = 200,
        batch_size: int = 128,
        lr: float = 1e-3,
        optimizer: str = "adam",
        weight_decay: float = 0.0,
        activation: Optional[Dict[str, Any]] = None,
        device: str | torch.device = "auto",
        random_state: Optional[int] = None,
        early_stopping: bool = False,
        patience: int = 20,
        num_workers: int = 0,
        loss: Any = "mse",
        loss_params: Optional[Dict[str, Any]] = None,
        loss_reduction: str = "mean",
        w0: float = 30.0,
        preserve_shape: bool = False,
        data_format: str = "channels_first",
        conv_kernel_size: int = 1,
        per_element: bool = False,
        stateful: bool = False,
        state: Optional[Dict[str, Any]] = None,
        state_reset: str = "batch",  # 'batch' | 'epoch' | 'none'
        stream_lr: Optional[float] = None,
        output_shape: Optional[Tuple[int, ...]] = None,
        lsm: Optional[Any] = None,
        lsm_train: bool = False,
        lsm_pretrain_epochs: int = 0,
        lsm_lr: Optional[float] = None,
    ) -> None:
        self.hidden_layers = hidden_layers
        self.hidden_width = hidden_width
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.optimizer = optimizer
        self.weight_decay = weight_decay
        self.activation = activation or {}
        self.device = device
        self.random_state = random_state
        self.early_stopping = early_stopping
        self.patience = patience
        self.num_workers = num_workers
        self.loss = loss
        self.loss_params = loss_params
        self.loss_reduction = loss_reduction
        self.w0 = w0
        self.preserve_shape = preserve_shape
        self.data_format = data_format
        self.conv_kernel_size = conv_kernel_size
        self.per_element = per_element
        self.stateful = stateful
        self.state = state or None
        self.state_reset = state_reset
        self.stream_lr = stream_lr
        self.output_shape = output_shape
        self.lsm = lsm
        self.lsm_train = lsm_train
        self.lsm_pretrain_epochs = lsm_pretrain_epochs
        self.lsm_lr = lsm_lr

    # Internal helpers
    def _device(self) -> torch.device:
        return choose_device(self.device)

    def _infer_input_shape(self, X: np.ndarray) -> tuple:
        if X.ndim < 2:
            raise ValueError("X must be at least 2D (batch, features...)")
        return tuple(X.shape[1:])

    def _flatten(self, X: np.ndarray) -> np.ndarray:
        return X.reshape(X.shape[0], -1).astype(np.float32, copy=False)

    def _make_optimizer(self, model: torch.nn.Module, lr: Optional[float] = None):
        lr = float(self.lr if lr is None else lr)
        if self.optimizer.lower() == "adamw":
            return torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=self.weight_decay)
        if self.optimizer.lower() == "sgd":
            return torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
        return torch.optim.Adam(model.parameters(), lr=lr, weight_decay=self.weight_decay)

    def _make_loss(self):
        # Built-in strings
        if isinstance(self.loss, str):
            name = self.loss.lower()
            params = self.loss_params or {}
            reduction = self.loss_reduction
            if name in ("l1", "mae"):
                return torch.nn.L1Loss(reduction=reduction)
            if name in ("mse", "l2"):
                return torch.nn.MSELoss(reduction=reduction)
            if name in ("smooth_l1", "huber_smooth"):
                beta = float(params.get("beta", 1.0))
                return torch.nn.SmoothL1Loss(beta=beta, reduction=reduction)
            if name in ("huber",):
                delta = float(params.get("delta", 1.0))
                return torch.nn.HuberLoss(delta=delta, reduction=reduction)
            raise ValueError(f"Unknown loss '{self.loss}'. Supported: mse, l1/mae, smooth_l1, huber, or a callable.")

        # Callable custom loss; may return tensor (any shape) or float
        if callable(self.loss):
            user_fn = self.loss
            params = self.loss_params or {}
            reduction = self.loss_reduction

            def _loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
                out = user_fn(pred, target, **params) if params else user_fn(pred, target)
                if not isinstance(out, torch.Tensor):
                    out = torch.as_tensor(out, dtype=pred.dtype, device=pred.device)
                if out.ndim == 0:
                    return out
                if reduction == "mean":
                    return out.mean()
                if reduction == "sum":
                    return out.sum()
                if reduction == "none":
                    return out
                raise ValueError(f"Unsupported reduction '{reduction}' for custom loss")

            return _loss

        raise TypeError("loss must be a string or a callable returning a scalar tensor")

    # Estimator API
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        *,
        validation_data: Optional[tuple[np.ndarray, np.ndarray]] = None,
        verbose: int = 0,
        noisy: Optional[float | np.ndarray] = None,
    ):
        seed_all(self.random_state)

        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)
        # Handle input shape
        self.input_shape_ = self._infer_input_shape(X)

        if self.preserve_shape:
            if X.ndim < 3:
                raise ValueError("preserve_shape=True requires X with at least 3 dims (N, C, ...).")
            if self.data_format not in {"channels_first", "channels_last"}:
                raise ValueError("data_format must be 'channels_first' or 'channels_last'")
            X_cf = np.moveaxis(X, -1, 1) if self.data_format == "channels_last" else X
            self._internal_input_shape_cf_ = tuple(X_cf.shape[1:])
            in_channels = int(X_cf.shape[1])
            nd = X_cf.ndim - 2
            # Targets
            if self.per_element:
                # Determine desired output channels
                if self.output_shape is not None:
                    n_targets = int(self.output_shape[-1] if self.data_format == "channels_last" else self.output_shape[0])
                else:
                    # Infer from targets
                    if self.data_format == "channels_last":
                        if y.ndim == X.ndim:
                            n_targets = int(y.shape[-1])
                        elif y.ndim == X.ndim - 1:
                            n_targets = 1
                        else:
                            raise ValueError("y must match X spatial dims, with optional channel last.")
                    else:
                        if y.ndim == X_cf.ndim:
                            n_targets = int(y.shape[1])
                        elif y.ndim == X_cf.ndim - 1:
                            n_targets = 1
                        else:
                            raise ValueError("y must match X spatial dims, with optional channel first.")
                # Prepare y in channels-first layout
                if self.data_format == "channels_last":
                    if y.ndim == X.ndim:
                        y_cf = np.moveaxis(y, -1, 1)
                    elif y.ndim == X.ndim - 1:
                        if n_targets != 1:
                            raise ValueError(f"Provided output_shape implies {n_targets} channels but y has no channel dimension")
                        y_cf = y[:, None, ...]
                else:
                    if y.ndim == X_cf.ndim:
                        y_cf = y
                    elif y.ndim == X_cf.ndim - 1:
                        if n_targets != 1:
                            raise ValueError(f"Provided output_shape implies {n_targets} channels but y has no channel dimension")
                        y_cf = y[:, None, ...]
            else:
                # pooled/vector targets
                y_vec = y.reshape(y.shape[0], -1) if y.ndim > 2 else (y[:, None] if y.ndim == 1 else y)
                if self.output_shape is not None:
                    n_targets = int(np.prod(self.output_shape))
                    if y_vec.shape[1] != n_targets:
                        raise ValueError(f"y has {y_vec.shape[1]} targets, expected {n_targets} from output_shape")
                else:
                    n_targets = int(y_vec.shape[1])
                y_cf = y_vec

            # Optional Conv LSM preprocessing
            lsm_model = None
            if self.lsm is not None:
                try:
                    from .lsm import LSMConv2dExpander, LSMConv2d
                except Exception:
                    LSMConv2dExpander = None  # type: ignore
                    LSMConv2d = None  # type: ignore
                if nd == 2:
                    if LSMConv2dExpander is not None and isinstance(self.lsm, LSMConv2dExpander):
                        if self.lsm_pretrain_epochs and self.lsm_pretrain_epochs > 0:
                            self.lsm.fit(X_cf, epochs=self.lsm_pretrain_epochs)
                        lsm_model = self.lsm.model
                        if lsm_model is None:
                            raise RuntimeError("Provided LSMConv2dExpander has no underlying model; call fit() or set .model.")
                        in_channels = int(self.lsm.out_channels)
                        if not self.lsm_train:
                            X_cf = self.lsm.transform(X_cf).astype(np.float32, copy=False)
                    elif LSMConv2d is not None and isinstance(self.lsm, LSMConv2d):
                        lsm_model = self.lsm
                        in_channels = int(getattr(lsm_model, 'out_channels'))
                        if not self.lsm_train:
                            with torch.no_grad():
                                X_cf_t = torch.from_numpy(X_cf).to(self._device())
                                X_cf = lsm_model(X_cf_t).cpu().numpy().astype(np.float32, copy=False)
                    elif hasattr(self.lsm, 'forward') and hasattr(self.lsm, 'out_channels'):
                        lsm_model = self.lsm
                        in_channels = int(getattr(lsm_model, 'out_channels'))
                        if not self.lsm_train:
                            with torch.no_grad():
                                X_cf_t = torch.from_numpy(X_cf).to(self._device())
                                X_cf = lsm_model(X_cf_t).cpu().numpy().astype(np.float32, copy=False)
                else:
                    if self.lsm is not None:
                        raise ValueError("Conv LSM is currently supported for 2D inputs only.")

            # Model
            if nd == 1:
                self.model_ = PSANNConv1dNet(
                    in_channels,
                    n_targets,
                    hidden_layers=self.hidden_layers,
                    hidden_channels=self.hidden_width,
                    kernel_size=self.conv_kernel_size,
                    act_kw=self.activation,
                    w0=self.w0,
                    segmentation_head=self.per_element,
                )
            elif nd == 2:
                self.model_ = PSANNConv2dNet(
                    in_channels,
                    n_targets,
                    hidden_layers=self.hidden_layers,
                    hidden_channels=self.hidden_width,
                    kernel_size=self.conv_kernel_size,
                    act_kw=self.activation,
                    w0=self.w0,
                    segmentation_head=self.per_element,
                )
            elif nd == 3:
                self.model_ = PSANNConv3dNet(
                    in_channels,
                    n_targets,
                    hidden_layers=self.hidden_layers,
                    hidden_channels=self.hidden_width,
                    kernel_size=self.conv_kernel_size,
                    act_kw=self.activation,
                    w0=self.w0,
                    segmentation_head=self.per_element,
                )
            else:
                raise ValueError(f"Unsupported number of spatial dims: {nd}. Supported: 1, 2, 3.")
            X_train_arr = X_cf.astype(np.float32, copy=False)
        else:
            n_features = int(np.prod(self.input_shape_))
            X_flat = self._flatten(X)
            y_vec = y.reshape(y.shape[0], -1) if y.ndim > 1 else y[:, None]
            if self.output_shape is not None:
                n_targets = int(np.prod(self.output_shape))
                if y_vec.shape[1] != n_targets:
                    raise ValueError(f"y has {y_vec.shape[1]} targets, expected {n_targets} from output_shape")
            else:
                n_targets = int(y_vec.shape[1])

            # Optional LSM preprocessing (flattened path only)
            X_train_arr = X_flat
            lsm_model = None
            if self.lsm is not None:
                try:
                    from .lsm import LSMExpander
                except Exception:
                    LSMExpander = None  # type: ignore
                if LSMExpander is not None and isinstance(self.lsm, LSMExpander):
                    if self.lsm_pretrain_epochs and self.lsm_pretrain_epochs > 0:
                        self.lsm.fit(X_train_arr, epochs=self.lsm_pretrain_epochs)
                    lsm_model = self.lsm.model
                    if lsm_model is None:
                        raise RuntimeError("Provided LSMExpander has no underlying model; call fit() or set .model.")
                    lsm_out = int(self.lsm.output_dim)
                    if not self.lsm_train:
                        # Precompute features
                        X_train_arr = self.lsm.transform(X_train_arr).astype(np.float32, copy=False)
                elif hasattr(self.lsm, 'forward'):
                    lsm_model = self.lsm
                    if not hasattr(lsm_model, 'output_dim'):
                        raise ValueError("Custom LSM module must define attribute 'output_dim'")
                    lsm_out = int(getattr(lsm_model, 'output_dim'))
                    if not self.lsm_train:
                        with torch.no_grad():
                            device_tmp = choose_device(self.device)
                            Z = lsm_model(torch.from_numpy(X_train_arr).to(device_tmp)).cpu().numpy()
                        X_train_arr = Z.astype(np.float32, copy=False)
                else:
                    raise ValueError("lsm must be an LSMExpander or a torch.nn.Module with 'output_dim'")

            # Build PSANN over (possibly expanded) features
            if self.lsm is not None and not self.preserve_shape:
                if lsm_model is not None and hasattr(lsm_model, 'output_dim'):
                    in_dim_psann = int(getattr(lsm_model, 'output_dim'))
                elif hasattr(self.lsm, 'output_dim'):
                    in_dim_psann = int(getattr(self.lsm, 'output_dim'))
                else:
                    in_dim_psann = int(X_train_arr.shape[1]) if isinstance(X_train_arr, np.ndarray) else int(n_features)
            else:
                in_dim_psann = int(X_train_arr.shape[1]) if isinstance(X_train_arr, np.ndarray) else int(n_features)
            self.model_ = PSANNNet(
                in_dim_psann,
                n_targets,
                hidden_layers=self.hidden_layers,
                hidden_width=self.hidden_width,
                act_kw=self.activation,
                state_cfg=(self.state if self.stateful else None),
                w0=self.w0,
            )
            y_cf = y_vec
        device = self._device()
        self.model_.to(device)

        # Optimizer, optionally with LSM params for joint training
        if self.lsm_train and self.lsm is not None and not self.preserve_shape:
            # Combine parameters
            if lsm_model is None:
                # If we precomputed features, there is no joint training
                opt = self._make_optimizer(self.model_)
            else:
                params = [
                    {"params": self.model_.parameters(), "lr": self.lr},
                    {"params": lsm_model.parameters(), "lr": float(self.lsm_lr) if self.lsm_lr is not None else self.lr},
                ]
                if self.optimizer.lower() == "adamw":
                    opt = torch.optim.AdamW(params, weight_decay=self.weight_decay)
                elif self.optimizer.lower() == "sgd":
                    opt = torch.optim.SGD(params, momentum=0.9)
                else:
                    opt = torch.optim.Adam(params, weight_decay=self.weight_decay)
        else:
            opt = self._make_optimizer(self.model_)
        loss_fn = self._make_loss()

        ds = TensorDataset(torch.from_numpy(X_train_arr), torch.from_numpy(y_cf.astype(np.float32, copy=False))) if (self.lsm is None or not self.lsm_train or self.preserve_shape) else TensorDataset(torch.from_numpy(X_flat), torch.from_numpy(y_cf.astype(np.float32, copy=False)))
        # If state should persist across batches/epoch, disable shuffling to preserve temporal order
        shuffle_batches = True
        if self.stateful and self.state_reset in ("epoch", "none"):
            shuffle_batches = False
        dl = DataLoader(ds, batch_size=self.batch_size, shuffle=shuffle_batches, num_workers=self.num_workers)

        # Prepare validation tensors if provided
        X_val_t = y_val_t = None
        if validation_data is not None:
            Xv, yv = validation_data
            Xv = np.asarray(Xv, dtype=np.float32)
            yv = np.asarray(yv, dtype=np.float32)
            if self.preserve_shape:
                Xv_cf = np.moveaxis(Xv, -1, 1) if self.data_format == "channels_last" else Xv
                if Xv_cf.shape[1] != self._internal_input_shape_cf_[0]:
                    raise ValueError("validation_data channels mismatch.")
                X_val_t = torch.from_numpy(Xv_cf).to(device)
                if self.per_element:
                    if self.data_format == "channels_last":
                        if yv.ndim == Xv.ndim:
                            yv_cf = np.moveaxis(yv, -1, 1)
                        elif yv.ndim == Xv.ndim - 1:
                            yv_cf = yv[:, None, ...]
                        else:
                            raise ValueError("validation y must match X spatial dims, optional channel last.")
                    else:
                        if yv.ndim == Xv_cf.ndim:
                            yv_cf = yv
                        elif yv.ndim == Xv_cf.ndim - 1:
                            yv_cf = yv[:, None, ...]
                        else:
                            raise ValueError("validation y must match X spatial dims, optional channel first.")
                    y_val_t = torch.from_numpy(yv_cf.astype(np.float32, copy=False)).to(device)
                else:
                    y_val_t = torch.from_numpy(yv.reshape(yv.shape[0], -1).astype(np.float32, copy=False)).to(device)
            else:
                n_features = int(np.prod(self.input_shape_))
                if tuple(Xv.shape[1:]) != self.input_shape_:
                    if int(np.prod(Xv.shape[1:])) != n_features:
                        raise ValueError(
                            f"validation_data X has shape {Xv.shape[1:]}, expected {self.input_shape_} (prod must match {n_features})."
                        )
                X_val_t = torch.from_numpy(self._flatten(Xv)).to(device)
                y_val_t = torch.from_numpy(yv.reshape(yv.shape[0], -1).astype(np.float32, copy=False)).to(device)

        # Prepare per-feature noise std (broadcast over batch) if requested
        noise_std_t: Optional[torch.Tensor] = None
        if noisy is not None:
            if self.preserve_shape:
                internal_shape = self._internal_input_shape_cf_
                if np.isscalar(noisy):
                    std = np.full((1, *internal_shape), float(noisy), dtype=np.float32)
                else:
                    arr = np.asarray(noisy, dtype=np.float32)
                    if tuple(arr.shape) == internal_shape:
                        std = arr.reshape(1, *internal_shape)
                    elif tuple(arr.shape) == self.input_shape_ and self.data_format == "channels_last":
                        std = np.moveaxis(arr, -1, 0).reshape(1, *internal_shape)
                    elif arr.ndim == 1 and arr.size == int(np.prod(internal_shape)):
                        std = arr.reshape(1, *internal_shape)
                    else:
                        raise ValueError(
                            f"noisy shape {arr.shape} not compatible with input shape {self.input_shape_}"
                        )
                noise_std_t = torch.from_numpy(std).to(device)
            else:
                n_features = int(np.prod(self.input_shape_))
                if np.isscalar(noisy):
                    std = np.full((1, n_features), float(noisy), dtype=np.float32)
                else:
                    arr = np.asarray(noisy, dtype=np.float32)
                    if arr.ndim == 1 and arr.shape[0] == n_features:
                        std = arr.reshape(1, -1)
                    elif tuple(arr.shape) == self.input_shape_:
                        std = arr.reshape(1, -1)
                    else:
                        raise ValueError(
                            f"noisy shape {arr.shape} not compatible with input shape {self.input_shape_} or flattened size {n_features}"
                        )
                noise_std_t = torch.from_numpy(std).to(device)

        best = float("inf")
        patience = self.patience
        best_state: Optional[Dict[str, torch.Tensor]] = None

        for epoch in range(self.epochs):
            if self.stateful and self.state_reset == "epoch" and hasattr(self.model_, "reset_state"):
                try:
                    self.model_.reset_state()
                except Exception:
                    pass
            self.model_.train()
            total = 0.0
            count = 0
            for xb, yb in dl:
                if self.stateful and self.state_reset == "batch" and hasattr(self.model_, "reset_state"):
                    # Reset at each batch to prevent leakage between batches
                    try:
                        self.model_.reset_state()
                    except Exception:
                        pass
                xb, yb = xb.to(device), yb.to(device)
                if noise_std_t is not None:
                    # Sample Gaussian noise per feature; broadcast over batch
                    noise = torch.randn_like(xb) * noise_std_t
                    xb = xb + noise
                opt.zero_grad()
                # If using LSM joint training, transform on the fly
                if self.lsm_train and self.lsm is not None and lsm_model is not None:
                    xb_in = lsm_model(xb)
                else:
                    xb_in = xb
                pred = self.model_(xb_in)
                loss = loss_fn(pred, yb)
                loss.backward()
                opt.step()
                if hasattr(self.model_, "commit_state_updates"):
                    self.model_.commit_state_updates()
                bs = xb.shape[0]
                total += float(loss.item()) * bs
                count += bs
            epoch_loss = total / max(count, 1)

            # Validation loss (if provided)
            val_loss = None
            if X_val_t is not None and y_val_t is not None:
                self.model_.eval()
                with torch.no_grad():
                    if self.lsm is not None and not self.preserve_shape:
                        if self.lsm_train and lsm_model is not None:
                            X_val_in = lsm_model(X_val_t)
                        else:
                            # Offline transform for validation
                            if hasattr(self.lsm, 'transform'):
                                X_val_in = torch.from_numpy(self.lsm.transform(X_val_t.cpu().numpy())).to(device)
                            elif hasattr(self.lsm, 'forward'):
                                X_val_in = self.lsm(X_val_t)
                            else:
                                X_val_in = X_val_t
                    else:
                        X_val_in = X_val_t
                    pred_val = self.model_(X_val_in)
                    val_loss = float(loss_fn(pred_val, y_val_t).item())

            # Logging
            if verbose:
                if val_loss is not None:
                    print(f"Epoch {epoch+1}/{self.epochs} - loss: {epoch_loss:.6f} - val_loss: {val_loss:.6f}")
                else:
                    print(f"Epoch {epoch+1}/{self.epochs} - loss: {epoch_loss:.6f}")

            # Early stopping: prefer validation loss when available
            metric = val_loss if val_loss is not None else epoch_loss
            if self.early_stopping:
                if metric + 1e-12 < best:
                    best = metric
                    patience = self.patience
                    best_state = {k: v.detach().cpu().clone() for k, v in self.model_.state_dict().items()}
                else:
                    patience -= 1
                    if patience <= 0 and best_state is not None:
                        if verbose:
                            print(f"Early stopping at epoch {epoch+1} (best metric: {best:.6f})")
                        self.model_.load_state_dict(best_state)
                        break
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        X = np.asarray(X, dtype=np.float32)
        if not hasattr(self, "input_shape_"):
            # Fallback to observed shape
            self.input_shape_ = tuple(X.shape[1:])
        # Validate and prepare
        if self.preserve_shape:
            X_arr = np.moveaxis(X, -1, 1) if self.data_format == "channels_last" else X
            if X_arr.shape[1] != self._internal_input_shape_cf_[0]:
                raise ValueError("X channels mismatch for predict().")
            # Apply conv LSM if configured
            if self.lsm is not None:
                try:
                    from .lsm import LSMConv2dExpander, LSMConv2d
                except Exception:
                    LSMConv2dExpander = None  # type: ignore
                    LSMConv2d = None  # type: ignore
                if X_arr.ndim == 4:
                    if LSMConv2dExpander is not None and isinstance(self.lsm, LSMConv2dExpander):
                        X_arr = self.lsm.transform(X_arr).astype(np.float32, copy=False)
                    elif (LSMConv2d is not None and isinstance(self.lsm, LSMConv2d)) or (hasattr(self.lsm, 'forward') and hasattr(self.lsm, 'out_channels')):
                        with torch.no_grad():
                            X_arr = self.lsm(torch.from_numpy(X_arr).to(device)).cpu().numpy().astype(np.float32, copy=False)
        else:
            if tuple(X.shape[1:]) != self.input_shape_:
                if int(np.prod(X.shape[1:])) != int(np.prod(self.input_shape_)):
                    raise ValueError(
                        f"X has shape {X.shape[1:]}, expected {self.input_shape_} (prod must match)."
                    )
            X_arr = self._flatten(X)
        device = self._device()
        self.model_.eval()
        with torch.no_grad():
            Xin = torch.from_numpy(X_arr).to(device)
            # Apply LSM transform if configured (flattened path)
            if self.lsm is not None and not self.preserve_shape:
                try:
                    from .lsm import LSMExpander
                except Exception:
                    LSMExpander = None  # type: ignore
                lsm_model = None
                if LSMExpander is not None and isinstance(self.lsm, LSMExpander):
                    lsm_model = self.lsm.model
                elif hasattr(self.lsm, 'forward'):
                    lsm_model = self.lsm
                if lsm_model is not None:
                    Xin = lsm_model(Xin)
            out = self.model_(Xin).cpu().numpy()
        if self.preserve_shape and self.per_element:
            # Return in input's data_format
            if self.data_format == "channels_last":
                out = np.moveaxis(out, 1, -1)
            return out
        else:
            if out.shape[1] == 1:
                out = out[:, 0]
            return out

    # Stateful inference helpers
    def reset_state(self) -> None:
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if hasattr(self.model_, "reset_state"):
            self.model_.reset_state()

    def step(self, x_t: np.ndarray, y_t: Optional[np.ndarray] = None, update: bool = False) -> np.ndarray:
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if not self.stateful:
            raise RuntimeError("step() requires stateful=True on the estimator.")
        # Prepare single input respecting preserve_shape/flatten
        xt = np.asarray(x_t, dtype=np.float32)
        if xt.ndim == 1:
            xt = xt[None, :]
        if self.preserve_shape:
            xt = np.moveaxis(xt, -1, 1) if self.data_format == "channels_last" else xt
        else:
            xt = xt.reshape(xt.shape[0], -1)
        device = self._device()
        # Temporarily set to train mode to allow state updates
        prev_mode = self.model_.training
        self.model_.train()
        with torch.no_grad():
            out = self.model_(torch.from_numpy(xt).to(device)).cpu().numpy()
        if hasattr(self.model_, "commit_state_updates"):
            self.model_.commit_state_updates()
        # Optional online update with target, without additional state update
        if update and y_t is not None:
            # Ensure streaming optimizer
            if not hasattr(self, "_stream_opt") or self._stream_opt is None:
                self._stream_opt = self._make_optimizer(self.model_, lr=self.stream_lr)
                self._stream_loss = self._make_loss()
            # Disable state updates during gradient pass
            if hasattr(self.model_, "set_state_updates"):
                self.model_.set_state_updates(False)
            self.model_.train()
            opt = self._stream_opt
            loss_fn = self._stream_loss
            opt.zero_grad()
            xb = torch.from_numpy(xt).to(device)
            pred = self.model_(xb)
            yt = np.asarray(y_t, dtype=np.float32)
            if yt.ndim == 0:
                yt = yt[None]
            if yt.ndim == 1:
                yt = yt[:, None]
            yb = torch.from_numpy(yt).to(device)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            if hasattr(self.model_, "commit_state_updates"):
                self.model_.commit_state_updates()
            if hasattr(self.model_, "set_state_updates"):
                self.model_.set_state_updates(True)
        # Restore mode
        self.model_.train(prev_mode)
        if out.shape[1] == 1:
            return out[0, 0]
        return out[0]

    def predict_sequence(self, X_seq: np.ndarray, *, reset_state: bool = True, return_sequence: bool = False) -> np.ndarray:
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if not self.stateful:
            raise RuntimeError("predict_sequence() requires stateful=True on the estimator.")
        Xs = np.asarray(X_seq, dtype=np.float32)
        if Xs.ndim == 3:
            if Xs.shape[0] != 1:
                raise ValueError("Only batch size 1 supported for predict_sequence (got N != 1).")
            Xs = Xs[0]
        if Xs.ndim != 2:
            raise ValueError("X_seq must be (T, D) or (1, T, D)")
        if reset_state:
            self.reset_state()
        outs = []
        for t in range(Xs.shape[0]):
            outs.append(self.step(Xs[t]))
        outs = np.asarray(outs)
        return outs if return_sequence else outs[-1]

    def predict_sequence_online(self, X_seq: np.ndarray, y_seq: np.ndarray, *, reset_state: bool = True) -> np.ndarray:
        """Online prediction with per-step target updates.

        - Preserves internal state across steps (no resets mid-sequence).
        - After each prediction, immediately updates model params with the true target.
        - Returns the sequence of predictions.
        """
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if not self.stateful:
            raise RuntimeError("predict_sequence_online() requires stateful=True")
        Xs = np.asarray(X_seq, dtype=np.float32)
        ys = np.asarray(y_seq, dtype=np.float32)
        if Xs.ndim == 3:
            if Xs.shape[0] != 1:
                raise ValueError("Only batch size 1 supported (got N != 1)")
            Xs = Xs[0]
        if Xs.ndim != 2:
            raise ValueError("X_seq must be (T, D) or (1, T, D)")
        if ys.ndim == 1:
            ys = ys[:, None]
        if ys.shape[0] != Xs.shape[0]:
            raise ValueError("y_seq must match X_seq length")
        if reset_state:
            self.reset_state()
        outs = []
        for t in range(Xs.shape[0]):
            yhat_t = self.step(Xs[t], y_t=ys[t], update=True)
            outs.append(yhat_t)
        return np.asarray(outs)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        y_pred = self.predict(X)
        try:
            return float(_sk_r2_score(y, y_pred))
        except Exception:
            # Minimal R^2 fallback
            y = np.asarray(y)
            y_pred = np.asarray(y_pred)
            u = ((y - y_pred) ** 2).sum()
            v = ((y - y.mean()) ** 2).sum()
            return float(1.0 - (u / v if v != 0 else np.nan))

    # Persistence
    def save(self, path: str) -> None:
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() before save().")
        params = self.get_params(deep=False) if hasattr(self, "get_params") else {}
        meta: Dict[str, Any] = {}
        # Avoid trying to pickle a custom callable in params
        if callable(params.get("loss", None)):
            params["loss"] = "mse"
            meta["note"] = "Original loss was a custom callable and is not serialized; defaulted to 'mse'."
        if hasattr(self, "input_shape_"):
            meta["input_shape"] = tuple(self.input_shape_)
        meta["preserve_shape"] = bool(getattr(self, "preserve_shape", False))
        meta["data_format"] = getattr(self, "data_format", "channels_first")
        if hasattr(self, "_internal_input_shape_cf_"):
            meta["internal_input_shape_cf"] = tuple(self._internal_input_shape_cf_)
        meta["per_element"] = bool(getattr(self, "per_element", False))
        payload = {
            "class": "PSANNRegressor",
            "params": params,
            "state_dict": self.model_.state_dict(),
            "meta": meta,
        }
        torch.save(payload, path)

    @classmethod
    def load(cls, path: str, map_location: Optional[str | torch.device] = None) -> "PSANNRegressor":
        payload = torch.load(path, map_location=map_location or "cpu")
        params = payload.get("params", {})
        obj = cls(**params)
        # Create a temp model to load weights; infer in/out from weights
        state = payload["state_dict"]
        # Build model based on saved state structure (MLP vs Conv)
        # Determine out_dim from either linear head or conv head/fc
        out_dim = None
        if "head.weight" in state:
            out_dim = state["head.weight"].shape[0]
        if out_dim is None and "fc.weight" in state:
            out_dim = state["fc.weight"].shape[0]
        if out_dim is None and "head.weight" in state:
            out_dim = state["head.weight"].shape[0]
        if "body.0.linear.weight" in state:
            if obj.hidden_layers > 0:
                in_dim = state.get("body.0.linear.weight").shape[1]
            else:
                in_dim = state.get("head.weight").shape[1]
            obj.model_ = PSANNNet(
                in_dim,
                out_dim,
                hidden_layers=obj.hidden_layers,
                hidden_width=obj.hidden_width,
                act_kw=obj.activation,
                state_cfg=(obj.state if getattr(obj, "stateful", False) else None),
                w0=obj.w0,
            )
        else:
            # Convolutional
            if "body.0.conv.weight" not in state:
                raise RuntimeError("Unrecognized state dict: cannot determine MLP or Conv architecture.")
            w = state["body.0.conv.weight"]
            in_channels = int(w.shape[1])
            nd = w.ndim - 2
            seg = "head.weight" in state and state["head.weight"].ndim >= 3 and "fc.weight" not in state
            if nd == 1:
                obj.model_ = PSANNConv1dNet(
                    in_channels,
                    int(out_dim),
                    hidden_layers=obj.hidden_layers,
                    hidden_channels=obj.hidden_width,
                    kernel_size=getattr(obj, "conv_kernel_size", 1),
                    act_kw=obj.activation,
                    w0=obj.w0,
                    segmentation_head=seg,
                )
            elif nd == 2:
                obj.model_ = PSANNConv2dNet(
                    in_channels,
                    int(out_dim),
                    hidden_layers=obj.hidden_layers,
                    hidden_channels=obj.hidden_width,
                    kernel_size=getattr(obj, "conv_kernel_size", 1),
                    act_kw=obj.activation,
                    w0=obj.w0,
                    segmentation_head=seg,
                )
            elif nd == 3:
                obj.model_ = PSANNConv3dNet(
                    in_channels,
                    int(out_dim),
                    hidden_layers=obj.hidden_layers,
                    hidden_channels=obj.hidden_width,
                    kernel_size=getattr(obj, "conv_kernel_size", 1),
                    act_kw=obj.activation,
                    w0=obj.w0,
                    segmentation_head=seg,
                )
            else:
                raise RuntimeError("Unsupported convolutional kernel dimensionality in saved state.")
        obj.model_.load_state_dict(state)
        obj.model_.to(choose_device(obj.device))
        # Restore input shape if available
        meta = payload.get("meta", {})
        if "input_shape" in meta:
            obj.input_shape_ = tuple(meta["input_shape"])  # type: ignore[assignment]
        if "preserve_shape" in meta:
            obj.preserve_shape = bool(meta["preserve_shape"])  # type: ignore[assignment]
        if "data_format" in meta:
            obj.data_format = str(meta["data_format"])  # type: ignore[assignment]
        if "internal_input_shape_cf" in meta:
            obj._internal_input_shape_cf_ = tuple(meta["internal_input_shape_cf"])  # type: ignore[assignment]
        if "per_element" in meta:
            obj.per_element = bool(meta["per_element"])  # type: ignore[assignment]
        return obj
