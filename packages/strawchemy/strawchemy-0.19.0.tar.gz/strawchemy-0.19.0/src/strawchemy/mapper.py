from __future__ import annotations

import dataclasses
from functools import cached_property, partial
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union, overload

from strawberry.annotation import StrawberryAnnotation
from strawberry.schema.config import StrawberryConfig
from strawchemy.strawberry.factories.aggregations import EnumDTOFactory
from strawchemy.strawberry.factories.enum import EnumDTOBackend, UpsertConflictFieldsEnumDTOBackend

from .config.base import StrawchemyConfig
from .dto.backend.strawberry import StrawberrryDTOBackend
from .dto.base import TYPING_NS
from .strawberry._field import (
    StrawchemyCreateMutationField,
    StrawchemyDeleteMutationField,
    StrawchemyField,
    StrawchemyUpdateMutationField,
    StrawchemyUpsertMutationField,
)
from .strawberry._registry import StrawberryRegistry
from .strawberry.dto import BooleanFilterDTO, EnumDTO, MappedStrawberryGraphQLDTO, OrderByDTO, OrderByEnum
from .strawberry.factories.inputs import AggregateFilterDTOFactory, BooleanFilterDTOFactory
from .strawberry.factories.types import (
    DistinctOnFieldsDTOFactory,
    InputFactory,
    OrderByDTOFactory,
    RootAggregateTypeDTOFactory,
    TypeDTOFactory,
    UpsertConflictFieldsDTOFactory,
)
from .strawberry.mutation import types
from .types import DefaultOffsetPagination

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from sqlalchemy.orm import DeclarativeBase
    from strawberry import BasePermission
    from strawberry.extensions.field_extension import FieldExtension
    from strawberry.types.arguments import StrawberryArgument
    from strawberry.types.field import _RESOLVER_TYPE
    from strawchemy.sqlalchemy.hook import QueryHook
    from strawchemy.validation.pydantic import PydanticMapper

    from .sqlalchemy.typing import QueryHookCallable
    from .strawberry.typing import FilterStatementCallable, MappedGraphQLDTO
    from .typing import AnyRepository, SupportedDialect
    from .validation.base import ValidationProtocol


T = TypeVar("T", bound="DeclarativeBase")

_TYPES_NS = TYPING_NS | vars(types)

__all__ = ("Strawchemy",)


class Strawchemy:
    """Main entry point for integrating SQLAlchemy models with Strawberry GraphQL.

    This class provides a cohesive interface to generate Strawberry GraphQL types,
    inputs, filters, and fields based on SQLAlchemy models. It manages configuration,
    type registration, and various factories for DTO generation.

    Attributes:
        config (StrawchemyConfig): The configuration object for Strawchemy.
        registry (StrawberryRegistry): The registry for Strawberry types.
        filter: Factory for creating boolean filter input types.
        aggregate_filter: Factory for creating aggregate filter input types.
        distinct_on: Decorator for creating distinct_on enum types.
        input: Factory for creating general input types.
        create_input: Factory for creating input types for create mutations.
        pk_update_input: Factory for creating input types for update-by-PK mutations.
        filter_update_input: Factory for creating input types for update-by-filter mutations.
        order: Factory for creating order_by input types.
        type: Factory for creating Strawberry output types.
        aggregate: Factory for creating aggregation root types.
        upsert_update_fields: Factory for creating enum DTOs for upsert update fields.
        upsert_conflict_fields: Factory for creating enum DTOs for upsert conflict fields.
        pydantic (PydanticMapper): A mapper for generating Pydantic models.
    """

    def __init__(
        self,
        config: Union[StrawchemyConfig, SupportedDialect],
        strawberry_config: Optional[StrawberryConfig] = None,
    ) -> None:
        """Initializes the Strawchemy instance.

        Sets up the configuration, registry, and various DTO factories
        required for type and field generation.

        Args:
            config: A StrawchemyConfig instance or a supported dialect string
                    (e.g., "postgresql", "mysql") to initialize a default config.
            strawberry_config: A StrawberryConfig instance to initialize the registry.
                If not provided, a default StrawberryConfig will be used.
        """
        self.config = StrawchemyConfig(config) if isinstance(config, str) else config
        self.registry = StrawberryRegistry(strawberry_config or StrawberryConfig())

        strawberry_backend = StrawberrryDTOBackend(MappedStrawberryGraphQLDTO)
        enum_backend = EnumDTOBackend(self.config.auto_snake_case)
        upsert_conflict_fields_enum_backend = UpsertConflictFieldsEnumDTOBackend(
            self.config.inspector, self.config.auto_snake_case
        )

        self._aggregate_filter_factory = AggregateFilterDTOFactory(self)
        self._order_by_factory = OrderByDTOFactory(self)
        self._distinct_on_enum_factory = DistinctOnFieldsDTOFactory(self.config.inspector)
        self._type_factory = TypeDTOFactory(self, strawberry_backend, order_by_factory=self._order_by_factory)
        self._input_factory = InputFactory(self, strawberry_backend)
        self._aggregation_factory = RootAggregateTypeDTOFactory(
            self, strawberry_backend, type_factory=self._type_factory
        )
        self._enum_factory = EnumDTOFactory(self.config.inspector, enum_backend)
        self._filter_factory = BooleanFilterDTOFactory(self, aggregate_filter_factory=self._aggregate_filter_factory)
        self._upsert_conflict_factory = UpsertConflictFieldsDTOFactory(
            self.config.inspector, upsert_conflict_fields_enum_backend
        )

        self.filter = self._filter_factory.input
        self.aggregate_filter = partial(self._aggregate_filter_factory.input, mode="aggregate_filter")
        self.distinct_on = self._distinct_on_enum_factory.decorator
        self.input = self._input_factory.input
        self.create_input = partial(self._input_factory.input, mode="create_input")
        self.pk_update_input = partial(self._input_factory.input, mode="update_by_pk_input")
        self.filter_update_input = partial(self._input_factory.input, mode="update_by_filter_input")
        self.order = partial(self._order_by_factory.input, mode="order_by")
        self.type = self._type_factory.type
        self.aggregate = partial(self._aggregation_factory.type, mode="aggregate_type")
        self.upsert_update_fields = self._enum_factory.input
        self.upsert_conflict_fields = self._upsert_conflict_factory.input

        # Register common types
        self.registry.register_enum(OrderByEnum, "OrderByEnum")

    def _annotation_namespace(self) -> dict[str, Any]:
        """Provides the namespace for Strawberry annotations.

        Combines the registry's 'object' namespace with internal Strawchemy types.

        Returns:
            A dictionary representing the annotation namespace.
        """
        return self.registry.namespace("object") | _TYPES_NS

    @cached_property
    def pydantic(self) -> PydanticMapper:
        """Provides access to a PydanticMapper instance.

        This mapper is used for generating Pydantic models corresponding
        to the SQLAlchemy models and Strawberry types.

        Returns:
            An instance of PydanticMapper.
        """
        from .validation.pydantic import PydanticMapper

        return PydanticMapper(self)

    @overload
    def field(
        self,
        resolver: _RESOLVER_TYPE[Any],
        *,
        filter_input: Optional[type[BooleanFilterDTO]] = None,
        order_by: Optional[type[OrderByDTO]] = None,
        distinct_on: Optional[type[EnumDTO]] = None,
        pagination: Optional[Union[bool, DefaultOffsetPagination]] = None,
        arguments: Optional[list[StrawberryArgument]] = None,
        id_field_name: Optional[str] = None,
        root_aggregations: bool = False,
        filter_statement: Optional[FilterStatementCallable] = None,
        execution_options: Optional[dict[str, Any]] = None,
        query_hook: Optional[Union[QueryHook[Any], Sequence[QueryHook[Any]]]] = None,
        repository_type: Optional[AnyRepository] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_classes: Optional[list[type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Sequence[object] = (),
        graphql_type: Optional[Any] = None,
        extensions: Optional[list[FieldExtension]] = None,
        root_field: bool = True,
    ) -> StrawchemyField: ...

    @overload
    def field(
        self,
        *,
        filter_input: Optional[type[BooleanFilterDTO]] = None,
        order_by: Optional[type[OrderByDTO]] = None,
        distinct_on: Optional[type[EnumDTO]] = None,
        pagination: Optional[Union[bool, DefaultOffsetPagination]] = None,
        arguments: Optional[list[StrawberryArgument]] = None,
        id_field_name: Optional[str] = None,
        root_aggregations: bool = False,
        filter_statement: Optional[FilterStatementCallable] = None,
        execution_options: Optional[dict[str, Any]] = None,
        query_hook: Optional[Union[QueryHookCallable[Any], Sequence[QueryHookCallable[Any]]]] = None,
        repository_type: Optional[AnyRepository] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_classes: Optional[list[type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Sequence[object] = (),
        graphql_type: Optional[Any] = None,
        extensions: Optional[list[FieldExtension]] = None,
        root_field: bool = True,
    ) -> Any: ...

    def field(
        self,
        resolver: Optional[_RESOLVER_TYPE[Any]] = None,
        *,
        filter_input: Optional[type[BooleanFilterDTO]] = None,
        order_by: Optional[type[OrderByDTO]] = None,
        distinct_on: Optional[type[EnumDTO]] = None,
        pagination: Optional[Union[bool, DefaultOffsetPagination]] = None,
        arguments: Optional[list[StrawberryArgument]] = None,
        id_field_name: Optional[str] = None,
        root_aggregations: bool = False,
        filter_statement: Optional[FilterStatementCallable] = None,
        execution_options: Optional[dict[str, Any]] = None,
        query_hook: Optional[Union[QueryHookCallable[Any], Sequence[QueryHookCallable[Any]]]] = None,
        repository_type: Optional[AnyRepository] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_classes: Optional[list[type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Sequence[object] = (),
        graphql_type: Optional[Any] = None,
        extensions: Optional[list[FieldExtension]] = None,
        root_field: bool = True,
    ) -> Any:
        """Creates a Strawberry GraphQL field with enhanced SQLAlchemy capabilities.

        This method extends the standard Strawberry field creation by integrating
        SQLAlchemy-specific features like automatic filtering, ordering, pagination,
        and aggregations based on SQLAlchemy models.

        Args:
            resolver: The resolver function for the field. If not provided,
                Strawchemy will attempt to generate one based on the model.
            filter_input: The input type for filtering results.
            order_by: The input type for ordering results.
            distinct_on: The enum type for 'distinct on' clauses (PostgreSQL).
            pagination: Enables pagination for the field. Can be True for default
                offset pagination or a DefaultOffsetPagination instance for customization.
            arguments: A list of additional StrawberryArgument instances for the field.
            id_field_name: The name of the ID field, used for certain operations.
            root_aggregations: If True, enables root-level aggregations for the field.
            filter_statement: A callable to generate a filter statement for the query.
            execution_options: SQLAlchemy execution options for the query.
            query_hook: A callable or sequence of callables to modify the SQLAlchemy query.
            repository_type: A custom repository class for data fetching logic.
            name: The name of the GraphQL field.
            description: The description of the GraphQL field.
            permission_classes: A list of permission classes for the field.
            deprecation_reason: The reason for deprecating the field.
            default: The default value for the field.
            default_factory: A factory function to generate the default value.
            metadata: Additional metadata for the field.
            directives: A sequence of directives for the field.
            graphql_type: The GraphQL type of the field. If not provided, it's inferred.
            extensions: A list of Strawberry FieldExtensions.
            root_field: Indicates if this is a root-level field.

        Returns:
            A StrawchemyField instance, which is a specialized StrawberryField.
        """
        namespace = self._annotation_namespace()
        type_annotation = StrawberryAnnotation.from_annotation(graphql_type, namespace) if graphql_type else None
        repository_type_ = repository_type if repository_type is not None else self.config.repository_type
        execution_options_ = execution_options if execution_options is not None else self.config.execution_options
        pagination = (
            DefaultOffsetPagination(limit=self.config.pagination_default_limit) if pagination is True else pagination
        )
        if pagination is None:
            pagination = self.config.pagination
        id_field_name = id_field_name or self.config.default_id_field_name

        field = StrawchemyField(
            config=self.config,
            repository_type=repository_type_,
            root_field=root_field,
            filter_statement=filter_statement,
            execution_options=execution_options_,
            filter_type=filter_input,
            order_by=order_by,
            pagination=pagination,
            id_field_name=id_field_name,
            distinct_on=distinct_on,
            root_aggregations=root_aggregations,
            query_hook=query_hook,
            python_name=None,
            graphql_name=name,
            type_annotation=type_annotation,
            is_subscription=False,
            permission_classes=permission_classes or [],
            deprecation_reason=deprecation_reason,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            directives=directives,
            extensions=extensions or [],
            registry_namespace=namespace,
            description=description,
            arguments=arguments,
        )
        return field(resolver) if resolver else field

    def create(
        self,
        input_type: type[MappedGraphQLDTO[T]],
        resolver: Optional[_RESOLVER_TYPE[Any]] = None,
        *,
        repository_type: Optional[AnyRepository] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_classes: Optional[list[type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Sequence[object] = (),
        graphql_type: Optional[Any] = None,
        extensions: Optional[list[FieldExtension]] = None,
        validation: Optional[ValidationProtocol[T]] = None,
    ) -> Any:
        """Creates a Strawberry GraphQL mutation field for creating new model instances.

        This method generates a mutation field that handles the creation of
        SQLAlchemy model instances based on the provided input type. It integrates
        with Strawchemy's repository system for data persistence and allows for
        custom validation.

        Args:
            input_type: The Strawberry input type representing the data for creating
                a new model instance. This should be a `MappedGraphQLDTO`.
            resolver: An optional custom resolver function for the mutation. If not
                provided, Strawchemy will use a default resolver.
            repository_type: An optional custom repository class for data fetching
                and persistence logic. Defaults to the repository configured in
                `StrawchemyConfig`.
            name: The name of the GraphQL mutation field.
            description: The description of the GraphQL mutation field.
            permission_classes: A list of permission classes for the field.
            deprecation_reason: The reason for deprecating the field.
            default: The default value for the field (typically not used for mutations).
            default_factory: A factory function to generate the default value.
            metadata: Additional metadata for the field.
            directives: A sequence of directives for the field.
            graphql_type: The GraphQL return type of the mutation. If not provided,
                it's inferred, typically to be the corresponding output type of the model.
            extensions: A list of Strawberry FieldExtensions.
            validation: An optional validation protocol instance to validate
                the input data before creation.

        Returns:
            A `StrawchemyCreateMutationField` instance, which is a specialized
            StrawberryField configured for create mutations.
        """
        namespace = self._annotation_namespace()
        type_annotation = StrawberryAnnotation.from_annotation(graphql_type, namespace) if graphql_type else None
        repository_type_ = repository_type if repository_type is not None else self.config.repository_type

        field = StrawchemyCreateMutationField(
            input_type,
            config=self.config,
            repository_type=repository_type_,
            python_name=None,
            graphql_name=name,
            type_annotation=type_annotation,
            is_subscription=False,
            permission_classes=permission_classes or [],
            deprecation_reason=deprecation_reason,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            directives=directives,
            extensions=extensions or [],
            registry_namespace=namespace,
            description=description,
            validation=validation,
        )
        return field(resolver) if resolver else field

    def upsert(
        self,
        input_type: type[MappedGraphQLDTO[T]],
        update_fields: type[EnumDTO],
        conflict_fields: type[EnumDTO],
        resolver: Optional[_RESOLVER_TYPE[Any]] = None,
        *,
        repository_type: Optional[AnyRepository] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_classes: Optional[list[type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Sequence[object] = (),
        graphql_type: Optional[Any] = None,
        extensions: Optional[list[FieldExtension]] = None,
        validation: Optional[ValidationProtocol[T]] = None,
    ) -> Any:
        """Creates a Strawberry GraphQL mutation field for upserting model instances.

        This method generates a mutation field that handles the "upsert"
        (update or insert) of SQLAlchemy model instances. It uses the provided
        input type, update fields enum, and conflict fields enum to determine
        the behavior on conflict. It integrates with Strawchemy's repository
        system and allows for custom validation.

        Args:
            input_type: The Strawberry input type representing the data for
                the upsert operation. This should be a `MappedGraphQLDTO`.
            update_fields: An `EnumDTO` specifying which fields to update if a
                conflict occurs and an update is performed.
            conflict_fields: An `EnumDTO` specifying the fields to use for
                conflict detection (e.g., primary key or unique constraints).
            resolver: An optional custom resolver function for the mutation. If not
                provided, Strawchemy will use a default resolver.
            repository_type: An optional custom repository class for data fetching
                and persistence logic. Defaults to the repository configured in
                `StrawchemyConfig`.
            name: The name of the GraphQL mutation field.
            description: The description of the GraphQL mutation field.
            permission_classes: A list of permission classes for the field.
            deprecation_reason: The reason for deprecating the field.
            default: The default value for the field (typically not used for mutations).
            default_factory: A factory function to generate the default value.
            metadata: Additional metadata for the field.
            directives: A sequence of directives for the field.
            graphql_type: The GraphQL return type of the mutation. If not provided,
                it's inferred, typically to be the corresponding output type of the model.
            extensions: A list of Strawberry FieldExtensions.
            validation: An optional validation protocol instance to validate
                the input data before the upsert operation.

        Returns:
            A `StrawchemyUpsertMutationField` instance, which is a specialized
            StrawberryField configured for upsert mutations.
        """
        namespace = self._annotation_namespace()
        type_annotation = StrawberryAnnotation.from_annotation(graphql_type, namespace) if graphql_type else None
        repository_type_ = repository_type if repository_type is not None else self.config.repository_type

        field = StrawchemyUpsertMutationField(
            input_type,
            update_fields_enum=update_fields,
            conflict_fields_enum=conflict_fields,
            config=self.config,
            repository_type=repository_type_,
            python_name=None,
            graphql_name=name,
            type_annotation=type_annotation,
            is_subscription=False,
            permission_classes=permission_classes or [],
            deprecation_reason=deprecation_reason,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            directives=directives,
            extensions=extensions or [],
            registry_namespace=namespace,
            description=description,
            validation=validation,
        )
        return field(resolver) if resolver else field

    def update(
        self,
        input_type: type[MappedGraphQLDTO[T]],
        filter_input: type[BooleanFilterDTO],
        resolver: Optional[_RESOLVER_TYPE[Any]] = None,
        *,
        repository_type: Optional[AnyRepository] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_classes: Optional[list[type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Sequence[object] = (),
        graphql_type: Optional[Any] = None,
        extensions: Optional[list[FieldExtension]] = None,
        validation: Optional[ValidationProtocol[T]] = None,
    ) -> Any:
        """Creates a Strawberry GraphQL mutation field for updating model instances.

        This method generates a mutation field that handles updating existing
        SQLAlchemy model instances based on filter criteria. It uses the provided
        input type for the update data and a filter input type to specify which
        records to update. It integrates with Strawchemy's repository system and
        allows for custom validation.

        Args:
            input_type: The Strawberry input type representing the data to update
                on the model instances. This should be a `MappedGraphQLDTO`.
            filter_input: The Strawberry input type used to filter which model
                instances should be updated. This should be a `BooleanFilterDTO`.
            resolver: An optional custom resolver function for the mutation. If not
                provided, Strawchemy will use a default resolver.
            repository_type: An optional custom repository class for data fetching
                and persistence logic. Defaults to the repository configured in
                `StrawchemyConfig`.
            name: The name of the GraphQL mutation field.
            description: The description of the GraphQL mutation field.
            permission_classes: A list of permission classes for the field.
            deprecation_reason: The reason for deprecating the field.
            default: The default value for the field (typically not used for mutations).
            default_factory: A factory function to generate the default value.
            metadata: Additional metadata for the field.
            directives: A sequence of directives for the field.
            graphql_type: The GraphQL return type of the mutation. If not provided,
                it's inferred, typically to be a list of the corresponding output
                type of the model or a success/failure indicator.
            extensions: A list of Strawberry FieldExtensions.
            validation: An optional validation protocol instance to validate
                the input data before the update operation.

        Returns:
            A `StrawchemyUpdateMutationField` instance, which is a specialized
            StrawberryField configured for update mutations.
        """
        namespace = self._annotation_namespace()
        type_annotation = StrawberryAnnotation.from_annotation(graphql_type, namespace) if graphql_type else None
        repository_type_ = repository_type if repository_type is not None else self.config.repository_type

        field = StrawchemyUpdateMutationField(
            config=self.config,
            input_type=input_type,
            filter_type=filter_input,
            repository_type=repository_type_,
            python_name=None,
            graphql_name=name,
            type_annotation=type_annotation,
            is_subscription=False,
            permission_classes=permission_classes or [],
            deprecation_reason=deprecation_reason,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            directives=directives,
            extensions=extensions or [],
            registry_namespace=namespace,
            description=description,
            validation=validation,
        )
        return field(resolver) if resolver else field

    def update_by_ids(
        self,
        input_type: type[MappedGraphQLDTO[T]],
        resolver: Optional[_RESOLVER_TYPE[Any]] = None,
        *,
        repository_type: Optional[AnyRepository] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_classes: Optional[list[type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Sequence[object] = (),
        graphql_type: Optional[Any] = None,
        extensions: Optional[list[FieldExtension]] = None,
        validation: Optional[ValidationProtocol[T]] = None,
    ) -> Any:
        """Creates a Strawberry GraphQL mutation field for updating model instances by IDs.

        This method generates a mutation field that handles updating existing
        SQLAlchemy model instances based on their primary key(s). The input type
        should typically include the ID(s) of the record(s) to update and the
        data to apply. It integrates with Strawchemy's repository system and
        allows for custom validation.

        Args:
            input_type: The Strawberry input type representing the data for updating
                model instances. This should be a `MappedGraphQLDTO`, usually
                generated by `pk_update_input`, which includes primary key fields.
            resolver: An optional custom resolver function for the mutation. If not
                provided, Strawchemy will use a default resolver.
            repository_type: An optional custom repository class for data fetching
                and persistence logic. Defaults to the repository configured in
                `StrawchemyConfig`.
            name: The name of the GraphQL mutation field.
            description: The description of the GraphQL mutation field.
            permission_classes: A list of permission classes for the field.
            deprecation_reason: The reason for deprecating the field.
            default: The default value for the field (typically not used for mutations).
            default_factory: A factory function to generate the default value.
            metadata: Additional metadata for the field.
            directives: A sequence of directives for the field.
            graphql_type: The GraphQL return type of the mutation. If not provided,
                it's inferred, typically to be the corresponding output type of the
                model or a list thereof.
            extensions: A list of Strawberry FieldExtensions.
            validation: An optional validation protocol instance to validate
                the input data before the update operation.

        Returns:
            A `StrawchemyUpdateMutationField` instance, specialized for updates
            by ID.
        """
        namespace = self._annotation_namespace()
        type_annotation = StrawberryAnnotation.from_annotation(graphql_type, namespace) if graphql_type else None
        repository_type_ = repository_type if repository_type is not None else self.config.repository_type

        field = StrawchemyUpdateMutationField(
            config=self.config,
            input_type=input_type,
            repository_type=repository_type_,
            python_name=None,
            graphql_name=name,
            type_annotation=type_annotation,
            is_subscription=False,
            permission_classes=permission_classes or [],
            deprecation_reason=deprecation_reason,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            directives=directives,
            extensions=extensions or [],
            registry_namespace=namespace,
            description=description,
            validation=validation,
        )
        return field(resolver) if resolver else field

    def delete(
        self,
        filter_input: Optional[type[BooleanFilterDTO]] = None,
        resolver: Optional[_RESOLVER_TYPE[Any]] = None,
        *,
        repository_type: Optional[AnyRepository] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_classes: Optional[list[type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Sequence[object] = (),
        graphql_type: Optional[Any] = None,
        extensions: Optional[list[FieldExtension]] = None,
    ) -> Any:
        """Creates a Strawberry GraphQL mutation field for deleting model instances.

        This method generates a mutation field that handles the deletion of
        SQLAlchemy model instances. Deletion can be based on filter criteria
        provided via `filter_input` or by ID if the `filter_input` is structured
        to accept primary key(s). It integrates with Strawchemy's repository
        system for data persistence.

        Args:
            filter_input: The Strawberry input type used to filter which model
                instances should be deleted. This should be a `BooleanFilterDTO`.
                If deleting by ID, this DTO should contain the ID field(s).
                If None, the mutation might be configured to delete a single
                record based on an ID passed directly (implementation dependent).
            resolver: An optional custom resolver function for the mutation. If not
                provided, Strawchemy will use a default resolver.
            repository_type: An optional custom repository class for data fetching
                and persistence logic. Defaults to the repository configured in
                `StrawchemyConfig`.
            name: The name of the GraphQL mutation field.
            description: The description of the GraphQL mutation field.
            permission_classes: A list of permission classes for the field.
            deprecation_reason: The reason for deprecating the field.
            default: The default value for the field (typically not used for mutations).
            default_factory: A factory function to generate the default value.
            metadata: Additional metadata for the field.
            directives: A sequence of directives for the field.
            graphql_type: The GraphQL return type of the mutation. If not provided,
                it's inferred, often to indicate success/failure or the number
                of records deleted.
            extensions: A list of Strawberry FieldExtensions.

        Returns:
            A `StrawchemyDeleteMutationField` instance, which is a specialized
            StrawberryField configured for delete mutations.
        """
        namespace = self._annotation_namespace()
        type_annotation = StrawberryAnnotation.from_annotation(graphql_type, namespace) if graphql_type else None
        repository_type_ = repository_type if repository_type is not None else self.config.repository_type

        field = StrawchemyDeleteMutationField(
            filter_input,
            config=self.config,
            repository_type=repository_type_,
            python_name=None,
            graphql_name=name,
            type_annotation=type_annotation,
            is_subscription=False,
            permission_classes=permission_classes or [],
            deprecation_reason=deprecation_reason,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            directives=directives,
            extensions=extensions or [],
            registry_namespace=namespace,
            description=description,
        )
        return field(resolver) if resolver else field
