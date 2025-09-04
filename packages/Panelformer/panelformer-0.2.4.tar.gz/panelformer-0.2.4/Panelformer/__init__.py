"""
Panelformer Package

An enhanced panel time series forecasting model built on top of the Temporal Fusion Transformer (TFT),
incorporating cross-entity attention, adaptive trend weighting, and multi-scale decomposition.

Submodules:
- model: Core Panelformer model
- attention: Segment-based and cross-entity attention mechanisms
- decomposition: Series decomposition layers and utilities
- utils: Visualization and evaluation tools
"""
 
from .model import Panelformer
from . import attention
from . import decomposition
from . import utils

__all__ = [
    "Panelformer",
    "attention",
    "decomposition",
    "utils",
]

'''
utils contains:
- plot_residuals : Function to plot residuals of the model predictions.
- plot_actual_vs_predicted : Function to plot actual vs predicted values.
- plot_error_distribution : Function to plot the distribution of prediction errors.
- calculate_metrics : Function to calculate and print detailed regression metrics and plots for model evaluation.
'''