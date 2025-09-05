# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from typing import Tuple

import torch

NS = "cuequivariance_ops"

torch_ops = getattr(torch.ops, NS)

__all__ = []

try:
    import onnxscript
    from onnxscript import BOOL, FLOAT, INT64
    from onnxscript import opset20 as op

    _onnx_opset = onnxscript.values.Opset(NS, version=1)

    @onnxscript.script(_onnx_opset)
    def _triangle_attention(
        q: FLOAT, k: FLOAT, v: FLOAT, b: FLOAT, mask: BOOL, scale: float
    ) -> Tuple[FLOAT, FLOAT, FLOAT]:
        o, sm_lse, sm_max = _onnx_opset.triangle_attention(
            q, k, v, b, mask, scale=scale, plugin_namespace="cuequivariance_ops"
        )
        return o, sm_lse, sm_max

    @onnxscript.script(_onnx_opset, default_opset=op)
    def _segmented_transpose(
        tensor: FLOAT,
        segment_info: FLOAT,
        input_contiguous_as_info: bool,
    ) -> FLOAT:
        return _onnx_opset.segmented_transpose(
            tensor,
            segment_info,
            contiguous=input_contiguous_as_info,
        )

    @onnxscript.script(_onnx_opset, default_opset=op)
    def _fused_tensor_product_fwd(
        in0: FLOAT,
        in1: FLOAT,
        in2: FLOAT,
        tp_path_csr_offsets_fwd: INT64,
        tp_path_csr_offsets_dgrad_in0: INT64,
        tp_path_csr_offsets_dgrad_in1: INT64,
        tp_path_csr_offsets_dgrad_in2: INT64,
        tp_path_offsets_fwd: INT64,
        tp_path_offsets_dgrad_in0: INT64,
        tp_path_offsets_dgrad_in1: INT64,
        tp_path_offsets_dgrad_in2: INT64,
        tp_path_cg_values_fwd: FLOAT,
        tp_path_cg_values_dgrad_in0: FLOAT,
        tp_path_cg_values_dgrad_in1: FLOAT,
        tp_path_cg_values_dgrad_in2: FLOAT,
        connection_mode: int,
        output_stride: int,
    ) -> FLOAT:
        return _onnx_opset.fused_tensor_product(
            in0,
            in1,
            in2,
            tp_path_csr_offsets_fwd,
            tp_path_csr_offsets_dgrad_in0,
            tp_path_csr_offsets_dgrad_in1,
            tp_path_csr_offsets_dgrad_in2,
            tp_path_offsets_fwd,
            tp_path_offsets_dgrad_in0,
            tp_path_offsets_dgrad_in1,
            tp_path_offsets_dgrad_in2,
            tp_path_cg_values_fwd,
            tp_path_cg_values_dgrad_in0,
            tp_path_cg_values_dgrad_in1,
            tp_path_cg_values_dgrad_in2,
            connection_mode=connection_mode,
            output_stride=output_stride,
        )

    @onnxscript.script(_onnx_opset, default_opset=op)
    def _tensor_product_uniform_1d_jit(
        in0: FLOAT,
        in1: FLOAT,
        in2: FLOAT,
        number_of_output_segments: int,
        number_of_paths: int,
        data: FLOAT,
        math_code: int,
    ):
        return _onnx_opset.tensor_product_uniform_4x1d(
            in0,
            in1,
            in2,
            data,
            number_of_output_segments=number_of_output_segments,
            number_of_paths=number_of_paths,
            math_code=math_code,
        )

    op_table = {
        torch_ops.triangle_attention.default: _triangle_attention,
        torch_ops.segmented_transpose.default: _segmented_transpose,
        torch_ops.fused_tensor_product_fwd.default: _fused_tensor_product_fwd,
        torch_ops.tensor_product_uniform_1d_jit.default: _tensor_product_uniform_1d_jit,
    }

    __all__ += ["op_table"]

except ImportError:
    pass

try:
    from onnxruntime_extensions import PyCustomOpDef, onnx_op

    @onnx_op(
        op_type="cuequivariance_ops::triangle_attention",
        inputs=[
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_bool,
        ],
        outputs=[
            PyCustomOpDef.dt_float,  # Output: o
            PyCustomOpDef.dt_float,  # Output: sm_lse
            PyCustomOpDef.dt_float,  # Output: sm_max
        ],
        attrs={
            "scale": PyCustomOpDef.dt_float,
        },
    )
    def ort_triangle_attention(*args, **kwargs):
        scale = kwargs["scale"]
        cargs = [torch.from_numpy(i).cuda() for i in args]
        o, sm_lse, sm_max = torch.ops.cuequivariance_ops.triangle_attention(
            *cargs, scale
        )
        return o.cpu().numpy(), sm_lse.cpu().numpy(), sm_max.cpu().numpy()
finally:
    pass
