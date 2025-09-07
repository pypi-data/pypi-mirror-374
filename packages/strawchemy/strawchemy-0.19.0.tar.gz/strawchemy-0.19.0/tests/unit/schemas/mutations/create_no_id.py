from __future__ import annotations

from strawchemy import Strawchemy

import strawberry
from tests.unit.models import Group

strawchemy = Strawchemy("postgresql")


@strawchemy.create_input(Group, exclude=["id"])
class GroupInput: ...


@strawchemy.type(Group, include="all")
class GroupType: ...


@strawberry.type
class Mutation:
    create_group: GroupType = strawchemy.create(GroupInput)
