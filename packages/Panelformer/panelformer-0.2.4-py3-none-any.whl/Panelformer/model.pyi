from .attention import CrossEntityAttention as CrossEntityAttention, SegmentwiseInterpretableMultiHeadAttention as SegmentwiseInterpretableMultiHeadAttention
from .decomposition import EnhancedSeriesDecomp as EnhancedSeriesDecomp, compute_component_weights as compute_component_weights
from _typeshed import Incomplete
from pytorch_forecasting.models.temporal_fusion_transformer import TemporalFusionTransformer

class Panelformer(TemporalFusionTransformer):
    multihead_attn: Incomplete
    decomposition: Incomplete
    trend_processor: Incomplete
    cross_series_attn: Incomplete
    trend_weight_network: Incomplete
    output_layer: Incomplete
    def __init__(self, *args, segment_size: int = 8, decomposition_kernel_sizes=[3, 7, 15, 31], trend_processing_layers: int = 2, use_cross_series_attention: bool = True, adaptive_trend_weight: bool = True, **kwargs) -> None: ...
    def forward(self, x): ...
