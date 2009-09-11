"""
Pythonic implementation of the DCI (Data Context Interaction) pattern
(http://www.artima.com/articles/dci_vision.html).

Author: Arjan Molenaar

Inspired by the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""

from operator import attrgetter


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
    """
    newsubj = rolecls.__new__(rolecls)
    newsubj.__dict__ = subj.__dict__
    return newsubj


class context(object):
    """
    Role assignment method for contexts (``with`` statement).

    >>> class A(object): pass
    >>> class MyRole(object):
    ...     __metaclass__ = RoleType
    >>> a = A()
    >>> a                          # doctest: +ELLIPSIS
    <roles.A object at 0x...>
    >>> with MyRole(a, method=context):
    ...    a                       # doctest: +ELLIPSIS
    <roles.A+MyRole object at 0x...>
    >>> a                          # doctest: +ELLIPSIS
    <roles.A object at 0x...>
    """
    def __init__(self, rolecls, subj):
        self.rolecls = rolecls
        self.subj = subj
        # Role last added is the role to revoke
        self.role = rolecls.__bases__[0]

    def __enter__(self):
        return instance(self.rolecls, self.subj)

    def __exit__(self, exc_type, exc_value, traceback):
        #instance(self.oldcls, self.subj)
        #assert isinstance(self.subj, self.rolecls)
        self.role.revoke(self.subj)


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

    >>> cap.cache()
    {('a',): 'A', ('b',): 'B'}

    Clear the cache:
    
    >>> cap.clear()
    >>> cap.cache()
    {}

    Due to the caching, we can not take key-value arguments:

    >>> cap(s='a')     # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    TypeError: wrapper() got an unexpected keyword argument 's'
    """
    func._cache = {}

    def wrapper(*args):
        cache = func._cache
        try:
            return cache[args]
        except KeyError:
            result = func(*args)
            cache[args] = result
            return result

    def cache():
        return func._cache
    wrapper.cache = cache
    def clear():
        func._cache.clear()
    wrapper.clear = clear
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

    Caching

    One more thing: role classes are cached. This means that if I want to
    assign a role to a different instance, the same role class is applied:

    >>> person = Person('Joe')
    >>> someone = Person('Jane')
    >>> Biker(someone).__class__ is Biker(person).__class__
    True

    Instant application of roles

    The default behaviour you do not want roles to be applied to the object directly,
    but create shallow copies of an object with roles applied, you can use the
    clone function.

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
        rolecls = self.newclass(cls, rolebases)
        return method(rolecls, subj)


    __call__ = assign


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
            self.lookup.clear()


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
                raise NoRoleException('No role found for %s' % cls)
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
    NoRoleException: No role found for <class 'roles.X'>

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
            raise NotARoleException('could not apply @assignto() to class %s: not a role' % (rolecls,))
        return toprolecls


    def wrapper(rolecls):
        toprolecls = toprole(rolecls)

        if not isinstance(toprolecls, RoleFactoryType):
            # Replace class type by extended factory type
            toprolecls.__class__ = RoleFactoryType

        toprolecls.register(cls, rolecls, rolecls is toprolecls)

        return rolecls

    return wrapper

class NotARoleException(Exception):
    pass


class NoRoleException(Exception):
    pass


def psyco_optimize():
    """
    Optimize roles module with Psyco. ImportError is raised if Psyco
    is not available.

    >>> try:
    ...     psyco_optimize()
    ... except ImportError:
    ...     pass # No psyco
    """
    import psyco

    # Bind some methods to psyco
    psyco.bind(RoleType.assign)
    psyco.bind(RoleType.revoke)
    # decorated: provide original function for optimization
    psyco.bind(RoleType.newclass.wrapped_func)

    psyco.bind(RoleFactoryType.__call__)
    # decorated: provide original function for optimization
    psyco.bind(RoleFactoryType.lookup.wrapped_func)

    #psyco.bind(cached)
    #psyco.bind(assignto)


# vim:sw=4:et:ai
