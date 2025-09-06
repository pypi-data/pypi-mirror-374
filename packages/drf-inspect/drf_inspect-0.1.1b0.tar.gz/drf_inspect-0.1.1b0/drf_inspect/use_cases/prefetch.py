from django.apps import apps
from django.db.models import Prefetch

from drf_inspect.models import PrefetchOverride, SerializerFieldBom, SerializerFieldNodeChild


def build_prefetch(
    fbom: SerializerFieldBom,
    overrides: list[PrefetchOverride] | None = None,
) -> list[Prefetch]:
    # _apply_overrides(self, overrides: list[PrefetchOverride] | None = None):
    for override in overrides or []:
        if override.ref in fbom.refs:
            fbom.refs[override.ref].model_attrs.update(override.attrs)
        else:
            if not override.lookup:
                raise ValueError(
                    'you must specify a lookup for PrefetchOverride since the model '
                    f'{override.model!r} not in fbom.refs yet.'
                )

            # _add_to_refs()
            target = fbom.get_root()
            *lookup_path, attr = override.lookup.split('__')
            for lookup in lookup_path:
                for model_lookup, model_label in target.children.items():
                    if model_lookup == lookup:
                        target = fbom.refs[model_label]
                        break
                else:
                    raise ValueError(f'lookup {lookup} not found in fbom children of {target.ref}')

            fbom.refs[override.ref] = SerializerFieldNodeChild(
                model_label=override.ref,
                attrs=override.attrs,
            )
            target.children[attr] = override.ref
            target.model_attrs.add(attr)

    def _build_inner(node_ref: str, prefetch_lookup: str) -> list[Prefetch]:
        node = fbom.refs.get(node_ref)
        if not node:
            raise ValueError(f'{node_ref} is not presented in bom ref')

        if not node.model_label:
            return []

        inner = []
        for ch_name, ch_ref in node.children.items():
            children_prefetches = _build_inner(ch_ref, prefetch_lookup=ch_name)
            inner.extend(children_prefetches)

        model = apps.get_model(node.model_label)

        if len(node.model_attrs) == 1 and '*' in node.model_attrs:
            node.model_attrs = ()

        return [Prefetch(prefetch_lookup, queryset=model.objects.only(*node.model_attrs).prefetch_related(*inner))]

    # _build_prefetches(self):
    prefetches = []
    root = fbom.get_root()
    for child_name, child_ref in root.children.items():
        prefetches.extend(_build_inner(child_ref, prefetch_lookup=child_name))

    return prefetches
