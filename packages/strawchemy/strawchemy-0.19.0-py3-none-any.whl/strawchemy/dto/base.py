from __future__ import annotations

import contextlib
import dataclasses
import types
import typing
import warnings
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass, field
from types import new_class
from typing import (
    TYPE_CHECKING,
    Annotated,
    ClassVar,
    ForwardRef,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    runtime_checkable,
)

from typing_extensions import Self, TypeAlias, override

from strawchemy.dto.exceptions import DTOError, EmptyDTOError
from strawchemy.graph import Node
from strawchemy.utils import is_type_hint_optional, non_optional_type_hint

from .types import (
    DTOAuto,
    DTOConfig,
    DTOFieldConfig,
    DTOMissing,
    DTOSkip,
    DTOUnset,
    ExcludeFields,
    IncludeFields,
    Purpose,
    PurposeConfig,
)
from .utils import config

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Hashable, Iterable, Mapping
    from typing import Any, Union


__all__ = ("DTOFactory", "DTOFieldDefinition", "MappedDTO", "ModelInspector")

T = TypeVar("T")
DTOBaseT = TypeVar("DTOBaseT", bound="DTOBase[Any]")
ModelT = TypeVar("ModelT")
ToMappedProtocolT = TypeVar("ToMappedProtocolT", bound="ToMappedProtocol[Any]")
ModelFieldT = TypeVar("ModelFieldT")
FieldVisitor: TypeAlias = "Callable[[ToMappedProtocol[Any], DTOFieldDefinition[Any, Any], Any], Any]"

TYPING_NS = vars(typing) | vars(types)


class VisitorProtocol(Protocol, Generic[ModelT]):
    def field_value(
        self, parent: ToMappedProtocol[ModelT], field: DTOFieldDefinition[Any, Any], value: Any, level: int
    ) -> Any: ...

    def model(
        self,
        parent: ToMappedProtocol[ModelT],
        model_cls: type[ModelT],
        params: dict[str, Any],
        override: dict[str, Any],
        level: int,
    ) -> ModelT: ...


@runtime_checkable
class ToMappedProtocol(Protocol, Generic[ModelT]):
    def to_mapped(
        self,
        visitor: Optional[VisitorProtocol[ModelT]] = None,
        override: Optional[dict[str, Any]] = None,
        level: int = 0,
    ) -> Any: ...


class DTOBase(Generic[ModelT]):
    """Base class to define DTO mapping classes."""

    if TYPE_CHECKING:
        __dto_model__: type[ModelT]
        __dto_config__: ClassVar[DTOConfig]
        __dto_field_definitions__: ClassVar[dict[str, DTOFieldDefinition[Any, Any]]]
        __dto_tags__: set[str]


class MappedDTO(DTOBase[ModelT]):
    """Base class to define DTO mapping classes."""

    def to_mapped(
        self,
        visitor: Optional[VisitorProtocol[ModelT]] = None,
        override: Optional[dict[str, Any]] = None,
        level: int = 0,
    ) -> ModelT:
        """Create an instance of `self.__d_model__`.

        Fill the bound SQLAlchemy model recursively with values from this dataclass.
        """
        model_kwargs: dict[str, Any] = {}
        override = override or {}
        dc_fields: dict[str, dataclasses.Field[Any]] = {}
        if dataclasses.is_dataclass(self.__dto_model__):
            dc_fields = {f.name: f for f in dataclasses.fields(self.__dto_model__)}

        for name, field_def in self.__dto_field_definitions__.items():
            if (value := override.get(name, DTOMissing)) and value is not DTOMissing:
                model_kwargs[name] = value
                continue
            if (field := dc_fields.get(name)) and not field.init:
                continue

            if TYPE_CHECKING:
                value: Union[
                    Union[Union[Union[ModelT, ToMappedProtocol[Any]], list[ModelT]], list[ToMappedProtocol[Any]]],
                    type[DTOMissing],
                ]

            value = getattr(self, name)

            if isinstance(value, (list, tuple)):
                value = [
                    dto.to_mapped(visitor, level=level + 1)
                    if isinstance(dto, ToMappedProtocol)
                    else cast("ModelT", dto)
                    for dto in value
                ]
            if isinstance(value, ToMappedProtocol):
                value = value.to_mapped(visitor, level=level + 1)

            if visitor is not None:
                value = visitor.field_value(self, field_def, value, level + 1)

            if value is DTOUnset or value is self.__dto_config__.unset_sentinel:
                continue

            model_kwargs[field_def.model_field_name] = value
        model_kwargs |= override
        try:
            return (
                visitor.model(self, self.__dto_model__, model_kwargs, override, level + 1)
                if visitor
                else self.__dto_model__(**model_kwargs)
            )
        except TypeError as error:
            original_message = error.args[0] if isinstance(error.args[0], str) else repr(error)
            msg = f"{original_message} (model: {self.__dto_model__.__name__})"
            raise TypeError(msg) from error


class DTOBackend(Protocol, Generic[DTOBaseT]):
    dto_base: type[DTOBaseT]

    def build(
        self,
        name: str,
        model: type[Any],
        field_definitions: Iterable[DTOFieldDefinition[Any, Any]],
        base: Optional[type[Any]] = None,
        **kwargs: Any,
    ) -> type[DTOBaseT]:
        """Build a Data transfer object (DTO) from an SQAlchemy model.

        This inner factory is invoked by the public factory() method

        Args:
            name: Current DTO name
            model: SQLAlchemy model from which to generate the DTO
            field_definitions: Iterable of dto field generated for this model
            dto_config: DTO config
            base: Base class from which the DTO must inherit
            kwargs: Keyword arguments passed to needed to build the DTO


        Returns:
            A DTO generated after the given model.
        """
        raise NotImplementedError

    def update_forward_refs(self, dto: type[DTOBaseT], namespace: dict[str, type[DTOBaseT]]) -> Optional[bool]:
        """Update forward refs for the given DTO.

        Args:
            dto: DTO with forward references
            namespace: Dict that include

        Raises:
            NotImplementedError: _description_
        """
        with contextlib.suppress(NameError):
            dto.__annotations__ = get_type_hints(dto, localns={**TYPING_NS, **namespace}, include_extras=True)

    def copy(self, dto: type[DTOBaseT], name: str) -> type[DTOBaseT]:
        return new_class(name, (dto,))


@dataclass
class Reference(Generic[T, DTOBaseT]):
    name: str
    node: Node[Relation[T, DTOBaseT], None]

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


@dataclass
class Relation(Generic[T, DTOBaseT]):
    model: type[T] = field(compare=True)
    name: str = field(compare=False)
    dto: Optional[type[DTOBaseT]] = field(default=None, compare=False)
    forward_refs: list[Reference[T, DTOBaseT]] = field(default_factory=list, compare=False)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.model.__name__})"


class ModelInspector(Protocol, Generic[ModelT, ModelFieldT]):
    def field_definitions(
        self, model: type[Any], dto_config: DTOConfig
    ) -> Iterable[tuple[str, DTOFieldDefinition[ModelT, ModelFieldT]]]: ...

    def id_field_definitions(
        self, model: type[Any], dto_config: DTOConfig
    ) -> list[tuple[str, DTOFieldDefinition[ModelT, ModelFieldT]]]: ...

    def field_definition(
        self, model_field: ModelFieldT, dto_config: DTOConfig
    ) -> DTOFieldDefinition[ModelT, ModelFieldT]: ...

    def get_type_hints(self, type_: type[Any], include_extras: bool = True) -> dict[str, Any]: ...

    def relation_model(self, model_field: ModelFieldT) -> type[Any]: ...

    def model_field_type(self, field_definition: DTOFieldDefinition[ModelT, ModelFieldT]) -> Any:
        type_hint = (
            field_definition.type_hint_override if field_definition.has_type_override else field_definition.type_hint
        )
        if get_origin(type_hint) is Annotated:
            return get_args(type_hint)[0]
        return non_optional_type_hint(type_hint)

    def relation_cycle(
        self, field: DTOFieldDefinition[Any, ModelFieldT], node: Node[Relation[ModelT, Any], None]
    ) -> bool: ...

    def has_default(self, model_field: ModelFieldT) -> bool: ...

    def required(self, model_field: ModelFieldT) -> bool: ...

    def is_foreign_key(self, model_field: ModelFieldT) -> bool: ...

    def is_primary_key(self, model_field: ModelFieldT) -> bool: ...

    def reverse_relation_required(self, model_field: ModelFieldT) -> bool: ...


@dataclass
class DTOFieldDefinition(Generic[ModelT, ModelFieldT]):
    dto_config: DTOConfig

    model: type[ModelT]
    model_field_name: str

    _name: str = field(init=False)

    type_hint: Any
    is_relation: bool = False
    config: DTOFieldConfig = field(default_factory=DTOFieldConfig)
    _model_field: Union[ModelFieldT, type[DTOMissing]] = DTOMissing
    related_model: Optional[type[ModelT]] = None
    related_dto: Optional[Union[type[DTOBase[ModelT]], ForwardRef]] = None
    self_reference: bool = False
    uselist: bool = False
    init: bool = True
    type_hint_override: Any = DTOMissing
    partial: Optional[bool] = None
    alias: Optional[str] = None
    default: Any = DTOMissing
    default_factory: Union[Callable[..., Any], type[DTOMissing]] = DTOMissing

    _type: Any = DTOMissing

    def __post_init__(self) -> None:
        self._name = self.model_field_name

        # Purpose config
        if self.purpose_config.partial is not None:
            self.partial = self.purpose_config.partial
        if self.purpose_config.alias is not None:
            self._name = self.purpose_config.alias
            self.alias = self.purpose_config.alias
        if self.purpose_config.type_override is not DTOMissing:
            self.type_hint_override = self.purpose_config.type_override

        # DTO config
        if self.dto_config.partial is not None:
            self.partial = self.dto_config.partial
        if (alias := self.dto_config.alias(self.model_field_name)) is not None:
            self._name = alias
            self.alias = alias
        if (type_override_ := self.dto_config.type_overrides.get(self.type_hint, DTOMissing)) is not DTOMissing:
            self.type_hint_override = type_override_

        if self.partial:
            self.default = self.dto_config.partial_default

    @property
    def model_field(self) -> ModelFieldT:
        if self._model_field is DTOMissing:
            msg = "Field does not have a model_field set"
            raise DTOError(msg)
        return self._model_field

    @model_field.setter
    def model_field(self, value: ModelFieldT) -> None:
        self._model_field = value

    @property
    def has_model_field(self) -> bool:
        return self._model_field is not DTOMissing

    @property
    def model_identity(self) -> Union[type[ModelT], ModelFieldT]:
        try:
            return self.model_field
        except DTOError:
            return self.model

    @property
    def purpose_config(self) -> PurposeConfig:
        return self.config.purpose_config(self.dto_config)

    @property
    def name(self) -> str:
        return self._name

    @property
    def type_(self) -> Any:
        if self._type is not DTOMissing:
            return self._type
        type_hint = self.type_hint_override if self.has_type_override else self.type_hint
        return Optional[type_hint] if self.partial else type_hint

    @type_.setter
    def type_(self, value: Any) -> None:
        self._type = value

    @property
    def has_type_override(self) -> bool:
        return self.type_hint_override is not DTOMissing

    @property
    def allowed_purposes(self) -> set[Purpose]:
        return self.config.purposes

    @property
    def complete(self) -> bool:
        return self.dto_config.purpose is Purpose.COMPLETE and Purpose.COMPLETE in self.allowed_purposes

    @property
    def required(self) -> bool:
        required_by_purpose = self.dto_config.purpose is Purpose.READ or (
            self.dto_config.purpose is Purpose.COMPLETE and Purpose.COMPLETE in self.allowed_purposes
        )
        return required_by_purpose and not self.partial

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.type_})"


class DTOFactory(Generic[ModelT, ModelFieldT, DTOBaseT]):
    """Base class for implementing DTO factory.

    Provide methods to inspect SQLAlchemy models and iterating over
    fields to convert.
    """

    def __init__(
        self,
        inspector: ModelInspector[ModelT, ModelFieldT],
        backend: DTOBackend[DTOBaseT],
        handle_cycles: bool = True,
        type_map: Optional[dict[Any, Any]] = None,
    ) -> None:
        """Initialize internal state to keep track of generated DTOs."""
        # Mapping of all existing dtos names to their class, both declared and generated
        self.dtos: dict[str, type[DTOBaseT]] = {}
        # If True, factory will keep references cycles when generating DTOs,
        # they are removed otherwise
        self.handle_cycles: bool = handle_cycles
        self.inspector = inspector
        self.backend = backend
        self.type_map = type_map or {}

        self._dto_cache: dict[Hashable, type[DTOBaseT]] = {}
        self._unresolved_refs: defaultdict[str, list[type[DTOBaseT]]] = defaultdict(list)
        self._scoped_dto_names: dict[Hashable, str] = {}

    def should_exclude_field(
        self,
        field: DTOFieldDefinition[Any, ModelFieldT],
        dto_config: DTOConfig,
        node: Node[Relation[Any, DTOBaseT], None],
        has_override: bool,
    ) -> bool:
        """Whether the model field should be excluded from the dto or not."""
        explictly_excluded = node.is_root and field.model_field_name in dto_config.exclude
        explicitly_included = node.is_root and field.model_field_name in dto_config.include

        # Exclude fields not present in init if purpose is write
        if dto_config.purpose is Purpose.WRITE and not explicitly_included:
            explictly_excluded = explictly_excluded or not field.init
        if dto_config.include == "all" and not explictly_excluded:
            explicitly_included = True

        excluded = dto_config.purpose not in field.allowed_purposes
        if node.is_root:
            excluded = excluded or (explictly_excluded or not explicitly_included)
        else:
            excluded = excluded or explictly_excluded
        return not has_override and excluded

    def _resolve_basic_type(self, field: DTOFieldDefinition[ModelT, ModelFieldT], dto_config: DTOConfig) -> Any:
        type_hint = self.type_map.get(field.type_hint, field.type_)
        overriden_by_type_map = field.type_hint in dto_config.type_overrides or field.type_hint in self.type_map

        if overriden_by_type_map or field.has_type_override:
            return type_hint

        if not field.has_type_override and field.complete and is_type_hint_optional(type_hint):
            type_hint = non_optional_type_hint(type_hint)
        return type_hint

    def _resolve_relation_type(
        self,
        field: DTOFieldDefinition[ModelT, ModelFieldT],
        dto_config: DTOConfig,
        node: Node[Relation[ModelT, DTOBaseT], None],
        **factory_kwargs: Any,
    ) -> Any:
        type_hint = self.type_map.get(field.type_hint, field.type_)
        relation_model = self.inspector.relation_model(field.model_field)
        dto_name = self._scoped_dto_names.get(
            self._scoped_cache_key(relation_model, dto_config), self.dto_name(relation_model.__name__, dto_config, node)
        )
        relation_child = Relation(relation_model, name=dto_name)
        parent = node.find_parent(lambda parent: parent.value == relation_child)

        if relation_model is node.value.model:
            dto = Self
            field.self_reference = True
        elif parent is not None:
            dto = ForwardRef(parent.value.name)
            if self.handle_cycles:
                node.value.forward_refs.append(Reference(parent.value.name, parent))
            field.related_dto = dto
        else:
            child = node.insert_child(relation_child)
            dto = self.factory(
                model=relation_model,
                dto_config=dto_config,
                base=None,
                name=dto_name,
                parent_field_def=field,
                current_node=child,
                **factory_kwargs,
            )
            field.related_dto = dto

        if field.uselist:
            dto = list[dto]

        if (is_type_hint_optional(type_hint) and not field.complete) or field.partial:
            return Optional[dto]
        return dto

    def _resolve_type(
        self,
        field: DTOFieldDefinition[ModelT, ModelFieldT],
        dto_config: DTOConfig,
        node: Node[Relation[ModelT, DTOBaseT], None],
        **factory_kwargs: Any,
    ) -> Any:
        """Recursively resolve the type hint to a valid pydantic type."""
        if not field.is_relation:
            return self._resolve_basic_type(field, dto_config)
        return self._resolve_relation_type(field, dto_config, node, **factory_kwargs)

    def _node_or_root(
        self,
        model: type[Any],
        name: str,
        node: Optional[Node[Relation[Any, DTOBaseT], None]] = None,
    ) -> Node[Relation[Any, DTOBaseT], None]:
        return Node(Relation(model=model, name=name)) if node is None else node

    def _base_cache_key(self, dto_config: DTOConfig) -> Hashable:
        return frozenset(
            [
                (dto_config.purpose, dto_config.partial, dto_config.alias_generator),
                tuple(dto_config.type_overrides.items()),
            ]
        )

    def _root_cache_key(self, dto_config: DTOConfig) -> Hashable:
        root_key = [
            frozenset(dto_config.include if dto_config.include != "all" else ()),
            frozenset(dto_config.exclude),
            frozenset(dto_config.aliases.items()),
            frozenset(dto_config.annotation_overrides.items()),
        ]
        return frozenset(key for key in root_key if key)

    def _scoped_cache_key(self, model: type[Any], dto_config: DTOConfig) -> Hashable:
        return frozenset(
            [
                (model, self._base_cache_key(dto_config), frozenset()),
            ]
        )

    def _cache_key(
        self,
        model: type[Any],
        dto_config: DTOConfig,
        node: Node[Relation[Any, DTOBaseT], None],
        **factory_kwargs: Any,
    ) -> Hashable:
        base_key = self._base_cache_key(dto_config)
        node_key = frozenset()
        if node.is_root and dto_config.scope != "global":
            node_key = self._root_cache_key(dto_config)
        return (model, base_key, node_key)

    def _factory(
        self,
        name: str,
        model: type[ModelT],
        dto_config: DTOConfig,
        node: Node[Relation[Any, DTOBaseT], None],
        base: Optional[type[Any]] = None,
        parent_field_def: Optional[DTOFieldDefinition[ModelT, ModelFieldT]] = None,
        raise_if_no_fields: bool = False,
        backend_kwargs: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> type[DTOBaseT]:
        self_ref_fields: list[DTOFieldDefinition[ModelT, ModelFieldT]] = []
        field_definitions_dict: dict[str, DTOFieldDefinition[ModelT, ModelFieldT]] = {}

        def _gen() -> Iterable[DTOFieldDefinition[ModelT, ModelFieldT]]:
            iterable = self.iter_field_definitions(
                name=name,
                model=model,
                dto_config=dto_config,
                base=base,
                node=node,
                raise_if_no_fields=raise_if_no_fields,
                **kwargs,
            )
            for field_def in iterable:
                yield field_def
                field_definitions_dict[field_def.name] = field_def
                if field_def.self_reference:
                    self_ref_fields.append(field_def)

        dto = self.backend.build(
            name=name,
            model=model,
            field_definitions=_gen(),
            base=base,
            **(backend_kwargs or {}),
        )
        dto.__dto_field_definitions__ = field_definitions_dict
        for field_def in self_ref_fields:
            field_def.related_dto = dto
        return dto

    def type_hint_namespace(self) -> dict[str, Any]:
        return TYPING_NS | self.dtos

    def dto_name(
        self, base_name: str, dto_config: DTOConfig, node: Optional[Node[Relation[Any, DTOBaseT], None]] = None
    ) -> str:
        return f"{base_name}{dto_config.purpose.value.capitalize()}DTO"

    def root_dto_name(
        self, model: type[ModelT], dto_config: DTOConfig, node: Optional[Node[Relation[Any, DTOBaseT], None]] = None
    ) -> str:
        return self.dto_name(model.__name__, dto_config, node)

    def iter_field_definitions(
        self,
        name: str,
        model: type[ModelT],
        dto_config: DTOConfig,
        base: Optional[type[DTOBase[ModelT]]],
        node: Node[Relation[ModelT, DTOBaseT], None],
        raise_if_no_fields: bool = False,
        **factory_kwargs: Any,
    ) -> Generator[DTOFieldDefinition[ModelT, ModelFieldT], None, None]:
        no_fields = True
        annotations: dict[str, Any] = dto_config.annotation_overrides
        if base:
            with suppress(NameError):
                base.__annotations__ = self.inspector.get_type_hints(base)
                annotations = base.__annotations__ | dto_config.annotation_overrides

        for model_field_name, field_def in self.inspector.field_definitions(model, dto_config):
            has_override = model_field_name in annotations
            has_auto_override = has_override and annotations[model_field_name] is DTOAuto

            if has_override and annotations[model_field_name] is not DTOAuto:
                no_fields = False
                field_def.type_ = annotations[model_field_name]

            if self.should_exclude_field(field_def, dto_config, node, has_override):
                continue

            if not has_override or has_auto_override:
                no_fields = False
                field_def.type_ = self._resolve_type(field_def, dto_config, node, **factory_kwargs)
                if field_def.type_ is DTOSkip:
                    continue

            yield field_def
            no_fields = False

        if no_fields:
            msg = f"{name} DTO generated from {model.__qualname__} have no fields"
            if raise_if_no_fields:
                raise EmptyDTOError(msg)
            warnings.warn(msg, stacklevel=2)

    def factory(
        self,
        model: type[ModelT],
        dto_config: DTOConfig,
        base: Optional[type[Any]] = None,
        name: Optional[str] = None,
        parent_field_def: Optional[DTOFieldDefinition[ModelT, ModelFieldT]] = None,
        current_node: Optional[Node[Relation[Any, DTOBaseT], None]] = None,
        raise_if_no_fields: bool = False,
        tags: Optional[set[str]] = None,
        backend_kwargs: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> type[DTOBaseT]:
        """Build a Data transfer object (DTO) from an SQAlchemy model."""
        dto_config = dto_config.with_base_annotations(base) if base else dto_config
        if not name:
            name = base.__name__ if base else self.root_dto_name(model, dto_config, current_node)
        node = self._node_or_root(model, name, current_node)

        scoped_cache_key = self._scoped_cache_key(model, dto_config) if not dto_config.exclude_from_scope else DTOUnset
        cache_key = self._cache_key(model, dto_config, node, **kwargs)

        if dto_config.scope == "global":
            self._scoped_dto_names[self._scoped_cache_key(model, dto_config)] = name

        if (dto := self._dto_cache.get(cache_key)) or (dto := self._dto_cache.get(scoped_cache_key)):
            return self.backend.copy(dto, name) if node.is_root else dto

        dto = self._factory(
            name,
            model,
            dto_config,
            node,
            base,
            parent_field_def,
            raise_if_no_fields,
            backend_kwargs,
            **kwargs,
        )

        dto.__dto_config__ = dto_config
        dto.__dto_model__ = model
        dto.__dto_tags__ = tags or set()

        self.dtos[name] = dto
        if node.is_root and base is not None:
            self.dtos[base.__name__] = dto
        node.value.dto = dto

        if self.handle_cycles and node.value.dto:
            for incomplete_dto in self._unresolved_refs.pop(name, []):
                self.backend.update_forward_refs(incomplete_dto, self.type_hint_namespace())

        self.backend.update_forward_refs(dto, self.type_hint_namespace())

        for ref in node.value.forward_refs:
            self._unresolved_refs[ref.name].append(dto)

        self._dto_cache[cache_key] = dto

        if dto_config.scope is not None:
            self._dto_cache[self._scoped_cache_key(model, dto_config)] = dto

        return dto

    def decorator(
        self,
        model: type[ModelT],
        purpose: Purpose,
        include: Optional[IncludeFields] = None,
        exclude: Optional[ExcludeFields] = None,
        partial: Optional[bool] = None,
        type_map: Optional[Mapping[Any, Any]] = None,
        aliases: Optional[Mapping[str, str]] = None,
        alias_generator: Optional[Callable[[str], str]] = None,
        **kwargs: Any,
    ) -> Callable[[type[Any]], type[DTOBaseT]]:
        def wrapper(class_: type[Any]) -> type[DTOBaseT]:
            return self.factory(
                model=model,
                dto_config=config(
                    purpose=purpose,
                    include=include,
                    exclude=exclude,
                    partial=partial,
                    type_map=type_map,
                    aliases=aliases,
                    alias_generator=alias_generator,
                ),
                base=class_,
                name=class_.__name__,
                **kwargs,
            )

        return wrapper
