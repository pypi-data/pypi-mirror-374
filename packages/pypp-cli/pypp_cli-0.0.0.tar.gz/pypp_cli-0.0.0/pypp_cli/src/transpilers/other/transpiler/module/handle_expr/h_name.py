import ast


from pypp_cli.src.transpilers.other.transpiler.deps import Deps
from pypp_cli.src.transpilers.other.transpiler.maps.d_types import (
    CustomMappingEntry,
    CustomMappingFromLibEntry,
    CustomMappingStartsWithEntry,
    CustomMappingStartsWithFromLibEntry,
    ToStringEntry,
)
from pypp_cli.src.transpilers.other.transpiler.module.mapping.util import (
    calc_string_fn,
    find_map_entry,
)


def handle_name(node: ast.Name, d: Deps) -> str:
    if node.id in d.cpp_includes.include_map:
        d.add_inc(d.cpp_includes.include_map[node.id])
    name: str = node.id
    if name in d.user_namespace:
        # In this case there is no need to check the maps, because it wont be in there.
        return "me::" + name

    for k, v in d.maps.name.items():
        e = find_map_entry(v, d)
        if e is None:
            continue
        if isinstance(e, ToStringEntry):
            if name == k:
                d.add_incs(e.includes)
                return e.to
        elif isinstance(e, CustomMappingEntry):
            if name == k:
                d.add_incs(e.includes)
                return e.mapping_fn(node, d)
        elif isinstance(e, CustomMappingFromLibEntry):
            if name.startswith(k):
                d.add_incs(e.includes)
                return calc_string_fn(e)(node, d)
        elif isinstance(e, CustomMappingStartsWithEntry):
            if name.startswith(k):
                d.add_incs(e.includes)
                return e.mapping_fn(node, d, name)
        elif isinstance(e, CustomMappingStartsWithFromLibEntry):
            if name.startswith(k):
                d.add_incs(e.includes)
                return calc_string_fn(e)(node, d, name)
    return name
