from __future__ import annotations

import itertools
import logging
from dataclasses import dataclass
from types import ModuleType
from types import UnionType
from typing import Annotated
from typing import Any
from typing import Literal
from typing import TypeAliasType
from typing import cast
from typing import get_args as get_generic_args
from typing import get_origin
from typing import get_type_hints

from docnote import DOCNOTE_CONFIG_ATTR
from docnote import DocnoteConfig
from docnote import DocnoteConfigParams
from docnote import Note

from docnote_extract._extraction import ModulePostExtraction
from docnote_extract._extraction import TrackingRegistry
from docnote_extract._module_tree import ConfiguredModuleTreeNode
from docnote_extract._utils import validate_config
from docnote_extract.crossrefs import Crossref
from docnote_extract.crossrefs import Crossreffed
from docnote_extract.crossrefs import is_crossreffed
from docnote_extract.summaries import Singleton

logger = logging.getLogger(__name__)


def normalize_namespace_item(
        name_in_parent: str,
        value: Any,
        parent_annotations: dict[str, Any],
        parent_effective_config: DocnoteConfig,
        ) -> NormalizedObj:
    """Given a single item from a namespace (ie, **not a module**), this
    creates a NormalizedObj and returns it.
    """
    # Here we're associating the object with any module-level annotations,
    # but we're not yet separating the docnote annotations from the rest
    raw_annotation = parent_annotations.get(name_in_parent, Singleton.MISSING)
    normalized_annotation = normalize_annotation(raw_annotation)

    config_params: DocnoteConfigParams = \
        parent_effective_config.get_stackables()
    config_params.update(normalized_annotation.config_params)

    # All done. Filtering comes later; here we JUST want to do the
    # normalization!
    return NormalizedObj(
        obj_or_stub=value,
        annotateds=normalized_annotation.annotateds,
        effective_config=DocnoteConfig(**config_params),
        notes=normalized_annotation.notes,
        typespec=normalized_annotation.typespec,
        canonical_module=getattr(value, '__module__', Singleton.UNKNOWN),
        canonical_name=None)


@dataclass(slots=True)
class NormalizedAnnotation:
    typespec: TypeSpec | None
    notes: tuple[Note, ...]
    config_params: DocnoteConfigParams
    annotateds: tuple[LazyResolvingValue, ...]


def normalize_annotation(
        annotation: Any | Literal[Singleton.MISSING]
        ) -> NormalizedAnnotation:
    """Given the annotation for a particular $thing, this extracts out
    any the type hint itself, any attached notes, config params, and
    also any additional ``Annotated`` extras.
    """
    if annotation is Singleton.MISSING:
        return NormalizedAnnotation(
            typespec=None,
            notes=(),
            config_params={},
            annotateds=())
    if is_crossreffed(annotation):
        return NormalizedAnnotation(
            typespec=TypeSpec.from_typehint(annotation),
            notes=(),
            config_params={},
            annotateds=())

    all_annotateds: tuple[Any, ...]
    origin = get_origin(annotation)
    if origin is Annotated:
        type_ = annotation.__origin__
        all_annotateds = annotation.__metadata__

    else:
        type_ = annotation
        all_annotateds = ()

    config_params: DocnoteConfigParams = {}

    notes: list[Note] = []
    external_annotateds: list[LazyResolvingValue] = []
    for annotated in all_annotateds:
        # Note: if the note has its own config, that gets used later; it
        # doesn't modify the rest of the notes!
        if isinstance(annotated, Note):
            notes.append(annotated)
        elif isinstance(annotated, DocnoteConfig):
            config_params.update(annotated.as_nontotal_dict())
        else:
            external_annotateds.append(
                LazyResolvingValue.from_annotated(annotated))

    return NormalizedAnnotation(
        typespec=TypeSpec.from_typehint(type_),
        notes=tuple(notes),
        config_params=config_params,
        annotateds=tuple(external_annotateds))


def normalize_module_dict(
        module: ModulePostExtraction,
        module_tree: Annotated[
                ConfiguredModuleTreeNode,
                Note('''Note that this needs to be the ^^full^^ firstparty
                    module tree, and not just the node for the current module!
                    ''')]
        ) -> dict[str, NormalizedObj]:
    from_annotations: dict[str, Any] = get_type_hints(
        module, include_extras=True)
    dunder_all: set[str] = set(getattr(module, '__all__', ()))
    retval: dict[str, NormalizedObj] = {}

    # Note that, though rare, it's theoretically possible for values to appear
    # in a module's annotations but not its __dict__. (This is much more common
    # for classes, but syntactically valid here, and might be used to surface
    # some kind of docnote or something.)
    bare_annotations = {
        name: Singleton.MISSING for name in from_annotations
        if name not in module.__dict__}

    for name, obj in itertools.chain(
        module.__dict__.items(),
        bare_annotations.items()
    ):
        canonical_module, canonical_name = _get_or_infer_canonical_origin(
            name,
            obj,
            tracking_registry=module._docnote_extract_import_tracking_registry,
            containing_module=module.__name__,
            containing_dunder_all=dunder_all,
            containing_annotation_names=set(from_annotations))

        # Here we're starting to construct an effective config for the object.
        # Note that this is kinda unseparable from the next part, since we're
        # iterating over all of the annotations and separating them out into
        # docnote-vs-not. I mean, yes, we could actually carve this out into
        # a separate function, but it would be more effort than it's worth.
        config_params: DocnoteConfigParams
        if canonical_module is Singleton.UNKNOWN or canonical_module is None:
            config_params = {}
        else:
            # Remember that we're checking EVERYTHING in the module right now,
            # including things we've imported, so this might be outside the
            # firstparty tree. Therefore, we need a fallback here.
            try:
                canonical_module_node = module_tree.find(canonical_module)
            except (KeyError, ValueError):
                config_params = {}
            else:
                config_params = (
                    canonical_module_node.effective_config.get_stackables())

        # This gets any config that was attrached via decorator, for classes
        # and functions.
        if hasattr(obj, DOCNOTE_CONFIG_ATTR):
            decorated_config = getattr(obj, DOCNOTE_CONFIG_ATTR)
            # Beware: remove this, and you'll run into infinite loops!
            if not is_crossreffed(decorated_config):
                config_params.update(decorated_config.as_nontotal_dict())

        raw_annotation = from_annotations.get(name, Singleton.MISSING)
        normalized_obj_annotations = normalize_annotation(raw_annotation)
        config_params.update(normalized_obj_annotations.config_params)

        # All done. Filtering comes later; here we JUST want to do the
        # normalization!
        retval[name] = NormalizedObj(
            obj_or_stub=obj,
            annotateds=normalized_obj_annotations.annotateds,
            effective_config=DocnoteConfig(**config_params),
            notes=normalized_obj_annotations.notes,
            typespec=normalized_obj_annotations.typespec,
            canonical_module=canonical_module,
            canonical_name=canonical_name)

    return retval


def _get_or_infer_canonical_origin(
        name_in_containing_module: str,
        obj: Any,
        *,
        tracking_registry: TrackingRegistry,
        containing_module: str,
        containing_dunder_all: set[str],
        containing_annotation_names: set[str]
        ) -> tuple[
            str | Literal[Singleton.UNKNOWN] | None,
            str | Literal[Singleton.UNKNOWN] | None]:
    """Call this on a module member to retrieve its __module__
    attribute, as well as the name it was assigned within that module,
    or to try and infer the canonical source of the object when no
    __module__ attribute is available.
    """
    if isinstance(obj, ModuleType):
        return None, None

    if obj is Singleton.MISSING:
        return containing_module, name_in_containing_module

    if is_crossreffed(obj):
        metadata = obj._docnote_extract_metadata
        if metadata.traversals:
            logger.warning(
                'Canonical source not inferred due to traversals on module '
                + 'attribute. %s:%s -> %s',
                containing_module, name_in_containing_module, metadata)
            return Singleton.UNKNOWN, Singleton.UNKNOWN

        return metadata.module_name, metadata.toplevel_name

    # Do this next. This allows us more precise tracking of non-stubbed objects
    # that are imported from a re-exported location. In other words, we want
    # the import location to be canonical, and would prefer to have that rather
    # than the definition location, which is what we would get from
    # ``__module__`` and ``__name__`.
    canonical_from_registry = tracking_registry.get(id(obj), None)
    # Note that the None could be coming EITHER from the default in the above
    # .get(), OR because we had multiple conflicting references to it, and we
    # therefore can't use the registry to infer its location.
    if canonical_from_registry is not None:
        return canonical_from_registry

    canonical_module, canonical_name = _get_dunder_module_and_name(obj)
    if canonical_module is None:
        if (
            # Summary:
            # ++  not imported from a tracking module
            # ++  no ``__module__`` attribute
            # ++  name contained within ``__all__``
            # Conclusion: assume it's a canonical member.
            name_in_containing_module in containing_dunder_all
            # Summary:
            # ++  not imported from a tracking module (or at least not uniquely
            #     so) -- therefore, either a reftype or an actual value
            # ++  no ``__module__`` attribute
            # ++  name contained within **module annotations**
            # Conclusion: assume it's a canonical member. This is almost
            # guaranteed; otherwise you'd have to annotate something you just
            # imported
            or name_in_containing_module in containing_annotation_names
        ):
            canonical_module = containing_module
            canonical_name = name_in_containing_module

        else:
            canonical_module = Singleton.UNKNOWN
            canonical_name = Singleton.UNKNOWN

    # Purely here to be defensive.
    elif canonical_name is None:
        raise RuntimeError(
            'Impossible branch! ``__module__`` detected without ``__name__``!')

    return canonical_module, canonical_name


def _get_dunder_module_and_name(
        obj: Any
        ) -> tuple[str, str] | tuple[None, None]:
    """So, things are a bit more complicated than simply getting the
    ``__module__`` attribute of an object and using it. The problem is
    that INSTANCES of a class will inherit its ``__module__`` value.
    This causes problems with... well, basically everything ^^except^^
    classes, functions, methods, descriptors, and generators that are
    defined within the module being inspected.

    I thought about trying to import the ``__module__`` and then
    comparing the actual ``obj`` against ``__module__.__name__``, but
    that's a whole can of worms.

    Instead, we're simply limiting the ``__module__`` value to only
    return something if the ``__name__`` is also defined. This should
    limit it to only the kinds of objects that don't cause problems.
    """
    canonical_name = getattr(obj, '__name__', None)
    if canonical_name is None:
        return None, None
    else:
        return obj.__module__, canonical_name


@dataclass(slots=True)
class NormalizedObj:
    """This is a normalized representation of an object. It contains the
    (stubbed) runtime value of the object along with any annotateds
    (from ``Annotated``), as well as the unpacked-from-``Annotated``
    type itself.
    """
    obj_or_stub: Annotated[
            Any,
            Note('''This is the actual runtime value of the object. It might
                be a ``RefType`` stub or an actual object.''')]
    notes: tuple[Note, ...]
    effective_config: Annotated[
            DocnoteConfig,
            Note('''This contains the end result of all direct configs on the
                object, layered on top of any stackable config items from
                parent scope(s).''')]
    annotateds: tuple[object, ...]
    typespec: Annotated[
            TypeSpec | None,
            Note('''This is a normalized representation of the type that was
                declared on the object.''')]

    # Where the value was declared. String if known (because it had a
    # __module__ or it had a docnote). None in some weird situations, like
    # object.__init_subclass__.
    canonical_module: str | Literal[Singleton.UNKNOWN] | None
    # What name the object had in the module it was declared. String if
    # known, None if not applicable (because it isn't a direct child of a
    # module)
    canonical_name: str | Literal[Singleton.UNKNOWN] | None

    def __post_init__(self):
        validate_config(
            self.effective_config,
            f'Object effective config for {self.obj_or_stub} '
            + f'({self.canonical_module=}, {self.canonical_name=})')


@dataclass(slots=True, frozen=True)
class TypeSpec:
    """This is used as a container for ``NormalizedType``s. At the
    moment, it's pretty simple: just a tuple to expand out unions.
    This remains private, though, because if and when python introduces
    an intersection type, this will get a whole lot more complicated.
    """
    _types: tuple[NormalizedType, ...]

    def __format__(self, fmtinfo: str) -> str:
        """If you don't want to actually resolve the annotation, and you
        just want to stringify it, then use normal string formatting.
        """
        raise NotImplementedError

    @classmethod
    def from_typehint(
            cls,
            typehint: Crossreffed | type | TypeAliasType | UnionType | list
            ) -> TypeSpec:
        """Converts an extracted type hint into a NormalizedType
        instance.

        TODO: this needs a way to (either optionally or automatically)
        expand private type aliases.
        """
        if is_crossreffed(typehint):
            return cls((NormalizedType(typehint._docnote_extract_metadata),))

        elif isinstance(typehint, UnionType):
            norm_types = set()
            for union_member in typehint.__args__:
                norm_types.update(cls.from_typehint(union_member)._types)
            return cls(tuple(norm_types))

        elif isinstance(typehint, TypeAliasType):
            return cls((NormalizedType(Crossref(
                module_name=typehint.__module__,
                toplevel_name=typehint.__name__)),))

        # This is the case in some special forms, like the argspec for
        # callables
        elif isinstance(typehint, list):
            return cls((NormalizedType(
                primary=None,
                params=tuple(
                    TypeSpec.from_typehint(generic_arg)
                    for generic_arg in typehint)),))

        else:
            origin = get_origin(typehint)
            # Non-generics
            if origin is None:
                # This is necessary because we're using TypeGuard instead of
                # TypeIs so that we can have pseudo-intersections.
                typehint = cast(type, typehint)
                return cls((NormalizedType(Crossref(
                    module_name=typehint.__module__,
                    toplevel_name=typehint.__name__)),))

            # Generics
            else:
                return cls((NormalizedType(
                    primary=origin,
                    params=tuple(
                        TypeSpec.from_typehint(generic_arg)
                        for generic_arg in get_generic_args(typehint))),))


@dataclass(slots=True, frozen=True)
class NormalizedType:
    """This is used for all type annotations after normalization.
    """
    # None is used for some special forms (for example, the argspec for
    # callables)
    primary: Crossref | None
    params: tuple[TypeSpec, ...] = ()


@dataclass(slots=True, frozen=True)
class LazyResolvingValue:
    _crossref: Crossref | None
    _value: Literal[Singleton.MISSING] | Any

    def __format__(self, fmtinfo: str) -> str:
        """If you don't want to actually resolve the annotation, and you
        just want to stringify it, then use normal string formatting.
        """
        raise NotImplementedError

    def __call__(self) -> Any:
        """Resolves the actual annotation. Note that the import hook
        must be uninstalled **before** calling this!
        """
        raise NotImplementedError

    @classmethod
    def from_annotated(
            cls,
            annotated: Crossreffed | Any
            ) -> LazyResolvingValue:
        """Converts a reftype-based ``Annotated[]`` member into a
        ``LazyResolvingValue`` instance. If the member was not
        a reftype, returns the value back.

        TODO: this should recurse into containers.
        """
        if is_crossreffed(annotated):
            return cls(
                _crossref=annotated._docnote_extract_metadata,
                _value=Singleton.MISSING)
        else:
            return cls(
                _crossref=None,
                _value=annotated)

    def __post_init__(self):
        if not ((self._crossref is None) ^ (self._value is Singleton.MISSING)):
            raise TypeError(
                'LazyResolvingValue can only have a crossref xor value!',
                self)
