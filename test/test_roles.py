import unittest
from roles import RoleType


class A(object):
    pass

class R(object):
    __metaclass__ = RoleType


class CachingTestCase(unittest.TestCase):

    def test_application(self):
        a = A()
        b = A()
        assert R(a).__class__ is R(b).__class__


    def test_application_classes(self):
        """
        This is basically what happens:
        """

        a = A()
        b = A()

        R(a)
        cls1 = a.__class__
        R.revoke(a)

        R(b)
        cls2 = b.__class__
        R.revoke(b)

        self.assertEquals(id(cls1), id(cls2))
        assert cls1 is cls2, (cls1, cls2)

    def test_played_by_before(self):
        a = A()
        with R.played_by(a):
            pass
        assert a.__class__ is A, (a.__class__, A)

    def test_played_by_already_assigned(self):
        a = A()
        R(a)
        with R.played_by(a):
            pass
        assert isinstance(a, R)

    def test_played_by_e(self):
        a = A()
        b = A()
        ctx = R.played_by(a)
        a_in_role = ctx.__enter__()
        cls1 = a_in_role.__class__

        ctx2 = R.played_by(b)
        b_in_role = ctx2.__enter__()
        cls2 = b_in_role.__class__

        assert cls1 is cls2, (cls1, cls2)

    def test_played_by(self):
        a = A()
        with R.played_by(a):
            cls1 = a.__class__
        b = A()
        with R.played_by(b):
            cls2 = b.__class__
        assert a.__class__ is b.__class__
        assert cls1 is cls2, (cls1, cls2)

    def test_played_by_nested(self):
        a = A()
        with R.played_by(a):
            b = A()
            with R.played_by(b):
                assert a.__class__ is b.__class__, (a.__class__, b.__class__)
            assert a.__class__ is not b.__class__, (a.__class__, b.__class__)
        assert a.__class__ is b.__class__, (a.__class__, b.__class__)


if __name__ == '__main__':
    unittest.main()

# vim:sw=4:et:ai
