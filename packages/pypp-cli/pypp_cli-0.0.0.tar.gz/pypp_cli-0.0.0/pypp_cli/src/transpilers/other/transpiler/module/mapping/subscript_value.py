from pypp_cli.src.transpilers.other.transpiler.deps import Deps
from pypp_cli.src.transpilers.other.transpiler.maps.d_types import (
    SubscriptableTypeMapValue,
)
from pypp_cli.src.transpilers.other.transpiler.module.mapping.util import is_one


def lookup_cpp_subscript_value_type(cpp_value: str, d: Deps) -> tuple[str, str]:
    if cpp_value in d.maps.subscriptable_type:
        r: SubscriptableTypeMapValue = d.maps.subscriptable_type[cpp_value]
        if is_one(r, d):
            return cpp_value + "<", ">"
    return cpp_value + "[", "]"
