

def rolecontext(*types):
    """
    Define a function as a context for a (set of) role(s).
    
    When the function is called all objects will have the specified role
    applied for certain.

    >>> from roles import RoleType
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

    If the person already has the biker role, the context is left as is:

    >>> Biker(person)            # doctest: +ELLIPSIS
    <roles.context.Person+Biker object at 0x...>
    >>> bikerFunc(person)
    'bike, bike'
    >>> isinstance(person, Biker)
    True
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
