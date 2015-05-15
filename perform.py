"""
Test performance between roles and zope3 implementations
"""

from timeit import timeit

import roles


setup_role = \
"""
from roles import RoleType

class A:
    pass

class Role(metaclass=RoleType):
    def func(self): pass

a = A()
"""

setup_rolefactory = \
"""
from roles import RoleType
from roles.factory import assignto

class A:
    pass

class Role(metaclass=RoleType):
    def func(self): pass

@assignto(A)
class Subrole(Role):
    pass

a = A()
"""


setup_zope = \
"""
from zope import interface, component

class A:
    pass

class Iface(interface.Interface):
    pass

class Adapter:
    interface.implements(Iface)
    component.adapts(A)
    def __init__(self, ctx): self.ctx = ctx
    def func(self): pass
component.provideAdapter(Adapter)
"""

print 'Construction of object				%2.3fs' % timeit('a=A()', setup=setup_role)
print 'Construction of roles				%2.3fs' % timeit('a=A();Role(a).func()', setup=setup_role)
print 'Construction of roles in context		%2.3fs' % timeit('a=A()\nwith Role.played_by(a): a.func()', setup=setup_role)

print 'Construction of roles from factory		%2.3fs' % timeit('a=A();Role(a).func()', setup=setup_rolefactory)
print 'Construction of roles from factory in context	%.3fs' % timeit('a=A()\nwith Role.played_by(a): a.func()', setup=setup_rolefactory)

print 'Construction of zope adapters			%.3fs' % timeit('a=A();b=Iface(a);b.func()', setup=setup_zope)


def profile():
    import cProfile
    import pstats

    from roles import RoleType

    class A:
        def func(self): pass

    class Role(metaclass=RoleType):
        def func(self): pass

    a = A()

    #cProfile.run('timeit("Role(a)", setup=setup)', 'profile.prof')
    cProfile.run('for x in xrange(10000): Role(a)', 'profile.prof')
    p = pstats.Stats('profile.prof')
    p.strip_dirs().sort_stats('time').print_stats(40)
 
