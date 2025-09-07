from __future__ import annotations

from strawchemy import Strawchemy

import strawberry
from tests.unit.models import SQLDataTypes

strawchemy = Strawchemy("postgresql")


@strawchemy.order(SQLDataTypes, include="all")
class SQLDataTypesOrderBy: ...


@strawchemy.type(SQLDataTypes, include="all")
class SQLDataTypesType: ...


@strawberry.type
class Query:
    sql_data_types: list[SQLDataTypesType] = strawchemy.field(order_by=SQLDataTypesOrderBy)
