from pypp_cli.src.transpilers.other.transpiler.d_types import PySpecificImpFrom
from pypp_cli.src.transpilers.other.transpiler.maps.d_types import SubscriptableTypeMap

SUBSCRIPTABLE_TYPE_MAP: SubscriptableTypeMap = {
    "pypp::PyList": {None},
    "pypp::PyDict": {None},
    "pypp::PyTup": {None},
    "pypp::PySet": {None},
    "pypp::PyDefaultDict": {PySpecificImpFrom("collections", "defaultdict")},
    "pypp::Uni": {PySpecificImpFrom("pypp_python", "Uni")},
}


def subscriptable_type_warning_msg(installed_library: str, full_type_str: str) -> str:
    return (
        f"Py++ transpiler already considers {full_type_str} a subscriptable type. "
        f"Library {installed_library} is potentially changing this behavior."
    )
