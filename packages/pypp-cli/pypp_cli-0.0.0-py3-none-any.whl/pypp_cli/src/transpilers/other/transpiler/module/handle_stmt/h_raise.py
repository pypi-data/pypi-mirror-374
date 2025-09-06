import ast

from pypp_cli.src.transpilers.other.transpiler.deps import Deps
from pypp_cli.src.transpilers.other.transpiler.module.mapping.exceptions import (
    lookup_cpp_exception_type,
)
from pypp_cli.src.transpilers.other.transpiler.module.util.inner_strings import (
    calc_inside_rd,
)


def handle_raise(node: ast.Raise, d: Deps) -> str:
    assert node.cause is None, "exception cause not supported"
    assert node.exc is not None, "raising without exception type is not supported"
    exe_str = d.handle_expr(node.exc)
    inside_str = calc_inside_rd(exe_str)
    python_exception_type = exe_str.split("(", 1)[0]
    cpp_exception_type = lookup_cpp_exception_type(python_exception_type, d)
    return f"throw {cpp_exception_type}({inside_str});"
