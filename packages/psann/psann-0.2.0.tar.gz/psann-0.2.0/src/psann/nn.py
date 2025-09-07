from __future__ import annotations

from typing import Dict, Optional

import torch
import torch.nn as nn

from .activations import SineParam
from .utils import init_siren_linear_
from .state import StateController


class PSANNBlock(nn.Module):
    """Linear layer followed by parameterized sine activation.

    Optional per-feature persistent state acts as an amplitude modulator.
    """

    def __init__(self, in_features: int, out_features: int, *, act_kw: Optional[Dict] = None, state_cfg: Optional[Dict] = None) -> None:
        super().__init__()
        act_kw = act_kw or {}
        self.linear = nn.Linear(in_features, out_features)
        self.act = SineParam(out_features, **act_kw)
        self.state_ctrl = StateController(out_features, **state_cfg) if state_cfg else None
        self.enable_state_updates = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.linear(x)
        y = self.act(z)
        if self.state_ctrl is not None:
            update_flag = self.training and self.enable_state_updates
            y = self.state_ctrl.apply(y, feature_dim=1, update=update_flag)  # (N, F)
        return y


class PSANNNet(nn.Module):
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_width: int = 64,
        act_kw: Optional[Dict] = None,
        state_cfg: Optional[Dict] = None,
        w0: float = 30.0,
    ) -> None:
        super().__init__()
        act_kw = act_kw or {}

        layers = []
        prev = input_dim
        for i in range(hidden_layers):
            block = PSANNBlock(prev, hidden_width, act_kw=act_kw, state_cfg=state_cfg)
            layers.append(block)
            prev = hidden_width
        self.body = nn.Sequential(*layers)
        self.head = nn.Linear(prev, output_dim)

        # SIREN-inspired initialization
        if hidden_layers > 0:
            if isinstance(self.body[0], PSANNBlock):
                init_siren_linear_(self.body[0].linear, is_first=True, w0=w0)
            for block in list(self.body)[1:]:
                init_siren_linear_(block.linear, is_first=False, w0=w0)
        init_siren_linear_(self.head, is_first=False, w0=w0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if len(self.body) > 0:
            x = self.body(x)
        return self.head(x)

    def reset_state(self) -> None:
        for m in self.modules():
            if isinstance(m, PSANNBlock) and getattr(m, "state_ctrl", None) is not None:
                # reset to 1.0 by default
                m.state_ctrl.reset_like_init(1.0)

    def commit_state_updates(self) -> None:
        for m in self.modules():
            if isinstance(m, PSANNBlock) and getattr(m, "state_ctrl", None) is not None:
                m.state_ctrl.commit()

    def set_state_updates(self, enabled: bool) -> None:
        for m in self.modules():
            if isinstance(m, PSANNBlock):
                m.enable_state_updates = bool(enabled)
