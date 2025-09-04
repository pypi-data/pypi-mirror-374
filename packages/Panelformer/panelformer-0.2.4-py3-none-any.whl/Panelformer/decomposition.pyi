from _typeshed import Incomplete
from torch import nn

class MultiScaleMovingAvg(nn.Module):
    kernel_sizes: Incomplete
    n_kernels: Incomplete
    kernel_weights: Incomplete
    softmax: Incomplete
    def __init__(self, kernel_sizes=[3, 7, 15, 31]) -> None: ...
    def forward(self, x): ...

class EnhancedSeriesDecomp(nn.Module):
    moving_avg: Incomplete
    def __init__(self, kernel_sizes=[3, 7, 15, 31]) -> None: ...
    def forward(self, x): ...

def compute_component_weights(seasonal, trend): ...
