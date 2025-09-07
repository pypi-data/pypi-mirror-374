from __future__ import annotations

from strawchemy import Strawchemy

import strawberry
from tests.unit.models import Fruit

strawchemy = Strawchemy("postgresql")


@strawchemy.type(Fruit, include="all")
class FruitType:
    pass


@strawchemy.order(Fruit, include="all")
class FruitOrderBy:
    pass


@strawberry.type
class Query:
    fruit: list[FruitType] = strawchemy.field(order_by=FruitOrderBy)
