"""Pythonic implementation of the DCI (Data Context Interaction) pattern
(http://www.artima.com/articles/dci_vision.html).

Author: Arjan Molenaar

Inspired by the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""
from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from operator import attrgetter
from typing import (
    Callable,
    Dict,
    Hashable,
    Iterator,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

T = TypeVar("T", bound=Hashable)
R = TypeVar("R", bound=Hashable)
G = TypeVar("G", bound=Hashable)


def instance(rolecls: Type[R], subj: T) -> R:
    """Apply the role class to the subject. This is the default role assignment
    method.

    >>> class Person:
    ...     def __init__(self, name): self.name = name
    ...     def am(self): print(self.name, 'is')
    >>> class Biker(metaclass=RoleType):
    ...     def bike(self): print(self.name, 'bikes')
    ...
    >>> person = Person('Joe')
    >>> biker = Biker(person, method=instance)
    >>> biker # doctest: +ELLIPSIS
    <roles.role.Person+Biker object at 0x...>
    >>> person # doctest: +ELLIPSIS
    <roles.role.Person+Biker object at 0x...>
    >>> person is biker
    True
    >>> biker.bike()
    Joe bikes
    """
    subj.__class__ = rolecls  # type: ignore[assignment]
    return subj  # type: ignore[return-value]


def clone(rolecls: Type[R], subj: T) -> R:
    """Returns a new subject instance with role applied. Both instances refer
    to the same instance dict.

    >>> class Person:
    ...     def __init__(self, name): self.name = name
    ...     def am(self): print(self.name, 'is')
    >>> class Biker(metaclass=RoleType):
    ...     def bike(self): print(self.name, 'bikes')
    ...
    >>> person = Person('Joe')
    >>> biker = Biker(person, method=clone)
    >>> biker # doctest: +ELLIPSIS
    <roles.role.Person+Biker object at 0x...>
    >>> person # doctest: +ELLIPSIS
    <roles.role.Person object at 0x...>
    >>> person is biker
    False
    >>> person.__dict__ is biker.__dict__
    True
    >>> biker.bike()
    Joe bikes

    Note that ``clone`` has a serious downside: since only the instance dict is
    cloned, everything defined in the class (properties, methods) are not
    accessible by the role.
    """

    newsubj: R = rolecls.__new__(rolecls)
    newsubj.__dict__ = subj.__dict__
    return newsubj


class AdapterMixin:
    def __getattr__(self, key):
        return getattr(self.role_subject, key)

    def __setattr__(self, key, val):
        return setattr(self.role_subject, key, val)


def adapter(rolecls, subj):
    """Create a wrapper object. The subject is defined as ``subject``
    attribute. This is a kind of last resort method. If you need to use this
    method a lot, then maybe the roles are not the right tool for the job.

    >>> class Person:
    ...     def __init__(self, name): self.name = name
    ...     def am(self): print(self.name, 'is')
    >>> class Biker(metaclass=RoleType):
    ...     def bike(self): print(self.name, 'bikes')
    ...
    >>> person = Person('Joe')
    >>> biker = Biker(person, method=adapter)
    >>> biker # doctest: +ELLIPSIS
    <roles.role.AdapterMixin+Person+Biker object at 0x...>
    >>> person # doctest: +ELLIPSIS
    <roles.role.Person object at 0x...>
    >>> biker.role_subject # doctest: +ELLIPSIS
    <roles.role.Person object at 0x...>
    >>> person is biker
    False
    >>> person.__dict__ is biker.__dict__
    False
    >>> biker.role_subject is person
    True
    >>> biker.bike()
    Joe bikes
    >>> biker.am()
    Joe is
    >>> biker.name = 'Jake'
    >>> person.name
    'Jake'
    """

    adaptercls = rolecls.newclass(rolecls, (AdapterMixin,) + rolecls.__bases__)
    newsubj = adaptercls.__new__(adaptercls)
    newsubj.__dict__["role_subject"] = subj
    return newsubj


EXCLUDED = ("__doc__", "__module__", "__dict__", "__weakref__", "__slots__")


@lru_cache(maxsize=None)
def class_fields(cls: Type, exclude: Sequence[str] = EXCLUDED) -> Set[str]:
    """Get all fields declared in a class, including superclasses.

    Don't forget to clear the cache if fields are added to a class or
    role!
    """
    attrs = set()
    for c in cls.__mro__:
        if c in (type, object):
            break
        attrs.update(list(c.__dict__.keys()))
    return attrs.difference(exclude)


class RoleType(type):
    """``RoleType`` is a metaclass that provides role support to classes. The
    initialization process has been altered to provide addition and removal of
    roles.

    It starts with a normal class:

    >>> class Person:
    ...     def __init__(self, name): self.name = name
    ...     def am(self): print(self.name, 'is')

    Apart from that a few roles can be defined. Simple objects with a default
    ``__init__()`` (no arguments) and the ``RoleType`` as metaclass:

    >>> class Carpenter(metaclass=RoleType):
    ...     def chop(self): print(self.name, 'chops')
    >>> class Biker(metaclass=RoleType):
    ...     def bike(self): print(self.name, 'bikes')

    Now, by default an object has no roles (in this case our person).

    >>> person = Person('Joe')

    Roles can be added by calling the ``assign()`` method:

    >>> Carpenter.assign(person)   # doctest: +ELLIPSIS
    <roles.role.Person+Carpenter object at 0x...>

    Or by calling the role on the subject:

    >>> Carpenter(person)  # doctest: +ELLIPSIS
    <roles.role.Person+Carpenter object at 0x...>

    The persons methods can be invoked:

    >>> person.am()
    Joe is

    As well as the role's methods:

    >>> person.chop()
    Joe chops

    The default behaviour is to apply the role directly to the instance.

    >>> person            # doctest: +ELLIPSIS
    <roles.role.Person+Carpenter object at 0x...>

    The module contains a function ``clone()`` that can be provided to the
    ``asign()`` method to create proxy instances (the default function is
    called ``instance()`` and can also be found in this module):

    >>> biker = Biker.assign(person, method=clone)
    >>> biker                             # doctest: +ELLIPSIS
    <roles.role.Person+Carpenter+Biker object at 0x...>
    >>> biker is person
    False

    Objects can contain multiple roles:

    >>> biker = Biker.assign(person)
    >>> biker                             # doctest: +ELLIPSIS
    <roles.role.Person+Carpenter+Biker object at 0x...>
    >>> biker.__class__.__bases__
    (<class 'roles.role.Person'>, <class 'roles.role.Carpenter'>, <class 'roles.role.Biker'>)

    Note that a new class is assigned, with the roles applied (roles first).

    Roles can be revoked:

    >>> Carpenter.revoke(biker)          # doctest: +ELLIPSIS
    <roles.role.Person+Biker object at 0x...>
    >>> biker.__class__.__bases__
    (<class 'roles.role.Person'>, <class 'roles.role.Biker'>)

    Revoking a non-existant role has no effect:

    >>> Carpenter.revoke(biker)          # doctest: +ELLIPSIS
    <roles.role.Person+Biker object at 0x...>


    Roles do not allow for overriding methods.

    >>> class Incognito(metaclass=RoleType):
    ...     def am(self): return 'under cover'
    >>> Incognito(Person)                # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    TypeError: Can not apply role when overriding methods: am

    *Caching*

    One more thing: role classes are cached. This means that if I want to
    assign a role to a different instance, the same role class is applied:

    >>> person = Person('Joe')
    >>> someone = Person('Jane')
    >>> Biker(someone).__class__ is Biker(person).__class__
    True

    *Changing role application*

    If for some reason the role should not be directly applied to the instance,
    another application method can be assigned.

    Here is an example that uses the ``clone`` method:

    >>> person = Person('Joe')
    >>> person.__class__
    <class 'roles.role.Person'>
    >>> biker = Biker(person, method=clone)
    >>> biker # doctest: +ELLIPSIS
    <roles.role.Person+Biker object at 0x...>
    >>> person.__class__
    <class 'roles.role.Person'>
    >>> biker.bike()
    Joe bikes
    """

    def overrides(self, subj: T) -> Set[str]:
        """Return a set of attributes (methods alike) found in both the role
        and subject instance."""
        try:
            instance_fields = list(subj.__dict__.keys())
        except AttributeError:
            instance_fields = []

        return class_fields(self).intersection(
            class_fields(subj.__class__).union(instance_fields)
        )

    def newclassname(self, bases: Tuple[Type, ...]) -> str:
        """Generate a new name bases on the base classes.

        The last field is the data class.
        """
        namegetter = attrgetter("__name__")
        names = list(map(namegetter, bases))
        # names.reverse()
        return "+".join(names)

    @lru_cache(maxsize=None)
    def newclass(self, cls: Type[T], rolebases: Tuple[Type, ...]) -> Type[R]:
        """Create a new role class."""
        # Role class not yet defined, define a new class
        d: Dict[str, object] = {"__module__": cls.__module__, "__doc__": cls.__doc__}
        try:
            d["__slots__"] = cls.__slots__
        except AttributeError:
            pass

        return type(self.newclassname(rolebases), rolebases, d)

    def assign(
        self, subj: T, method: Callable[[Type[R], T], R] = instance
    ) -> Union[T, R]:
        """Call is invoked when a role should be assigned to an object."""
        if isinstance(subj, self):
            return subj  # type: ignore[return-value]

        # Trait check should go here; provide @override for explicit overrides.
        o = self.overrides(subj)
        if o:
            raise TypeError(
                "Can not apply role when overriding methods: %s" % ", ".join(o)
            )

        cls = type(subj)

        if isinstance(cls, RoleType):
            # Create a sibling class
            rolebases = cls.__bases__ + (self,)
        else:
            # First role class
            rolebases = (cls, self)

        rolecls = self.newclass(cls, rolebases)

        return method(rolecls, subj)

    def revoke(self, subj: R, method: Callable[[Type[T], R], T] = instance) -> T:
        """Retract the role from subj.

        By default the ``instance`` strategy is used.
        """
        if not isinstance(subj, self):
            return subj  # type: ignore[return-value]

        cls = type(subj)
        rolebases = tuple(b for b in cls.__bases__ if b is not self)
        # Fall back to original class as soon as no roles are attached anymore
        rolecls = self.newclass(cls, rolebases) if len(rolebases) > 1 else rolebases[0]
        return method(rolecls, subj)

    __call__ = assign  # type: ignore[assignment]

    @contextmanager
    def played_by(self, subj: T) -> Iterator[Union[T, R]]:
        """Shorthand for using roles in with statements.

        >>> class Biker(metaclass=RoleType):
        ...     def bike(self): return 'bike, bike'
        >>> class Person:
        ...     pass
        >>> john = Person()
        >>> with Biker.played_by(john):
        ...     john.bike()
        'bike, bike'
        """
        if isinstance(subj, self):
            yield subj  # type: ignore[misc]
        else:
            newsubj: Union[T, R] = self.assign(subj)
            try:
                yield newsubj
            finally:
                self.revoke(newsubj)
