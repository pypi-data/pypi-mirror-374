import ast
import inspect
import sys
import textwrap
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from rest_framework import serializers


IGNORED_CALL_ATTRS = {
    'all',
    'filter',
    'exclude',
    'values',
    'values_list',
    'get',
    'first',
    'last',
    'exists',
    'count',
    'aggregate',
    'annotate',
    'order_by',
}


@dataclass
class MethodParseResult:
    """Результат парсинга метода AST: chains: цепочки атрибутов от исходного instance (project.xxx),
    var_chains: цепочки, привязанные к локальным переменным (i.env), и serializer_calls — имена вызванных сериалайзеров"""

    chains: Set[Tuple[str, ...]]
    var_chains: Dict[str, Set[Tuple[str, ...]]]  # var_name -> set of chains (relative)
    serializer_calls: Set[str]


class _MethodVisitor(ast.NodeVisitor):
    """
    AST visitor:
     - собирает Attribute chains вида project.vcs.url -> ("project","vcs","url")
     - собирает вызовы Call.func names -> serializer calls
     - отслеживает comprehensions / for-loops: i in project_dependency.occurrences.all() ->
         сопоставляет var 'i' с chain ("project_dependency","occurrences","all")
       затем все Attribute вида i.env будут сохранены in var_chains['i'] as ("env",)
    """

    def __init__(self, instance_name: str):
        self.instance_name = instance_name
        self.chains: Set[Tuple[str, ...]] = set()
        self.var_chains: Dict[str, Set[Tuple[str, ...]]] = defaultdict(set)
        self.serializer_calls: Set[str] = set()
        # mapping loop var -> chain (tuple)
        self._loop_var_to_chain: Dict[str, Tuple[str, ...]] = {}

    # helper to get full dotted path list/tuple for Attribute or Name
    def _unwind_attribute(self, node: ast.AST) -> Optional[Tuple[str, ...]]:
        parts: List[str] = []
        cur = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            return tuple(reversed(parts))
        # Also support Subscript(Name['key'])? skip for now
        return None

    def visit_Attribute(self, node: ast.Attribute):
        tup = self._unwind_attribute(node)
        if tup:
            # tup is like ("project","vcs","url") or ("i","env")
            if tup[0] == self.instance_name:
                self.chains.add(tup)
            else:
                # could be var reference like ("i", "env")
                var = tup[0]
                if var in self._loop_var_to_chain:
                    # register relative chain (without var)
                    self.var_chains[var].add(tuple(tup[1:]))
        # descend
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # collect serializer constructor calls (simple heuristic)
        func = node.func
        if isinstance(func, ast.Name):
            self.serializer_calls.add(func.id)
        elif isinstance(func, ast.Attribute):
            # e.g. serializers.RepositorySerializer -> attr name
            self.serializer_calls.add(func.attr)
        # Also check Calls like project_dependency.occurrences.all() -- we still need to visit this for loop var mapping
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        # for target in iter: if iter is attribute chain starting at instance -> map target -> chain
        # target can be Name or tuple; we handle simple Name
        chain = self._unwind_attribute(node.iter) if isinstance(node.iter, ast.Attribute) else None
        if chain and chain[0] == self.instance_name:
            # chain like ("project_dependency","occurrences","all")
            # map target variable to this chain (so later i.env becomes model under occurrences)
            if isinstance(node.target, ast.Name):
                self._loop_var_to_chain[node.target.id] = chain
        # descend into body (to catch attributes inside)
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp):
        # comprehensions: elt and generators
        # handle generators: for target in iter
        for gen in node.generators:
            chain = self._unwind_attribute(gen.iter) if isinstance(gen.iter, ast.Attribute) else None
            if chain and chain[0] == self.instance_name:
                if isinstance(gen.target, ast.Name):
                    self._loop_var_to_chain[gen.target.id] = chain
        self.generic_visit(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        for gen in node.generators:
            chain = self._unwind_attribute(gen.iter) if isinstance(gen.iter, ast.Attribute) else None
            if chain and chain[0] == self.instance_name:
                if isinstance(gen.target, ast.Name):
                    self._loop_var_to_chain[gen.target.id] = chain
        self.generic_visit(node)

    def visit_With(self, node: ast.With):
        # with something as var: treat similar if assigned from attribute call
        for item in node.items:
            context_expr = item.context_expr
            if isinstance(context_expr, ast.Attribute):
                chain = self._unwind_attribute(context_expr)
                if (
                    chain
                    and chain[0] == self.instance_name
                    and item.optional_vars
                    and isinstance(item.optional_vars, ast.Name)
                ):
                    self._loop_var_to_chain[item.optional_vars.id] = chain
        self.generic_visit(node)


def extract_attr_chains_and_serializer_calls(method) -> MethodParseResult:
    """
    Parse method source and return chains and serializer call names.
    chains are tuples like ("project","vcs","url") for direct attributes,
    var_chains map variable->set of tuples (relative attributes used on that var).
    serializer_calls is set of names called in AST (e.g. "RepositorySerializer").
    """
    try:
        src = inspect.getsource(method)
    except (OSError, TypeError):
        return MethodParseResult(set(), {}, set())

    src = textwrap.dedent(src)
    tree = ast.parse(src)

    # find function def node (top-level)
    func_node = None
    for n in tree.body:
        if isinstance(n, ast.FunctionDef):
            func_node = n
            break
    if func_node is None:
        return MethodParseResult(set(), {}, set())

    # determine name of instance arg (second arg, after self)
    if len(func_node.args.args) < 2:
        return MethodParseResult(set(), {}, set())
    instance_name = func_node.args.args[1].arg

    visitor = _MethodVisitor(instance_name)
    visitor.visit(func_node)

    return MethodParseResult(
        chains=visitor.chains, var_chains=visitor.var_chains, serializer_calls=visitor.serializer_calls
    )


# ---------- resolving chains to models ----------


def _find_field_or_relation(model_cls, attr: str):
    """
    Try to find field (forward) or relation (reverse included) by attr name.
    Returns Field-like object or None.
    """
    with suppress(Exception):
        return model_cls._meta.get_field(attr)

    # try reverse accessors / related names
    for f in model_cls._meta.get_fields():
        if not getattr(f, 'is_relation', False):
            continue
        try:
            acc = f.get_accessor_name()
        except Exception:
            acc = None
        # forward name
        if getattr(f, 'name', None) == attr:
            return f
        if acc == attr:
            return f
    return None


def resolve_chains_to_models(root_model, parse: MethodParseResult):
    """
    root_model: Django model class (not label)
    chains: iterable of tuples starting with instance name, e.g. ("project","vcs","url")
    var_chains: mapping varname -> set of tuples like ("env",) (attributes used on that var)
    Returns: dict model_label -> set(attrs)
    """
    result: Dict[str, Set[str]] = defaultdict(set)

    # handle direct chains from instance (e.g. ("project","vcs","url"))
    for chain in parse.chains:
        # first element is instance name (skip it)
        if len(chain) < 2:
            continue
        steps = list(chain[1:])
        model = root_model
        for i, step in enumerate(steps):
            # ignore manager calls if step is one of ignored
            if step in IGNORED_CALL_ATTRS:
                continue

            field = _find_field_or_relation(model, step)
            if field is None:
                # attribute/property/JSON key — belongs to current model
                result[model._meta.label].add(step)
                break

            # if it's a relation and has related_model and not last step — descend
            if getattr(field, 'is_relation', False) and i < len(steps) - 1:
                related_model = getattr(field, 'related_model', None)
                if related_model is None:
                    # can't resolve — treat step as attribute of current model
                    result[model._meta.label].add(step)
                    break
                model = related_model
                continue

            # if it's relation and last step -> they asked for whole related object (or just accessed it)
            if getattr(field, 'is_relation', False) and i == len(steps) - 1:
                # record that current model needs the relation field (the fk/accessor)
                result[model._meta.label].add(step)
                break

            # otherwise normal field
            result[model._meta.label].add(step)
            break

    # handle var_chains: for each var -> we have a chain that led to that var,
    # e.g. loop var 'i' mapped to ("project_dependency","occurrences","all") earlier.
    # For each use i.attr1, i.attr2 we should assign attr1, attr2 to the model arrived at after resolving the var chain.

    # Note: we will provide a wrapper that receives also var_base_map and then process below.

    return dict(result)


# ---------- helper to find serializer class by name (search loaded modules) ----------
def find_serializer_class_by_name(name: str) -> Optional[type]:
    """
    Heuristic: search through sys.modules for class with __name__ == name and issubclass(serializers.BaseSerializer)
    Returns the class if found, else None.
    """
    import inspect as _inspect

    for module in list(sys.modules.values()):
        if not module:
            continue
        with suppress(Exception):
            for _, obj in _inspect.getmembers(module, _inspect.isclass):
                if obj.__name__ == name and _inspect.isclass(obj) and issubclass(obj, serializers.BaseSerializer):
                    return obj
    return None


# class _InstanceVisitor(ast.NodeVisitor):
#     def __init__(self, instance_name: str):
#         self.instance_name = instance_name
#         self.chains: list[list[str]] = []
#
#     def visit_Attribute(self, node: ast.Attribute):
#         parts = []
#         cur = node
#         while isinstance(cur, ast.Attribute):
#             parts.append(cur.attr)
#             cur = cur.value
#
#         if isinstance(cur, ast.Name) and cur.id == self.instance_name:
#             self.chains.append(list(reversed(parts)))
#
#         self.generic_visit(node)
#
#
# def extract_attr_chains_from_method(method) -> list[list[str]]:
#     """
#     Возвращает список цепочек атрибутов, к которым обращается метод.
#
#     def get_repository(self, project):
#         return project.vcs.url
#
#     -> [["vcs", "url"]]
#     """
#     try:
#         src = inspect.getsource(method)
#     except OSError:
#         return []
#
#     src = textwrap.dedent(src)
#     tree = ast.parse(src)
#
#     func_def = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
#     if len(func_def.args.args) < 2:
#         return []
#
#     instance_name = func_def.args.args[1].arg
#     visitor = _InstanceVisitor(instance_name)
#     visitor.visit(tree)
#     return visitor.chains
#
#
# IGNORED_CALL_ATTRS = {'all', 'filter', 'exclude', 'values', 'values_list', 'get', 'first', 'last', 'exists', 'count'}
#
#
# def _find_field_or_relation(model_cls, attr):
#     """
#     Попытка найти поле/relation у модели по имени accessor (включая reverse relations).
#     Возвращает Field или None.
#     """
#     with suppress(Exception):
#         # быстрый путь: прямое поле (forward)
#         return model_cls._meta.get_field(attr)
#
#     # если не нашли — попробуем найти relation среди всех полей (включая reverse)
#     for f in model_cls._meta.get_fields():
#         if not getattr(f, 'is_relation', False):
#             continue
#         # forward relation name -> f.name
#         if getattr(f, 'name', None) == attr:
#             return f
#         # reverse accessor name (get_accessor_name) может совпадать с attr
#         try:
#             acc = f.get_accessor_name()
#         except Exception:
#             acc = None
#         if acc == attr:
#             return f
#     return None
#
#
# def resolve_chains_to_models(root_model, chains):
#     """
#     chains: list of list[str], e.g. [["vcs", "url"], ["repo_ref_name"]]
#     Возвращает dict: model_label -> set(attrs) — атрибуты для каждой модели.
#     """
#     result = defaultdict(set)
#
#     for chain in chains:
#         model = root_model
#         for i, step in enumerate(chain):
#             if step in IGNORED_CALL_ATTRS:
#                 continue
#
#             field = _find_field_or_relation(model, step)
#             if field is None:
#                 # не relation/поле: считаем атрибутом текущей модели (property, json key и т.д.)
#                 result[model._meta.label].add(step)
#                 break
#
#             # если это relation и не последний шаг — спускаемся в related_model
#             if getattr(field, 'is_relation', False) and i < len(chain) - 1:
#                 related_model = getattr(field, 'related_model', None)
#                 if related_model is None:
#                     # relation без related_mode, считаем атрибутом текущей модели
#                     result[model._meta.label].add(step)
#                     break
#                 model = related_model
#                 continue
#
#             # если это relation и последний шаг. это означает, что метод обратился к whole-related-object
#             # тогда добавляем fk (или сами поля?), добавить поле-ключ (step) на текущей модели
#             if getattr(field, 'is_relation', False) and i == len(chain) - 1:
#                 # обращение вида project.vcs (без конкретного поля)
#                 result[model._meta.label].add(step)
#                 break
#
#             # иначе — это обычное поле (не relation), добавляем его в текущую модель
#             result[model._meta.label].add(step)
#             break
#
#     return result
