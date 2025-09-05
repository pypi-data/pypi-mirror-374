# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import math
import os
from typing import Optional

import numpy as np
import torch
from scipy.stats import truncnorm

from cuequivariance_ops.triton.utils import Precision

from .fused_layer_norm_torch import layer_norm_transpose
from .gated_gemm_torch import (
    fused_sigmoid_gated_dual_gemm,
    fused_sigmoid_gated_dual_gemm_dual_x,
)

CUEQ_TRIMUL_FALLBACK_THRESHOLD: int = int(
    os.getenv("CUEQ_TRIMUL_FALLBACK_THRESHOLD", "100")
)


def _tri_mul_torch(
    x: torch.Tensor, direction: str, mask: Optional[torch.Tensor], **weights
) -> torch.Tensor:
    """Original PyTorch implementation of triangular multiplication."""
    # Input normalization and store for later use
    x = torch.nn.functional.layer_norm(
        x.float(),
        x.shape[-1:],
        weight=weights["norm_in_weight"].float(),
        bias=weights["norm_in_bias"].float(),
    ).to(x.dtype)
    x_in = x

    # Input projection and gating
    x = torch.nn.functional.linear(
        x, weights["p_in_weight"], bias=weights.get("p_in_bias")
    ) * torch.sigmoid(
        torch.nn.functional.linear(
            x, weights["g_in_weight"], bias=weights.get("g_in_bias")
        )
    )

    # Apply mask if provided
    if mask is not None:
        x = x * mask.unsqueeze(-1)

    # Split input and keep in original precision
    # a, b of shape [B, N, N, D]
    a, b = torch.chunk(x, 2, dim=-1)

    # Triangular projection using einsum based on direction
    if direction == "outgoing":
        # For outgoing edges: x[i,j] = sum_k x[i,k] * x[k,j]
        x = torch.einsum("bikd,bjkd->bijd", a.contiguous(), b.contiguous())
    else:  # incoming
        # For incoming edges: x[i,j] = sum_k x[k,i] * x[j,k]
        x = torch.einsum("bkid,bkjd->bijd", a.contiguous(), b.contiguous())

    # Output normalization and projection - simplified without dictionary switch
    x = torch.nn.functional.linear(
        torch.nn.functional.layer_norm(
            x.float(),
            x.shape[-1:],
            weight=weights["norm_out_weight"].float(),
            bias=weights["norm_out_bias"].float(),
        ).to(x.dtype),
        weights["p_out_weight"],
        bias=weights.get("p_out_bias"),
    ) * torch.sigmoid(
        torch.nn.functional.linear(
            x_in, weights["g_out_weight"], bias=weights.get("g_out_bias")
        )
    )

    return x


def _parse_precision(precision_input, p_in_weight=None, g_in_weight=None):
    """Parse precision input which can be a string or Precision enum."""
    if precision_input is None:
        return None
    if isinstance(precision_input, str):
        precision_str = precision_input.upper()
        if precision_str == "IEEE":
            precision = Precision.IEEE
        else:
            raise ValueError(
                f"Invalid precision string: {precision_input}. Must be one of: None, ieee"
            )
    else:
        raise ValueError(
            f"Invalid precision type: {type(precision_input)}. Must be string"
        )

    return precision


def _prod(nums):
    out = 1
    for n in nums:
        out = out * n
    return out


def ensure_dims(ten: torch.Tensor, n: int) -> torch.Tensor:
    """Ensure tensor has exactly n dimensions by adding or collapsing dimensions as needed.

    If tensor has fewer than n dimensions, adds 1-sized dimensions at the beginning.
    If tensor has more than n dimensions, collapses leading dimensions into the first dimension.

    Args:
        ten: Input tensor
        n: Target number of dimensions

    Returns:
        Tensor with exactly n dimensions
    """
    current_dims = len(ten.shape)

    if current_dims < n:
        # Add 1-sized dimensions at the beginning
        while len(ten.shape) < n:
            ten = ten.unsqueeze(0)
    elif current_dims > n:
        # Collapse leading dimensions into the first dimension
        # Keep the last n-1 dimensions as they are
        ten = ten.flatten(0, current_dims - n)

    return ten


def _calculate_fan(linear_weight_shape, fan="fan_in"):
    fan_out, fan_in = linear_weight_shape
    if fan == "fan_in":
        f = fan_in
    elif fan == "fan_out":
        f = fan_out
    elif fan == "fan_avg":
        f = (fan_in + fan_out) / 2
    else:
        raise ValueError("Invalid fan option")
    return f


def trunc_normal_init_(weights, scale=1.0, fan="fan_in"):
    shape = weights.shape
    f = _calculate_fan(shape, fan)
    scale = scale / max(1, f)
    a = -2
    b = 2
    std = math.sqrt(scale) / truncnorm.std(a=a, b=b, loc=0, scale=1)
    size = _prod(shape)
    samples = truncnorm.rvs(a=a, b=b, loc=0, scale=std, size=size)
    samples = np.reshape(samples, shape)
    with torch.no_grad():
        weights.copy_(torch.tensor(samples, device=weights.device))


def lecun_normal_init_(weights):
    trunc_normal_init_(weights, scale=1.0)


def bias_init_zero_(bias):
    with torch.no_grad():
        bias.fill_(0.0)


def bias_init_one_(bias):
    with torch.no_grad():
        bias.fill_(1.0)


def triangle_multiplicative_update(
    x: torch.Tensor,
    direction: str = "outgoing",
    mask: Optional[torch.Tensor] = None,
    norm_in_weight: Optional[torch.Tensor] = None,
    norm_in_bias: Optional[torch.Tensor] = None,
    p_in_weight: Optional[torch.Tensor] = None,
    p_in_bias: Optional[torch.Tensor] = None,
    g_in_weight: Optional[torch.Tensor] = None,
    g_in_bias: Optional[torch.Tensor] = None,
    norm_out_weight: Optional[torch.Tensor] = None,
    norm_out_bias: Optional[torch.Tensor] = None,
    p_out_weight: Optional[torch.Tensor] = None,
    p_out_bias: Optional[torch.Tensor] = None,
    g_out_weight: Optional[torch.Tensor] = None,
    g_out_bias: Optional[torch.Tensor] = None,
    eps: float = 1e-5,
    precision: Optional[Precision | str] = None,
) -> torch.Tensor:
    # Input validation
    if direction not in ["outgoing", "incoming"]:
        raise ValueError("direction must be either 'outgoing' or 'incoming'")

    # Store original shape for output restoration
    original_shape = x.shape

    # Ensure x has 4 dimensions
    x = ensure_dims(x, 4)

    if mask is not None:
        # Ensure mask has 3 dimensions
        mask = ensure_dims(mask, 3)

    # Initialize default weights if not provided
    hidden_dim = x.shape[-1]
    if norm_in_weight is None:
        norm_in_weight = torch.empty(hidden_dim, device=x.device, dtype=x.dtype)
        bias_init_one_(norm_in_weight)
    if norm_in_bias is None:
        norm_in_bias = torch.empty(hidden_dim, device=x.device, dtype=x.dtype)
        bias_init_zero_(norm_in_bias)
    if p_in_weight is None:
        p_in_weight = torch.empty(
            2 * hidden_dim, hidden_dim, device=x.device, dtype=x.dtype
        )
        lecun_normal_init_(p_in_weight)
    if g_in_weight is None:
        g_in_weight = torch.empty(
            2 * hidden_dim, hidden_dim, device=x.device, dtype=x.dtype
        )
        lecun_normal_init_(g_in_weight)
    if norm_out_weight is None:
        norm_out_weight = torch.empty(hidden_dim, device=x.device, dtype=x.dtype)
        bias_init_one_(norm_out_weight)
    if norm_out_bias is None:
        norm_out_bias = torch.empty(hidden_dim, device=x.device, dtype=x.dtype)
        bias_init_zero_(norm_out_bias)
    if p_out_weight is None:
        p_out_weight = torch.empty(
            hidden_dim, hidden_dim, device=x.device, dtype=x.dtype
        )
        lecun_normal_init_(p_out_weight)
    if g_out_weight is None:
        g_out_weight = torch.empty(
            hidden_dim, hidden_dim, device=x.device, dtype=x.dtype
        )
        lecun_normal_init_(g_out_weight)

    # Calculate output shape based on weight dimensions
    # The output dimension is determined by p_out_weight.shape[0]
    output_dim = p_out_weight.shape[0]
    output_shape = (*original_shape[:-1], output_dim)

    seq_len = x.shape[-2]

    if not torch._jit_internal.is_scripting() and not torch.compiler.is_compiling():
        # Use original PyTorch implementation for short sequences in eager mode only
        if seq_len <= CUEQ_TRIMUL_FALLBACK_THRESHOLD:
            weights = {
                "norm_in_weight": norm_in_weight,
                "norm_in_bias": norm_in_bias,
                "p_in_weight": p_in_weight,
                "g_in_weight": g_in_weight,
                "norm_out_weight": norm_out_weight,
                "norm_out_bias": norm_out_bias,
                "p_out_weight": p_out_weight,
                "g_out_weight": g_out_weight,
            }
            # Only add bias parameters if they are provided
            if p_in_bias is not None:
                weights["p_in_bias"] = p_in_bias
            if g_in_bias is not None:
                weights["g_in_bias"] = g_in_bias
            if p_out_bias is not None:
                weights["p_out_bias"] = p_out_bias
            if g_out_bias is not None:
                weights["g_out_bias"] = g_out_bias

            result = _tri_mul_torch(x, direction, mask, **weights)
            return result.view(output_shape)

    precision = _parse_precision(precision, p_in_weight, g_in_weight)

    # Continue with optimized implementation for longer sequences
    # Input normalization
    x = layer_norm_transpose(
        x, norm_in_weight, norm_in_bias, eps=eps, layout="bijd->bijd"
    )
    x_in = x

    # Gated dual gemm
    ab = fused_sigmoid_gated_dual_gemm(
        x,
        g_in_weight,
        p_in_weight,
        mask,
        transpose_out=True,
        precision=precision,
        b1=g_in_bias,
        b2=p_in_bias,
    )
    a, b = torch.chunk(ab, 2, dim=0)

    # Triangular projection
    if direction == "outgoing":
        x = torch.einsum("dbik,dbjk->dbij", a, b)
    else:
        x = torch.einsum("dbki,dbkj->dbij", a, b)

    # Output normalization
    x_out = layer_norm_transpose(
        x, norm_out_weight, norm_out_bias, eps=eps, layout="dbij->bijd"
    )

    # Output gating
    x = fused_sigmoid_gated_dual_gemm_dual_x(
        x_in,
        x_out,
        g_out_weight,
        p_out_weight,
        precision=precision,
        b1=g_out_bias,
        b2=p_out_bias,
    )

    return x.view(output_shape)
