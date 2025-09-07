from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from inspect import getmodule
from types import new_class
from typing import TYPE_CHECKING, Any, Optional, TypeVar, cast

from typing_extensions import override

from sqlalchemy.orm import DeclarativeBase, QueryableAttribute
from strawchemy.dto.base import DTOBackend, DTOBase, DTOFactory, DTOFieldDefinition, Relation
from strawchemy.dto.types import DTOConfig, ExcludeFields, IncludeFields, Purpose
from strawchemy.strawberry.dto import EnumDTO, GraphQLFieldDefinition
from strawchemy.utils import snake_to_lower_camel_case

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterable, Mapping

    from strawchemy.graph import Node
    from strawchemy.sqlalchemy.inspector import SQLAlchemyGraphQLInspector

T = TypeVar("T")


class EnumDTOBackend(DTOBackend[EnumDTO]):
    def __init__(self, to_camel: bool = True) -> None:
        self.dto_base = EnumDTO
        self.to_camel = to_camel

    @override
    def build(
        self,
        name: str,
        model: type[DeclarativeBase],
        field_definitions: Iterable[DTOFieldDefinition[DeclarativeBase, QueryableAttribute[Any]]],
        base: Optional[type[Any]] = None,
        values: Optional[Iterable[Any]] = None,
        **kwargs: Any,
    ) -> type[EnumDTO]:
        field_map = {
            snake_to_lower_camel_case(field.name) if self.to_camel else field.name: field for field in field_definitions
        }
        values = list(values or []) or field_map.keys()

        def exec_body(namespace: dict[str, Any]) -> Any:
            def to_field_definition(self: EnumDTO) -> DTOFieldDefinition[DeclarativeBase, QueryableAttribute[Any]]:
                return self.__field_definitions__[self.value]

            namespace["field_definition"] = property(to_field_definition)
            namespace["__field_definitions__"] = field_map

        base = new_class(name=f"{name}Base", bases=(DTOBase,), exec_body=exec_body)
        module = __name__
        if model_module := getmodule(model):
            module = model_module.__name__
        return cast(
            "type[EnumDTO]",
            EnumDTO(value=name, names=list(zip(list(field_map), values)), type=base, module=module),
        )

    @override
    @classmethod
    def copy(cls, dto: type[EnumDTO], name: str) -> EnumDTO:  # pyright: ignore[reportIncompatibleMethodOverride]
        enum = EnumDTO(value=name, names=[(value.name, value.value) for value in dto])
        enum.__field_definitions__ = dto.__field_definitions__
        return enum


class UpsertConflictFieldsEnumDTOBackend(EnumDTOBackend):
    def __init__(self, inspector: SQLAlchemyGraphQLInspector, to_camel: bool = True) -> None:
        self.dto_base = EnumDTO
        self.to_camel = to_camel
        self._inspector = inspector

    @override
    def build(
        self,
        name: str,
        model: type[DeclarativeBase],
        field_definitions: Iterable[DTOFieldDefinition[DeclarativeBase, QueryableAttribute[Any]]],
        base: Optional[type[Any]] = None,
        values: Optional[Iterable[Any]] = None,
        **kwargs: Any,
    ) -> type[EnumDTO]:
        constraint_columns = self._inspector.unique_constraints(model)
        constraint_map = {column.key: constraint for constraint in constraint_columns for column in constraint.columns}
        field_definitions = list(field_definitions)
        return super().build(
            name,
            model,
            field_definitions,
            base,
            [constraint_map[field.model_field_name] for field in field_definitions],
            **kwargs,
        )


class EnumDTOFactory(DTOFactory[DeclarativeBase, QueryableAttribute[Any], EnumDTO]):
    inspector: SQLAlchemyGraphQLInspector

    def __init__(
        self,
        inspector: SQLAlchemyGraphQLInspector,
        backend: Optional[DTOBackend[EnumDTO]] = None,
        handle_cycles: bool = True,
        type_map: Optional[dict[Any, Any]] = None,
    ) -> None:
        super().__init__(inspector, backend or EnumDTOBackend(), handle_cycles, type_map)

    @override
    def dto_name(
        self, base_name: str, dto_config: DTOConfig, node: Optional[Node[Relation[Any, EnumDTO], None]] = None
    ) -> str:
        return f"{base_name}Fields"

    @override
    def should_exclude_field(
        self,
        field: DTOFieldDefinition[Any, QueryableAttribute[Any]],
        dto_config: DTOConfig,
        node: Node[Relation[Any, EnumDTO], None],
        has_override: bool,
    ) -> bool:
        return super().should_exclude_field(field, dto_config, node, has_override) or field.is_relation

    @override
    def iter_field_definitions(
        self,
        name: str,
        model: type[DeclarativeBase],
        dto_config: DTOConfig,
        base: Optional[type[DTOBase[DeclarativeBase]]],
        node: Node[Relation[DeclarativeBase, EnumDTO], None],
        raise_if_no_fields: bool = False,
        **kwargs: Any,
    ) -> Generator[DTOFieldDefinition[DeclarativeBase, QueryableAttribute[Any]], None, None]:
        for field in super().iter_field_definitions(name, model, dto_config, base, node, raise_if_no_fields, **kwargs):
            yield GraphQLFieldDefinition.from_field(field)

    @override
    def decorator(
        self,
        model: type[DeclarativeBase],
        purpose: Purpose = Purpose.READ,
        include: Optional[IncludeFields] = None,
        exclude: Optional[ExcludeFields] = None,
        partial: Optional[bool] = None,
        type_map: Optional[Mapping[Any, Any]] = None,
        aliases: Optional[Mapping[str, str]] = None,
        alias_generator: Optional[Callable[[str], str]] = None,
        **kwargs: Any,
    ) -> Callable[[type[Any]], type[EnumDTO]]:
        return super().decorator(
            model,
            purpose,
            include=include,
            exclude=exclude,
            partial=partial,
            aliases=aliases,
            alias_generator=alias_generator,
            type_map=type_map,
            **kwargs,
        )

    def input(
        self,
        model: type[DeclarativeBase],
        include: Optional[IncludeFields] = None,
        exclude: Optional[ExcludeFields] = None,
        partial: Optional[bool] = None,
        type_map: Optional[Mapping[Any, Any]] = None,
        aliases: Optional[Mapping[str, str]] = None,
        alias_generator: Optional[Callable[[str], str]] = None,
        **kwargs: Any,
    ) -> Callable[[type[Any]], type[EnumDTO]]:
        return super().decorator(
            model,
            Purpose.WRITE,
            include=include,
            exclude=exclude,
            partial=partial,
            aliases=aliases,
            alias_generator=alias_generator,
            type_map=type_map,
            **kwargs,
        )

    def upsert_conflict_fields(
        self,
        model: type[DeclarativeBase],
        name: Optional[str] = None,
    ) -> type[Enum]:
        name = name or f"{model.__name__}ConflictFields"
        return cast(
            "type[Enum]",
            Enum(
                name,
                [
                    (f"{'_'.join(col.key for col in constraint.columns)}", constraint)
                    for constraint in self.inspector.unique_constraints(model)
                ],
            ),
        )
