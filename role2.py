"""
Another approach to roles implementing them.
"""


def addrole(role_class, subject):
    """
    >>> class A(object):
    ...     def a(self): print 'a'
    >>> class R(object):
    ...     def r(self): print 'r'
    >>> class T(object):
    ...     def t(self): print 't'
    >>> a = A()
    >>> addrole(R, a)
    >>> a.__roles__
    [<class '__main__.R'>]
    >>> addrole(T, a)
    >>> a.__roles__
    [<class '__main__.T'>, <class '__main__.R'>]

    Roles will only be added once:

    >>> addrole(R, a)
    >>> a.__roles__
    [<class '__main__.T'>, <class '__main__.R'>]
    """
    try:
        roles = subject.__roles__
    except AttributeError:
        # No __roles__
        roles = subject.__roles__ = []
    if not role_class in roles:
        roles.insert(0, role_class)


def delrole(role_class, subject):
    """
    Remove an existing role from a class instance.
    >>> class A(object):
    ...     def a(self): print 'a'
    >>> class R(object):
    ...     def r(self): print 'r'
    >>> class T(object):
    ...     def t(self): print 't'
    >>> a = A()
    >>> addrole(R, a)
    >>> addrole(T, a)
    >>> delrole(R, a)
    >>> a.__roles__
    [<class '__main__.T'>]
    >>> delrole(R, a)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    ValueError: No role R defined on subject

    """
    try:
        subject.__dict__['__roles__'].remove(role_class)
    except ValueError:
        raise ValueError('No role ' + role_class.__name__ + ' defined on subject')


def role_wrapper(self, func):
    def wrapper_role_func(*args, **kwargs):
        return func(self, *args, **kwargs)
    wrapper_role_func.__name__ = 'role ' + func.__name__ + ' bound as role to ' + str(self)
    return wrapper_role_func


class Trait(object):
    """
    This small trait class can be used as base class or mixin class for
    classes that should support roles. By overriding ``object.__getattribute__``
    this class checks for 
    >>> class A(Trait):
    ...     def a(self): print 'a'
    >>> class R(object):
    ...     def r(self): print 'r'
    >>> a = A()
    >>> a.a                        # doctest: +ELLIPSIS
    <bound method A.a of <__main__.A object at 0x...>>

    Now add a role. Old behaviour should still work:

    >>> addrole(R, a)
    >>> a.a                        # doctest: +ELLIPSIS
    <bound method A.a of <__main__.A object at 0x...>>

    Can fetch role method:

    >>> a.r                        # doctest: +ELLIPSIS
    <function role r at 0x...>

    And it can be executed as well:

    >>> a.r()                      # doctest: +ELLIPSIS
    r
    """

    def __getattr__(self, key):
        """
        This approach to roles prefers the default object behaviour, so that's
        prevailed. If an object member (method or attribute) is not found the
        default way, the roles are checked.
        """
        try:
            return super(Trait, self).__getattr__(self, key)
        except AttributeError, e:
            # check roles:
            try:
                for r in self.__dict__['__roles__']:
                    try:
                        m = getattr(r, key)
                    except AttributeError:
                        pass
                    else:
                        return role_wrapper(self, m.im_func)
                    raise e
            except KeyError:
                raise e


if __name__ == '__main__':
    import doctest, timeit
    doctest.testmod()
    setup1 = """class A(object):
    def x(self): pass
a=A()"""
    setup2 = """import trait
class A(trait.Trait):
    def x(self): pass
a=A()"""
    stmt = "a.x"
    print '* Timing', '*' * 69
    print ' no trait:  ', timeit.timeit(stmt, setup=setup1), 'sec'
    print ' with trait:', timeit.timeit(stmt, setup=setup2), 'sec'
    print '*' * 78


# vim:sw=4:et:ai
