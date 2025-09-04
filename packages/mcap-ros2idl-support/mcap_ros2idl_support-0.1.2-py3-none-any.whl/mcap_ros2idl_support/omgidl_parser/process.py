from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Union, cast

from mcap_ros2idl_support.message_definition import (
    AggregatedKind,
    MessageDefinitionField,
    UnionCase,
)
from mcap_ros2idl_support.omgidl_parser.parse import (
    Constant,
    Enum,
    Field,
    Module,
    Struct,
    Typedef,
)
from mcap_ros2idl_support.omgidl_parser.parse import Union as IDLUnion

# ---------------------------------------------------------------------------
# Message definition dataclasses -------------------------------------------------


@dataclass
class IDLStructDefinition:
    name: str
    definitions: List[MessageDefinitionField]
    aggregatedKind: AggregatedKind = AggregatedKind.STRUCT
    annotations: Optional[Dict[str, Any]] = None


@dataclass
class IDLModuleDefinition:
    name: str
    definitions: List[MessageDefinitionField]
    aggregatedKind: AggregatedKind = AggregatedKind.MODULE
    annotations: Optional[Dict[str, Any]] = None


@dataclass
class IDLUnionDefinition:
    name: str
    switchType: str
    cases: List[UnionCase]
    defaultCase: Optional[MessageDefinitionField] = None
    aggregatedKind: AggregatedKind = AggregatedKind.UNION
    annotations: Optional[Dict[str, Any]] = None


IDLMessageDefinition = Union[
    IDLStructDefinition, IDLModuleDefinition, IDLUnionDefinition
]

# ---------------------------------------------------------------------------
# Map building -------------------------------------------------------------------


Definition = Union[Struct, Module, Constant, Enum, Typedef, IDLUnion]


def build_map(definitions: Iterable[Definition]) -> dict[str, Definition]:
    """Traverse parsed nodes and return a map of fully scoped names to nodes."""

    idl_map: dict[str, Definition] = {}

    def traverse(defn: Definition, scope: List[str]) -> None:
        if isinstance(defn, Module):
            for sub in defn.definitions:
                traverse(sub, [*scope, defn.name])
            scoped = "::".join([*scope, defn.name])
            idl_map[scoped] = defn
        elif isinstance(defn, Enum):
            scoped = "::".join([*scope, defn.name])
            idl_map[scoped] = defn
            for enumerator in defn.enumerators:
                scoped_enum = "::".join([*scope, defn.name, enumerator.name])
                idl_map[scoped_enum] = enumerator
        else:
            scoped = "::".join([*scope, defn.name])
            idl_map[scoped] = defn

    for definition in definitions:
        traverse(definition, [])

    return idl_map


# ---------------------------------------------------------------------------
# Conversion helpers -------------------------------------------------------------


def _resolve_typedef(
    type_name: str,
    typedefs: Dict[str, Typedef],
) -> tuple[str, List[int], bool, Optional[int], Optional[int]]:
    """Resolve typedef chain returning final type and collected modifiers.

    Returns a tuple of (type, array_lengths, is_sequence, sequence_bound,
    string_upper_bound).
    """

    t = type_name
    array_lengths: List[int] = []
    is_sequence = False
    seq_bound: Optional[int] = None
    str_bound: Optional[int] = None
    visited: set[str] = set()
    while t in typedefs and t not in visited:
        visited.add(t)
        td = typedefs[t]
        base_type = td.type

        # Detect composing variable length arrays within typedef chains.
        if isinstance(base_type, str) and base_type in typedefs:
            inner_td = typedefs[base_type]
            outer_has_array = bool(td.array_lengths) or td.is_sequence
            inner_has_array = bool(inner_td.array_lengths) or inner_td.is_sequence
            if outer_has_array and inner_has_array:
                outer_fixed = bool(td.array_lengths) and not td.is_sequence
                inner_fixed = bool(inner_td.array_lengths) and not inner_td.is_sequence
                if not (outer_fixed and inner_fixed):
                    raise ValueError(
                        (
                            "We do not support composing variable length arrays "
                            "with typedefs"
                        )
                    )

        if isinstance(base_type, tuple):
            if base_type[0] == "sequence":
                is_sequence = True
                seq_bound = base_type[2]
                base_type = base_type[1]
            else:
                str_bound = base_type[1]
                base_type = base_type[0]
        t = base_type
        if td.array_lengths:
            array_lengths.extend(td.array_lengths)
        if td.is_sequence:
            is_sequence = True
            if td.sequence_bound is not None:
                seq_bound = td.sequence_bound
        # string bounds are not currently represented on Typedef in parse.py
    return t, array_lengths, is_sequence, seq_bound, str_bound


def _convert_constant(
    const: Constant,
    typedefs: Dict[str, Typedef],
    idl_map: Dict[str, Definition],
) -> MessageDefinitionField:
    t, _arr, _is_seq, _seq_bound, _str_bound = _resolve_typedef(const.type, typedefs)
    enum_type = None
    is_complex = False
    ref = idl_map.get(t)
    if isinstance(ref, Enum):
        enum_type = t
        t = "uint32"
    elif isinstance(ref, (Struct, IDLUnion)):
        is_complex = True
    return MessageDefinitionField(
        name=const.name,
        type=t,
        isComplex=is_complex,
        enumType=enum_type,
        isConstant=True,
        value=const.value,
        valueText=str(const.value),
    )


def _convert_field(
    field: Field,
    typedefs: Dict[str, Typedef],
    idl_map: Dict[str, Definition],
) -> MessageDefinitionField:
    t, td_arrays, td_is_seq, td_seq_bound, td_str_bound = _resolve_typedef(
        field.type, typedefs
    )

    field_has_array = bool(field.array_lengths) or field.is_sequence
    td_has_array = bool(td_arrays) or td_is_seq
    field_fixed = bool(field.array_lengths) and not field.is_sequence
    td_fixed = bool(td_arrays) and not td_is_seq
    if field_has_array and td_has_array and (not field_fixed or not td_fixed):
        raise ValueError(
            "We do not support composing variable length arrays with typedefs"
        )

    array_lengths = list(field.array_lengths)
    if td_arrays:
        array_lengths.extend(td_arrays)
    if len(array_lengths) > 1:
        raise ValueError(
            "Multi-dimensional arrays are not supported in MessageDefinition type"
        )
    is_sequence = field.is_sequence or td_is_seq
    sequence_bound = field.sequence_bound if field.is_sequence else td_seq_bound
    upper_bound = (
        field.string_upper_bound
        if field.string_upper_bound is not None
        else td_str_bound
    )

    enum_type = None
    is_complex = False
    ref = idl_map.get(t)
    if isinstance(ref, Enum):
        enum_type = t
        t = "uint32"
    elif isinstance(ref, (Struct, IDLUnion)):
        is_complex = True

    annotations = field.annotations or None
    default_value = None
    if annotations and "default" in annotations:
        default_value = annotations["default"]

    is_array = bool(array_lengths) or is_sequence

    return MessageDefinitionField(
        type=t,
        name=field.name,
        isComplex=is_complex,
        isArray=is_array,
        arrayLength=array_lengths[0] if array_lengths else None,
        arrayUpperBound=sequence_bound if is_sequence else None,
        enumType=enum_type,
        upperBound=upper_bound,
        defaultValue=default_value,
    )


def _convert_union(
    name: str,
    union: IDLUnion,
    typedefs: Dict[str, Typedef],
    idl_map: Dict[str, Definition],
) -> IDLUnionDefinition:
    switch_type, _arr, _is_seq, _seq_bound, _str_bound = _resolve_typedef(
        union.switch_type, typedefs
    )
    ref = idl_map.get(switch_type)
    if isinstance(ref, Enum):
        switch_type = "uint32"

    cases: List[UnionCase] = []
    for case in union.cases:
        field_def = _convert_field(case.field, typedefs, idl_map)
        # ``case.predicates`` may be typed broadly by the parser, but by this
        # stage they should have been resolved to integers or booleans.
        predicates = cast(List[int | bool], case.predicates)
        cases.append(UnionCase(predicates=predicates, type=field_def))

    default_field = None
    if union.default is not None:
        default_field = _convert_field(union.default, typedefs, idl_map)

    return IDLUnionDefinition(
        name=name,
        switchType=switch_type,
        cases=cases,
        defaultCase=default_field,
        annotations=union.annotations or None,
    )


# ---------------------------------------------------------------------------
# Public API ---------------------------------------------------------------------


def to_idl_message_definitions(
    idl_map: dict[str, Definition],
) -> List[IDLMessageDefinition]:
    """Convert map entries into flattened message definitions."""

    typedefs: Dict[str, Typedef] = {
        name: node for name, node in idl_map.items() if isinstance(node, Typedef)
    }

    message_definitions: List[IDLMessageDefinition] = []
    top_level_consts: List[MessageDefinitionField] = []

    for scoped_name, node in idl_map.items():
        if isinstance(node, Struct):
            fields = [_convert_field(f, typedefs, idl_map) for f in node.fields]
            message_definitions.append(
                IDLStructDefinition(
                    name=scoped_name,
                    definitions=fields,
                    annotations=node.annotations or None,
                )
            )
        elif isinstance(node, Module):
            const_fields = [
                _convert_constant(d, typedefs, idl_map)
                for d in node.definitions
                if isinstance(d, Constant)
            ]
            if const_fields:
                message_definitions.append(
                    IDLModuleDefinition(name=scoped_name, definitions=const_fields)
                )
        elif isinstance(node, Constant):
            if "::" not in scoped_name:
                top_level_consts.append(_convert_constant(node, typedefs, idl_map))
        elif isinstance(node, Enum):
            const_fields = [
                _convert_constant(e, typedefs, idl_map) for e in node.enumerators
            ]
            message_definitions.append(
                IDLModuleDefinition(name=scoped_name, definitions=const_fields)
            )
        elif isinstance(node, IDLUnion):
            message_definitions.append(
                _convert_union(scoped_name, node, typedefs, idl_map)
            )
        # Typedefs are only used for resolution; they do not produce output.

    if top_level_consts:
        message_definitions.append(
            IDLModuleDefinition(name="", definitions=top_level_consts)
        )

    return message_definitions


def parse_idl_message_definitions(source: str) -> List[IDLMessageDefinition]:
    """Parse IDL text and return flattened message definitions."""

    from mcap_ros2idl_support.omgidl_parser.parse import parse_idl

    parsed = parse_idl(source)
    idl_map = build_map(parsed)
    return to_idl_message_definitions(idl_map)


__all__ = [
    "IDLStructDefinition",
    "IDLModuleDefinition",
    "IDLUnionDefinition",
    "IDLMessageDefinition",
    "build_map",
    "to_idl_message_definitions",
    "parse_idl_message_definitions",
]
