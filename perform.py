"""
Test performance between roles and zope3 implementations
"""

from timeit import timeit

import roles


setup_role = \
"""
from roles import RoleType

class A(object):
    pass

class Role(object):
    __metaclass__ = RoleType
    def func(self): pass

a = A()
"""

setup_rolefactory = \
"""
from roles import RoleType, assignto

class A(object):
    pass

class Role(object):
    __metaclass__ = RoleType
    def func(self): pass

@assignto(A)
class Subrole(Role):
    pass

a = A()
"""


setup_zope = \
"""
from zope import interface, component

class A(object):
    pass

class Iface(interface.Interface):
    pass

class Adapter(object):
    interface.implements(Iface)
    component.adapts(A)
    def __init__(self, ctx): self.ctx = ctx
    def func(self): pass
component.provideAdapter(Adapter)
"""

print 'Construction of object				%.3fs' % timeit('a=A()', setup=setup_role)
print 'Construction of roles				%.3fs' % timeit('a=A();Role(a).func()', setup=setup_role)

reload(roles)
try:
    roles.psyco_optimize()
except ImportError:
    pass
else:
    print 'Construction of roles (psyco)			%.3fs' % timeit('a=A();Role(a).func()', setup=setup_role)

reload(roles)
print 'Construction of roles from factory		%.3fs' % timeit('a=A();Role(a).func()', setup=setup_rolefactory)

reload(roles)
try:
    roles.psyco_optimize()
except ImportError:
    pass
else:
    print 'Construction of roles from factory (psyco)	%.3fs' % timeit('a=A();Role(a).func()', setup=setup_rolefactory)

print 'Construction of zope adapters			%.3fs' % timeit('a=A();b=Iface(a);b.func()', setup=setup_zope)


def profile():
    import cProfile
    import pstats

    from roles import RoleType

    class A(object):
        def func(self): pass

    class Role(object):
        __metaclass__ = RoleType
        def func(self): pass

    a = A()

    #cProfile.run('timeit("Role(a)", setup=setup)', 'profile.prof')
    cProfile.run('for x in xrange(10000): Role(a)', 'profile.prof')
    p = pstats.Stats('profile.prof')
    p.strip_dirs().sort_stats('time').print_stats(40)

