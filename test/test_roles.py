from typing import Union

import pytest

from roles import RoleType


class A:
    b: int

    def a(self):
        pass


class B(A):
    def b(self):
        pass


class C(B):
    def c(self):
        pass


class R(metaclass=RoleType):
    pass


class U(R):
    """clashes with class A."""

    def b(self):
        pass


def test_application():
    a = A()
    b = A()

    assert R(a).__class__ is R(b).__class__  # type: ignore[call-arg]


def test_application_classes():
    """This is basically what happens:"""

    a = A()
    b = A()

    R(a)  # type: ignore[call-arg]
    cls1 = a.__class__
    R.revoke(a)

    R(b)  # type: ignore[call-arg]
    cls2 = b.__class__
    R.revoke(b)

    assert id(cls1) == id(cls2)
    assert cls1 is cls2, (cls1, cls2)


def test_played_by_before():
    a = A()
    with R.played_by(a):
        pass

    assert a.__class__ is A, (a.__class__, A)


def test_played_by_already_assigned():
    a = A()
    R(a)  # type: ignore[call-arg]
    with R.played_by(a):
        pass

    assert isinstance(a, R)


def test_played_by_as():
    a = A()
    b = A()
    a_in_role: Union[A, R]
    with R.played_by(a) as a_in_role:
        cls1 = a_in_role.__class__  # type: ignore[attr-defined]

    b_in_role: Union[B, R]
    with R.played_by(b) as b_in_role:  # type: ignore[assignment]
        cls2 = b_in_role.__class__  # type: ignore[attr-defined]

    assert cls1 is cls2, (cls1, cls2)


def test_played_by():
    a = A()
    with R.played_by(a):
        cls1 = a.__class__
    b = A()
    with R.played_by(b):
        cls2 = b.__class__
    assert a.__class__ is b.__class__
    assert cls1 is cls2, (cls1, cls2)


def test_played_by_nested():
    a = A()
    with R.played_by(a):
        b = A()
        with R.played_by(b):
            assert a.__class__ is b.__class__, (a.__class__, b.__class__)
        assert a.__class__ is not b.__class__, (a.__class__, b.__class__)
    assert a.__class__ is b.__class__, (a.__class__, b.__class__)


def test_overrides():
    """Test if TypeError is raised when field clashes exist."""

    c = C()
    with R.played_by(c):
        pass  # okay

    with pytest.raises(TypeError) as exc_info:
        with U.played_by(c):
            pass  # okay
    assert exc_info.value.args[0] == "Can not apply role when overriding methods: b"


def test_instance_overrides():
    """Test if TypeError is raised when field clashes exist."""

    a = A()
    with U.played_by(a):
        pass  # okay

    a.b = 3
    with pytest.raises(TypeError) as exc_info:
        with U.played_by(a):
            pass  # okay
    assert exc_info.value.args[0] == "Can not apply role when overriding methods: b"
