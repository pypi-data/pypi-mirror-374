from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True, slots=True)
class AngInc:
    # Angle Bracket Include
    val: str


@dataclass(frozen=True, slots=True)
class QInc:
    # Quotes Include
    val: str


CppInclude = Union[AngInc, QInc]


@dataclass(frozen=True, slots=True)
class PySpecificImpFrom:
    frm: str
    name: str


@dataclass(frozen=True, slots=True)
class PyImport:
    name: str
    as_name: str | None = None


type PySpecificImport = Union[PySpecificImpFrom, PyImport]


@dataclass(frozen=True, slots=True)
class PyImports:
    # key: module name, value: list of names imported from that module
    imp_from: dict[str, list[str]]
    imp: set[PyImport]


def is_imported(py_imports: PyImports, imp: PySpecificImport) -> bool:
    if isinstance(imp, PyImport):
        return imp in py_imports.imp
    # PySpecificImpFrom
    return imp.frm in py_imports.imp_from and imp.name in py_imports.imp_from[imp.frm]
