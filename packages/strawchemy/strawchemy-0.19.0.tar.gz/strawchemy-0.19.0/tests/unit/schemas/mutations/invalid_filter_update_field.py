from __future__ import annotations

from strawchemy import Strawchemy

import strawberry
from tests.unit.models import Group

strawchemy = Strawchemy("postgresql")


@strawchemy.type(Group, include="all")
class GroupType: ...


@strawchemy.filter_update_input(Group, include="all")
class GroupPartial: ...


@strawchemy.filter(Group, include="all")
class GroupFilter: ...


@strawberry.type
class Mutation:
    update_groups: GroupType = strawchemy.update(GroupPartial, GroupFilter)
