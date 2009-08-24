"""
Pythonic implementation of the DCI (Data Context Interaction) pattern
(http://www.artima.com/articles/dci_vision.html).

The difference with mixins is that this role is applied only to the subject
instance, not to the subject class (alas, a new class is constructed).

Author: Arjan Molenaar

Based on the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
Money transfer example by David Byers and Serge Beaumont.
"""

from operator import attrgetter


class RoleType(type):
    """
    ``RoleType`` is a metaclass that provides role support to classes. The
    initialization process has been altered to provide addition and (in the
    future) removal of roles.

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

    >>> carpenter = Carpenter.apply(person)
    >>> carpenter.__roles__
    (<class '__main__.Carpenter'>,)

    Or by calling the role on the subject:

    >>> carpenter = Carpenter(person)
    >>> carpenter.__roles__
    (<class '__main__.Carpenter'>,)

    The persons methods can be invoked:

    >>> carpenter.am()
    Joe is

    As well as the role's methods:

    >>> carpenter.chop()
    Joe chops

    Objects can contain multiple roles:

    >>> biking_carpenter = Biker.apply(carpenter)
    >>> biking_carpenter.__roles__
    (<class '__main__.Biker'>, <class '__main__.Carpenter'>)
    
    Note that a new class is assigned, with the roles applied (roles first):

    >>> biking_carpenter.__class__
    <class '__main__.Person+Carpenter+Biker'>
    >>> biking_carpenter.__class__.__bases__
    (<class '__main__.Biker'>, <class '__main__.Carpenter'>, <class '__main__.Person'>)

    Roles can be revoked:

    >>> biker = Carpenter.revoke(biking_carpenter)
    >>> biker.__roles__
    (<class '__main__.Biker'>,)
    >>> biker.__class__.__bases__
    (<class '__main__.Biker'>, <class '__main__.Person'>)

    Caching
    -------

    One more thing: role classes are cached. This means that if I want to
    apply a role to a different instance, the same role class is applied:

    >>> someone = Person('Jane')
    >>> Biker(someone).__class__ is Biker(person).__class__
    True

    Instant application of roles
    ----------------------------

    If you do not want "stub" objects for each role applied (this will make
    roles be applied in a context), you can override the ``dup()`` method and
    for example change the original object instance class to get the role
    applied:

    >>> def nodup(role, rolecls, subj):
    ...     subj.__class__ = rolecls
    ...     return subj
    >>> orig_dup = RoleType.dup
    >>> RoleType.dup = nodup

    Now no new class instance is created, but the roles are applied directly to
    the subject instance:

    >>> person.__class__
    <class '__main__.Person'>
    >>> Biker(person)   # doctest: +ELLIPSIS
    <__main__.Person+Biker object at 0x...>
    >>> person.__class__
    <class '__main__.Person+Biker'>
    >>> person.bike()
    Joe bikes

    (revert to original behaviour:)
    >>> RoleType.dup = orig_dup
    """

    _role_cache = {}


    def dup(role, rolecls, subj):
        """
        Do some duplication for the role.
        """
        from copy import copy
        newsubj = copy(subj)
        newsubj.__dict__ = subj.__dict__
        newsubj.__class__ = rolecls
        return newsubj


    def newclass(role, cls, rolebases):
        """
        Create a new role class and cache it
        """
        role_cache = RoleType._role_cache
        try:
            rolecls = role_cache[rolebases]
        except KeyError:
            # Role class not yet defined, define a new class
            namegetter = attrgetter('__name__')
            names = map(namegetter, rolebases)
            names.reverse()
            rolename = "+".join(names)
            #rolename = cls.__name__ + "+" + role.__name__
            rolecls = type(rolename, rolebases, {})
            role_cache[rolebases] = rolecls
        return rolecls


    def apply(role, subj):
        """
        Call is invoked when new instances of a class (role) are requested.
        """
        cls = type(subj)
        try:
            if role in cls.__roles__:
                return subj
        except AttributeError:
            # __roles__ is not defined, provide dummy (no roles)
            rolebases = (role, cls)
        else:
            # Create a sibling class
            rolebases = (role,) + cls.__bases__

        rolecls = role.newclass(cls, rolebases)
        try:
            roles = (role,) + cls.__roles__
        except AttributeError:
            roles = (role,)
        rolecls.__roles__ = roles

        return role.dup(rolecls, subj)


    def revoke(role, subj):
        """
        Retract the role from subj. Returning a new subject (or the same one,
        if ``dup()`` has been overwritten).
        """
        cls = type(subj)
        if role not in cls.__roles__:
            return subj
        rolebases = tuple(b for b in cls.__bases__ if b is not role)

        rolecls = role.newclass(cls, rolebases)
        roles = tuple(r for r in cls.__roles__ if r is not role)
        rolecls.__roles__ = roles
        return role.dup(rolecls, subj)


    def __call__(role, subj):
        return role.apply(subj)


if __name__ == '__main__':

    import doctest
    print 'Running doctests...'
    doctest.testmod()

    print

    class MoneySource(object):
        __metaclass__ = RoleType

        def transfer_to(self, ctx, amount):
            if self.balance >= amount:
                self.withdraw(amount)
                ctx.sink.receive(ctx, amount)


    class MoneySink(object):
        __metaclass__ = RoleType

        def receive(self, ctx, amount):
            self.deposit(amount)


    class Account(object):

        def __init__(self, amount):
            print "Creating a new account with balance of " + str(amount)
            self.balance = amount
            super(Account, self).__init__()

        def withdraw(self, amount):
            print "Withdraw " + str(amount) + " from " + str(self)
            self.balance -= amount

        def deposit(self, amount):
            print "Deposit " + str(amount) + " in " + str(self)
            self.balance += amount


    class Context(object):
        """Holds Context state."""
        pass


    class TransferMoney(object):
        def __init__(self, source, sink):
            self.context = Context()
            print 'creating source'
            self.context.source = MoneySource(source)
            print 'creating sink'
            self.context.sink = MoneySink(MoneySource(sink))

        def __call__(self, amount):
            self.context.source.transfer_to(self.context, amount)


    src = Account(1000)
    dst = Account(0)

    t = TransferMoney(src, dst)
    t(100)

    print src, src.balance
    assert src.balance == 900
    print dst, dst.balance
    assert dst.balance == 100
    
    print "We can still access the original attributes", t.context.sink.balance
    assert t.context.sink.balance == 100
    print "Is it still an Account?", isinstance(t.context.sink, Account)
    assert isinstance(t.context.sink, Account)
    print "Object equality?", dst == t.context.sink


# vim: sw=4:et:ai
