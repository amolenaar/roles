"""
Pythonic implementation of the DCI (Data Context Interaction) pattern
(http://www.artima.com/articles/dci_vision.html).

The difference with mixins is that this role is applied only to the subject
instance, not to the subject class (alas, a new class is constructed).

Roles can be applied and revoked. Multiple roles can be applied to an instance.
Revocation can happen in any particular order.

As a basic example, consider some domain class:

>>> class DomainClass(object):
...     def __init__(self, a=3):
...         self.a = a
>>> instance = DomainClass()

The instance should participate in a collaboration in which it fulfills a
particular role:

>>> class MyRole(object):
...     __metaclass__ = RoleType
...     def rolefunc(self):
...          return self.a

>>> inrole = MyRole(instance)
>>> inrole       # doctest: +ELLIPSIS
<__main__.DomainClass+MyRole object at 0x...>
>>> isinstance(inrole, DomainClass)
True

Now the inrole instance can be invoked with the rolefunc() method as if
it was the DomainClass' one:

>>> inrole.rolefunc()
3

Author: Arjan Molenaar

Based on the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
Money transfer example by David Byers and Serge Beaumont.
"""

from operator import attrgetter
from cache import cached


def shalowclone(obj):
    """
    Duplicate the instance, but share the state (__dict__) with the original
    instance.
    """
    from copy import copy
    newobj = copy(obj)
    newobj.__dict__ = obj.__dict__
    return newobj


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
    >>> person.__roles__    # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    AttributeError: 'Person' object has no attribute '__roles__'

    Roles can be added by calling the ``apply()`` method:

    >>> Carpenter.apply(person)    # doctest: +ELLIPSIS
    <__main__.Person+Carpenter object at 0x...>
    >>> person.__roles__
    (<class '__main__.Carpenter'>,)

    Or by calling the role on the subject:

    >>> Carpenter(person)  # doctest: +ELLIPSIS
    <__main__.Person+Carpenter object at 0x...>

    The persons methods can be invoked:

    >>> person.am()
    Joe is

    As well as the role's methods:

    >>> person.chop()
    Joe chops

    Objects can contain multiple roles:

    >>> Biker.apply(person)   # doctest: +ELLIPSIS
    <__main__.Person+Carpenter+Biker object at 0x...>
    >>> person.__roles__
    (<class '__main__.Biker'>, <class '__main__.Carpenter'>)
    
    Note that a new class is assigned, with the roles applied (roles first):

    >>> person.__class__
    <class '__main__.Person+Carpenter+Biker'>
    >>> person.__class__.__bases__
    (<class '__main__.Biker'>, <class '__main__.Carpenter'>, <class '__main__.Person'>)

    Roles can be revoked:

    >>> Carpenter.revoke(person)   # doctest: +ELLIPSIS
    <__main__.Person+Biker object at 0x...>
    >>> person.__roles__
    (<class '__main__.Biker'>,)
    >>> person.__class__.__bases__
    (<class '__main__.Biker'>, <class '__main__.Person'>)

    Caching
    -------

    One more thing: role classes are cached. This means that if I want to
    apply a role to a different instance, the same role class is applied:

    >>> person = Person('Joe')
    >>> someone = Person('Jane')
    >>> Biker(someone).__class__ is Biker(person).__class__
    True

    Instant application of roles
    ----------------------------

    If you do not want roles to be applied to the object directly,
    but create shalow copies of an object with roles applied, you can use the
    shalowclone function.

    This can be done by creating a custom role type like this, overriding the
    ``roll()`` method:

    >>> class CustomRoleType(RoleType):
    ...     def roll(role, rolecls, subj):
    ...         newsubj = shalowclone(subj)
    ...         newsubj.__class__ = rolecls
    ...         return newsubj

    >>> class Biker(object):
    ...     __metaclass__ = CustomRoleType
    ...     def bike(self): print self.name, 'bikes'

    Now no new class instance is created, but the roles are no longer applied to
    the subject instance directly.

    >>> person = Person('Joe')
    >>> person.__class__
    <class '__main__.Person'>
    >>> biker = Biker(person)
    >>> biker # doctest: +ELLIPSIS
    <__main__.Person+Biker object at 0x...>
    >>> person.__class__
    <class '__main__.Person'>
    >>> biker.bike()
    Joe bikes
    """


    def roll(role, rolecls, subj):
        """
        Apply the role class to the subject.
        Returns the subject
        """
        subj.__class__ = rolecls
        return subj


    @cached
    def newclass(self, cls, rolebases):
        """
        Create a new role class.
        """
        # Role class not yet defined, define a new class
        namegetter = attrgetter('__name__')
        names = map(namegetter, rolebases)
        names.reverse()
        rolename = "+".join(names)
        rolecls = type(rolename, rolebases, {
                '__module__': cls.__module__,
                '__doc__': cls.__doc__ })
        return rolecls


    def apply(self, subj):
        """
        Call is invoked when new instances of a class (role) are requested.
        """
        cls = type(subj)
        try:
            if self in cls.__roles__:
                return subj
        except AttributeError:
            # __roles__ is not defined, provide dummy (no roles)
            rolebases = (self, cls)
        else:
            # Create a sibling class
            rolebases = (self,) + cls.__bases__

        rolecls = self.newclass(cls, rolebases)
        try:
            roles = (self,) + cls.__roles__
        except AttributeError:
            roles = (self,)
        rolecls.__roles__ = roles

        return self.roll(rolecls, subj)


    def revoke(self, subj):
        """
        Retract the role from subj. Returning a new subject (or the same one,
        if ``roll()`` has been overwritten).
        """
        cls = type(subj)
        if self not in cls.__roles__:
            return subj
        rolebases = tuple(b for b in cls.__bases__ if b is not self)

        rolecls = self.newclass(cls, rolebases)
        roles = tuple(r for r in cls.__roles__ if r is not self)
        rolecls.__roles__ = roles
        return self.roll(rolecls, subj)


    __call__ = apply


class RoleFactoryType(RoleType):
    """
    RoleFactoryType is a special kind of RoleType: with the ``@role_for`` class
    decorator this class is applied to any RoleType instance.

    Now subroles are able to be automatically applied to specific instances.
    Thus, the Role class is acting as a factory for it's own types.

    Note that this metaclass is automatically applied the first time
    ``@role_for`` is used to decorate a role class.
    """


    def register(self, cls, rolecls):
        """
        Register a new roleclass for a specific class.
        """
        try:
            self._factory[cls] = rolecls
        except AttributeError:
            self._factory = {}
            self.register(cls, rolecls)
            self.lookup.clear()


    @cached
    def lookup(self, subj):
        """
        Find a specific Role type for a subject. The returned role class
        is a subclass of the factory role.
        """
        get = self._factory.get
        for t in type(subj).__mro__:
            rolecls = get(t)
            if rolecls: return rolecls
        else:
            return self


    def __call__(self, subj):
        return self.lookup(subj).apply(subj)


class role_for(object):
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

    >>> @role_for(A)
    ... class MySubRole(MyRole): pass 

    Note that the metaclass has changed to RoleFactoryType:

    >>> MyRole.__class__
    <class '__main__.RoleFactoryType'>

    >>> MyRole(A())            # doctest: +ELLIPSIS
    <__main__.A+MySubRole object at 0x...>

    This also works for subclasses of A:

    >>> class B(A): pass
    >>> class C(B): pass
    >>> MyRole(C())           # doctest: +ELLIPSIS
    <__main__.C+MySubRole object at 0x...>

    You can also apply the decorator to the root role directly:

    >>> @role_for(object)
    ... class AnyRole(object):
    ...     __metaclass__ = RoleType

    >>> AnyRole(A())  # doctest: +ELLIPSIS
    <__main__.A+AnyRole object at 0x...>
    """

    def __init__(self, cls):
        self.cls = cls


    def toprole(self, rolecls):
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
            raise NotARoleException('could not apply @role_for() to class %s: not a role' % (rolecls,))
        return toprolecls


    def __call__(self, rolecls):
        toprolecls = self.toprole(rolecls)

        if not isinstance(toprolecls, RoleFactoryType):
            # Replace class type by extended factory type
            toprolecls.__class__ = RoleFactoryType

        # Register factory class
        toprolecls.register(self.cls, rolecls)

        return rolecls


class NotARoleException(Exception):
    pass


if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim:sw=4:et:ai
