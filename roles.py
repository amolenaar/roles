"""
Pythonic implementation of the DCI (Data Context Interaction) pattern
(http://www.artima.com/articles/dci_vision.html).

Author: Arjan Molenaar

Inspired by the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""

# TODO: decorator that "lifts" objects automatically when entering a method.
# The easy way to go would be in Python3.0, where you can assign annotations
# to an object. E.g.
#    def m(a: SomeRole): pass
# Now a should coerce to the SomeRole type. Eventually a decorator could be
# applied.

from operator import attrgetter
from contextlib import contextmanager


def instance(rolecls, subj):
    """
    Apply the role class to the subject. This is the default role assignment
    method.
    """
    subj.__class__ = rolecls
    return subj


def clone(rolecls, subj):
    """
    Returns a new subject instance with role applied. Both instances refer to
    the same instance dict.

    >>> class Person(object):
    ...     def __init__(self, name): self.name = name
    ...     def am(self): print self.name, 'is'
    >>> class Biker(object):
    ...     __metaclass__ = RoleType
    ...     def bike(self): print self.name, 'bikes'

    >>> person = Person('Joe')
    >>> person.__class__
    <class 'roles.Person'>
    >>> biker = Biker(person, method=clone)
    >>> biker # doctest: +ELLIPSIS
    <roles.Person+Biker object at 0x...>
    >>> person.__class__
    <class 'roles.Person'>
    >>> biker.bike()
    Joe bikes
    """
    newsubj = rolecls.__new__(rolecls)
    newsubj.__dict__ = subj.__dict__
    return newsubj


def cached(func):
    """
    Cache the output of the function invocation.

    >>> @cached
    ... def cap(s): return s.upper()
    >>> cap('a')
    'A'
    >>> cap('b')
    'B'

    Show cache contents:

    >>> cap.cache
    {('a',): 'A', ('b',): 'B'}

    Clear the cache:
    
    >>> cap.cache.clear()
    >>> cap.cache
    {}

    Due to the caching, we can not take key-value arguments:

    >>> cap(s='a')     # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    TypeError: wrapper() got an unexpected keyword argument 's'
    """
    cache = {}

    def wrapper(*args):
        key = args
        try:
            return cache[key]
        except KeyError:
            pass # not in cache
        cache[key] = result = func(*args)
        return result

    wrapper.cache = cache
    wrapper.wrapped_func = func
    return wrapper



class RoleType(type):
    """
    ``RoleType`` is a metaclass that provides role support to classes. The
    initialization process has been altered to provide addition and removal of
    roles.

    It starts with a normal class:

    >>> class Person(object):
    ...     def __init__(self, name): self.name = name
    ...     def am(self): print self.name, 'is'

    Apart from that a few roles can be defined. Simple objects with a default
    ``__init__()`` (no arguments) and the ``RoleType`` as metaclass:

    >>> class Carpenter(object):
    ...     __metaclass__ = RoleType
    ...     def chop(self): print self.name, 'chops'
    >>> class Biker(object):
    ...     __metaclass__ = RoleType
    ...     def bike(self): print self.name, 'bikes'

    Now, by default an object has no roles (in this case our person).

    >>> person = Person('Joe')

    Roles can be added by calling the ``assign()`` method:

    >>> Carpenter.assign(person)   # doctest: +ELLIPSIS
    <roles.Person+Carpenter object at 0x...>

    Or by calling the role on the subject:

    >>> Carpenter(person)  # doctest: +ELLIPSIS
    <roles.Person+Carpenter object at 0x...>

    The persons methods can be invoked:

    >>> person.am()
    Joe is

    As well as the role's methods:

    >>> person.chop()
    Joe chops

    The default behaviour is to apply the role directly to the instance.

    >>> person            # doctest: +ELLIPSIS
    <roles.Person+Carpenter object at 0x...>

    The module contains a function ``clone()`` that can be provided to the
    ``asign()`` method to create proxy instances (the default function is
    called ``instance()`` and can also be found in this module):

    >>> biker = Biker.assign(person, method=clone)
    >>> biker                             # doctest: +ELLIPSIS
    <roles.Person+Carpenter+Biker object at 0x...>
    >>> biker is person
    False

    Objects can contain multiple roles:

    >>> biker = Biker.assign(person)
    >>> biker                             # doctest: +ELLIPSIS
    <roles.Person+Carpenter+Biker object at 0x...>
    >>> biker.__class__.__bases__
    (<class 'roles.Biker'>, <class 'roles.Carpenter'>, <class 'roles.Person'>)
    
    Note that a new class is assigned, with the roles applied (roles first):

    >>> biker.__class__
    <class 'roles.Person+Carpenter+Biker'>
    >>> biker.__class__.__bases__
    (<class 'roles.Biker'>, <class 'roles.Carpenter'>, <class 'roles.Person'>)

    Roles can be revoked:

    >>> Carpenter.revoke(biker)          # doctest: +ELLIPSIS
    <roles.Person+Biker object at 0x...>
    >>> biker.__class__.__bases__
    (<class 'roles.Biker'>, <class 'roles.Person'>)

    Revoking a non-existant role has no effect:

    >>> Carpenter.revoke(biker)          # doctest: +ELLIPSIS
    <roles.Person+Biker object at 0x...>

    Caching

    One more thing: role classes are cached. This means that if I want to
    assign a role to a different instance, the same role class is applied:

    >>> person = Person('Joe')
    >>> someone = Person('Jane')
    >>> Biker(someone).__class__ is Biker(person).__class__
    True

    Changing role application

    If for some reason the role should not be directly applied to the instance,
    another application method can be assigned.

    Here is an example that uses the ``clone`` method:

    >>> person = Person('Joe')
    >>> person.__class__
    <class 'roles.Person'>
    >>> biker = Biker(person, method=clone)
    >>> biker # doctest: +ELLIPSIS
    <roles.Person+Biker object at 0x...>
    >>> person.__class__
    <class 'roles.Person'>
    >>> biker.bike()
    Joe bikes
    """



    @cached
    def newclass(self, cls, rolebases):
        """
        Create a new role class.
        """
        # Role class not yet defined, define a new class
        namegetter = attrgetter('__name__')
        names = list(map(namegetter, rolebases))
        names.reverse()
        rolename = "+".join(names)
        rolecls = type(rolename, rolebases, {
                '__module__': cls.__module__,
                '__doc__': cls.__doc__ })
        return rolecls


    def assign(self, subj, method=instance):
        """
        Call is invoked when a role should be assigned to an object.
        """
        cls = type(subj)

        if issubclass(cls, self):
            return subj

        if isinstance(cls, RoleType):
            # Create a sibling class
            rolebases = (self,) + cls.__bases__
        else:
            # First role class
            rolebases = (self, cls)

        rolecls = self.newclass(cls, rolebases)

        return method(rolecls, subj)


    def revoke(self, subj, method=instance):
        """
        Retract the role from subj. Returning a new subject (or the same one,
        if ``roll()`` has been overwritten).
        """
        if not isinstance(subj, self):
            return subj

        cls = type(subj)
        rolebases = tuple(b for b in cls.__bases__ if b is not self)
        # Fall back to original class as soon as no roles are attached anymore
        if len(rolebases) > 1:
            rolecls = self.newclass(cls, rolebases)
        else:
            rolecls = rolebases[0]
        return method(rolecls, subj)


    __call__ = assign


    @contextmanager
    def played_by(self, subj):
        """
        Shorthand for using roles in with statements

        >>> class Biker(object):
        ...     __metaclass__ = RoleType
        ...     def bike(self): return 'bike, bike'
        >>> class Person(object):
        ...     pass
        >>> john = Person()
        >>> with Biker.played_by(john):
        ...     john.bike()
        'bike, bike'
        """
        if isinstance(subj, self):
            yield subj
        else:
            self.assign(subj)
            try:
                yield subj
            finally:
                self.revoke(subj)


class RoleFactoryType(RoleType):
    """
    ``RoleFactoryType`` is a special kind of RoleType: with the ``@assignto``
    class decorator this class is applied to any RoleType instance.

    Now subroles are able to be automatically applied to specific instances.
    Thus, the Role class is acting as a factory for it's own types.

    Note that this metaclass is automatically applied the first time
    ``@assignto`` is used to decorate a role class. There is no need
    to assign ``RoleFactoryType`` explicitly.

    """


    def register(self, cls, rolecls, strict):
        """
        Register a new roleclass for a specific class.

        Note: ``strict`` is set if the topmost role has ``assignto()`` applied.
        """
        try:
            self._factory[cls] = rolecls
        except AttributeError:
            self._factory = {}
            self._factory[cls] = rolecls
            self._strict = strict
            self.lookup.cache.clear()


    @cached
    def lookup(self, cls):
        """
        Find a specific Role type for a subject. The returned role class
        is a subclass of the factory role.
        """
        get = self._factory.get
        for t in cls.__mro__:
            rolecls = get(t)
            if rolecls: return rolecls
        else:
            if self._strict:
                raise NoRoleError('No role found for %s' % cls)
            return self


    def assign(self, subj, method=instance):
        rolecls = self.lookup(type(subj))
        return RoleType.assign(rolecls, subj, method)


    def revoke(self, subj, method=instance):
        rolecls = self.lookup(type(subj))
        return RoleType.revoke(rolecls, subj, method)


    __call__ = assign


def assignto(cls):
    """
    Class decorator for RoleTypes.

    If a role type is defined as metaclass, this class is used to tell the
    factory which concrete role to use for a certain subject instance.

    Given a class:

    >>> class A(object): pass
    
    And a role:

    >>> class MyRole(object):
    ...     __metaclass__ = RoleType

    You can provide implementations for several roles like this:

    >>> @assignto(A)
    ... class MySubRole(MyRole): pass 

    Note that the metaclass has changed to RoleFactoryType:

    >>> MyRole.__class__
    <class 'roles.RoleFactoryType'>

    >>> MyRole(A())            # doctest: +ELLIPSIS
    <roles.A+MySubRole object at 0x...>

    This also works for subclasses of A:

    >>> class B(A): pass
    >>> class C(B): pass
    >>> c = C()
    >>> MyRole(c)             # doctest: +ELLIPSIS
    <roles.C+MySubRole object at 0x...>

    >>> MyRole.revoke(c)     # doctest: +ELLIPSIS
    <roles.C object at 0x...>

    You can also apply the decorator to the root role directly:

    >>> @assignto(A)
    ... class AnyRole(object):
    ...     __metaclass__ = RoleType

    >>> a = A()
    >>> AnyRole(a)            # doctest: +ELLIPSIS
    <roles.A+AnyRole object at 0x...>

    >>> AnyRole.revoke(a)     # doctest: +ELLIPSIS
    <roles.A object at 0x...>

    Now some other class should not be assigned this role:

    >>> class X(object): pass
    >>> AnyRole(X())          # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    NoRoleError: No role found for <class 'roles.X'>

    And this still works:

    >>> MyRole(A())            # doctest: +ELLIPSIS
    <roles.A+MySubRole object at 0x...>
    """

    def toprole(rolecls):
        """
        Find topmost RoleType class. This is where the role should be
        registered.
        """
        toprolecls = None
        for r in rolecls.__mro__:
            if isinstance(r, RoleType):
                toprolecls = r
            else:
                break

        if not toprolecls:
            raise NotARoleError('could not apply @assignto() to class %s: not a role' % (rolecls,))
        return toprolecls


    def wrapper(rolecls):
        toprolecls = toprole(rolecls)

        if not isinstance(toprolecls, RoleFactoryType):
            # Replace class type by extended factory type
            toprolecls.__class__ = RoleFactoryType

        toprolecls.register(cls, rolecls, rolecls is toprolecls)

        return rolecls

    return wrapper


class NotARoleError(TypeError):
    """
    Exception thrown by role factory if the assigned type is not a role
    (hence, the metaclass is not ``RoleType``).
    """
    pass


class NoRoleError(TypeError):
    """
    Exception thrown by role factory if no role could be applied to an
    instance.
    """
    pass


def rolecontext(*types):
    """
    Define a function as a context for a (set of) role(s).
    
    When the function is called all objects will have the specified role
    applied for certain.

    >>> class Person(object): pass
    >>> class Biker(object):
    ...     __metaclass__ = RoleType
    ...     def bike(self): return 'bike, bike'

    >>> person = Person()

    Now, by applying the ``@rolecontext`` decorator to the function, the
    role is automatically applied for this function invocation.

    >>> @rolecontext(Biker)
    ... def bikerFunc(b):
    ...    return b.bike()
    >>> bikerFunc(person)
    'bike, bike'
    """
    def funcwrapper(func):
        def contextwrapper(*args, **kwargs):
            flags = []
            for a, t in zip(args, types):
                if isinstance(a, t):
                    flags.append(False)
                else:
                    t(a)
                    flags.append(True)
            try:
                return func(*args, **kwargs)
            finally:
                for a, t, f in zip(args, types, flags):
                    if f:
                        t.revoke(a)

        contextwrapper.__name__ = func.__name__
        contextwrapper.__doc__ = func.__doc__
        contextwrapper.__dict__ = func.__dict__.copy()
        contextwrapper.__module__ = func.__module__

        return contextwrapper
    return funcwrapper

# vim:sw=4:et:ai
