from __future__ import annotations

from strawchemy import Strawchemy

import strawberry
from tests.unit.models import GeoModel

strawchemy = Strawchemy("postgresql")


@strawchemy.type(GeoModel, include="all")
class GeosFieldsType: ...


@strawchemy.filter(GeoModel, include="all")
class GeosFieldsFilter: ...


@strawberry.type
class Query:
    geo: list[GeosFieldsType] = strawchemy.field(filter_input=GeosFieldsFilter)
