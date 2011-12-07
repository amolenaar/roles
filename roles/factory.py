"""
This is a not-so-DCI extension that allows multiple role implementations to be
dispatched. This means that it allows you to have role implementations specific
for certain object types. Counterside is that the code becomes a lot more
cryptic and not easier to reason about.

Author: Arjan Molenaar
"""

from __future__ import absolute_import

from .role import RoleType, cached, instance


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
            if rolecls:
                return rolecls
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
    <class 'roles.factory.RoleFactoryType'>

    >>> MyRole(A())           # doctest: +ELLIPSIS
    <roles.factory.A+MySubRole object at 0x...>

    This also works for subclasses of A:

    >>> class B(A): pass
    >>> class C(B): pass
    >>> c = C()
    >>> MyRole(c)             # doctest: +ELLIPSIS
    <roles.factory.C+MySubRole object at 0x...>

    >>> MyRole.revoke(c)      # doctest: +ELLIPSIS
    <roles.factory.C object at 0x...>

    All other class fall back to the default role:

    >>> class D(object): pass
    >>> d = D()
    >>> MyRole(d)             # doctest: +ELLIPSIS
    <roles.factory.D+MyRole object at 0x...>

    You can also apply the decorator to the root role directly:

    >>> @assignto(A)
    ... class AnyRole(object):
    ...     __metaclass__ = RoleType

    >>> a = A()
    >>> AnyRole(a)            # doctest: +ELLIPSIS
    <roles.factory.A+AnyRole object at 0x...>

    >>> AnyRole.revoke(a)     # doctest: +ELLIPSIS
    <roles.factory.A object at 0x...>

    Now some other class should not be assigned this role:

    >>> class X(object): pass
    >>> AnyRole(X())          # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    NoRoleError: No role found for <class 'roles.factory.X'>

    And this still works:

    >>> MyRole(A())           # doctest: +ELLIPSIS
    <roles.factory.A+MySubRole object at 0x...>

    The usage of ``@assignto()`` is resticted to role types:

    >>> @assignto(A)
    ... class NotARole(object):
    ...     pass
    Traceback (most recent call last):
      ...
    NotARoleError: Could not apply @assignto() to class <class 'roles.factory.NotARole'>: not a role

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
            raise NotARoleError('Could not apply @assignto() to class %s: not a role' % (rolecls,))
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


# vim:sw=4:et:ai
