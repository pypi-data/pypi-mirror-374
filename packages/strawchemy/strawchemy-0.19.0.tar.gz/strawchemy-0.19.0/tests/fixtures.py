from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING

import pytest
from strawchemy import Strawchemy, StrawchemyConfig

import strawberry
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.amber import AmberSnapshotExtension
from tests.utils import sqlalchemy_pydantic_factory

from .syrupy import GraphQLFileExtension

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion
    from tests.typing import MappedPydanticFactory

__all__ = ("fx_sqlalchemy_pydantic_factory", "strawchemy")


@pytest.fixture
def graphql_snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.use_extension(GraphQLFileExtension)


@pytest.fixture
def sql_snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.use_extension(AmberSnapshotExtension)


@pytest.fixture
def strawchemy() -> Strawchemy:
    return Strawchemy(StrawchemyConfig("postgresql"))


@pytest.fixture(name="sqlalchemy_pydantic_factory")
def fx_sqlalchemy_pydantic_factory() -> MappedPydanticFactory:
    if not find_spec("pydantic"):
        pytest.skip("pydantic is not installed")
    return sqlalchemy_pydantic_factory()


@pytest.fixture
def sync_query() -> type[DefaultQuery]:
    return DefaultQuery


@strawberry.type
class DefaultQuery:
    @strawberry.field
    def hello(self) -> str:
        return "World"
