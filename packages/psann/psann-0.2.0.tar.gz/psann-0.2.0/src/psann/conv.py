from __future__ import annotations

from typing import Optional, Sequence

import torch
import torch.nn as nn

from .activations import SineParam
from .utils import init_siren_linear_


class _PSANNConvBlockNd(nn.Module):
    def __init__(
        self,
        conv: nn.Module,
        out_channels: int,
        *,
        act_kw: Optional[dict] = None,
    ) -> None:
        super().__init__()
        self.conv = conv
        act_kw = dict(act_kw or {})
        act_kw.setdefault("feature_dim", 1)  # channel dimension
        self.act = SineParam(out_channels, **act_kw)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.conv(x)
        return self.act(z)


class PSANNConv1dNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_channels: int = 64,
        kernel_size: int | Sequence[int] = 1,
        act_kw: Optional[dict] = None,
        w0: float = 30.0,
        segmentation_head: bool = False,
    ) -> None:
        super().__init__()
        ks = kernel_size if isinstance(kernel_size, int) else int(kernel_size[0])

        layers = []
        c = in_channels
        for i in range(hidden_layers):
            conv = nn.Conv1d(c, hidden_channels, kernel_size=ks, padding=(ks // 2 if ks > 1 else 0))
            block = _PSANNConvBlockNd(conv, hidden_channels, act_kw=act_kw)
            layers.append(block)
            c = hidden_channels
        self.body = nn.Sequential(*layers)
        self.segmentation_head = segmentation_head
        if segmentation_head:
            self.head = nn.Conv1d(c, out_dim, kernel_size=1)
        else:
            self.pool = nn.AdaptiveAvgPool1d(1)
            self.fc = nn.Linear(c, out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, C, L)
        if len(self.body) > 0:
            x = self.body(x)
        if self.segmentation_head:
            return self.head(x)  # (N, out_dim, L)
        x = self.pool(x).squeeze(-1)  # (N, C)
        return self.fc(x)


class PSANNConv2dNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_channels: int = 64,
        kernel_size: int | Sequence[int] = 1,
        act_kw: Optional[dict] = None,
        w0: float = 30.0,
        segmentation_head: bool = False,
    ) -> None:
        super().__init__()
        ks = kernel_size if isinstance(kernel_size, int) else int(kernel_size[0])

        layers = []
        c = in_channels
        for i in range(hidden_layers):
            conv = nn.Conv2d(c, hidden_channels, kernel_size=ks, padding=(ks // 2 if ks > 1 else 0))
            block = _PSANNConvBlockNd(conv, hidden_channels, act_kw=act_kw)
            layers.append(block)
            c = hidden_channels
        self.body = nn.Sequential(*layers)
        self.segmentation_head = segmentation_head
        if segmentation_head:
            self.head = nn.Conv2d(c, out_dim, kernel_size=1)
        else:
            self.pool = nn.AdaptiveAvgPool2d(1)
            self.fc = nn.Linear(c, out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, C, H, W)
        if len(self.body) > 0:
            x = self.body(x)
        if self.segmentation_head:
            return self.head(x)  # (N, out_dim, H, W)
        x = self.pool(x).flatten(1)  # (N, C)
        return self.fc(x)


class PSANNConv3dNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_channels: int = 64,
        kernel_size: int | Sequence[int] = 1,
        act_kw: Optional[dict] = None,
        w0: float = 30.0,
        segmentation_head: bool = False,
    ) -> None:
        super().__init__()
        ks = kernel_size if isinstance(kernel_size, int) else int(kernel_size[0])

        layers = []
        c = in_channels
        for i in range(hidden_layers):
            conv = nn.Conv3d(c, hidden_channels, kernel_size=ks, padding=(ks // 2 if ks > 1 else 0))
            block = _PSANNConvBlockNd(conv, hidden_channels, act_kw=act_kw)
            layers.append(block)
            c = hidden_channels
        self.body = nn.Sequential(*layers)
        self.segmentation_head = segmentation_head
        if segmentation_head:
            self.head = nn.Conv3d(c, out_dim, kernel_size=1)
        else:
            self.pool = nn.AdaptiveAvgPool3d(1)
            self.fc = nn.Linear(c, out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, C, D, H, W)
        if len(self.body) > 0:
            x = self.body(x)
        if self.segmentation_head:
            return self.head(x)  # (N, out_dim, D, H, W)
        x = self.pool(x).flatten(1)  # (N, C)
        return self.fc(x)
