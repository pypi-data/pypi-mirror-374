# PSANN Technical Details

This document explains the core components of PSANN, the math behind the sine activation with learned parameters, the stateful time-series extensions, and directions for further research.

## 1) Parameterized Sine Activation

Given a pre-activation vector z (e.g., z = xW + b), the unit output is

    h = A · exp(−d · g(z)) · sin(f · z)

where A (amplitude), f (frequency), and d (decay) are learnable scalars per output feature (neuron). The decay function g(·) controls how amplitude diminishes with activation magnitude:

- abs: g(z) = |z|
- relu: g(z) = max(0, z)
- none: g(z) = 0 (no decay)

Parameterization:

- A, f, d are stored in an unconstrained space and mapped through softplus to keep them positive and stable.
- Optional bounds clamp values post-transform.
- Weight initialization uses SIREN-style heuristics to maintain gradient flow at start.

Intuition:

- f scales oscillation, A scales amplitude, and d adds an envelope that attenuates with |z| (or only for positive z via relu), which helps stabilize extreme activations and encourages compact representations of oscillatory signals.

## 2) PSANN Blocks and Networks

- PSANNBlock: Linear -> SineParam. Optionally integrates a persistent state controller (see §3).
- PSANNNet: MLP stack of PSANNBlocks with a linear head.
- Conv variants (PSANNConv1d/2d/3d): ConvNd -> SineParam across channels -> optional global average pool -> linear head. With per-element (segmentation) mode, the head is a 1×1 ConvNd returning outputs at each position.

## 3) Persistent State for Time Series

Each PSANNBlock can maintain a per-feature “amplitude-like” state s that modulates activations over time. The state is updated from the magnitude of the current activations and clipped to avoid explosion.

Update rule per feature:

    s_t ← ρ · s_{t−1} + (1 − ρ) · β · E[|y_t|]
    s_t ← max_abs · tanh(s_t / max_abs)

where ρ ∈ (0, 1) controls persistence, β scales updates, and max_abs bounds the state using a smooth tanh saturation. The expectation E is taken over non-feature dimensions (batch/spatial), producing a feature-wise update.

Implementation details:

- During forward, state values are used to scale activations. Parameter updates to the state are deferred and committed safely after each optimizer step to avoid autograd in-place issues.
- A detach flag controls whether the state used for scaling participates in the computation graph (attached vs detached semantics).
- Training reset policy: `state_reset` ∈ {batch, epoch, none} controls reset frequency; shuffling is disabled when state spans across batches.

Streaming API:

- step(x_t, y_t=None, update=False): emits a prediction and (optionally) performs an immediate gradient update using the provided target while keeping the current state (no additional state update during the gradient pass).
- predict_sequence_online(X_seq, y_seq): iterates over a sequence, applying per-step updates to prevent error compounding.

## 4) Multi-Dimensional Inputs

Two modes support general input shapes X ∈ R^{N×…}:

- Flattened MLP: flatten features to (N, F).
- Preserve shape with ConvNd: channels-first internal layout; supports both channels-first and channels-last inputs; optional per-element head.

Gaussian input noise for regularization can be scalar, per-feature vector (flattened size), or a tensor matching the original feature shape (broadcasted appropriately in both modes).

## 5) Loss Functions

Built-in: mse/l2, l1/mae, smooth_l1 (β), huber (δ).
Custom: pass a callable loss that returns a tensor or scalar; reduction is applied as configured (mean/sum/none).

## 6) Initialization and Stability

- Linear layers use SIREN-inspired uniform inits to keep gradients healthy.
- Sine parameters are softplus-mapped; decay introduces a stabilizing envelope.
- State updates are bounded by tanh, and deferred application avoids in-place autograd issues.

## 7) Research Directions

1. Frequency/Amplitude Scheduling and Priors
   - Spectral regularization on f to bias networks toward certain frequency bands.
   - Parameter tying across layers or learned gating networks controlling A, f, d.

2. Physics-Informed and Hybrid Models
   - Constrain f and d to physical regimes (e.g., damped harmonic motion), or add physics penalties to the loss.
   - Couple PSANN blocks with classical filters (Kalman-like) or ARIMA components.

3. State Dynamics and RNN Hybrids
   - Learn the state update (ρ, β, max_abs) or replace it with a tiny gated network.
   - Truncated BPTT windows with sequence-aware batching and curriculum schedules.

4. Spatial Models and Per-Element Outputs
   - Deeper conv PSANNs with multi-scale features; attention over spatial tokens.
   - Segmentation and dense forecasting with spatiotemporal consistency regularizers.

5. Representation Learning
   - Self-supervised objectives (contrastive/predictive coding) before fine-tuning.
   - Frequency-domain pretext tasks to align sine parameters to data spectra.

6. Robustness and Calibration
   - Uncertainty estimation (ensembles, MC dropout) for time-series forecasts.
   - Robust losses (Huber variants) and constraints to mitigate drift.

7. Deployment and Acceleration

   - torch.compile/ONNX export; kernel fusion for sine + exp; quantization-aware training.

## 8) Practical Guidance

- Start with modest hidden width (32–128) and 2–3 layers; tune f and d in activation config for your domain.
- For long sequences, prefer detached state during streaming; use `stream_lr` lower than training `lr`.
- When preserving shape, begin with `conv_kernel_size=1` and widen channels before increasing kernel size.
- Prefer SmoothL1/Huber on noisy targets.

