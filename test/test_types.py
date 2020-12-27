import pytest

import unittest
from roles import RoleType


class SimpleRole(metaclass=RoleType):
    __slots__ = ()

    def inrole(self):
        return "in role"


def test_class():
    class Cls:
        pass

    c = Cls()
    SimpleRole(c)
    c.inrole()

def test_class_with_args():
    class Cls:
        def __init__(self, a, b):
            pass

    c = Cls(1, 2)
    SimpleRole(c)
    c.inrole()

def test_class_with_slots():
    class Cls:
        __slots__ = ('a', 'b')

        def __init__(self):
            pass

    c = Cls()
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(c)
    assert exc_info.value.args[0] == "__class__ assignment: 'Cls+SimpleRole' object layout differs from 'Cls'"

def test_dict():
    d = dict()
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(d)
    assert exc_info.value.args[0] == "__class__ assignment only supported for heap types or ModuleType subclasses"

def test_dict_subclass():
    class Dict(dict):
        pass
    d = Dict()
    d['a'] = 3
    SimpleRole(d)
    assert 'Dict+SimpleRole'== d.__class__.__name__
    assert 3 == d['a']
    d.inrole()

def test_list():
    d = ['a', 'b']
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(d)
    assert exc_info.value.args[0] == "__class__ assignment only supported for heap types or ModuleType subclasses"


def test_list_subclass():
    class List(list):
        pass
    d = List(['a', 'b'])
    SimpleRole(d)
    assert 'List+SimpleRole' == d.__class__.__name__
    assert 'a' == d[0]
    d.inrole()

def test_tuple():
    d = ('a', 'b')
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(d)
    assert exc_info.value.args[0] == "__class__ assignment only supported for heap types or ModuleType subclasses"

def test_tuple_subclass():
    class Tuple(tuple):
        pass
    d = Tuple(['a', 'b'])
    SimpleRole(d)
    assert 'Tuple+SimpleRole' == d.__class__.__name__
    assert 'a' == d[0]
    d.inrole()

def test_userdict():
    import sys
    if sys.version_info >= (3, 0, 0):
        return

    from UserDict import UserDict
    d = UserDict()
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(d)
    assert str(exc_info) == "class UserDict has no attribute '__mro__'"

def test_namedtuple():
    """
    Can't assign roles to namedtuple's.
    """
    from collections import namedtuple
    import math

    Point = namedtuple('Point', 'x y')
    p = Point(1, 2)

    class Vector(metaclass=RoleType):
        pass

    with pytest.raises(TypeError) as exc_info:
        Vector(p)
    assert exc_info.value.args[0] == "__class__ assignment: 'Point+Vector' object layout differs from 'Point'"
