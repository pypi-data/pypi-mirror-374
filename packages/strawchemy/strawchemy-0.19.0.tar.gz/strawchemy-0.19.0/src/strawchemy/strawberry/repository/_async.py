"""Asynchronous repository implementation for Strawchemy.

This module provides an asynchronous implementation of the Strawchemy repository
pattern, built on top of SQLAlchemy's asynchronous API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, TypeVar

from strawchemy.sqlalchemy.repository import SQLAlchemyGraphQLAsyncRepository
from strawchemy.strawberry._utils import default_session_getter, dto_model_from_type, strawberry_contained_user_type

from ._base import GraphQLResult, StrawchemyRepository

if TYPE_CHECKING:
    from sqlalchemy import Select
    from strawberry import Info
    from strawchemy.sqlalchemy.typing import AnyAsyncSession
    from strawchemy.strawberry.dto import BooleanFilterDTO, EnumDTO, OrderByDTO
    from strawchemy.strawberry.mutation.input import Input, InputModel
    from strawchemy.strawberry.typing import AsyncSessionGetter

__all__ = ("StrawchemyAsyncRepository",)

T = TypeVar("T")


@dataclass
class StrawchemyAsyncRepository(StrawchemyRepository[T]):
    """Asynchronous repository implementation for GraphQL data access.

    This class provides asynchronous methods for querying and mutating data
    through GraphQL, using SQLAlchemy's asynchronous API under the hood.

    Args:
        type: The Strawberry GraphQL type this repository works with
        info: The GraphQL resolver info object
        session_getter: Callable to get an async database session
        session: Optional explicit async database session to use
        filter_statement: Optional base SQLAlchemy select statement to apply to all queries
        execution_options: Optional execution options for SQLAlchemy
        deterministic_ordering: Whether to ensure deterministic ordering of results
    """

    type: type[T]
    info: Info[Any, Any]

    # sqlalchemy related settings
    session_getter: AsyncSessionGetter = default_session_getter
    session: Optional[AnyAsyncSession] = None
    filter_statement: Optional[Select[tuple[Any]]] = None
    execution_options: Optional[dict[str, Any]] = None
    deterministic_ordering: bool = False

    def graphql_repository(self) -> SQLAlchemyGraphQLAsyncRepository[Any]:
        """Create and configure the underlying async SQLAlchemy GraphQL repository.

        Returns:
            A configured SQLAlchemyGraphQLAsyncRepository instance
        """
        return SQLAlchemyGraphQLAsyncRepository(
            model=dto_model_from_type(strawberry_contained_user_type(self.type)),
            session=self.session or self.session_getter(self.info),
            statement=self.filter_statement,
            execution_options=self.execution_options,
            deterministic_ordering=self.deterministic_ordering,
        )

    async def get_one_or_none(
        self,
        filter_input: Optional[BooleanFilterDTO] = None,
        order_by: Optional[list[OrderByDTO]] = None,
        distinct_on: Optional[list[EnumDTO]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> GraphQLResult[Any, T]:
        """Asynchronously get at most one result matching the criteria or None.

        Args:
            filter_input: Optional filter conditions
            order_by: Optional ordering criteria
            distinct_on: Optional fields to apply DISTINCT on
            limit: Optional maximum number of results to return
            offset: Optional number of results to skip

        Returns:
            A GraphQLResult containing the result or None
        """
        query_results = await self.graphql_repository().get_one(
            selection=self._tree,
            dto_filter=filter_input or None,
            order_by=list(order_by or []),
            distinct_on=distinct_on,
            limit=limit,
            offset=offset,
            query_hooks=self._query_hooks,
        )
        return GraphQLResult(query_results, self._tree)

    async def get_one(
        self,
        filter_input: Optional[BooleanFilterDTO] = None,
        order_by: Optional[list[OrderByDTO]] = None,
        distinct_on: Optional[list[EnumDTO]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> GraphQLResult[Any, T]:
        """Asynchronously get exactly one result matching the criteria.

        Args:
            filter_input: Optional filter conditions
            order_by: Optional ordering criteria
            distinct_on: Optional fields to apply DISTINCT on
            limit: Optional maximum number of results to return
            offset: Optional number of results to skip

        Returns:
            A GraphQLResult containing the single result

        Raises:
            NoResultFound: If no results are found
            MultipleResultsFound: If multiple results are found
        """
        query_results = await self.graphql_repository().get_one(
            selection=self._tree,
            dto_filter=filter_input or None,
            order_by=list(order_by or []),
            distinct_on=distinct_on,
            limit=limit,
            offset=offset,
            query_hooks=self._query_hooks,
        )
        return GraphQLResult(query_results, self._tree)

    async def get_by_id(self, **kwargs: Any) -> GraphQLResult[Any, T]:
        """Asynchronously get an entity by its primary key.

        Args:
            **kwargs: Primary key field names and values

        Returns:
            A GraphQLResult containing the found entity

        Raises:
            NoResultFound: If no entity with the given ID exists
        """
        query_results = await self.graphql_repository().get_by_id(
            selection=self._tree, query_hooks=self._query_hooks, **kwargs
        )
        return GraphQLResult(query_results, self._tree)

    async def list(
        self,
        filter_input: Optional[BooleanFilterDTO] = None,
        order_by: Optional[list[OrderByDTO]] = None,
        distinct_on: Optional[list[EnumDTO]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> GraphQLResult[Any, T]:
        """Asynchronously get a list of entities matching the criteria.

        Args:
            filter_input: Optional filter conditions
            order_by: Optional ordering criteria
            distinct_on: Optional fields to apply DISTINCT on
            limit: Optional maximum number of results to return
            offset: Optional number of results to skip

        Returns:
            A GraphQLResult containing the list of matching entities
        """
        query_results = await self.graphql_repository().list(
            selection=self._tree,
            dto_filter=filter_input or None,
            order_by=list(order_by or []),
            distinct_on=distinct_on,
            limit=limit,
            offset=offset,
            query_hooks=self._query_hooks,
        )
        return GraphQLResult(query_results, self._tree)

    async def create(self, data: Input[InputModel]) -> GraphQLResult[InputModel, T]:
        """Asynchronously create a new entity.

        Args:
            data: The input data for the new entity

        Returns:
            A GraphQLResult containing the created entity
        """
        query_results = await self.graphql_repository().create(data, self._tree)
        return GraphQLResult(query_results, self._tree)

    async def upsert(
        self,
        data: Input[InputModel],
        filter_input: Optional[BooleanFilterDTO] = None,
        update_fields: Optional[list[EnumDTO]] = None,
        conflict_fields: Optional[EnumDTO] = None,
    ) -> GraphQLResult[InputModel, T]:
        """Asynchronously insert or update an entity.

        Args:
            data: The input data for the entity
            filter_input: Optional filter to find existing entity
            update_fields: Optional fields to update if entity exists
            conflict_fields: Optional fields to detect conflicts on

        Returns:
            A GraphQLResult containing the upserted entity
        """
        query_results = await self.graphql_repository().upsert(
            data, self._tree, update_fields, conflict_fields, filter_input
        )
        return GraphQLResult(query_results, self._tree)

    async def update_by_id(self, data: Input[InputModel]) -> GraphQLResult[InputModel, T]:
        """Asynchronously update an entity by its ID.

        Args:
            data: The input data containing the ID and fields to update

        Returns:
            A GraphQLResult containing the updated entity

        Raises:
            NoResultFound: If no entity with the given ID exists
        """
        query_results = await self.graphql_repository().update_by_ids(data, self._tree)
        return GraphQLResult(query_results, self._tree)

    async def update_by_filter(
        self, data: Input[InputModel], filter_input: BooleanFilterDTO
    ) -> GraphQLResult[InputModel, T]:
        """Asynchronously update entities matching the given filter.

        Args:
            data: The input data containing fields to update
            filter_input: The filter criteria to select entities to update

        Returns:
            A GraphQLResult containing the updated entities
        """
        query_results = await self.graphql_repository().update_by_filter(data, filter_input, self._tree)
        return GraphQLResult(query_results, self._tree)

    async def delete(self, filter_input: Optional[BooleanFilterDTO]) -> GraphQLResult[Any, T]:
        """Asynchronously delete entities matching the given filter.

        Args:
            filter_input: The filter criteria to select entities to delete

        Returns:
            A GraphQLResult containing the deleted entities
        """
        query_results = await self.graphql_repository().delete(self._tree, filter_input or None)
        return GraphQLResult(query_results, self._tree)
