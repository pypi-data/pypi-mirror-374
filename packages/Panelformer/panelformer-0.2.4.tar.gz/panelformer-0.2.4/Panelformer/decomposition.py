"""
decomposition.py

Contains components for time series decomposition including:
- Multi-Scale Moving Average
- Enhanced Trend-Seasonal Decomposition
- Weight Computation for Trend and Seasonal Emphasis
"""

import torch
from torch import nn
import torch.nn.functional as F


class MultiScaleMovingAvg(nn.Module):
    """
    Applies multiple moving averages at different scales and learns a weighted combination.
    """
    def __init__(self, kernel_sizes=[3, 7, 15, 31]):
        super(MultiScaleMovingAvg, self).__init__()
        self.kernel_sizes = kernel_sizes
        self.n_kernels = len(kernel_sizes)

        # Create a learnable weight for each kernel size
        self.kernel_weights = nn.Parameter(torch.ones(self.n_kernels) / self.n_kernels)
        self.softmax = nn.Softmax(dim=0)

    def forward(self, x):
        # x shape: (batch, time, features)
        batch_size, seq_len, n_features = x.shape
        x_permuted = x.permute(0, 2, 1)  # (batch, features, time)

        # Apply moving average with different kernel sizes
        ma_outputs = []
        for k_size in self.kernel_sizes:
            # Create kernel
            kernel = torch.ones(1, 1, k_size, device=x.device) / k_size
            kernel = kernel.repeat(n_features, 1, 1)  # (features, 1, kernel_size)

            # Apply padding
            pad_size = k_size // 2
            x_padded = F.pad(x_permuted, pad=(pad_size, pad_size), mode='replicate')

            # Apply convolution
            ma = F.conv1d(x_padded, kernel, groups=n_features)
            ma_outputs.append(ma.permute(0, 2, 1))  # Back to (batch, time, features)

        # Compute adaptive weights
        weights = self.softmax(self.kernel_weights)

        # Weighted sum of moving averages
        ma_combined = torch.zeros_like(x)
        for i, ma in enumerate(ma_outputs):
            ma_combined += weights[i] * ma

        return ma_combined


class EnhancedSeriesDecomp(nn.Module):
    """
    Decomposes a time series into seasonal and trend components using a multi-scale MA.
    """
    def __init__(self, kernel_sizes=[3, 7, 15, 31]):
        super(EnhancedSeriesDecomp, self).__init__()
        self.moving_avg = MultiScaleMovingAvg(kernel_sizes)

    def forward(self, x):
        # Extract trend using multi-scale moving average
        trend = self.moving_avg(x)
        # Extract seasonal component (residual)
        seasonal = x - trend
        return seasonal, trend


def compute_component_weights(seasonal, trend):
    """
    Compute normalized variance-based weights for seasonal and trend components.
    """
    # Compute variance along the time dimension
    seasonal_var = torch.var(seasonal, dim=1, keepdim=True)  # Shape: (batch, 1, features)
    trend_var = torch.var(trend, dim=1, keepdim=True)        # Shape: (batch, 1, features)

    # Normalize variances to get weights
    total_var = seasonal_var + trend_var
    seasonal_weight = seasonal_var / (total_var + 1e-8)  # Avoid division by zero
    trend_weight = trend_var / (total_var + 1e-8)

    return seasonal_weight, trend_weight
