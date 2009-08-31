"""
Pythonic implementation of the DCI (Data Context Interaction) pattern
(http://www.artima.com/articles/dci_vision.html).

The difference with mixins is that this role is applied only to the subject
instance, not to the subject class (alas, a new class is constructed).

Roles can be applied and revoked. Multiple roles can be applied to an instance.
Revocation can happen in any particular order.

As a basic example, consider some domain class:

>>> from roles import RoleType
>>> class DomainClass(object):
...     def __init__(self, a=3):
...         self.a = a
>>> instance = DomainClass()

The instance should participate in a collaboration in which it fulfills a
particular role:

>>> class MyRole(object):
...     __metaclass__ = RoleType
...     def rolefunc(self):
...          return self.a

>>> inrole = MyRole(instance)
>>> inrole       # doctest: +ELLIPSIS
<__main__.DomainClass+MyRole object at 0x...>
>>> isinstance(inrole, DomainClass)
True

Now the inrole instance can be invoked with the rolefunc() method as if
it was the DomainClass' one:

>>> inrole.rolefunc()
3
"""

from distutils.core import setup

VERSION = '0.1.0'

setup(
    name='roles',
    version=VERSION,
    description='Small implementation of Roles',
    long_description=__doc__,
    author='Arjan Molenaar',
    author_email='gaphor@gmail.com',
    url='http://github.org/amolenaar/roles',
    license="BSD License",
    py_modules = ['roles'],
    keywords="role DCI",
    platforms=["All"],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities'],
    zip_safe=False)

#vim:sw=4:et:ai
