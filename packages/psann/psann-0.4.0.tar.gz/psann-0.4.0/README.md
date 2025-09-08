# PSANN — Parameterized Sine-Activated Neural Networks

Sklearn-style estimators powered by PyTorch. PSANN uses sine activations with learnable amplitude, frequency, and decay, plus optional persistent state for time series, conv variants that preserve spatial shape, and a segmentation head for per-element outputs.

• Docs: see TECHNICAL_DETAILS.md for math and design.

## Features

- Sklearn API: `fit`, `predict`, `score`, `get_params`, `set_params`.
- SineParam activation: learnable amplitude/frequency/decay with stable transforms and bounds.
- Multi-D inputs: flatten automatically (MLP) or preserve shape with Conv1d/2d/3d PSANN blocks.
- Segmentation head: per-timestep/pixel outputs via 1×1 ConvNd head.
- Stateful time series: persistent per-unit amplitude-like state with bounded updates and controlled resets.
- Online streaming: `step` and `predict_sequence_online` with per-step target updates; separate `stream_lr`.
- Training ergonomics: verbose logging, validation, early stopping, Gaussian input noise, multiple losses (MSE/L1/Huber/SmoothL1) or custom callable.
- Save/load: torch checkpoints with estimator params and metadata.

## Installation

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate     # macOS/Linux
pip install --upgrade pip
pip install -e .                # editable install from source
```

Optional plotting for examples:

```bash
pip install .[viz]
```

## Quick Start

```python
import numpy as np
from psann import PSANNRegressor

rs = np.random.RandomState(42)
X = np.linspace(-4, 4, 1000).reshape(-1, 1).astype(np.float32)
y = 0.8 * np.exp(-0.25 * np.abs(X)) * np.sin(3.5 * X) + 0.05 * rs.randn(*X.shape)

model = PSANNRegressor(
    hidden_layers=2,
    hidden_width=64,
    epochs=200,
    lr=1e-3,
    activation={"amplitude_init": 1.0, "frequency_init": 1.0, "decay_init": 0.1},
    early_stopping=True,
    patience=20,
)
model.fit(X, y, verbose=1)
print("R^2:", model.score(X, y))
```

## Stateful Time Series (Streaming)

Train with one-step pairs, then stream predictions while preserving state. Use online updates to avoid compounding errors.

```python
model = PSANNRegressor(
    hidden_layers=2,
    hidden_width=32,
    epochs=200,
    lr=1e-3,
    stateful=True,
    state={"rho": 0.985, "beta": 1.0, "max_abs": 3.0, "init": 1.0, "detach": True},
    state_reset="none",
    stream_lr=3e-4,
)
model.fit(X_train, y_train, validation_data=(X_val, y_val), verbose=1)

# Free-run over a sequence
free_preds = model.predict_sequence(X_test, reset_state=True, return_sequence=True)

# Online (per-step update using targets)
online_preds = model.predict_sequence_online(X_test, y_test, reset_state=True)
```

## Multi-D Inputs and Segmentation

- Flattened MLP (default): `(N, ...) -> (N, F)`.
- Preserve shape with conv PSANN: `preserve_shape=True`, `data_format="channels_first|last"`.
- Per-element outputs: `per_element=True` swaps the global pooling head for a 1×1 ConvNd head.

```python
# Channels-first images: (N, C, H, W)
X = np.random.randn(256, 1, 8, 8).astype(np.float32)
y = np.sin(X).astype(np.float32)  # per-pixel

model = PSANNRegressor(preserve_shape=True, data_format="channels_first", per_element=True,
                       hidden_layers=2, hidden_width=24, conv_kernel_size=3, epochs=20)
model.fit(X, y)
Yhat = model.predict(X[:4])      # (4, 1, 8, 8)
```

## Examples

- `examples/01_basic_regression.py`: minimal 1D regression with PSANNRegressor.
- `examples/02_verbose_val_noise.py`: verbose training, validation data, Gaussian noise.
- `examples/03_custom_loss.py`: custom (MAPE-style) loss and save/load note.
- `examples/04_multidim_flatten_mlp.py`: multi-D inputs via flattened MLP.
- `examples/05_conv_preserve_shape_regression.py`: shape-preserving conv PSANN for vector targets.
- `examples/06_segmentation_2d.py`: per-pixel outputs with segmentation head.
- `examples/07_recurrent_forecasting.py`: stateful forecasting with step/sequence APIs.
- `examples/08_psann_vs_lstm.py`: stateful PSANN vs LSTM on modulated sine.
- `examples/09_stateful_attached_vs_lstm.py`: attached updates (detach=False) vs LSTM.
- `examples/10_2d_timeseries_attention_vs_lstm.py`: PSANN encoder + Transformer attention vs LSTM.
- `examples/11_2d_classification_psann_vs_cnn.py`: PSANN conv vs simple CNN.
- `examples/12_online_streaming_updates.py`: online per-step updates to avoid compounding errors.
- `examples/13_online_vs_freerun_plot.py`: visualization of free-run vs online-updated predictions.

## Optional LSM Preprocessor

You can pre-train a liquid-state-machine style expander to increase feature dimensionality before PSANN. The expander is trained to maximize OLS R^2 of reconstructing inputs from expanded features.

```python
from psann import LSMExpander, PSANNRegressor

X = ...  # (N, D)
lsm = LSMExpander(output_dim=256, hidden_layers=2, hidden_width=128, sparsity=0.9)
lsm.fit(X, epochs=50)

model = PSANNRegressor(hidden_layers=2, hidden_width=64, lsm=lsm, lsm_train=False)
model.fit(X_train, y_train)

# Jointly fine-tune LSM while training PSANN
model = PSANNRegressor(hidden_layers=2, hidden_width=64, lsm=lsm, lsm_train=True, lsm_lr=5e-4)
model.fit(X_train, y_train, validation_data=(X_val, y_val), verbose=1)
```

## PyPI Publishing

```bash
pip install build twine
python -m build         # creates sdist + wheel in dist/
twine check dist/*
twine upload dist/*     # requires PyPI credentials
```

Ensure `pyproject.toml` metadata (name, authors, URLs) reflects your project before uploading.

## License

MIT (see LICENSE).

## Technical Details

See TECHNICAL_DETAILS.md for the activation math, state update rule, conv design, training behavior, and research ideas.
