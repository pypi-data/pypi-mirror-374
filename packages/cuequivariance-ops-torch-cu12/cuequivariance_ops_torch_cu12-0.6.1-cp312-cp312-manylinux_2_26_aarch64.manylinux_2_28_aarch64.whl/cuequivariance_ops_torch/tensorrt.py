# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.


import cupy as cp
import numpy as np
import tensorrt as trt
import torch
from polygraphy.json import from_json, to_json

import cuequivariance_ops_torch._ext as ops
from cuequivariance_ops_torch import (
    int_mappings_to_mode,
    tensor_product_info_as_ctype,
)
from cuequivariance_ops_torch.triangle_attention import (
    CUEQ_TRIATTN_FALLBACK_THRESHOLD,
    _triangle_attention_torch,
)
from cuequivariance_ops_torch.utils import get_operator_from_module

trt_to_torch = {
    trt.DataType.FLOAT: torch.float,
    trt.DataType.HALF: torch.float16,
    trt.DataType.BF16: torch.bfloat16,
    trt.DataType.INT32: torch.int32,
    trt.DataType.INT64: torch.int64,
}


class SegmentedTransposePlugin(trt.IPluginV2DynamicExt):
    def __init__(self, fc=None):
        trt.IPluginV2DynamicExt.__init__(self)

        self.num_outputs = 1
        self.plugin_namespace = "cuequivariance_ops"
        self.plugin_type = "segmented_transpose"
        self.plugin_version = "1"

        fc_dict = {}
        if fc is not None:
            for f in fc:
                fc_dict[f.name] = f.data
            self.contiguous = fc_dict["contiguous"]

    def get_output_datatype(self, index, input_types):
        return input_types[0]

    def get_output_dimensions(self, output_index, inputs, exprBuilder):
        output_dims = trt.DimsExprs(inputs[0])
        return output_dims

    def serialize(self):
        return to_json(self.__dict__)

    def configure_plugin(self, inp, out):
        pass

    def supports_format_combination(self, pos, in_out, num_inputs):
        assert num_inputs == 2
        assert pos < len(in_out)

        desc = in_out[pos]
        if desc.format != trt.TensorFormat.LINEAR:
            return False

        # first input should be (b)float16 or float32
        if pos == 0:
            return (
                desc.type == trt.DataType.FLOAT
                or desc.type == trt.DataType.HALF
                or desc.type == trt.DataType.BF16
            )
        elif pos == 1:
            return desc.type == trt.DataType.INT32 or desc.type == trt.DataType.INT64
        else:
            # should have the same type as the input[0]
            return in_out[0].type == desc.type

    def enqueue(self, input_desc, output_desc, inputs, outputs, workspace, stream):
        i_bs = [np.prod(i.dims) * i.type.itemsize for i in input_desc]
        o_bs = [np.prod(o.dims) * o.type.itemsize for o in output_desc]

        i_mem = [
            cp.cuda.UnownedMemory(inputs[i], i_bs[i], self) for i in range(len(inputs))
        ]
        o_mem = cp.cuda.UnownedMemory(outputs[0], o_bs[0], self)

        i_ptr = [cp.cuda.MemoryPointer(i, 0) for i in i_mem]
        o_ptr = cp.cuda.MemoryPointer(o_mem, 0)

        i_nd = [
            cp.ndarray((i_bs[i],), dtype=cp.uint8, memptr=i_ptr[i])
            for i in range(len(inputs))
        ]
        o_nd = cp.ndarray((o_bs[0],), dtype=cp.uint8, memptr=o_ptr)

        i_t = [
            torch.as_tensor(i_nd[i], device="cuda")
            .view(dtype=trt_to_torch[input_desc[i].type])
            .view(tuple(input_desc[i].dims))
            for i in range(len(inputs))
        ]
        ret = (
            torch.as_tensor(o_nd, device="cuda")
            .view(dtype=trt_to_torch[output_desc[0].type])
            .view(tuple(output_desc[0].dims))
        )

        ops.segmented_transpose(
            ret,
            i_t[0],
            i_t[1],
            bool(self.contiguous[0]),
            stream,
        )

        return 0

    def clone(self):
        cloned_plugin = SegmentedTransposePlugin()
        cloned_plugin.__dict__.update(self.__dict__)
        return cloned_plugin

    def get_serialization_size(self):
        return len(to_json(self.__dict__))


class SegmentedTransposePluginCreator(trt.IPluginCreator):
    def __init__(self):
        trt.IPluginCreator.__init__(self)
        self.name = "segmented_transpose"
        self.plugin_namespace = "cuequivariance_ops"
        self.plugin_version = "1"
        self.field_names = trt.PluginFieldCollection(
            [
                trt.PluginField("contiguous"),
            ]
        )

    def create_plugin(self, name, fc):
        pl = SegmentedTransposePlugin(fc)
        return pl

    def deserialize_plugin(self, name, data):
        j = dict(from_json(data.decode("utf-8")))
        deserialized = SegmentedTransposePlugin()
        deserialized.__dict__.update(j)
        return deserialized


class FusedTensorProductPlugin(trt.IPluginV2DynamicExt):
    def __init__(self, fc=None):
        trt.IPluginV2DynamicExt.__init__(self)

        self.num_outputs = 1
        self.plugin_namespace = "cuequivariance_ops"
        self.plugin_type = "fused_tensor_product"
        self.plugin_version = "1"

        fc_dict = {}

        if fc is not None:
            for f in fc:
                fc_dict[f.name] = f.data

            self.connection_mode = fc_dict["connection_mode"]
            self.stride_out = fc_dict["output_stride"]

    def get_output_datatype(self, index, input_types):
        return input_types[0]

    def get_output_dimensions(self, output_index, inputs, exprBuilder):
        output_dims = trt.DimsExprs(inputs[0])
        output_dims[len(output_dims) - 1] = exprBuilder.constant(self.stride_out[0])
        return output_dims

    def serialize(self):
        return to_json(self.__dict__)

    def configure_plugin(self, inp, out):
        pass

    def supports_format_combination(self, pos, in_out, num_inputs):
        assert num_inputs == 15
        assert pos < len(in_out)

        desc = in_out[pos]
        if desc.format != trt.TensorFormat.LINEAR:
            return False

        # first input should be (b)float16 or float32
        if pos == 0:
            return (
                desc.type == trt.DataType.FLOAT
                or desc.type == trt.DataType.HALF
                or desc.type == trt.DataType.BF16
            )
        elif pos > 2 and pos < num_inputs:
            return desc.type == trt.DataType.INT32
        else:
            # should have the same type as the input[0]
            return in_out[0].type == desc.type

    def enqueue(self, input_desc, output_desc, inputs, outputs, workspace, stream):
        i_bs = [np.prod(i.dims) * i.type.itemsize for i in input_desc]
        o_bs = [np.prod(o.dims) * o.type.itemsize for o in output_desc]

        # This needed in case inputs[2] is null
        attrs = cp.cuda.runtime.pointerGetAttributes(inputs[0])
        i_mem = [
            cp.cuda.UnownedMemory(inputs[i], i_bs[i], self, device_id=attrs.device)
            for i in range(len(inputs))
        ]
        o_mem = cp.cuda.UnownedMemory(outputs[0], o_bs[0], self)

        i_ptr = [cp.cuda.MemoryPointer(i, 0) for i in i_mem]
        o_ptr = cp.cuda.MemoryPointer(o_mem, 0)

        i_nd = [
            cp.ndarray((i_bs[i],), dtype=cp.uint8, memptr=i_ptr[i])
            for i in range(len(inputs))
        ]
        o_nd = cp.ndarray((o_bs[0],), dtype=cp.uint8, memptr=o_ptr)

        i_t = [
            torch.as_tensor(i_nd[i], device="cuda")
            .view(dtype=trt_to_torch[input_desc[i].type])
            .view(tuple(input_desc[i].dims))
            for i in range(len(inputs))
        ]
        ret = (
            torch.as_tensor(o_nd, device="cuda")
            .view(dtype=trt_to_torch[output_desc[0].type])
            .view(tuple(output_desc[0].dims))
        )

        fwd_fun = get_operator_from_module(
            ops,
            "fused_tensor_product_fwd",
            (i_t[0].dtype, i_t[1].dtype, i_t[2].dtype, ret.dtype, torch.float32),
        )

        tp_info_fwd = tensor_product_info_as_ctype(
            i_t[3],
            i_t[7],
            i_t[11],
        )

        fwd_fun(
            ret,
            i_t[0],
            i_t[1],
            i_t[2],
            getattr(ops.ConnectionMode, int_mappings_to_mode[self.connection_mode[0]]),
            tp_info_fwd,
            stream_id=stream,
        )

        return 0

    def clone(self):
        cloned_plugin = FusedTensorProductPlugin()
        cloned_plugin.__dict__.update(self.__dict__)
        return cloned_plugin

    def get_serialization_size(self):
        return len(to_json(self.__dict__))


class FusedTensorProductPluginCreator(trt.IPluginCreator):
    def __init__(self):
        trt.IPluginCreator.__init__(self)
        self.name = "fused_tensor_product"
        self.plugin_namespace = "cuequivariance_ops"
        self.plugin_version = "1"
        self.field_names = trt.PluginFieldCollection(
            [trt.PluginField("connection_mode"), trt.PluginField("output_stride")]
        )

    def create_plugin(self, name, fc):
        pl = FusedTensorProductPlugin(fc)
        return pl

    def deserialize_plugin(self, name, data):
        j = dict(from_json(data.decode("utf-8")))
        deserialized = FusedTensorProductPlugin()
        deserialized.__dict__.update(j)
        return deserialized


class TensorProductUniform4x1dPlugin(trt.IPluginV2DynamicExt):
    def __init__(self, fc=None):
        trt.IPluginV2DynamicExt.__init__(self)

        self.num_outputs = 1
        self.plugin_namespace = ""
        self.plugin_type = "tensor_product_uniform_4x1d"
        self.plugin_version = "1"

        fc_dict = {}

        if fc is not None:
            for f in fc:
                fc_dict[f.name] = f.data

            self.number_of_output_segments = fc_dict["number_of_output_segments"]
            self.number_of_paths = fc_dict["number_of_paths"]
            self.math_code = fc_dict["math_code"]

    def get_output_datatype(self, index, input_types):
        return input_types[0]

    def get_output_dimensions(self, output_index, inputs, exprBuilder):
        in0_dims = trt.DimsExprs(inputs[0])
        in1_dims = trt.DimsExprs(inputs[1])
        in2_dims = trt.DimsExprs(inputs[2])
        o0 = exprBuilder.operation(
            trt.DimensionOperation.MAX,
            in0_dims[0],
            exprBuilder.operation(trt.DimensionOperation.MAX, in1_dims[0], in2_dims[0]),
        )
        o2 = exprBuilder.operation(
            trt.DimensionOperation.MAX,
            in0_dims[2],
            exprBuilder.operation(
                trt.DimensionOperation.MAX,
                in1_dims[2],
                in2_dims[2] if len(in2_dims) >= 3 else in1_dims[2],
            ),
        )
        output_dims = trt.DimsExprs(
            [o0, exprBuilder.constant(self.number_of_output_segments), o2]
        )
        return output_dims

    def serialize(self):
        return to_json(self.__dict__)

    def configure_plugin(self, inp, out):
        pass

    def supports_format_combination(self, pos, in_out, num_inputs):
        assert num_inputs == 4
        assert pos < len(in_out)

        desc = in_out[pos]
        if desc.format != trt.TensorFormat.LINEAR:
            return False

        # first input should be (b)float16 or float32
        if pos == 0:
            return (
                desc.type == trt.DataType.FLOAT
                or desc.type == trt.DataType.HALF
                or desc.type == trt.DataType.BF16
            )
        elif pos == 3:
            return desc.type == trt.DataType.INT8 or desc.type == trt.DataType.INT32
        else:
            # should have the same type as the input[0]
            return in_out[0].type == desc.type

    def enqueue(self, input_desc, output_desc, inputs, outputs, workspace, stream):
        i_bs = [np.prod(i.dims) * i.type.itemsize for i in input_desc]
        o_bs = [np.prod(o.dims) * o.type.itemsize for o in output_desc]

        i_mem = [
            cp.cuda.UnownedMemory(inputs[i], i_bs[i], self) if i_bs[i] > 0 else None
            for i in range(len(inputs))
        ]
        o_mem = cp.cuda.UnownedMemory(outputs[0], o_bs[0], self)

        i_ptr = [cp.cuda.MemoryPointer(i, 0) if i is not None else None for i in i_mem]
        o_ptr = cp.cuda.MemoryPointer(o_mem, 0)

        i_nd = [
            cp.ndarray((i_bs[i],), dtype=cp.uint8, memptr=p) if p is not None else None
            for i, p in enumerate(i_ptr)
        ]
        o_nd = cp.ndarray((o_bs[0],), dtype=cp.uint8, memptr=o_ptr)

        i_t = [
            torch.as_tensor(nd, device="cuda")
            .view(dtype=trt_to_torch[input_desc[i].type])
            .view(tuple(input_desc[i].dims))
            if nd is not None
            else None
            for i, nd in enumerate(i_nd)
        ]
        ret = (
            torch.as_tensor(o_nd, device="cuda")
            .view(dtype=trt_to_torch[output_desc[0].type])
            .view(tuple(output_desc[0].dims))
        )

        ops.tensor_product_uniform_1d_fwd(
            self.number_of_paths,
            i_t[3],
            self.math_code,
            i_t[:-1] if i_t[2] is not None else i_t[:-2],
            ret,
            stream,
        )

        return 0

    def clone(self):
        cloned_plugin = TensorProductUniform4x1dPlugin()
        cloned_plugin.__dict__.update(self.__dict__)
        return cloned_plugin

    def get_serialization_size(self):
        return len(to_json(self.__dict__))


class TensorProductUniform4x1dPluginCreator(trt.IPluginCreator):
    def __init__(self):
        trt.IPluginCreator.__init__(self)
        self.name = "tensor_product_uniform_4x1d"
        self.plugin_namespace = "cuequivariance_ops"
        self.plugin_version = "1"
        self.field_names = trt.PluginFieldCollection(
            [
                trt.PluginField("number_of_paths"),
                trt.PluginField("number_of_output_segments"),
                trt.PluginField("math_code"),
            ]
        )

    def create_plugin(self, name, fc):
        pl = TensorProductUniform4x1dPlugin(fc)
        return pl

    def deserialize_plugin(self, name, data):
        j = dict(from_json(data.decode("utf-8")))
        deserialized = TensorProductUniform4x1dPlugin()
        deserialized.__dict__.update(j)
        return deserialized


trt_to_torch = {
    trt.DataType.FLOAT: torch.float,
    trt.DataType.HALF: torch.float16,
    trt.DataType.BF16: torch.bfloat16,
    trt.DataType.INT32: torch.int32,
    trt.DataType.INT64: torch.int64,
    trt.DataType.BOOL: torch.bool,
}


class TriangularAttentionPlugin(trt.IPluginV2DynamicExt):
    def __init__(self, fc=None):
        trt.IPluginV2DynamicExt.__init__(self)

        self.num_outputs = 3
        self.plugin_namespace = "cuequivariance_ops"
        self.plugin_type = "triangle_attention"
        self.plugin_version = "1"
        self.scale = 1.0
        self.use_tf32 = True

        # fc_dict = {}

    def get_output_datatype(self, index, input_types):
        return input_types[0] if trt.DataType.FLOAT else trt.DataType.FLOAT

    def get_output_dimensions(self, output_index, inputs, exprBuilder):
        shape = inputs[0]
        if output_index == 0:
            return shape
        else:
            oshape = trt.DimsExprs([shape[0], shape[1], shape[2], shape[3]])
            return oshape

    def serialize(self):
        return to_json(self.__dict__)

    def configure_plugin(self, inp, out):
        pass

    def supports_format_combination(self, pos, in_out, num_inputs):
        assert pos < len(in_out)

        desc = in_out[pos]
        if desc.format != trt.TensorFormat.LINEAR:
            return False
        ret = False

        if pos == 0:
            return (
                desc.type == trt.DataType.FLOAT
                or desc.type == trt.DataType.HALF
                or desc.type == trt.DataType.BF16
            )
        elif pos < 3 or pos == num_inputs:
            ret = desc.type == in_out[0].type
        elif pos == 3 or pos > num_inputs:
            ret = desc.type == trt.DataType.FLOAT
        else:
            ret = desc.type == trt.DataType.BOOL
        # print(f"supports_format_combination({pos}:{num_inputs}, {desc.type}): {ret}")
        return ret

    def enqueue(self, input_desc, output_desc, inputs, outputs, workspace, stream):
        with torch.cuda.stream(torch.cuda.ExternalStream(stream)):
            i_bs = [np.prod(i.dims) * i.type.itemsize for i in input_desc]
            o_bs = [np.prod(o.dims) * o.type.itemsize for o in output_desc]

            i_mem = [
                cp.cuda.UnownedMemory(inputs[i], i_bs[i], self)
                for i in range(len(inputs))
            ]
            o_mem = cp.cuda.UnownedMemory(outputs[0], o_bs[0], self)
            l_mem = cp.cuda.UnownedMemory(outputs[1], o_bs[1], self)

            i_ptr = [cp.cuda.MemoryPointer(i, 0) for i in i_mem]
            o_ptr = cp.cuda.MemoryPointer(o_mem, 0)
            l_ptr = cp.cuda.MemoryPointer(l_mem, 0)

            i_nd = [
                cp.ndarray((i_bs[i],), dtype=cp.uint8, memptr=i_ptr[i])
                for i in range(len(inputs))
            ]
            o_nd = cp.ndarray((o_bs[0],), dtype=cp.uint8, memptr=o_ptr)
            l_nd = cp.ndarray((o_bs[1],), dtype=cp.uint8, memptr=l_ptr)

            i_t = [
                torch.as_tensor(i_nd[i], device="cuda")
                .view(dtype=trt_to_torch[input_desc[i].type])
                .view(tuple(input_desc[i].dims))
                for i in range(len(inputs))
            ]
            ret = (
                torch.as_tensor(o_nd, device="cuda")
                .view(dtype=trt_to_torch[output_desc[0].type])
                .view(tuple(output_desc[0].dims))
            )
            l_ret = (
                torch.as_tensor(l_nd, device="cuda")
                .view(dtype=trt_to_torch[output_desc[1].type])
                .view(tuple(output_desc[1].dims))
            )
            m_ret = (
                torch.as_tensor(l_nd, device="cuda")
                .view(dtype=trt_to_torch[output_desc[1].type])
                .view(tuple(output_desc[1].dims))
            )

        mask = i_t[4] if len(inputs) == 5 else None

        seq_len = i_t[0].shape[-2]
        # print (f"seq_len = {seq_len}, threshold={CUEQ_TRIATTN_FALLBACK_THRESHOLD}")
        if seq_len <= CUEQ_TRIATTN_FALLBACK_THRESHOLD:
            # Use original PyTorch implementation for short sequences
            out = _triangle_attention_torch(
                i_t[0], i_t[1], i_t[2], i_t[3], mask, self.scale
            )
            ret.copy_(out)
        else:
            ops.triangle_attention(
                ret,
                l_ret,
                m_ret,
                i_t[0],
                i_t[1].detach().contiguous(),
                i_t[2].detach().contiguous(),
                mask,
                i_t[3].detach().contiguous(),
                self.scale,
                self.use_tf32,
                stream,
            )

        return 0

    def clone(self):
        cloned_plugin = TriangularAttentionPlugin()
        cloned_plugin.__dict__.update(self.__dict__)
        return cloned_plugin

    def get_serialization_size(self):
        return len(to_json(self.__dict__))


class TriangularAttentionPluginCreator(trt.IPluginCreator):
    def __init__(self):
        trt.IPluginCreator.__init__(self)
        self.name = "triangle_attention"
        self.plugin_namespace = "cuequivariance_ops"
        self.plugin_version = "1"
        self.field_names = trt.PluginFieldCollection([])

    def create_plugin(self, name, fc):
        pl = TriangularAttentionPlugin(fc)
        return pl

    def deserialize_plugin(self, name, data):
        j = dict(from_json(data.decode("utf-8")))
        deserialized = TriangularAttentionPlugin()
        deserialized.__dict__.update(j)
        return deserialized


PLUGINS_REGISTRY = None


def register_plugins():
    global PLUGINS_REGISTRY
    if PLUGINS_REGISTRY is None:
        PLUGINS_REGISTRY = trt.get_plugin_registry()
        PLUGINS_REGISTRY.register_creator(
            FusedTensorProductPluginCreator(), "cuequivariance_ops"
        )
        PLUGINS_REGISTRY.register_creator(
            SegmentedTransposePluginCreator(), "cuequivariance_ops"
        )
        PLUGINS_REGISTRY.register_creator(
            TensorProductUniform4x1dPluginCreator(), "cuequivariance_ops"
        )
        PLUGINS_REGISTRY.register_creator(
            TriangularAttentionPluginCreator(), "cuequivariance_ops"
        )
        PLUGINS_REGISTRY.register_creator(
            TriangularAttentionPluginCreator(), "cuequivariance_ops"
        )
