from dataclasses import dataclass

from pypp_cli.src.transpilers.other.transpiler.maps.ann_assign import (
    ANN_ASSIGN_MAP,
)
from pypp_cli.src.transpilers.other.transpiler.maps.attr import (
    ATTR_CALC_ENTRY_FN_MAP,
    ATTR_MAP,
)
from pypp_cli.src.transpilers.other.transpiler.maps.call.call import (
    CALL_CALC_ENTRY_FN_MAP,
    CALL_MAP,
)
from pypp_cli.src.transpilers.other.transpiler.maps.fn_arg_passed_by_value import (
    FN_ARG_PASSED_BY_VALUE_MAP,
    fn_arg_passed_by_value_warning_msg,
)
from pypp_cli.src.transpilers.other.transpiler.maps.util.calc_import_map import (
    ImportMap,
    ImportMapCltr,
)
from pypp_cli.src.transpilers.other.transpiler.maps.name import NAME_MAP
from pypp_cli.src.transpilers.other.transpiler.maps.d_types import (
    AnnAssignsMap,
    AttrMap,
    CallMap,
    FnArgByValueMap,
    NameMap,
    SubscriptableTypeMap,
)
from pypp_cli.src.transpilers.other.transpiler.maps.subscriptable_types import (
    SUBSCRIPTABLE_TYPE_MAP,
    subscriptable_type_warning_msg,
)
from pypp_cli.src.transpilers.other.transpiler.maps.util.calc_map_1 import (
    BASE_CALC_ENTRY_FN_MAP,
    MapCltr1,
)
from pypp_cli.src.transpilers.other.transpiler.maps.util.calc_map_2 import MapCltr2


@dataclass(frozen=True, slots=True)
class Maps:
    name: NameMap
    call: CallMap
    attr: AttrMap
    fn_arg_passed_by_value: FnArgByValueMap
    subscriptable_type: SubscriptableTypeMap
    import_: ImportMap
    ann_assign: AnnAssignsMap


@dataclass(frozen=True, slots=True)
class MapsCltr:
    _cltr1: MapCltr1
    _cltr2: MapCltr2
    _import_cltr: ImportMapCltr

    def calc_maps(self) -> Maps:
        return Maps(
            self._cltr1.calc_map_1(
                NAME_MAP, BASE_CALC_ENTRY_FN_MAP, "name_map", "name"
            ),
            self._cltr1.calc_map_1(
                CALL_MAP,
                CALL_CALC_ENTRY_FN_MAP,
                "call_map",
                "call",
            ),
            self._cltr1.calc_map_1(
                ATTR_MAP, ATTR_CALC_ENTRY_FN_MAP, "attr_map", "attr"
            ),
            self._cltr2.calc_map_2(
                FN_ARG_PASSED_BY_VALUE_MAP,
                "always_pass_by_value",
                fn_arg_passed_by_value_warning_msg,
            ),
            self._cltr2.calc_map_2(
                SUBSCRIPTABLE_TYPE_MAP,
                "subscriptable_types",
                subscriptable_type_warning_msg,
            ),
            self._import_cltr.calc_import_map(),
            self._cltr1.calc_map_1(
                ANN_ASSIGN_MAP,
                BASE_CALC_ENTRY_FN_MAP,
                "ann_assign_map",
                "ann_assign",
            ),
        )
