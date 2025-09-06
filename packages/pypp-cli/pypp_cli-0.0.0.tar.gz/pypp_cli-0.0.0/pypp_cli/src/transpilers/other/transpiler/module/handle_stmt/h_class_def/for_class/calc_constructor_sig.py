from pypp_cli.src.transpilers.other.transpiler.module.handle_stmt.h_class_def.util import (  # noqa: E501
    ARG_PREFIX,
)


def calc_constructor_signature_for_class(
    class_name: str, field_types: dict[str, str]
) -> str:
    ret: list[str] = []
    for n, t in field_types.items():
        ret.append(f"{t} {ARG_PREFIX}{n}")
    return class_name + "(" + ", ".join(ret) + ")"
