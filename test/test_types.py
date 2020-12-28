from typing import Dict

import pytest

from roles import RoleType


class SimpleRole(metaclass=RoleType):
    __slots__ = ()

    def inrole(self):
        return "in role"


def test_class():
    class Cls:
        pass

    c = Cls()
    SimpleRole(c)  # type: ignore[call-arg]

    assert c.inrole()  # type: ignore[attr-defined]


def test_class_with_args():
    class Cls:
        def __init__(self, a, b):
            pass

    c = Cls(1, 2)
    SimpleRole(c)  # type: ignore[call-arg]

    assert c.inrole()  # type: ignore[attr-defined]


def test_class_with_slots():
    class Cls:
        __slots__ = ("a", "b")

        def __init__(self):
            pass

    c = Cls()
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(c)  # type: ignore[call-arg]
    assert (
        exc_info.value.args[0]
        == "__class__ assignment: 'Cls+SimpleRole' object layout differs from 'Cls'"
    )


def test_dict():
    d: Dict[int, int] = dict()
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(d)  # type: ignore[call-arg]
    assert (
        exc_info.value.args[0]
        == "__class__ assignment only supported for heap types or ModuleType subclasses"
    )


def test_dict_subclass():
    class Dict(dict):
        pass

    d = Dict()
    d["a"] = 3
    SimpleRole(d)  # type: ignore[call-arg]
    assert "Dict+SimpleRole" == d.__class__.__name__
    assert 3 == d["a"]

    assert d.inrole()  # type: ignore[attr-defined]


def test_list():
    d = ["a", "b"]
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(d)  # type: ignore[call-arg]
    assert (
        exc_info.value.args[0]
        == "__class__ assignment only supported for heap types or ModuleType subclasses"
    )


def test_list_subclass():
    class List(list):
        pass

    d = List(["a", "b"])
    SimpleRole(d)  # type: ignore[call-arg]
    assert "List+SimpleRole" == d.__class__.__name__
    assert "a" == d[0]
    assert d.inrole()  # type: ignore[attr-defined]


def test_tuple():
    d = ("a", "b")
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(d)  # type: ignore[call-arg]
    assert (
        exc_info.value.args[0]
        == "__class__ assignment only supported for heap types or ModuleType subclasses"
    )


def test_tuple_subclass():
    class Tuple(tuple):
        pass

    d = Tuple(["a", "b"])
    SimpleRole(d)  # type: ignore[call-arg]
    assert "Tuple+SimpleRole" == d.__class__.__name__
    assert "a" == d[0]
    assert d.inrole()  # type: ignore[attr-defined]


def test_userdict():
    import sys

    if sys.version_info >= (3, 0, 0):
        return

    from UserDict import UserDict

    d = UserDict()
    with pytest.raises(TypeError) as exc_info:
        SimpleRole(d)  # type: ignore[call-arg]
    assert str(exc_info) == "class UserDict has no attribute '__mro__'"


def test_namedtuple():
    """Can't assign roles to namedtuple's."""
    from collections import namedtuple

    Point = namedtuple("Point", "x y")
    p = Point(1, 2)

    class Vector(metaclass=RoleType):
        pass

    with pytest.raises(TypeError) as exc_info:
        Vector(p)  # type: ignore[call-arg]
    assert (
        exc_info.value.args[0]
        == "__class__ assignment: 'Point+Vector' object layout differs from 'Point'"
    )
