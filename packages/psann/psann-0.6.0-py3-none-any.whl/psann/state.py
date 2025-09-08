from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn


class StateController(nn.Module):
    """Persistent per-feature state with bounded updates.

    Intended to modulate amplitude over time while preventing explosion.

    Update rule (per feature):
        s <- rho * s + (1 - rho) * beta * reduce(mean(abs(y), over batch/spatial))
        s <- clip(s)  # tanh scaling to [-max_abs, max_abs]

    Applied as an amplitude multiplier on activations: y <- s * y
    """

    def __init__(
        self,
        size: int,
        *,
        init: float = 1.0,
        rho: float = 0.95,
        beta: float = 1.0,
        max_abs: float = 5.0,
        detach: bool = True,
    ) -> None:
        super().__init__()
        assert size > 0
        self.size = int(size)
        self.rho = float(rho)
        self.beta = float(beta)
        self.max_abs = float(max_abs)
        self.detach = bool(detach)

        state = torch.full((self.size,), float(init))
        self.register_buffer("state", state)

    def reset(self, value: Optional[float] = None) -> None:
        v = float(value) if value is not None else float(self.state.mean().item())
        with torch.no_grad():
            self.state.fill_(v)

    def reset_like_init(self, init: float = 1.0) -> None:
        with torch.no_grad():
            self.state.fill_(float(init))

    def apply(self, y: torch.Tensor, feature_dim: int, update: bool = True) -> torch.Tensor:
        # Use a detached copy of state for forward to avoid versioning issues
        fd = feature_dim if feature_dim >= 0 else (y.ndim + feature_dim)
        shape = [1] * y.ndim
        shape[fd] = self.size
        # Use detached state for forward if detach=True, else use live buffer
        s = (self.state.detach() if self.detach else self.state).view(*shape)
        y_scaled = y * s

        if update:
            # Compute proposed new state based on scaled activation magnitude
            reduce_dims = [d for d in range(y_scaled.ndim) if d != fd]
            if reduce_dims:
                m = y_scaled.abs().mean(dim=reduce_dims)
            else:
                m = y_scaled.abs()
            new_s = self.rho * self.state + (1.0 - self.rho) * (self.beta * m)
            new_s = self.max_abs * torch.tanh(new_s / max(self.max_abs, 1e-6))
            if self.detach:
                new_s = new_s.detach()
            # Defer commit until after backward
            self._pending_state = new_s
        return y_scaled

    def commit(self) -> None:
        new_s = getattr(self, "_pending_state", None)
        if new_s is None:
            return
        with torch.no_grad():
            self.state.copy_(new_s)
        self._pending_state = None
