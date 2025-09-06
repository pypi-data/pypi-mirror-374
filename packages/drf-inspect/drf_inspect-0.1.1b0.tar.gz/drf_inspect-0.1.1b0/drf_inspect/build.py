"""
# AI-Generated

This module contains two main helper functions `build_fbom_dict()` and `build_serializer_graph()`
which are used for creating the Flat BOM (Bill Of Materials) and a serializer graph respectively.
It also utilises helpers from the 'helpers' module for constructing the BOM.


Functions:

- build_fbom_dict(serializer_cls: Type): -> dict
  This function builds a Flat BOM (Bill Of Materials) dictionary structure from provided Django serializer class.
  It traverses all fields of the serializer and adds path, source, and type attribute in the fbom object.
  For any nested serializers, it performs the operation recursively. If a field type is unknown, it raises a ValueError.
  It adds additional annotations to the BOM, assures the existence of relation fields, and finally returns the Flat BOM dictionary.
  Argument:
    serializer_cls : A Django serializer class to build the BOM from.
  Returns:
    A dictionary representing the BOM for the provided serializer class.

- build_serializer_graph(serializer_cls: Type): -> SerializerFieldBom
  This function is for building recursive serializer relations and attributes. It wraps the output into a SerializerFieldBom.
  The method internally calls `build_fbom_dict()` to construct the data and then validates it.
  Argument:
    serializer_cls: A Django serializer class to build the graph from.
  Returns:
    An instance of SerializerFieldBom.

"""

from typing import Optional

from rest_framework import serializers

from drf_inspect import helpers, models


# noinspection PyProtectedMember
def build_fbom_dict(serializer_cls) -> dict:
    serializer = serializer_cls(read_only=True)
    fbom: dict = {
        '$serializer': helpers._serializer_path(serializer_cls),
    }

    root_model_label: Optional[str] = None
    if issubclass(serializer_cls, serializers.ModelSerializer):
        if model := getattr(serializer_cls.Meta, 'model', None):  # type: ignore[attr]
            root_model_label = model._meta.label
            fbom['$model'] = root_model_label

    for field_name, field in serializer.get_fields().items():
        source = field.source if field.source and field.source != '*' else field_name
        path = source.split('.') if source else [field_name]

        nested: Optional[dict] = None

        if isinstance(field, serializers.ModelSerializer):
            if len(path) > 1:
                helpers._add_attr(fbom, path[0])
            nested = build_fbom_dict(field.__class__)

        elif isinstance(field, serializers.ListSerializer):
            if isinstance(field.child, serializers.ModelSerializer):
                if len(path) > 1:
                    helpers._add_attr(fbom, path[0])
                nested = build_fbom_dict(field.child.__class__)

        elif isinstance(field, serializers.Serializer):
            nested = build_fbom_dict(field.__class__)

        elif isinstance(field, serializers.SerializerMethodField):
            method_name = field.method_name or f'get_{field_name}'
            helpers._add_method(fbom, field_name, method_name)

        elif isinstance(field, serializers.Field):
            # do nothing. need for exception to be raised properly
            pass

        else:
            raise ValueError(
                f'unknown field type {field.__class__.__name__} in serializer {serializer_cls.__class__.__name__}'
            )

        parent = helpers._ensure_path_node(fbom, root_model_label, path[:-1])
        helpers._add_attr(parent, path[-1])

        if nested is not None:
            helpers._place_nested_at_path(fbom, root_model_label, path, nested)

    helpers._add_annotations(fbom)
    helpers._ensure_relation_children(fbom)

    return fbom


def build_serializer_graph(serializer_cls) -> models.SerializerFieldBom:
    fbom_nodes_dict = build_fbom_dict(serializer_cls)

    fbom_nodes = models.SerializerFieldNode.model_validate(fbom_nodes_dict)
    fbom = models.SerializerFieldBom.from_root_node(fbom_nodes)

    return fbom
