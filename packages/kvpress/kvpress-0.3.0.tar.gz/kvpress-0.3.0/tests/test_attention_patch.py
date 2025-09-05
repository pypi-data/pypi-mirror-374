# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import torch

from kvpress.attention_patch import search_hyperplane


def test_search_hyperplane():
    bsz, seq_len, head_dim = 50, 500, 128
    X = torch.rand(bsz, seq_len, head_dim)
    Y = search_hyperplane(X)
    assert torch.exp(torch.bmm(X, Y.unsqueeze(-1))).max() == 0
