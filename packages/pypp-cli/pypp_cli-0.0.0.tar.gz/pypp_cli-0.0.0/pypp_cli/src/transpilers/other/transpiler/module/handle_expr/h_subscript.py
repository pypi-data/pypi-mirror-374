import ast

from pypp_cli.src.transpilers.other.transpiler.deps import Deps
from pypp_cli.src.transpilers.other.transpiler.module.handle_expr.h_tuple import (
    handle_tuple_inner_args,
)
from pypp_cli.src.transpilers.other.transpiler.module.mapping.subscript_value import (
    lookup_cpp_subscript_value_type,
)


def handle_subscript(node: ast.Subscript, d: Deps) -> str:
    value_cpp_str = d.handle_expr(node.value)
    if value_cpp_str == "pypp::PyDefaultDict":
        assert isinstance(node.slice, ast.Tuple), (
            "defaultdict must be called as defaultdict[KeyType, ValueType]"
        )
        assert len(node.slice.elts) == 2, "2 types expected when calling defaultdict"
    if isinstance(node.slice, ast.Tuple):
        slice_cpp_str = handle_tuple_inner_args(node.slice, d)
    else:
        slice_cpp_str: str = d.handle_expr(node.slice)
    v1, v2 = lookup_cpp_subscript_value_type(value_cpp_str, d)
    return v1 + slice_cpp_str + v2
