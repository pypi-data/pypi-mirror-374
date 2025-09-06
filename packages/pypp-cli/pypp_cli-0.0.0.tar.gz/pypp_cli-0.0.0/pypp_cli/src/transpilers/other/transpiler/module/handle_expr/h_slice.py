import ast

from pypp_cli.src.transpilers.other.transpiler.d_types import QInc
from pypp_cli.src.transpilers.other.transpiler.deps import Deps


def handle_slice(node: ast.Slice, d: Deps):
    # NOTE: The C++ code handles Nones for start, but this code just wont use that.
    # Which is maybe fine
    d.add_inc(QInc("slice/creators.h"))
    lower: str = "0" if node.lower is None else d.handle_expr(node.lower)
    step: str = "1" if node.step is None else d.handle_expr(node.step)
    upper: str = "std::nullopt" if node.upper is None else d.handle_expr(node.upper)
    return f"pypp::py_slice({lower}, {upper}, {step})"
