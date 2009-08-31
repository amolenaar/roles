"""
Test performance between roles and zope3 implementations
"""

from timeit import timeit

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

setup_role2 = \
"""
from role2 import Trait, addrole

class Role(object):
    def func(self): pass

class T(Trait):
    pass

t = T()
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

#print 'Construction of object		', timeit('a=A()', setup=setup_role)
#print 'Construction of trait object	', timeit('t=T()', setup=setup_role2)
print 'Construction of roles			', timeit('a=A();Role(a).func()', setup=setup_role)
print 'Construction of roles from factory	', timeit('a=A();Role(a).func()', setup=setup_rolefactory)
#print 'Construction of traits		', timeit('t=T();addrole(Role, t);t.func()', setup=setup_role2)
print 'Construction of zope adapters		', timeit('a=A();b=Iface(a);b.func()', setup=setup_zope)

## TODO: compare performance to zope.interface and zope.component

import cProfile
import pstats

from role import RoleType

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

