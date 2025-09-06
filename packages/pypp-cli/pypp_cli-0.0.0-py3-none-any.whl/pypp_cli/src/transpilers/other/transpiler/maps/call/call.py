import ast
from typing import Callable

from pypp_cli.src.transpilers.other.transpiler.d_types import (
    QInc,
    PySpecificImpFrom,
    AngInc,
    PyImport,
)
from pypp_cli.src.transpilers.other.transpiler.maps.util.util import (
    calc_cpp_includes,
)
from pypp_cli.src.transpilers.other.transpiler.maps.d_types import (
    CallMapEntry,
    LeftAndRightEntry,
    CallMap,
    ToStringEntry,
    CustomMappingEntry,
    CustomMappingStartsWithEntry,
    ReplaceDotWithDoubleColonEntry,
)
from pypp_cli.src.transpilers.other.transpiler.maps.util.calc_map_1 import (
    BASE_CALC_ENTRY_FN_MAP,
    calc_replace_dot_with_double_colon_entry,
)
from pypp_cli.src.transpilers.other.transpiler.maps.call.default_dict_map_fn import (
    good_default_dict,
)


def _default_dict(_node: ast.Call, _d) -> str:
    raise Exception(
        "defaultdict must be called with type info "
        "(i.e. defaultdict[KeyType, ValueType])"
    )


def _tuple_get(node: ast.Call, d) -> str:
    assert len(node.args) == 2, "tg should have 2 arguments"
    tuple_arg = d.handle_expr(node.args[0])
    index_arg = d.handle_expr(node.args[1])
    return f"{tuple_arg}.get<{index_arg}>()"


def _dict_get(node: ast.Call, d) -> str:
    assert len(node.args) == 2, "dg should have 2 arguments"
    dict_arg = d.handle_expr(node.args[0])
    index_arg = d.handle_expr(node.args[1])
    return f"{dict_arg}.dg({index_arg})"


def _union_get(node: ast.Call, d) -> str:
    assert len(node.args) == 2, "ug should have 2 arguments"
    union_arg = d.handle_expr(node.args[0])
    type_arg = d.handle_expr(node.args[1])
    return f"{union_arg}.ug<{type_arg}>()"


def _union_isinst(node: ast.Call, d) -> str:
    assert len(node.args) == 2, "isinst should have 2 arguments"
    obj_arg = d.handle_expr(node.args[0])
    type_arg = d.handle_expr(node.args[1])
    return f"{obj_arg}.isinst<{type_arg}>()"


def _union_is_none(node: ast.Call, d) -> str:
    assert len(node.args) == 1, "is_none should have 1 argument"
    obj_arg = d.handle_expr(node.args[0])
    return f"{obj_arg}.is_none()"


def _list_reserve(node: ast.Call, d) -> str:
    assert len(node.args) == 2, "list_reserve should have 2 arguments"
    list_arg = d.handle_expr(node.args[0])
    size_arg = d.handle_expr(node.args[1])
    return f"{list_arg}.reserve({size_arg})"


def _pypp_time(node: ast.Call, d, caller_str: str) -> str:
    fn: str = caller_str[caller_str.rfind(".") + 1 :]
    return f"pypp::time::{fn}({d.handle_exprs(node.args)})"


CALL_MAP: CallMap = {
    "print": {None: ToStringEntry("pypp::print", [QInc("pypp_util/print.h")])},
    # TODO: This can be deleted now that I can use print(Ref(a))
    "print_address": {
        PySpecificImpFrom("pypp_python", "print_address"): LeftAndRightEntry(
            "pypp::print(&",
            ")",
            [QInc("pypp_util/print.h")],
        )
    },
    "len": {None: LeftAndRightEntry("", ".len()", [])},
    "to_std_string": {
        PySpecificImpFrom("pypp_python", "to_std_string"): LeftAndRightEntry(
            "", ".str()", []
        )
    },
    "to_c_string": {
        PySpecificImpFrom("pypp_python", "to_c_string"): LeftAndRightEntry(
            "", ".str().c_str()", []
        )
    },
    "pypp::PyStr": {
        None: ToStringEntry("pypp::to_pystr", [QInc("pypp_util/to_py_str.h")])
    },
    "pypp::PySlice": {
        None: ToStringEntry("pypp::py_slice", [QInc("slice/creators.h")])
    },
    "mov": {
        PySpecificImpFrom("pypp_python", "mov"): ToStringEntry(
            "std::move", [AngInc("utility")]
        )
    },
    "pypp_get_resources": {
        PySpecificImpFrom("pypp_python", "pypp_get_resources"): ToStringEntry(
            "pypp::pypp_get_resources", [QInc("pypp_resources.h")]
        )
    },
    "int_pow": {
        PySpecificImpFrom("pypp_python", "int_pow"): ToStringEntry(
            "pypp::int_pow", [QInc("pypp_util/math.h")]
        )
    },
    "pypp::PyDefaultDict": {
        PySpecificImpFrom("collections", "defaultdict"): CustomMappingEntry(
            _default_dict, []
        )
    },
    "tg": {PySpecificImpFrom("pypp_python", "tg"): CustomMappingEntry(_tuple_get, [])},
    "dg": {PySpecificImpFrom("pypp_python", "dg"): CustomMappingEntry(_dict_get, [])},
    "ug": {PySpecificImpFrom("pypp_python", "ug"): CustomMappingEntry(_union_get, [])},
    "isinst": {
        PySpecificImpFrom("pypp_python", "isinst"): CustomMappingEntry(
            _union_isinst, []
        )
    },
    "is_none": {
        PySpecificImpFrom("pypp_python", "is_none"): CustomMappingEntry(
            _union_is_none, []
        )
    },
    "list_reserve": {
        PySpecificImpFrom("pypp_python", "list_reserve"): CustomMappingEntry(
            _list_reserve, []
        )
    },
    "pypp::PyDefaultDict<": {
        PySpecificImpFrom("collections", "defaultdict"): CustomMappingStartsWithEntry(
            good_default_dict, []
        )
    },
    "os.": {PyImport("os"): ReplaceDotWithDoubleColonEntry([QInc("pypp_os.h")], True)},
    "shutil.": {
        PyImport("shutil"): ReplaceDotWithDoubleColonEntry(
            [QInc("pypp_shutil.h")], True
        )
    },
    "pypp_time.": {
        PySpecificImpFrom("pypp_python", "pypp_time"): CustomMappingStartsWithEntry(
            _pypp_time, [QInc("pypp_time.h")]
        )
    },
}


def _calc_left_and_right_entry(obj: dict) -> LeftAndRightEntry:
    return LeftAndRightEntry(obj["left"], obj["right"], calc_cpp_includes(obj))


CALL_CALC_ENTRY_FN_MAP: dict[str, Callable[[dict], CallMapEntry]] = {
    **BASE_CALC_ENTRY_FN_MAP,
    "left_and_right": _calc_left_and_right_entry,
    "replace_dot_with_double_colon": calc_replace_dot_with_double_colon_entry,
}
