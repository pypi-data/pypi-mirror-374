from __future__ import annotations

from strawchemy import Strawchemy

import strawberry
from tests.unit.models import Group, Tag, User

strawchemy = Strawchemy("postgresql")


@strawchemy.type(User, include="all")
class GraphQLUser:
    pass


@strawchemy.type(Group, include="all", scope="schema")
class GraphQLGroup:
    pass


@strawchemy.type(Tag, include="all")
class GraphQLTag:
    pass


@strawberry.type
class Query:
    user: GraphQLUser = strawchemy.field()
    tag: GraphQLTag = strawchemy.field()
