from typing import TYPE_CHECKING, Callable

import numpy as np
from flax import nnx
from jax import core, numpy as jnp
from jax.extend.core import Primitive
from onnx import TensorProto, helper
from jax.interpreters import batching
from onnx.mapping import NP_TYPE_TO_TENSOR_TYPE as np2ONNX

from jax2onnx.plugin_system import PrimitiveLeafPlugin, register_primitive

if TYPE_CHECKING:
    from jax2onnx.converter.jaxpr_converter import Jaxpr2OnnxConverter


# Global variable to store the original function
_ORIGINAL_DOT_PRODUCT_ATTENTION_CALL: Callable | None = None


def _dpa_inputs_f64_no_full_mask():
    rng = np.random.RandomState(0)
    q = rng.randn(2, 8, 4, 16).astype(np.float64)
    k = rng.randn(2, 8, 4, 16).astype(np.float64)
    v = rng.randn(2, 8, 4, 16).astype(np.float64)

    # mask shape (B, H, Q, K); start with all masked, then unmask diagonal
    mask = np.ones((2, 4, 8, 8), dtype=bool)
    idx = np.arange(8)
    mask[:, :, idx, idx] = False  # guarantee at least one unmasked per row

    bias = np.zeros((2, 4, 8, 8), dtype=np.float64)
    return [q, k, v, mask, bias]


# Callable definitions for test cases
def dpa_with_mask(q, k, v, mask):
    return nnx.dot_product_attention(q, k, v, mask=mask)


def dpa_with_bias(q, k, v, bias):
    return nnx.dot_product_attention(q, k, v, bias=bias)


def dpa_with_mask_and_bias(q, k, v, mask, bias):
    return nnx.dot_product_attention(q, k, v, mask=mask, bias=bias)


nnx.dot_product_attention_p = Primitive("nnx.dot_product_attention")
nnx.dot_product_attention_p.multiple_results = False


@register_primitive(
    jaxpr_primitive=nnx.dot_product_attention_p.name,
    jax_doc="https://flax.readthedocs.io/en/latest/api_reference/flax.nnx/nn/attention.html#flax.nnx.dot_product_attention",
    onnx=[
        {
            "component": "Shape",
            "doc": "https://onnx.ai/onnx/operators/onnx__Shape.html",
        },
        {
            "component": "Gather",
            "doc": "https://onnx.ai/onnx/operators/onnx__Gather.html",
        },
        {"component": "Cast", "doc": "https://onnx.ai/onnx/operators/onnx__Cast.html"},
        {"component": "Sqrt", "doc": "https://onnx.ai/onnx/operators/onnx__Sqrt.html"},
        {"component": "Div", "doc": "https://onnx.ai/onnx/operators/onnx__Div.html"},
        {
            "component": "Einsum",
            "doc": "https://onnx.ai/onnx/operators/onnx__Einsum.html",
        },
        {
            "component": "Softmax",
            "doc": "https://onnx.ai/onnx/operators/onnx__Softmax.html",
        },
    ],
    since="v0.1.0",
    context="primitives.nnx",
    component="dot_product_attention",
    testcases=[
        {
            "testcase": "dpa_basic",
            "callable": lambda q, k, v: nnx.dot_product_attention(q, k, v),
            "input_shapes": [(2, 8, 4, 16), (2, 8, 4, 16), (2, 8, 4, 16)],
            "rtol_f64": 1e-6,
            "atol_f64": 1e-6,
        },
        {
            "testcase": "dpa_with_tensor_mask",
            "callable": dpa_with_mask,
            "input_shapes": [(2, 8, 4, 16), (2, 8, 4, 16), (2, 8, 4, 16), (2, 4, 8, 8)],
            "input_dtypes": [np.float32, np.float32, np.float32, np.bool_],
            "run_only_f32_variant": True,
        },
        {
            "testcase": "dpa_with_bias",
            "callable": dpa_with_bias,
            "input_shapes": [(2, 8, 4, 16), (2, 8, 4, 16), (2, 8, 4, 16), (2, 4, 8, 8)],
            "run_only_f32_variant": True,
        },
        {
            "testcase": "dpa_with_causal_mask",
            "callable": dpa_with_mask,
            "input_values": [
                np.random.randn(1, 8, 4, 16).astype(np.float32),
                np.random.randn(1, 8, 4, 16).astype(np.float32),
                np.random.randn(1, 8, 4, 16).astype(np.float32),
                np.tril(np.ones((1, 4, 8, 8), dtype=bool)),
            ],
            "rtol_f64": 1e-6,
            "atol_f64": 1e-6,
        },
        {
            "testcase": "dpa_with_mask_and_bias",
            "callable": dpa_with_mask_and_bias,
            # switch from shapes/dtypes → concrete values to avoid fully-masked rows
            "input_values": _dpa_inputs_f64_no_full_mask(),
            "expected_output_shapes": [(2, 8, 4, 16)],  # optional but nice
            "expected_output_dtypes": [np.float64],  # keep it f64
            "rtol_f64": 1e-6,
            "atol_f64": 1e-6,
            "run_only_f64_variant": True,
        },
    ],
)
class DotProductAttentionPlugin(PrimitiveLeafPlugin):

    @staticmethod
    def abstract_eval(q, k, v, *args, **kwargs):
        # The output shape is always the same as the query's shape.
        return core.ShapedArray(q.shape, q.dtype)

    def to_onnx(self, s: "Jaxpr2OnnxConverter", node_inputs, node_outputs, params):
        # Inputs/outputs
        q_sym = s.get_name(node_inputs[0])
        k_sym = s.get_name(node_inputs[1])
        v_sym = s.get_name(node_inputs[2])
        out_sym = s.get_name(node_outputs[0])

        # Figure out which optional args are present using the flags we set in bind()
        has_mask = bool(params.get("has_mask", False))
        has_bias = bool(params.get("has_bias", False))

        next_idx = 3
        mask_sym = s.get_name(node_inputs[next_idx]) if has_mask else None
        next_idx += 1 if has_mask else 0
        bias_sym = s.get_name(node_inputs[next_idx]) if has_bias else None

        # Shapes and dtypes
        q_shape = node_inputs[0].aval.shape  # (B, T, N, H)
        k_shape = node_inputs[1].aval.shape  # (B, T, N, H)
        np_dtype = node_inputs[0].aval.dtype
        B, T, N, H = q_shape
        S = k_shape[1]  # kv_length

        # Helper: cast a tensor to a target dtype if needed
        def _cast_to(sym: str, target_dt):
            cur = s.builder.get_dtype(sym)
            if cur is not None and np.dtype(cur) == np.dtype(target_dt):
                return sym
            out = s.builder.get_unique_name(f"{sym}_cast_{np.dtype(target_dt).name}")
            s.add_node(
                helper.make_node(
                    "Cast",
                    inputs=[sym],
                    outputs=[out],
                    name=s.get_unique_name("CastDPA"),
                    to=np2ONNX[np.dtype(target_dt)],
                )
            )
            r = s.builder.get_rank(sym) or 0
            s.add_shape_info(out, (None,) * r, target_dt)
            return out

        # q -> (B, N, T, H)
        q_t = s.get_unique_name("q_T")
        s.add_node(helper.make_node("Transpose", [q_sym], [q_t], perm=[0, 2, 1, 3]))
        s.add_shape_info(q_t, (B, N, T, H), np_dtype)

        # k -> (B, N, H, S)
        k_t = s.get_unique_name("k_T")
        s.add_node(helper.make_node("Transpose", [k_sym], [k_t], perm=[0, 2, 3, 1]))
        s.add_shape_info(k_t, (B, N, H, S), np_dtype)

        # logits = (q / sqrt(H)) @ k^T   <== equivalent to (q @ k^T) * (1/sqrt(H))
        scale_const = s.get_constant_name(np.array(1.0 / np.sqrt(H), dtype=np_dtype))
        q_scaled = s.get_unique_name("q_scaled")
        s.add_node(helper.make_node("Mul", [q_t, scale_const], [q_scaled]))
        s.add_shape_info(q_scaled, (B, N, T, H), np_dtype)

        logits = s.get_unique_name("attn_scores")
        s.add_node(helper.make_node("MatMul", [q_scaled, k_t], [logits]))
        s.add_shape_info(logits, (B, N, T, S), np_dtype)

        cur_logits = logits

        # + bias (added to logits; NOT scaled)
        if has_bias and bias_sym is not None:
            if s.builder.get_dtype(bias_sym) is None or np.dtype(
                s.builder.get_dtype(bias_sym)
            ) != np.dtype(np_dtype):
                bias_sym = _cast_to(bias_sym, np_dtype)
            add_b = s.get_unique_name("logits_plus_bias")
            s.add_node(helper.make_node("Add", [cur_logits, bias_sym], [add_b]))
            s.add_shape_info(add_b, (B, N, T, S), np_dtype)
            cur_logits = add_b

        # apply mask using dtype min (Flax semantics): where(mask, x, finfo(dtype).min)
        if has_mask and mask_sym is not None:
            mdt = s.builder.get_dtype(mask_sym)
            if mdt is None or np.dtype(mdt) != np.dtype(bool):
                mask_bool = s.get_unique_name("mask_bool")
                s.add_node(
                    helper.make_node(
                        "Cast", [mask_sym], [mask_bool], to=TensorProto.BOOL
                    )
                )
                s.add_shape_info(mask_bool, (B, N, T, S), bool)
                mask_sym = mask_bool
            big_neg = s.get_constant_name(
                np.array(np.finfo(np_dtype).min, dtype=np_dtype)
            )
            masked = s.get_unique_name("masked_logits")
            s.add_node(
                helper.make_node("Where", [mask_sym, cur_logits, big_neg], [masked])
            )
            s.add_shape_info(masked, (B, N, T, S), np_dtype)
            cur_logits = masked

        # softmax over last dim (kv_length)
        weights = s.get_unique_name("attn_weights")
        s.add_node(helper.make_node("Softmax", [cur_logits], [weights], axis=-1))
        s.add_shape_info(weights, (B, N, T, S), np_dtype)

        # v -> (B, N, S, H)
        v_t = s.get_unique_name("v_T")
        s.add_node(helper.make_node("Transpose", [v_sym], [v_t], perm=[0, 2, 1, 3]))
        s.add_shape_info(v_t, (B, N, S, H), np_dtype)

        # output: (B, N, T, H) -> (B, T, N, H)
        out_t = s.get_unique_name("out_T")
        s.add_node(helper.make_node("MatMul", [weights, v_t], [out_t]))
        s.add_shape_info(out_t, (B, N, T, H), np_dtype)

        s.add_node(helper.make_node("Transpose", [out_t], [out_sym], perm=[0, 2, 1, 3]))
        s.add_shape_info(out_sym, q_shape, np_dtype)

    @staticmethod
    def get_monkey_patch():
        def patched(q, k, v, mask=None, bias=None, **kwargs):
            has_mask = mask is not None
            has_bias = bias is not None
            inputs = [q, k, v]
            if has_mask:
                inputs.append(mask)
            if has_bias:
                inputs.append(bias)
            # Pass kwargs through to the primitive binding
            return nnx.dot_product_attention_p.bind(
                *inputs, has_mask=has_mask, has_bias=has_bias, **kwargs
            )

        return patched

    @staticmethod
    def patch_info():
        return {
            "patch_targets": [nnx],
            "patch_function": lambda _: DotProductAttentionPlugin.get_monkey_patch(),
            "target_attribute": "dot_product_attention",
        }


nnx.dot_product_attention_p.def_abstract_eval(DotProductAttentionPlugin.abstract_eval)


def dpa_batch(xs, dims, **params):
    bdim = next((d for d in dims if d is not None), None)
    if bdim is not None:
        xs = [jnp.moveaxis(x, d, 0) if d is not None else x for x, d in zip(xs, dims)]
    return nnx.dot_product_attention_p.bind(*xs, **params), 0


batching.primitive_batchers[nnx.dot_product_attention_p] = dpa_batch
