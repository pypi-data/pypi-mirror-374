"""
attention.py

Contains attention mechanism modules for time series modeling, including:
- Scaled Dot-Product Attention
- Segment-wise Interpretable Multi-Head Attention
- Cross-Entity Attention

These modules enable temporal and cross-entity dependencies to be captured effectively.
"""

import torch
from torch import nn
import torch.nn.functional as F
import math
from typing import Tuple


class ScaledDotProductAttention(nn.Module):
    """
    Compute scaled dot-product attention with optional dropout and causal masking.
    """
    def __init__(self, dropout: float = None, scale: bool = True):
        super(ScaledDotProductAttention, self).__init__()
        self.dropout = nn.Dropout(p=dropout) if dropout is not None else None
        self.softmax = nn.Softmax(dim=-1)
        self.scale = scale

    def forward(self, q, k, v, mask=None):
        # Compute attention scores
        attn = torch.bmm(q, k.permute(0, 2, 1))  # Query-key overlap

        if self.scale:
            dimension = torch.as_tensor(k.size(-1), dtype=attn.dtype, device=attn.device).sqrt()
            attn = attn / dimension

        # Apply causal mask
        if mask is not None:
            attn = attn.masked_fill(mask, -1e9)

        # Apply softmax and dropout
        attn = self.softmax(attn)
        if self.dropout is not None:
            attn = self.dropout(attn)

        # Compute weighted sum of values
        output = torch.bmm(attn, v)
        return output, attn


class SegmentwiseInterpretableMultiHeadAttention(nn.Module):
    """
    Segment-wise interpretable multi-head attention using causal masking
    and segment-based key-value selection.
    """
    def __init__(self, n_head: int, d_model: int, segment_size: int, dropout: float = 0.0):
        super(SegmentwiseInterpretableMultiHeadAttention, self).__init__()

        self.n_head = n_head
        self.d_model = d_model
        self.segment_size = segment_size
        self.d_k = self.d_q = self.d_v = d_model // n_head
        self.dropout = nn.Dropout(p=dropout)

        self.v_layer = nn.Linear(self.d_model, self.d_v)
        self.q_layers = nn.ModuleList([nn.Linear(self.d_model, self.d_q) for _ in range(self.n_head)])
        self.k_layers = nn.ModuleList([nn.Linear(self.d_model, self.d_k) for _ in range(self.n_head)])
        self.attention = ScaledDotProductAttention(dropout=dropout)
        self.w_h = nn.Linear(self.d_v, self.d_model, bias=False)

        # Projection layer for skip connection
        self.skip_projection = nn.Linear(d_model, d_model)

        self.init_weights()

    def init_weights(self):
        for name, p in self.named_parameters():
            if "bias" not in name:
                torch.nn.init.xavier_uniform_(p)
            else:
                torch.nn.init.zeros_(p)

    def forward(self, q, k, v, mask=None) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size, q_len, _ = q.shape
        _, kv_len, _ = k.shape

        # Dynamically compute number of segments
        num_full_segments = kv_len // self.segment_size
        remainder = kv_len % self.segment_size

        if remainder > 0:
            # Add a smaller segment for the remainder
            num_segments = num_full_segments + 1
        else:
            num_segments = num_full_segments

        # Reshape keys and values into segments
        k_segments = []
        v_segments = []
        mask_segments = []  # To store masks for each segment

        for i in range(num_segments):
            start_idx = i * self.segment_size
            end_idx = min((i + 1) * self.segment_size, kv_len)
            k_seg = k[:, start_idx:end_idx, :]  # Shape: [batch_size, segment_len, d_model]
            v_seg = v[:, start_idx:end_idx, :]

            # Pad shorter segments to match segment_size
            if k_seg.size(1) < self.segment_size:
                pad_len = self.segment_size - k_seg.size(1)
                k_seg = F.pad(k_seg, (0, 0, 0, pad_len))  # Pad along the sequence length dimension
                v_seg = F.pad(v_seg, (0, 0, 0, pad_len))

            k_segments.append(k_seg)
            v_segments.append(v_seg)

            # Handle the mask for this segment
            if mask is not None:
                mask_seg = mask[:, :, start_idx:end_idx]  # Extract the mask for this segment
                if mask_seg.size(-1) < self.segment_size:
                    pad_len = self.segment_size - mask_seg.size(-1)
                    mask_seg = F.pad(mask_seg, (0, pad_len), value=True)  # Pad with True (masked)
                mask_segments.append(mask_seg)

        # Stack segments into single tensors
        k_segments = torch.stack(k_segments, dim=1)  # Shape: [batch_size, num_segments, segment_size, d_model]
        v_segments = torch.stack(v_segments, dim=1)  # Shape: [batch_size, num_segments, segment_size, d_model]
        if mask is not None:
            mask_segments = torch.stack(mask_segments, dim=1)  # Shape: [batch_size, num_segments, q_len, segment_size]

        heads = []
        attns = []

        vs = self.v_layer(v)  # Apply linear projection to values

        for i in range(self.n_head):
            qs = self.q_layers[i](q)  # Project queries
            head_segments = []
            attn_segments = []

            for seg_idx in range(num_segments):
                # Extract the current segment of keys, values, and mask
                k_seg = k_segments[:, seg_idx, :, :]  # Shape: [batch_size, segment_size, d_model]
                v_seg = v_segments[:, seg_idx, :, :]
                mask_seg = mask_segments[:, seg_idx, :, :] if mask is not None else None

                # Ensure k_seg has the correct shape for the linear layer
                assert k_seg.size(-1) == self.d_model, f"k_seg last dimension ({k_seg.size(-1)}) must match d_model ({self.d_model})"

                # Create causal mask for this segment
                if mask_seg is None:
                    causal_mask = torch.triu(
                        torch.ones(q_len, self.segment_size, dtype=torch.bool, device=q.device),
                        diagonal=1
                    ).unsqueeze(0)  # Shape: [1, q_len, segment_size]
                else:
                    causal_mask = mask_seg | torch.triu(
                        torch.ones(q_len, self.segment_size, dtype=torch.bool, device=q.device),
                        diagonal=1
                    ).unsqueeze(0)  # Combine causal mask with existing mask

                # Compute attention for this segment
                k_seg_proj = self.k_layers[i](k_seg)  # Project keys for this segment
                v_seg_proj = self.v_layer(v_seg)  # Project values for this segment
                head_seg, attn_seg = self.attention(qs, k_seg_proj, v_seg_proj, mask=causal_mask)

                head_segments.append(head_seg)
                attn_segments.append(attn_seg)

            # Concatenate attention outputs from all segments
            head = torch.cat(head_segments, dim=1)
            attn = torch.cat(attn_segments, dim=1)

            # Apply dropout to the concatenated head
            head_dropout = self.dropout(head)
            heads.append(head_dropout)
            attns.append(attn)

        # Stack outputs from all heads
        head = torch.stack(heads, dim=2) if self.n_head > 1 else heads[0]
        attn = torch.stack(attns, dim=2)

        # Average over heads and apply final linear layer
        outputs = torch.mean(head, dim=2) if self.n_head > 1 else head
        outputs = self.w_h(outputs)
        outputs = self.dropout(outputs)
        return outputs, attn


class CrossEntityAttention(nn.Module):
    """
    Cross-Entity Attention for modeling inter-entity dependencies in multivariate time series.
    """
    def __init__(self, hidden_size, num_heads, dropout=0.0):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.dropout = dropout
        assert hidden_size % num_heads == 0, "embed_dim must be divisible by n_heads"
        self.d_k = hidden_size // num_heads

        self.q_linear = nn.Linear(hidden_size, hidden_size)
        self.k_linear = nn.Linear(hidden_size, hidden_size)
        self.v_linear = nn.Linear(hidden_size, hidden_size)
        self.out_linear = nn.Linear(hidden_size, hidden_size)
        
        # Add dropout layer for attention probabilities
        self.attn_dropout = nn.Dropout(dropout)

    def forward(self, query, context):
        if context.dim() == 2:
            context = context.unsqueeze(1)  # (B, 1, H)

        B, T, _ = query.size()
        _, S, _ = context.size()

        Q = self.q_linear(query)  # (B, T, H)
        K = self.k_linear(context)  # (B, S, H)
        V = self.v_linear(context)  # (B, S, H)

        Q = Q.view(B, T, self.num_heads, self.d_k).transpose(1, 2)  # (B, n_heads, T, d_k)
        K = K.view(B, S, self.num_heads, self.d_k).transpose(1, 2)  # (B, n_heads, S, d_k)
        V = V.view(B, S, self.num_heads, self.d_k).transpose(1, 2)  # (B, n_heads, S, d_k)

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        attn = torch.softmax(scores, dim=-1)
        attn = self.attn_dropout(attn)  # apply dropout here

        output = torch.matmul(attn, V)

        output = output.transpose(1, 2).contiguous().view(B, T, self.hidden_size)
        output = self.out_linear(output)
        return output