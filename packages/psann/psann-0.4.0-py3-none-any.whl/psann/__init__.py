"""PSANN: Parameterized Sine-Activated Neural Networks.

Sklearn-style API with PyTorch backend.
"""

from .sklearn import PSANNRegressor
from .lsm import LSM, LSMExpander, LSMConv2d, LSMConv2dExpander

__all__ = [
    "PSANNRegressor",
    "LSM",
    "LSMExpander",
    "LSMConv2d",
    "LSMConv2dExpander",
]

__version__ = "0.2.0"
