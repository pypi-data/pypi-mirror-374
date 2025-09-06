from typing import Any, Optional

from django.db import models
from pydantic import BaseModel, ConfigDict, Field, computed_field


class SerializerFieldBom(BaseModel):
    refs: dict[str, 'SerializerFieldNodeChild'] = Field(default_factory=dict)

    @classmethod
    def from_root_node(cls, fbom_node: 'SerializerFieldNode') -> 'SerializerFieldBom':
        return cls(refs=cls._collect_refs(fbom_node))

    def get_root(self):
        for node in self.refs.values():
            return node

    @property
    def root_model_attrs(self) -> set[str]:
        """Возвращает атрибуты модели из root"""
        return self.get_root().model_attrs

    @classmethod
    def _collect_refs(cls, fbom_node: 'SerializerFieldNode') -> dict:
        """
        root -> полная нода
        остальные -> облегчённые, где children = {name: ref}
        """
        result: dict[str, SerializerFieldNodeChild] = {fbom_node.ref: _make_child_from_node(fbom_node)}

        def _parse_ref(node: 'SerializerFieldNode'):
            if not node.ref:
                return

            if node.ref not in result:
                result[node.ref] = _make_child_from_node(node)
            else:
                existing = result[node.ref]

                for _child in node.children:
                    existing.children.update(_child.ref)

            for node_child in node.children.values():
                _parse_ref(node_child)

        for child in fbom_node.children.values():
            _parse_ref(child)

        return result

    def __repr__(self):
        return self.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True, exclude={'attrs'})


class BaseSerializerFieldNode(BaseModel):
    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True, serialize_by_alias=True)

    serializer: Optional[str] = Field(None, alias='$serializer')

    model_label: Optional[str] = Field(None, alias='$model')
    attrs: Optional[set[str]] = Field(default_factory=set, alias='$attrs')
    annotations: Optional[set[str]] = Field(default_factory=set, alias='$annotations')
    model_attrs: Optional[set[str]] = Field(default=None)

    def model_post_init(self, context: Any, /) -> None:
        self.model_attrs = self.attrs.difference(self.annotations)

    @computed_field(alias='$ref')
    @property
    def ref(self) -> str:
        return self.model_label or self.serializer


class SerializerFieldNode(BaseSerializerFieldNode):
    children: Optional[dict[str, 'SerializerFieldNode']] = Field(default_factory=dict, alias='$children')

    # атрибуты для понимания, какие еще элементы могут быть в запросах
    methods: Optional[dict] = Field(None, alias='$methods')
    hints: Optional[dict[str, list[str]]] = Field(None, alias='$hints')


class SerializerFieldNodeChild(BaseSerializerFieldNode):
    children: Optional[dict[str, str | None]] = Field(default_factory=dict, alias='$children_refs')


class PrefetchOverride(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: Optional[str | type[models.Model]]
    attrs: Optional[set[str]] = Field(default_factory=set)
    lookup: Optional[str] = Field(default='')

    # noinspection PyProtectedMember
    def model_post_init(self, context: Any, /) -> None:
        if isinstance(self.model, str):
            return

        self.model = self.model._meta.label

    @property
    def ref(self):
        return self.model


def _make_child_from_node(node: SerializerFieldNode) -> SerializerFieldNodeChild:
    return SerializerFieldNodeChild(
        serializer=node.serializer,
        children={label: _child.ref for label, _child in node.children.items()},
        model_label=node.model_label,
        attrs=node.attrs,
        annotations=node.annotations,
    )
