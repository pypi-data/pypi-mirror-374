from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Protocol

from typing_extensions import TypeAlias

if TYPE_CHECKING:
    from strawchemy.dto.backend.pydantic import MappedPydanticDTO
    from strawchemy.dto.base import DTOFactory

    from sqlalchemy.orm import DeclarativeBase, QueryableAttribute
    from strawberry.types.execution import ExecutionResult


MappedPydanticFactory: TypeAlias = "DTOFactory[DeclarativeBase, QueryableAttribute[Any], MappedPydanticDTO[Any]]"
AnyFactory: TypeAlias = "MappedPydanticFactory"
AnyQueryExecutor: TypeAlias = "SyncQueryExecutor | AsyncQueryExecutor"


class SyncQueryExecutor(Protocol):
    def __call__(self, query: str, variable_values: Optional[dict[str, Any]] = None) -> ExecutionResult: ...


class AsyncQueryExecutor(Protocol):
    async def __call__(self, query: str, variable_values: Optional[dict[str, Any]] = None) -> ExecutionResult: ...
