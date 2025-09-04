from __future__ import annotations

import codecs
import threading
from dataclasses import dataclass, field
from typing import Any, List, Optional
from typing import Union as TypingUnion

from lark import Lark, Transformer

# A slightly larger subset grammar supporting modules, structs, constants, enums,
# typedefs and unions
IDL_GRAMMAR = r"""
start: definition+

definition: annotations? (module
          | struct
          | constant
          | enum
          | typedef
          | union)
          | import_stmt
          | include_stmt

module: "module" NAME "{" definition* "}" semicolon?

struct: "struct" NAME "{" field* "}" semicolon?

enum: "enum" NAME "{" enumerator ("," enumerator)* "}" semicolon?

enumerator: annotations? NAME enum_value?
enum_value: "@value" "(" INT ")"

constant: "const" type NAME "=" const_value semicolon
# Allow multiple adjacent string literals, which are concatenated (e.g., "part1" "part2")
const_value: STRING+ -> const_string
           | BOOL -> const_bool
           | const_sum

const_sum: const_atom ("+" const_atom)*

?const_atom: SIGNED_INT -> const_int
          | SIGNED_FLOAT -> const_float
          | scoped_name

typedef: "typedef" type NAME array? semicolon

union: "union" NAME "switch" "(" type ")" "{" union_case+ "}" semicolon?
union_case: "case" case_predicates ":" field
          | "default" ":" field
case_predicates: const_value ("," const_value)*

field: annotations? type NAME array? semicolon

import_stmt: "import" STRING semicolon

include_stmt: "#include" (STRING | "<" /[^>]+/ ">")

type: sequence_type
    | string_type
    | BUILTIN_TYPE
    | scoped_name

sequence_type: "sequence" "<" type ("," const_sum)? ">"

string_type: STRING_KW string_bound?
           | WSTRING_KW string_bound?

string_bound: "<" const_sum ">"

scoped_name: NAME ("::" NAME)*

BUILTIN_TYPE: /(unsigned\s+(short|long(\s+long)?)|long\s+double|double|float|short|long\s+long|long|int8|uint8|int16|uint16|int32|uint32|int64|uint64|byte|octet|wchar|char|boolean)\b/  # noqa: E501
STRING_KW: "string"
WSTRING_KW: "wstring"
NAME: /[A-Za-z_][A-Za-z0-9_]*/

array: ("[" const_sum "]")+

semicolon: ";"

%import common.INT
BOOL.2: /(?i:\btrue\b|\bfalse\b)/
%import common.SIGNED_INT
%import common.SIGNED_FLOAT
# STRING matches both double-quoted and single-quoted string literals, including
# escaped characters. We avoid inline regex flags (e.g., ``(?s)``) so the grammar
# works with Python's built-in ``re`` module without requiring the third-party
# ``regex`` package. Instead, ``[\s\S]`` is used to match any character,
# including newlines, within escape sequences.
STRING: /"(?:\\[\s\S]|[^"\\])*"|'(?:\\[\s\S]|[^'\\])*'/
%import common.WS

COMMENT: /\/\/[^\n]*|\/\*[\s\S]*?\*\//
%ignore WS
%ignore COMMENT

# Annotations support two parameter formats:
#   - Named parameters: @foo(bar=1, baz=2)
#   - Single value:     @foo(42)
# Both forms are supported via the annotation_params rule below.
annotation: "@" NAME ("(" annotation_params ")")?
annotation_params: named_annotation_params
                   | const_value
named_annotation_params: named_annotation_param ("," named_annotation_param)*
named_annotation_param: NAME "=" const_value
annotations: annotation+
"""


# Build a Lark parser per thread. Constructing the parser is relatively
# expensive, and doing it on every call to ``parse_idl`` results in significant
# overhead. Reusing a parser instance per thread drastically reduces the
# per-call parsing cost while remaining thread-safe.
_THREAD_LOCAL = threading.local()


def _get_parser() -> Lark:
    parser = getattr(_THREAD_LOCAL, "parser", None)
    if parser is None:
        parser = Lark(
            IDL_GRAMMAR, start="start", parser="lalr", maybe_placeholders=False
        )
        _THREAD_LOCAL.parser = parser
    return parser


@dataclass
class Field:
    name: str
    type: str
    array_lengths: List[int] = field(default_factory=list)
    is_sequence: bool = False
    sequence_bound: Optional[int] = None
    string_upper_bound: Optional[int] = None
    annotations: dict[str, Any] = field(default_factory=dict)


@dataclass
class Constant:
    name: str
    type: str
    value: TypingUnion[int, float, bool, str]
    annotations: dict[str, Any] = field(default_factory=dict)


@dataclass
class Enum:
    name: str
    enumerators: List[Constant] = field(default_factory=list)
    annotations: dict[str, Any] = field(default_factory=dict)


@dataclass
class Struct:
    name: str
    fields: List[Field] = field(default_factory=list)
    annotations: dict[str, Any] = field(default_factory=dict)


@dataclass
class Typedef:
    name: str
    type: str
    array_lengths: List[int] = field(default_factory=list)
    is_sequence: bool = False
    sequence_bound: Optional[int] = None
    annotations: dict[str, Any] = field(default_factory=dict)


@dataclass
class UnionCase:
    predicates: List[int | bool | str]
    field: Field


@dataclass
class Union:
    name: str
    switch_type: str
    cases: List[UnionCase] = field(default_factory=list)
    default: Optional[Field] = None
    annotations: dict[str, Any] = field(default_factory=dict)


@dataclass
class Module:
    name: str
    definitions: List[Struct | Module | Constant | Enum | Typedef | Union] = field(
        default_factory=list
    )
    annotations: dict[str, Any] = field(default_factory=dict)


class _Transformer(Transformer):
    _NORMALIZATION = {
        "long double": "float64",
        "double": "float64",
        "float": "float32",
        "short": "int16",
        "unsigned short": "uint16",
        "unsigned long long": "uint64",
        "unsigned long": "uint32",
        "long long": "int64",
        "long": "int32",
        "boolean": "bool",
        "octet": "uint8",
    }

    _BUILTIN_TYPES = {
        "float64",
        "float32",
        "int16",
        "uint16",
        "uint64",
        "uint32",
        "int64",
        "int32",
        "int8",
        "uint8",
        "byte",
        "octet",
        "wchar",
        "char",
        "string",
        "wstring",
        "bool",
    }

    def __init__(self):
        super().__init__()
        # Map identifiers (constants and enum values) to their evaluated numeric values
        self._constants: dict[str, int | float | bool | str] = {}

    def start(self, items):
        return [item for item in items if item is not None]

    def definition(self, items):
        if len(items) == 1:
            return items[0]
        annotations, decl = items
        if decl is None:
            return None
        if isinstance(annotations, dict) and hasattr(decl, "annotations"):
            decl.annotations = annotations
        return decl

    def NAME(self, token):
        return str(token)

    def scoped_name(self, items):
        return "::".join(items)

    def type(self, items):
        (t,) = items
        if isinstance(t, tuple):
            if t[0] == "sequence":
                inner, bound = t[1], t[2]
                return ("sequence", self._NORMALIZATION.get(inner, inner), bound)
            base, bound = t
            return (self._NORMALIZATION.get(base, base), bound)
        if isinstance(t, str):
            return self._NORMALIZATION.get(t, t)
        token = str(t)
        return self._NORMALIZATION.get(token, token)

    def sequence_type(self, items):
        inner = items[0]
        bound = items[1] if len(items) > 1 else None
        return ("sequence", inner, bound)

    def string_type(self, items):
        base = str(items[0])
        bound = items[1] if len(items) > 1 else None
        if bound is not None:
            return (base, bound)
        return base

    def string_bound(self, items):
        (value,) = items
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid string bound value: {value!r}")

    def INT(self, token):
        return int(token)

    def const_int(self, items):
        (token,) = items
        return int(token)

    def STRING(self, token):
        value = str(token)[1:-1]
        return codecs.decode(value, "unicode_escape")

    def array(self, items):
        return [int(itm) for itm in items]

    def semicolon(self, _):
        return None

    def import_stmt(self, _items):
        return None

    def include_stmt(self, _items):
        return None

    def annotation(self, items):
        name = items[0]
        value = items[1] if len(items) > 1 else True
        return (name, value)

    def annotation_params(self, items):
        (value,) = items
        return value

    def named_annotation_params(self, items):
        return dict(items)

    def named_annotation_param(self, items):
        name, value = items
        return (name, value)

    def annotations(self, items):
        return dict(items)

    def field(self, items):
        idx = 0
        annotations = {}
        if items and isinstance(items[0], dict):
            annotations = items[0]
            idx = 1
        type_, name, *rest = items[idx:]
        array_lengths: List[int] = []
        for itm in rest:
            if isinstance(itm, list):
                array_lengths = itm
        is_sequence = False
        sequence_bound = None
        string_upper_bound = None
        if isinstance(type_, tuple):
            if type_[0] == "sequence":
                is_sequence = True
                sequence_bound = type_[2]
                type_ = type_[1]
                if isinstance(type_, tuple):
                    string_upper_bound = type_[1]
                    type_ = type_[0]
            else:
                string_upper_bound = type_[1]
                type_ = type_[0]
        return Field(
            name=name,
            type=type_,
            array_lengths=array_lengths,
            is_sequence=is_sequence,
            sequence_bound=sequence_bound,
            string_upper_bound=string_upper_bound,
            annotations=annotations,
        )

    def const_string(self, items):
        return "".join(items)

    def const_bool(self, items):
        (token,) = items
        return str(token).lower() == "true"

    def const_float(self, items):
        (token,) = items
        return float(token)

    def const_sum(self, items):
        expr_items: list[Any] = []
        unresolved = False
        for item in items:
            if isinstance(item, str):
                val = self._constants.get(item, item)
                if val is item:
                    unresolved = True
                elif not isinstance(val, (int, float, bool, str)):
                    unresolved = True
                expr_items.append(val)
            else:
                expr_items.append(item)

        if not unresolved:
            total = expr_items[0]
            for val in expr_items[1:]:
                if not isinstance(total, (int, float)) or not isinstance(
                    val, (int, float)
                ):
                    raise ValueError("Addition only allowed on numeric constants")
                total += val
            return total
        return expr_items

    def const_value(self, items):
        (value,) = items
        return value

    def constant(self, items):
        # items: TYPE, NAME, value, None
        type_, name, value, _ = items
        const = Constant(name=name, type=type_, value=value)
        self._constants[name] = value
        return const

    def typedef(self, items):
        type_, name, *rest = items
        array_lengths: List[int] = []
        for itm in rest:
            if isinstance(itm, list):
                array_lengths = itm
        is_sequence = False
        sequence_bound = None
        if isinstance(type_, tuple) and type_[0] == "sequence":
            is_sequence = True
            sequence_bound = type_[2]
            type_ = type_[1]
        return Typedef(
            name=name,
            type=type_,
            array_lengths=array_lengths,
            is_sequence=is_sequence,
            sequence_bound=sequence_bound,
        )

    def case_predicates(self, items):
        return items

    def union_case(self, items):
        if len(items) == 1:
            (field,) = items
            predicates: List[int | str] = []
        else:
            predicates, field = items
        return UnionCase(predicates=predicates, field=field)

    def union(self, items):
        name = items[0]
        switch_type = items[1]
        cases: List[UnionCase] = []
        default: Optional[Field] = None
        for itm in items[2:]:
            if isinstance(itm, UnionCase):
                if itm.predicates:
                    cases.append(itm)
                else:
                    default = itm.field
        return Union(name=name, switch_type=switch_type, cases=cases, default=default)

    def enum_value(self, items):
        (_, _, val, _) = items
        return val

    def enumerator(self, items):
        idx = 0
        if items and isinstance(items[0], dict):
            idx = 1
        name = items[idx]
        value = items[idx + 1] if len(items) > idx + 1 else None
        return (name, value)

    def enum(self, items):
        name = items[0]
        enumerators_raw = [it for it in items[1:] if isinstance(it, tuple)]
        constants: List[Constant] = []
        current = -1
        for enum_name, enum_val in enumerators_raw:
            if enum_val is not None:
                current = enum_val
            else:
                current += 1
            constants.append(Constant(name=enum_name, type="uint32", value=current))
            # Register enumerator both as unscoped and scoped (EnumName::Enumerator)
            self._constants[enum_name] = current
            self._constants[f"{name}::{enum_name}"] = current
        return Enum(name=name, enumerators=constants)

    def struct(self, items):
        name = items[0]
        fields = [i for i in items[1:] if isinstance(i, Field)]
        return Struct(name=name, fields=fields)

    def module(self, items):
        name = items[0]
        definitions = [item for item in items[1:] if item is not None]
        return Module(name=name, definitions=definitions)

    def _eval_expr(self, expr: Any, seen: Optional[set[str]] = None) -> Any:
        if seen is None:
            seen = set()
        if isinstance(expr, list):
            total = None
            for item in expr:
                val = self._eval_expr(item, seen)
                if total is None:
                    total = val
                else:
                    if not isinstance(total, (int, float)) or not isinstance(
                        val, (int, float)
                    ):
                        raise ValueError("Addition only allowed on numeric constants")
                    total += val
            return total
        if isinstance(expr, str):
            if expr not in self._constants:
                raise ValueError(f"Unknown identifier '{expr}'")
            if expr in seen:
                raise ValueError(f"Circular constant reference '{expr}'")
            seen.add(expr)
            val = self._eval_expr(self._constants[expr], seen)
            seen.remove(expr)
            return val
        return expr

    def _resolve_sequence_bound(self, bound: Any) -> Any:
        if bound is not None and not isinstance(bound, int):
            return int(self._eval_expr(bound))
        return bound

    def resolve_constants(
        self, definitions: List[Struct | Module | Constant | Enum | Typedef | Union]
    ) -> None:
        def resolve_defs(
            defs: List[Struct | Module | Constant | Enum | Typedef | Union],
        ):
            for d in defs:
                if isinstance(d, Constant):
                    d.value = self._eval_expr(d.value)
                    self._constants[d.name] = d.value
                elif isinstance(d, Struct):
                    for f in d.fields:
                        f.sequence_bound = self._resolve_sequence_bound(
                            f.sequence_bound
                        )
                elif isinstance(d, Typedef):
                    d.sequence_bound = self._resolve_sequence_bound(d.sequence_bound)
                elif isinstance(d, Union):
                    for case in d.cases:
                        case.field.sequence_bound = self._resolve_sequence_bound(
                            case.field.sequence_bound
                        )
                        case.predicates = [self._eval_expr(p) for p in case.predicates]
                    if d.default:
                        d.default.sequence_bound = self._resolve_sequence_bound(
                            d.default.sequence_bound
                        )
                elif isinstance(d, Module):
                    resolve_defs(d.definitions)

        resolve_defs(definitions)

    def resolve_types(
        self, definitions: List[Struct | Module | Constant | Enum | Typedef | Union]
    ):
        named_types: set[str] = set()

        def collect(
            defs: List[Struct | Module | Constant | Enum | Typedef | Union],
            scope: List[str],
        ):
            for d in defs:
                if isinstance(d, (Struct, Union, Typedef, Enum)):
                    full = "::".join([*scope, d.name])
                    named_types.add(full)
                if isinstance(d, Module):
                    collect(d.definitions, [*scope, d.name])

        collect(definitions, [])

        def resolve_field(f: Field, scope: List[str]):
            if f.type in self._BUILTIN_TYPES:
                return
            if f.type.startswith("::"):
                f.type = f.type[2:]
                return
            if f.type in named_types:
                return
            resolved = None
            for i in range(len(scope), -1, -1):
                candidate = "::".join([*scope[:i], f.type])
                if candidate in named_types:
                    resolved = candidate
                    break
            if resolved:
                f.type = resolved

        def resolve(
            defs: List[Struct | Module | Constant | Enum | Typedef | Union],
            scope: List[str],
        ):
            for d in defs:
                if isinstance(d, Struct):
                    for f in d.fields:
                        resolve_field(f, scope)
                elif isinstance(d, Union):
                    d.switch_type = self._NORMALIZATION.get(
                        d.switch_type, d.switch_type
                    )
                    if (
                        d.switch_type not in self._BUILTIN_TYPES
                        and not d.switch_type.startswith("::")
                        and "::" not in d.switch_type
                    ):
                        for i in range(len(scope), -1, -1):
                            candidate = "::".join([*scope[:i], d.switch_type])
                            if candidate in named_types:
                                d.switch_type = candidate
                                break
                    for case in d.cases:
                        resolve_field(case.field, scope)
                    if d.default:
                        resolve_field(d.default, scope)
                elif isinstance(d, Typedef):
                    if (
                        d.type not in self._BUILTIN_TYPES
                        and not d.type.startswith("::")
                        and "::" not in d.type
                    ):
                        for i in range(len(scope), -1, -1):
                            candidate = "::".join([*scope[:i], d.type])
                            if candidate in named_types:
                                d.type = candidate
                                break
                elif isinstance(d, Module):
                    resolve(d.definitions, [*scope, d.name])

        resolve(definitions, [])


def parse_idl(source: str) -> List[Struct | Module | Constant | Enum | Typedef | Union]:
    """Parse an IDL definition string into structured objects."""
    parser = _get_parser()
    tree = parser.parse(source)
    transformer = _Transformer()
    result = transformer.transform(tree)
    transformer.resolve_constants(result)
    transformer.resolve_types(result)
    return result
