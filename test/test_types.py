

import unittest
from roles import RoleType, clone


class SimpleRole(object):
    __metaclass__ = RoleType
    def inrole(self):
        return "in role"


class TypesTest(unittest.TestCase):
    """
    Test application of roles on types.
    """

    def test_class(self):
        class Cls(object):
            pass

        c = Cls()
        SimpleRole(c)
        c.inrole()

    def test_class_with_args(self):
        class Cls(object):
            def __init__(self, a, b): pass

        c = Cls(1, 2)
        SimpleRole(c)
        c.inrole()


    def test_dict(self):
        d = dict()
        try:
            SimpleRole(d)
        except TypeError, e:
            self.assertEquals("__class__ assignment: only for heap types", str(e))
        else:
            assert False, "should not be reached"

    def test_dict_subclass(self):
        class Dict(dict): pass
        d = Dict()
        d['a'] = 3
        SimpleRole(d)
        self.assertEquals('Dict+SimpleRole', d.__class__.__name__)
        self.assertEquals(3, d['a'])
        d.inrole()


    def test_list(self):
        d = ['a', 'b']
        try:
            SimpleRole(d)
        except TypeError, e:
            self.assertEquals("__class__ assignment: only for heap types", str(e))
        else:
            assert False, "should not be reached"


    def test_list_subclass(self):
        class List(list): pass
        d = List(['a', 'b'])
        SimpleRole(d)
        self.assertEquals('List+SimpleRole', d.__class__.__name__)
        self.assertEquals('a', d[0])
        d.inrole()


    def test_tuple(self):
        d = ('a', 'b')
        try:
            SimpleRole(d)
        except TypeError, e:
            self.assertEquals("__class__ assignment: only for heap types", str(e))
        else:
            assert False, "should not be reached"


    def test_tuple_subclass(self):
        class Tuple(tuple): pass
        d = Tuple(['a', 'b'])
        SimpleRole(d)
        self.assertEquals('Tuple+SimpleRole', d.__class__.__name__)
        self.assertEquals('a', d[0])
        d.inrole()


    def test_userdict(self):
        import sys
        if sys.version_info >= (3,0,0):
            return

        from UserDict import UserDict
        d = UserDict()
        try:
            SimpleRole(d)
        except AttributeError, e:
            self.assertEquals("class UserDict has no attribute '__mro__'", str(e))
        else:
            assert False, "should not be reached"


    def test_namedtuple(self):
        """
        Can't assign roles to namedtuple's.
        """
        from collections import namedtuple
        import math

        Point = namedtuple('Point', 'x y')
        p = Point(1,2)

        class Vector(object):
            __metaclass__ = RoleType
            #def m(self):
            #    "Manhattan style distance calculation"
            #    return p.x + p.y
            #def distance(self):
            #    return math.sqrt(p.x * p.x + p.y * p.y)

        try:
            Vector(p)
        except TypeError, e:
            self.assertEquals("__class__ assignment: 'Point' object layout differs from 'Point+Vector'", str(e))
#        except AttributeError, e:
#            self.assertEquals("'Point' object has no attribute '__dict__'", str(e))
        else:
            assert False, "should not be reached"
        #assert p.manhattan() == 3


if __name__ == '__main__':
    unittest.main()

# vi: sw=4:et:ai
