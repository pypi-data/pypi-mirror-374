import contextlib
from typing import Optional

from django.apps import apps
from django.db import models
from rest_framework import serializers


def _serializer_path(serializer_cls: type[serializers.Serializer]) -> str:
    return f'{serializer_cls.__module__}.{serializer_cls.__name__}'


def _add_attr(node: dict, field_name: str) -> None:
    node.setdefault('$attrs', set()).add(field_name)


def _add_method(node: dict, name: str, method_name: str) -> None:
    node.setdefault('$methods', {})[name] = method_name


def _merge_nodes(dst: dict, src: dict) -> dict:
    if '$model' in src and '$model' not in dst:
        dst['$model'] = src['$model']

    if '$attrs' in src:
        for field_name in src['$attrs']:
            _add_attr(dst, field_name)

    if '$methods' in src:
        dst.setdefault('$methods', {}).update(src['$methods'])

    if '$hints' in src:
        dst.setdefault('$hints', {}).update(src['$hints'])

    if '$children' in src and src['$children']:
        dst_children = dst.setdefault('$children', {})
        for name, child in src['$children'].items():
            if name in dst_children:
                _merge_nodes(dst_children[name], child)
            else:
                dst_children[name] = child

    return dst


# noinspection PyProtectedMember
def _follow_one_step_model(current_model: type[models.Model], step: str) -> Optional[type[models.Model]]:
    with contextlib.suppress(Exception):
        field = current_model._meta.get_field(step)
        related_model = getattr(field, 'related_model', None)
        return related_model


# noinspection PyProtectedMember
def _ensure_path_node(root_node: dict, root_model_label: Optional[str], path: list[str]) -> dict:
    node = root_node
    current_model = apps.get_model(root_model_label) if root_model_label else None

    for step in path:
        children = node.setdefault('$children', {})
        if step not in children:
            children[step] = {}
        node = children[step]

        if current_model is not None:
            next_model = _follow_one_step_model(current_model, step)
            if next_model is not None:
                node.setdefault('$model', next_model._meta.label)
                current_model = next_model
            else:
                current_model = None

    return node


def _place_nested_at_path(root_node: dict, root_model_label: Optional[str], path: list[str], nested: dict) -> None:
    if not path:
        _merge_nodes(root_node, nested)
        return

    parent = _ensure_path_node(root_node, root_model_label, path[:-1])
    children = parent.setdefault('$children', {})
    name = path[-1]
    if name in children:
        _merge_nodes(children[name], nested)
    else:
        children[name] = nested


# noinspection PyProtectedMember
def _add_annotations(node: dict) -> None:
    for child in node.get('$children', {}).values():
        _add_annotations(child)

    model_label = node.get('$model')
    if not model_label or '$attrs' not in node:
        return

    model = apps.get_model(model_label)
    # this could be better
    model_field_names = {f.name for f in model._meta.get_fields()}.union({'pk'})
    node['$annotations'] = set(node['$attrs']).difference(model_field_names)


# noinspection PyProtectedMember
def _ensure_relation_children(node: dict) -> None:
    model_label = node.get('$model')
    if not model_label:
        return

    model = apps.get_model(model_label)
    children = node.setdefault('$children', {})

    for field_name in node.get('$attrs', set()):
        with contextlib.suppress(Exception):
            field = model._meta.get_field(field_name)
            if getattr(field, 'is_relation', False) and getattr(field, 'related_model', None):
                rel_model = field.related_model
                if field_name not in children:
                    rel_node = {
                        '$model': rel_model._meta.label,
                        '$bom_ref': field_name,
                        '$attrs': {'pk'},
                    }
                    # todo add edge cases handling

                    children[field_name] = rel_node

    for child in children.values():
        _ensure_relation_children(child)


def _collect_serializer_attrs_to_node(serializer_cls, node: dict):
    # not used yet
    serializer = serializer_cls(read_only=True)

    for field_name, field in serializer.get_fields().items():
        source = field.source if field.source and field.source != '*' else field_name

        if isinstance(field, serializers.ModelSerializer):
            _collect_serializer_attrs_to_node(field.__class__, node)

        elif isinstance(field, serializers.ListSerializer):
            if isinstance(field.child, serializers.ModelSerializer):
                _collect_serializer_attrs_to_node(field.child.__class__, node)
            else:
                node['$attrs'].add(source)

        elif isinstance(field, serializers.Serializer):
            _collect_serializer_attrs_to_node(field.__class__, node)

        elif isinstance(field, serializers.SerializerMethodField):
            method_name = field.method_name or f'get_{field_name}'
            node.setdefault('$methods', {})[field_name] = method_name

        elif isinstance(field, serializers.Field):
            node['$attrs'].add(source)

        else:
            raise ValueError(f'unknown field type {field.__class__.__name__} in serializer {serializer_cls.__name__}')


def _find_or_create_node(fbom: dict, model_label: str, serializer_cls) -> dict:
    """
    Находит ноду по $model, если нет — создает пустую структуру с $attrs и $children.
    """

    def _recursive_find(_node):
        if _node.get('$model') == model_label:
            return _node
        for child in _node.get('$children', {}).values():
            found = _recursive_find(child)
            if found:
                return found
        return None

    node = _recursive_find(fbom)
    if node is None:
        node = {
            '$attrs': set(),
            '$children': {},
            '$model': model_label,
            '$serializer': _serializer_path(serializer_cls),
            '$methods': {},
            '$method_attrs': {},
        }
        # добавляем в корень fbom, если не нашли
        fbom.setdefault('$children', {})[model_label.split('.')[-1]] = node
    return node
