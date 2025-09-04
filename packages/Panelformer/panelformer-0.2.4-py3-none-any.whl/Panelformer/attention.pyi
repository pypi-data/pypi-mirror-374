import torch
from _typeshed import Incomplete
from torch import nn

class ScaledDotProductAttention(nn.Module):
    dropout: Incomplete
    softmax: Incomplete
    scale: Incomplete
    def __init__(self, dropout: float = None, scale: bool = True) -> None: ...
    def forward(self, q, k, v, mask=None): ...

class SegmentwiseInterpretableMultiHeadAttention(nn.Module):
    n_head: Incomplete
    d_model: Incomplete
    segment_size: Incomplete
    d_k: Incomplete
    dropout: Incomplete
    v_layer: Incomplete
    q_layers: Incomplete
    k_layers: Incomplete
    attention: Incomplete
    w_h: Incomplete
    skip_projection: Incomplete
    def __init__(self, n_head: int, d_model: int, segment_size: int, dropout: float = 0.0) -> None: ...
    def init_weights(self) -> None: ...
    def forward(self, q, k, v, mask=None) -> tuple[torch.Tensor, torch.Tensor]: ...

class CrossEntityAttention(nn.Module):
    hidden_size: Incomplete
    num_heads: Incomplete
    dropout: Incomplete
    d_k: Incomplete
    q_linear: Incomplete
    k_linear: Incomplete
    v_linear: Incomplete
    out_linear: Incomplete
    attn_dropout: Incomplete
    def __init__(self, hidden_size, num_heads, dropout: float = 0.0) -> None: ...
    def forward(self, query, context): ...
