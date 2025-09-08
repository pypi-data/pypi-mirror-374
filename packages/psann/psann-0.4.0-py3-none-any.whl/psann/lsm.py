from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .utils import choose_device, seed_all


class MaskedLinear(nn.Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = True, sparsity: float = 0.8, random_state: Optional[int] = None):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.linear = nn.Linear(in_features, out_features, bias=bias)
        rs = torch.Generator()
        if random_state is not None:
            rs.manual_seed(int(random_state))
        # mask==1 keeps connection; expected density = 1 - sparsity
        density = max(0.0, min(1.0, 1.0 - float(sparsity)))
        mask = (torch.rand((out_features, in_features), generator=rs) < density).float()
        self.register_buffer("mask", mask)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.linear.weight * self.mask
        return F.linear(x, w, self.linear.bias)


class LSM(nn.Module):
    """Liquid State Machine-inspired expander (feed-forward, sparse layers).

    Expands input features to a higher-dimensional representation using sparse linear
    layers and a configurable nonlinearity. Intended as a learnable preprocessing step.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_width: int = 128,
        sparsity: float = 0.8,
        nonlinearity: str = "sine",
        bias: bool = True,
        random_state: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.input_dim = int(input_dim)
        self.output_dim = int(output_dim)
        self.hidden_layers = int(hidden_layers)
        self.hidden_width = int(hidden_width)
        self.sparsity = float(sparsity)
        self.nonlinearity = nonlinearity

        act = {
            "sine": torch.sin,
            "tanh": torch.tanh,
            "relu": F.relu,
        }.get(nonlinearity)
        if act is None:
            raise ValueError("nonlinearity must be one of: sine, tanh, relu")
        self._act = act

        layers = []
        in_dim = self.input_dim
        for i in range(self.hidden_layers):
            layers.append(MaskedLinear(in_dim, self.hidden_width, bias=bias, sparsity=self.sparsity, random_state=None if random_state is None else random_state + i))
            in_dim = self.hidden_width
        self.body = nn.Sequential(*layers)
        self.head = MaskedLinear(in_dim, self.output_dim, bias=bias, sparsity=self.sparsity, random_state=None if random_state is None else random_state + 999)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, input_dim)
        z = x
        for layer in self.body:
            z = self._act(layer(z))
        z = self.head(z)
        return z


class LSMExpander:
    """Trainable expander that optimizes an OLS reconstruction objective.

    Objective: Learn parameters of the LSM such that a linear OLS readout from
    the expanded features can reconstruct the original inputs with high R^2.
    """

    def __init__(
        self,
        output_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_width: int = 128,
        sparsity: float = 0.8,
        nonlinearity: str = "sine",
        epochs: int = 100,
        lr: float = 1e-3,
        ridge: float = 1e-4,
        batch_size: int = 256,
        device: str | torch.device = "auto",
        random_state: Optional[int] = None,
        early_stopping: bool = False,
        patience: int = 20,
        tol: float = 1e-6,
        val_split: Optional[float] = None,
        verbose: int = 0,
    ) -> None:
        self.output_dim = int(output_dim)
        self.hidden_layers = hidden_layers
        self.hidden_width = hidden_width
        self.sparsity = sparsity
        self.nonlinearity = nonlinearity
        self.epochs = epochs
        self.lr = lr
        self.ridge = ridge
        self.batch_size = batch_size
        self.device = device
        self.random_state = random_state
        self.early_stopping = early_stopping
        self.patience = patience
        self.tol = tol
        self.val_split = val_split
        self.verbose = verbose

        self.model: Optional[LSM] = None
        self.W_: Optional[torch.Tensor] = None  # OLS readout (output_dim -> input_dim)

    def _device(self) -> torch.device:
        return choose_device(self.device)

    def _ols_readout(self, Z: torch.Tensor, X: torch.Tensor, ridge: float) -> torch.Tensor:
        # Add bias term
        ones = torch.ones((Z.shape[0], 1), dtype=Z.dtype, device=Z.device)
        Zb = torch.cat([Z, ones], dim=1)
        # Solve (Zb^T Zb + ridge I) W = Zb^T X
        A = Zb.T @ Zb
        I = torch.eye(A.shape[0], dtype=A.dtype, device=A.device)
        b = Zb.T @ X
        W = torch.linalg.solve(A + ridge * I, b)
        return W  # shape: (out_dim+1, in_dim)

    def fit(
        self,
        X: np.ndarray,
        epochs: Optional[int] = None,
        *,
        validation_data: Optional[np.ndarray] = None,
        val_split: Optional[float] = None,
        early_stopping: Optional[bool] = None,
        patience: Optional[int] = None,
        tol: Optional[float] = None,
        verbose: Optional[int] = None,
    ) -> "LSMExpander":
        seed_all(self.random_state)
        X = np.asarray(X, dtype=np.float32)
        n_features = X.shape[1]
        device = self._device()
        self.model = LSM(n_features, self.output_dim, hidden_layers=self.hidden_layers, hidden_width=self.hidden_width, sparsity=self.sparsity, nonlinearity=self.nonlinearity, random_state=self.random_state).to(device)
        opt = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        # Resolve control params
        es = self.early_stopping if early_stopping is None else bool(early_stopping)
        pat = int(self.patience if patience is None else patience)
        tolerance = float(self.tol if tol is None else tol)
        verb = int(self.verbose if verbose is None else verbose)
        vs = self.val_split if val_split is None else val_split
        E = int(epochs) if epochs is not None else (10000 if es else self.epochs)

        # Train/val split
        if validation_data is not None:
            X_tr = X
            X_va = np.asarray(validation_data, dtype=np.float32)
        elif vs is not None or es:
            frac = 0.1 if vs is None else float(vs)
            frac = min(max(frac, 0.0), 0.9)
            n = X.shape[0]
            n_val = max(1, int(n * frac))
            rs = np.random.RandomState(self.random_state)
            idx = np.arange(n)
            rs.shuffle(idx)
            va_idx = idx[:n_val]
            tr_idx = idx[n_val:]
            X_tr = X[tr_idx]
            X_va = X[va_idx]
        else:
            X_tr = X
            X_va = None

        X_tr_t = torch.from_numpy(X_tr).to(device)
        X_va_t = torch.from_numpy(X_va).to(device) if X_va is not None else None

        best_r2 = -float("inf")
        best_state = None
        patience_left = pat

        # Full-batch optimization of LSM with OLS-in-the-loop readout
        for epoch in range(E):
            self.model.train()
            opt.zero_grad()
            Z_tr = self.model(X_tr_t)
            W = self._ols_readout(Z_tr, X_tr_t, ridge=self.ridge)
            ones_tr = torch.ones((Z_tr.shape[0], 1), dtype=Z_tr.dtype, device=Z_tr.device)
            Zb_tr = torch.cat([Z_tr, ones_tr], dim=1)
            X_hat_tr = Zb_tr @ W
            ss_res_tr = ((X_tr_t - X_hat_tr) ** 2).sum()
            ss_tot_tr = ((X_tr_t - X_tr_t.mean(dim=0, keepdim=True)) ** 2).sum().clamp_min(1e-8)
            loss = ss_res_tr / ss_tot_tr
            loss.backward()
            opt.step()

            # Validation R^2 using same W
            if X_va_t is not None:
                self.model.eval()
                with torch.no_grad():
                    Z_va = self.model(X_va_t)
                    ones_va = torch.ones((Z_va.shape[0], 1), dtype=Z_va.dtype, device=Z_va.device)
                    Zb_va = torch.cat([Z_va, ones_va], dim=1)
                    X_hat_va = Zb_va @ W
                    ss_res_va = ((X_va_t - X_hat_va) ** 2).sum()
                    ss_tot_va = ((X_va_t - X_va_t.mean(dim=0, keepdim=True)) ** 2).sum().clamp_min(1e-8)
                    r2_va = float(1.0 - (ss_res_va / ss_tot_va))
                if verb:
                    print(f"LSMExpander epoch {epoch+1}/{E} - val R^2: {r2_va:.6f}")
                if r2_va > best_r2 + tolerance:
                    best_r2 = r2_va
                    best_state = {k: v.detach().cpu().clone() for k, v in self.model.state_dict().items()}
                    patience_left = pat
                else:
                    patience_left -= 1
                    if es and patience_left <= 0:
                        if verb:
                            print(f"Early stopping LSM at epoch {epoch+1} (best R^2: {best_r2:.6f})")
                        break

        # Restore best state if available
        if best_state is not None:
            self.model.load_state_dict(best_state)
        self.model.eval()
        with torch.no_grad():
            X_all_t = torch.from_numpy(X).to(device)
            Z_all = self.model(X_all_t)
            self.W_ = self._ols_readout(Z_all, X_all_t, ridge=self.ridge).detach().cpu()
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LSMExpander not fitted; call fit() first or set .model externally.")
        X = np.asarray(X, dtype=np.float32)
        device = next(self.model.parameters()).device
        with torch.no_grad():
            Z = self.model(torch.from_numpy(X).to(device)).cpu().numpy()
        return Z

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)

    def score_reconstruction(self, X: np.ndarray) -> float:
        if self.model is None or self.W_ is None:
            raise RuntimeError("LSMExpander not fitted")
        X = np.asarray(X, dtype=np.float32)
        device = next(self.model.parameters()).device
        with torch.no_grad():
            Z = self.model(torch.from_numpy(X).to(device))
            ones = torch.ones((Z.shape[0], 1), dtype=Z.dtype, device=Z.device)
            Zb = torch.cat([Z, ones], dim=1)
            X_hat = Zb @ self.W_.to(device)
            ss_res = ((torch.from_numpy(X).to(device) - X_hat) ** 2).sum()
            ss_tot = ((torch.from_numpy(X).to(device) - torch.from_numpy(X).to(device).mean(dim=0, keepdim=True)) ** 2).sum().clamp_min(1e-8)
            r2 = 1.0 - float(ss_res.cpu() / ss_tot.cpu())
        return r2


# ----------------------------- Conv2d Variant -----------------------------

class MaskedConv2d(nn.Conv2d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 1, bias: bool = True, sparsity: float = 0.8, random_state: Optional[int] = None):
        super().__init__(in_channels, out_channels, kernel_size=kernel_size, padding=0, bias=bias)
        rs = torch.Generator()
        if random_state is not None:
            rs.manual_seed(int(random_state))
        k = self.kernel_size[0] * self.kernel_size[1]
        density = max(0.0, min(1.0, 1.0 - float(sparsity)))
        mask = (torch.rand((out_channels, in_channels, self.kernel_size[0], self.kernel_size[1]), generator=rs) < density).float()
        self.register_buffer("mask", mask)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.weight * self.mask
        return F.conv2d(x, w, self.bias, stride=self.stride, padding=self.padding, dilation=self.dilation, groups=self.groups)


class LSMConv2d(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        hidden_layers: int = 1,
        hidden_channels: int = 128,
        kernel_size: int = 1,
        sparsity: float = 0.8,
        nonlinearity: str = "sine",
        bias: bool = True,
        random_state: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        act = {
            "sine": torch.sin,
            "tanh": torch.tanh,
            "relu": F.relu,
        }.get(nonlinearity)
        if act is None:
            raise ValueError("nonlinearity must be one of: sine, tanh, relu")
        self._act = act

        layers = []
        c = in_channels
        for i in range(hidden_layers):
            layers.append(MaskedConv2d(c, hidden_channels, kernel_size=kernel_size, bias=bias, sparsity=sparsity, random_state=None if random_state is None else random_state + i))
            c = hidden_channels
        self.body = nn.Sequential(*layers)
        self.head = MaskedConv2d(c, out_channels, kernel_size=kernel_size, bias=bias, sparsity=sparsity, random_state=None if random_state is None else random_state + 777)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = x
        for layer in self.body:
            z = self._act(layer(z))
        z = self.head(z)
        return z


class LSMConv2dExpander:
    """Conv2d expander optimizing an OLS per-pixel reconstruction objective.

    Treats the readout as a 1x1 convolution learned in closed form via ridge-OLS by flattening N*H*W.
    """

    def __init__(
        self,
        out_channels: int,
        *,
        hidden_layers: int = 1,
        hidden_channels: int = 128,
        kernel_size: int = 1,
        sparsity: float = 0.8,
        nonlinearity: str = "sine",
        epochs: int = 50,
        lr: float = 1e-3,
        ridge: float = 1e-4,
        device: str | torch.device = "auto",
        random_state: Optional[int] = None,
    ) -> None:
        self.out_channels = int(out_channels)
        self.hidden_layers = hidden_layers
        self.hidden_channels = hidden_channels
        self.kernel_size = kernel_size
        self.sparsity = sparsity
        self.nonlinearity = nonlinearity
        self.epochs = epochs
        self.lr = lr
        self.ridge = ridge
        self.device = device
        self.random_state = random_state
        self.model: Optional[LSMConv2d] = None
        self.W_: Optional[torch.Tensor] = None  # (C_out+1, C_in)

    def _device(self) -> torch.device:
        return choose_device(self.device)

    def _ols_readout(self, Z: torch.Tensor, X: torch.Tensor, ridge: float) -> torch.Tensor:
        # Z: (N, C_out, H, W) -> (N*H*W, C_out)
        N, C_out, H, W = Z.shape
        Zf = Z.permute(0, 2, 3, 1).reshape(-1, C_out)
        Cin = X.shape[1]
        ones = torch.ones((Zf.shape[0], 1), dtype=Z.dtype, device=Z.device)
        Zb = torch.cat([Zf, ones], dim=1)
        A = Zb.T @ Zb
        I = torch.eye(A.shape[0], dtype=A.dtype, device=A.device)
        Xf = X.permute(0, 2, 3, 1).reshape(-1, Cin)
        b = Zb.T @ Xf
        W = torch.linalg.solve(A + ridge * I, b)
        return W  # (C_out+1, C_in)

    def fit(self, X: np.ndarray, epochs: Optional[int] = None) -> "LSMConv2dExpander":
        seed_all(self.random_state)
        X = np.asarray(X, dtype=np.float32)
        assert X.ndim == 4, "Expected channels-first (N, C, H, W) input"
        N, Cin, H, W = X.shape
        device = self._device()
        self.model = LSMConv2d(Cin, self.out_channels, hidden_layers=self.hidden_layers, hidden_channels=self.hidden_channels, kernel_size=self.kernel_size, sparsity=self.sparsity, nonlinearity=self.nonlinearity, random_state=self.random_state).to(device)
        opt = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        E = int(epochs) if epochs is not None else self.epochs
        X_t = torch.from_numpy(X).to(device)
        for _ in range(E):
            self.model.train()
            opt.zero_grad()
            Z = self.model(X_t)
            W = self._ols_readout(Z, X_t, ridge=self.ridge)
            # Reconstruct with 1x1 conv via channel-wise linear map
            Zf = Z.permute(0, 2, 3, 1).reshape(-1, Z.shape[1])
            ones = torch.ones((Zf.shape[0], 1), dtype=Z.dtype, device=Z.device)
            Zbf = torch.cat([Zf, ones], dim=1)
            Xf_hat = Zbf @ W
            Xf = X_t.permute(0, 2, 3, 1).reshape(-1, Cin)
            ss_res = ((Xf - Xf_hat) ** 2).sum()
            ss_tot = ((Xf - Xf.mean(dim=0, keepdim=True)) ** 2).sum().clamp_min(1e-8)
            loss = ss_res / ss_tot
            loss.backward()
            opt.step()

        # Store final readout
        self.model.eval()
        with torch.no_grad():
            Z = self.model(X_t)
            self.W_ = self._ols_readout(Z, X_t, ridge=self.ridge).detach().cpu()
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LSMConv2dExpander not fitted")
        X = np.asarray(X, dtype=np.float32)
        with torch.no_grad():
            Z = self.model(torch.from_numpy(X).to(self._device())).cpu().numpy()
        return Z

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)
