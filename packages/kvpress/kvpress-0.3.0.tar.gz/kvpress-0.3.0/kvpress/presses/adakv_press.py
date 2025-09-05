# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass

import torch

from kvpress.presses.base_press import BasePress
from kvpress.presses.scorer_press import ScorerPress


@dataclass
class AdaKVPress(BasePress):
    """
    AdaKV: Adaptive head-wise KV cache compression.

    Performs head-specific compression by selecting top-k tokens across all heads
    based on importance scores. Applies safeguards to ensure each head retains
    a minimum fraction of tokens.

    Based on AdaKV (https://arxiv.org/abs/2407.11550).

    Parameters
    ----------
    press : ScorerPress
        AdaKVPress and ObservedAttention are currently not supported.
    alpha_safeguard : float, default=0.20
        Minimum fraction of KV pairs that each head must retain.
        Ensures no attention head is compressed too aggressively. Even if tokens
        receive low global importance scores, each head retains at least this
        fraction of its original tokens.
    """

    press: ScorerPress
    alpha_safeguard: float = 0.20

    def __post_init__(self):
        assert isinstance(self.press, ScorerPress), "AdaKVPress requires a ScorerPress as input"
        assert 0 <= self.alpha_safeguard <= 1, "alpha_safeguard should be in [0, 1]"

    @property
    def compression_ratio(self):
        return self.press.compression_ratio

    @compression_ratio.setter
    def compression_ratio(self, value):
        self.press.compression_ratio = value

    def compress(self, module, hidden_states, keys, values, attentions, kwargs):
        if self.compression_ratio == 0:
            return keys, values

        assert module.config._attn_implementation != "eager", "eager mode not supported"

        # Compute scores
        scores = self.press.score(module, hidden_states, keys, values, attentions, kwargs)
        bsz, num_key_value_heads, q_len = scores.shape

        # Make sure to keep at least alpha * (1 - compression_ratio) KV pairs per head
        n_kept = int(q_len * (1 - self.compression_ratio))  # ScorerPress definition
        n_safe = int(n_kept * self.alpha_safeguard)
        top_indices = torch.topk(scores, n_safe, dim=-1).indices
        scores.scatter_(-1, top_indices, torch.finfo(scores.dtype).max)

        # Compute bottom-k across heads
        n_pruned = num_key_value_heads * (q_len - n_kept)
        indices = torch.topk(-scores.reshape(bsz, -1), n_pruned, dim=1).indices.flatten()

        # Save indices to mask during the attention mechanism. Please refer to attention_patch.py for more details
        batch_indices = torch.arange(bsz).repeat_interleave(n_pruned)
        head_indices = indices // q_len
        seq_indices = indices % q_len
        module.masked_key_indices = (batch_indices, head_indices, seq_indices)
        return keys, values
