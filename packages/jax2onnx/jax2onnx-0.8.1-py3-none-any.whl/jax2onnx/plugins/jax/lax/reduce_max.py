# file: jax2onnx/plugins/jax/lax/reduce_max.py

from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Optional, Sequence

import jax.numpy as jnp
from jax import lax

from jax2onnx.plugin_system import PrimitiveLeafPlugin, register_primitive
from jax2onnx.converter.jaxpr_converter import Jaxpr2OnnxConverter
from ._reduce_utils import add_reduce_node  # shared helper

if TYPE_CHECKING:
    from jax2onnx.converter.jaxpr_converter import Jaxpr2OnnxConverter


# --------------------------------------------------------------------------- #
# 🧪 regression helper: verify ReduceMax axes handling for opset ≥ 18
# --------------------------------------------------------------------------- #
def _check_reduce_max_axes_input(onnx_model) -> bool:
    """
    Return **True** iff every ReduceMax node in *onnx_model*:
      • carries **no** 'axes' attribute, and
      • has a 2-input (data, axes) signature.

    That is the required format since opset-18.
    """
    for node in onnx_model.graph.node:
        if node.op_type != "ReduceMax":
            continue
        has_axes_attr = any(attr.name == "axes" for attr in node.attribute)
        correct_input_count = len(node.input) == 2
        if has_axes_attr or not correct_input_count:
            return False
    return True


reduce_max_p = lax.reduce_max_p


@register_primitive(
    jaxpr_primitive=reduce_max_p.name,
    jax_doc="https://docs.jax.dev/en/latest/_autosummary/jax.lax.reduce_max.html",
    onnx=[
        {
            "component": "ReduceMax",
            "doc": "https://onnx.ai/onnx/operators/onnx__ReduceMax.html",
        }
    ],
    since="v0.2.0",
    context="primitives.lax",
    component="reduce_max",
    testcases=[
        {
            "testcase": "reduce_max",
            "callable": lambda x: jnp.max(x, axis=(0,)),
            "input_shapes": [(3, 3)],
        },
        {
            "testcase": "reduce_max_allaxes",
            "callable": lambda x: jnp.max(x),  # max over all axes
            "input_shapes": [(2, 3, 4)],
        },
        {
            "testcase": "reduce_max_keepdims",
            "callable": lambda x: jnp.max(x, axis=(1,), keepdims=True),
            "input_shapes": [(3, 4)],
        },
        {
            "testcase": "reduce_max_axes_input",
            "callable": lambda x: jnp.max(x, axis=(1,)),
            "input_shapes": [(2, 3)],
            # structural assertion only – fails with current implementation
            "post_check_onnx_graph": _check_reduce_max_axes_input,
            "skip_numeric_validation": True,
        },
    ],
)
class ReduceMaxPlugin(PrimitiveLeafPlugin):
    """Plugin for converting jax.lax.reduce_max (invoked via jnp.max) to ONNX ReduceMax."""

    primitive = reduce_max_p

    def to_onnx(
        self,
        conv: Jaxpr2OnnxConverter,
        node_inputs: List[Any],
        node_outputs: List[Any],
        params: dict[str, Any],
    ):
        # 1) Grab the JAX inputs and target ONNX names:
        x_var = node_inputs[0]
        input_name = conv.get_name(x_var)
        out_var = node_outputs[0]
        output_name = conv.get_name(out_var)

        # 2) Extract axes / keepdims from JAX parameters:
        axes: Optional[Sequence[int]] = params.get("axes", None)
        keepdims_flag: bool = params.get("keepdims", False)

        # 3) Emit the ReduceMax node via our shared helper:
        add_reduce_node(
            conv.builder,
            "ReduceMax",
            input_name,
            output_name,
            axes=list(axes) if axes is not None else None,
            keepdims=1 if keepdims_flag else 0,
        )

        # 4) Declare the output's value_info (shape & dtype):
        aval = out_var.aval
        out_dtype_enum = conv._ensure_onnx_dtype(aval.dtype)
        conv.builder.add_value_info(
            output_name,
            tuple(conv._dim_to_symbol_safe(d) for d in aval.shape),
            out_dtype_enum,
        )
