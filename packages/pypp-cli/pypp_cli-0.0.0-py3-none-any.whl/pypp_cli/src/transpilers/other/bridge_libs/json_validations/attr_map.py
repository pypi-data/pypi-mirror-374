from pypp_cli.src.transpilers.other.bridge_libs.json_validations.util.validate_1 import (  # noqa: E501
    BASE_VALIDATE_ENTRY_MAP,
    validate_1,
    validate_replace_dot_with_double_colon,
)


_S: str = "attr_map.json"

VALIDATE_ATTR_ENTRY_MAP = {
    **BASE_VALIDATE_ENTRY_MAP,
    "replace_dot_with_double_colon": validate_replace_dot_with_double_colon,
}


def validate_attr_map(attr_map: object):
    validate_1(attr_map, VALIDATE_ATTR_ENTRY_MAP, _S)
