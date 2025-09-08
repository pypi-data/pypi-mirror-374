from __future__ import annotations

from datetime import date, datetime, time, timedelta
from enum import Enum, IntEnum, StrEnum
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Type,
    TypeGuard,
    TypeVar,
)
from uuid import UUID

if TYPE_CHECKING:
    from iceaxe.alias_values import Alias
    from iceaxe.base import (
        DBFieldClassDefinition,
        TableBase,
    )
    from iceaxe.comparison import FieldComparison, FieldComparisonGroup
    from iceaxe.functions import FunctionMetadata


ALL_ENUM_TYPES = Type[Enum | StrEnum | IntEnum]
PRIMITIVE_TYPES = int | float | str | bool | bytes | UUID
PRIMITIVE_WRAPPER_TYPES = list[PRIMITIVE_TYPES] | PRIMITIVE_TYPES
DATE_TYPES = datetime | date | time | timedelta
JSON_WRAPPER_FALLBACK = list[Any] | dict[Any, Any]

T = TypeVar("T")


def is_base_table(obj: Any) -> TypeGuard[type[TableBase]]:
    from iceaxe.base import TableBase

    return isclass(obj) and issubclass(obj, TableBase)


def is_column(obj: T) -> TypeGuard[DBFieldClassDefinition[T]]:
    from iceaxe.base import DBFieldClassDefinition

    return isinstance(obj, DBFieldClassDefinition)


def is_comparison(obj: Any) -> TypeGuard[FieldComparison]:
    from iceaxe.comparison import FieldComparison

    return isinstance(obj, FieldComparison)


def is_comparison_group(obj: Any) -> TypeGuard[FieldComparisonGroup]:
    from iceaxe.comparison import FieldComparisonGroup

    return isinstance(obj, FieldComparisonGroup)


def is_function_metadata(obj: Any) -> TypeGuard[FunctionMetadata]:
    from iceaxe.functions import FunctionMetadata

    return isinstance(obj, FunctionMetadata)


def is_alias(obj: Any) -> TypeGuard[Alias]:
    from iceaxe.alias_values import Alias

    return isinstance(obj, Alias)


def column(obj: T) -> DBFieldClassDefinition[T]:
    if not is_column(obj):
        raise ValueError(f"Invalid column: {obj}")
    return obj
