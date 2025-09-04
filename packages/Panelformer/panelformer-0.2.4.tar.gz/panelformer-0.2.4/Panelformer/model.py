import torch
from torch import nn
from pytorch_forecasting.models.temporal_fusion_transformer import TemporalFusionTransformer
from pytorch_forecasting.models.temporal_fusion_transformer.sub_modules import GatedResidualNetwork

from .attention import SegmentwiseInterpretableMultiHeadAttention, CrossEntityAttention
from .decomposition import EnhancedSeriesDecomp, compute_component_weights

class Panelformer(TemporalFusionTransformer):
    """
    Panelformer extends the Temporal Fusion Transformer (TFT) with the following enhancements:

    1. Segment-wise attention mechanism.
    2. Multi-scale trend and seasonal decomposition.
    3. Cross-entity attention for shared learning across time series.
    4. Adaptive trend-seasonal weighting using learned gating.
    5. Deep trend processing pipeline using gated residual layers.

    Attributes:
        segment_size (int): Length of segments for attention.
        decomposition_kernel_sizes (list): Kernel sizes used for trend-seasonal decomposition.
        trend_processing_layers (int): Number of processing layers for trend component.
        use_cross_entity_attention (bool): If True, enables cross-entity attention.
        adaptive_trend_weight (bool): If True, enables learned weighting of trend and seasonal outputs.
    """

    def __init__(
        self, 
        *args, 
        segment_size=8,
        decomposition_kernel_sizes=[3, 7, 15, 31],
        trend_processing_layers=2,
        use_cross_series_attention=True,
        adaptive_trend_weight=True,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        # Store new hyperparameters
        self.hparams.segment_size = segment_size
        self.hparams.decomposition_kernel_sizes = decomposition_kernel_sizes
        self.hparams.trend_processing_layers = trend_processing_layers
        self.hparams.use_cross_series_attention = use_cross_series_attention
        self.hparams.adaptive_trend_weight = adaptive_trend_weight

        # 1. Replace standard attention with segmentwise attention
        self.multihead_attn = SegmentwiseInterpretableMultiHeadAttention(
            n_head=self.hparams.attention_head_size,
            d_model=self.hparams.hidden_size,
            dropout=self.hparams.dropout,
            segment_size=segment_size
        )

        # 2. Add enhanced series decomposition
        self.decomposition = EnhancedSeriesDecomp(kernel_sizes=decomposition_kernel_sizes)

        # 3. Add trend processing network
        trend_layers = []
        for _ in range(trend_processing_layers):
            trend_layers.append(
                GatedResidualNetwork(
                    input_size=self.hparams.hidden_size,
                    hidden_size=self.hparams.hidden_size,
                    output_size=self.hparams.hidden_size,
                    dropout=self.hparams.dropout
                )
            )
        self.trend_processor = nn.Sequential(*trend_layers)

        # 4. Add cross-series attention if enabled
        if use_cross_series_attention:
            self.cross_series_attn = CrossEntityAttention(
                hidden_size=self.hparams.hidden_size,
                num_heads=self.hparams.attention_head_size,
                dropout=self.hparams.dropout
            )

        # 5. Add adaptive trend weight network if enabled
        if adaptive_trend_weight:
            self.trend_weight_network = nn.Sequential(
                nn.Linear(self.hparams.hidden_size * 2, 64),
                nn.ReLU(),
                nn.Linear(64, 1),
                nn.Sigmoid()
            )

        # 6. Modify output layer to handle combined seasonal and trend components
        if self.n_targets > 1:
            self.output_layer = nn.ModuleList(
                [
                    nn.Linear(self.hparams.hidden_size * 2, output_size)
                    for output_size in self.hparams.output_size
                ]
            )
        else:
            self.output_layer = nn.Linear(
                self.hparams.hidden_size * 2, self.hparams.output_size
            )

    def forward(self, x):
        """
        Forward pass for Panelformer model.

        Args:
            x (dict): Batch input containing encoder/decoder features and metadata.

        Returns:
            dict: Model outputs including predictions, attention weights, trend forecasts, etc.
        """

        # Get standard inputs
        encoder_lengths = x["encoder_lengths"]
        decoder_lengths = x["decoder_lengths"]
        x_cat = torch.cat([x["encoder_cat"], x["decoder_cat"]], dim=1)
        x_cont = torch.cat([x["encoder_cont"], x["decoder_cont"]], dim=1)
        timesteps = x_cont.size(1)
        max_encoder_length = int(encoder_lengths.max())

        # Standard TFT embedding and variable selection
        input_vectors = self.input_embeddings(x_cat)
        input_vectors.update({
            name: x_cont[..., idx].unsqueeze(-1)
            for idx, name in enumerate(self.hparams.x_reals)
            if name in self.reals
        })

        # Static embedding
        if len(self.static_variables) > 0:
            static_embedding = {
                name: input_vectors[name][:, 0] for name in self.static_variables
            }
            static_embedding, static_variable_selection = (
                self.static_variable_selection(static_embedding)
            )
        else:
            static_embedding = torch.zeros(
                (x_cont.size(0), self.hparams.hidden_size),
                dtype=self.dtype,
                device=self.device,
            )
            static_variable_selection = torch.zeros(
                (x_cont.size(0), 0), dtype=self.dtype, device=self.device
            )

        # Variable selection with static context
        static_context_variable_selection = self.expand_static_context(
            self.static_context_variable_selection(static_embedding), timesteps
        )

        # Encoder variable selection
        embeddings_varying_encoder = {
            name: input_vectors[name][:, :max_encoder_length]
            for name in self.encoder_variables
        }
        embeddings_varying_encoder, encoder_sparse_weights = (
            self.encoder_variable_selection(
                embeddings_varying_encoder,
                static_context_variable_selection[:, :max_encoder_length],
            )
        )

        # Decoder variable selection
        embeddings_varying_decoder = {
            name: input_vectors[name][:, max_encoder_length:]
            for name in self.decoder_variables
        }
        embeddings_varying_decoder, decoder_sparse_weights = (
            self.decoder_variable_selection(
                embeddings_varying_decoder,
                static_context_variable_selection[:, max_encoder_length:],
            )
        )

        # Series decomposition after variable selection
        seasonal_enc, trend_enc = self.decomposition(embeddings_varying_encoder)
        seasonal_dec, trend_dec = self.decomposition(embeddings_varying_decoder)

        # LSTM for seasonal component
        input_hidden = self.static_context_initial_hidden_lstm(static_embedding).expand(
            self.hparams.lstm_layers, -1, -1
        )
        input_cell = self.static_context_initial_cell_lstm(static_embedding).expand(
            self.hparams.lstm_layers, -1, -1
        )

        encoder_output, (hidden, cell) = self.lstm_encoder(
            seasonal_enc,
            (input_hidden, input_cell),
            lengths=encoder_lengths,
            enforce_sorted=False,
        )
        decoder_output, _ = self.lstm_decoder(
            seasonal_dec,
            (hidden, cell),
            lengths=decoder_lengths,
            enforce_sorted=False,
        )

        lstm_output_encoder = self.post_lstm_gate_encoder(encoder_output)
        lstm_output_encoder = self.post_lstm_add_norm_encoder(lstm_output_encoder, seasonal_enc)

        lstm_output_decoder = self.post_lstm_gate_decoder(decoder_output)
        lstm_output_decoder = self.post_lstm_add_norm_decoder(lstm_output_decoder, seasonal_dec)

        lstm_output = torch.cat([lstm_output_encoder, lstm_output_decoder], dim=1)

        # Static enrichment
        static_context_enrichment = self.static_context_enrichment(static_embedding)
        attn_input = self.static_enrichment(
            lstm_output,
            self.expand_static_context(static_context_enrichment, timesteps),
        )

        # Attention
        attn_output, attn_output_weights = self.multihead_attn(
            q=attn_input[:, max_encoder_length:],  # Query only for predictions
            k=attn_input,
            v=attn_input,
            mask=self.get_attention_mask(
                encoder_lengths=encoder_lengths, decoder_lengths=decoder_lengths
            ),
        )

        # Cross-series attention if enabled
        if hasattr(self, 'cross_series_attn'):
            attn_output = self.cross_series_attn(attn_output, static_embedding)

        # Skip connections
        skip_tensor = attn_input[:, max_encoder_length:]
        min_len = min(attn_output.shape[1], skip_tensor.shape[1])
        attn_output = attn_output[:, :min_len, :]
        skip_tensor = skip_tensor[:, :min_len, :]
        attn_output = self.post_attn_gate_norm(attn_output, skip_tensor)

        seasonal_output = self.pos_wise_ff(attn_output)

        skip_tensor = lstm_output[:, max_encoder_length:]
        min_len = min(seasonal_output.shape[1], skip_tensor.shape[1])
        seasonal_output = seasonal_output[:, :min_len, :]
        skip_tensor = skip_tensor[:, :min_len, :]
        seasonal_output = self.pre_output_gate_norm(seasonal_output, skip_tensor)

        # Process trend component
        trend_all = torch.cat([trend_enc, trend_dec], dim=1)
        trend_output = trend_all[:, max_encoder_length:]  # Only decoder part
        processed_trend = self.trend_processor(trend_output)

        # Dynamically weigh seasonal and trend components
        if hasattr(self, 'trend_weight_network'):
            # Use learned weights
            combined_features = torch.cat([seasonal_output, processed_trend], dim=-1)
            trend_weight = self.trend_weight_network(combined_features)
            seasonal_weight = 1 - trend_weight

            weighted_seasonal = seasonal_output * seasonal_weight
            weighted_trend = processed_trend * trend_weight
        else:
            # Use variance-based weights
            seasonal_weight, trend_weight = compute_component_weights(seasonal_output, processed_trend)
            weighted_seasonal = seasonal_output * seasonal_weight
            weighted_trend = processed_trend * trend_weight

        # Combine components for final prediction
        combined_output = torch.cat([weighted_seasonal, weighted_trend], dim=-1)

        # Final output layer
        if self.n_targets > 1:
            output = [output_layer(combined_output) for output_layer in self.output_layer]
        else:
            output = self.output_layer(combined_output)

        return self.to_network_output(
            prediction=self.transform_output(output, target_scale=x["target_scale"]),
            trend_prediction=processed_trend,
            encoder_attention=attn_output_weights[..., :max_encoder_length],
            decoder_attention=attn_output_weights[..., max_encoder_length:],
            static_variables=static_variable_selection,
            encoder_variables=encoder_sparse_weights,
            decoder_variables=decoder_sparse_weights,
            decoder_lengths=decoder_lengths,
            encoder_lengths=encoder_lengths,
        )