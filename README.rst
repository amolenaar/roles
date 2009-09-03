Roles
=====

Library for Role based development.

Pythonic implementation of the DCI (Data Context Interaction) pattern
(http://www.artima.com/articles/dci_vision.html).

The difference with mixins is that this role is applied only to the subject
instance, not to the subject class (alas, a new class is constructed).

Roles can be assigned and revoked. Multiple roles can be applied to an
instance. Revocation can happen in any particular order.

As a basic example, consider a domain class:

>>> class Person(object):
...     def __init__(self, name):
...         self.name = name
>>> person = Person("John")

The instance should participate in a collaboration in which it fulfills a
particular role:

>>> from roles import RoleType
>>> class Carpenter(object):
...     __metaclass__ = RoleType
...     def chop(self):
...          return "chop, chop"

Assign the role to the person:

>>> Carpenter(person)    # doctest: +ELLIPSIS
<Person+Carpenter object at 0x...>
>>> person					# doctest: +ELLIPSIS
<Person+Carpenter object at 0x...>

The person is still a Person:

>>> isinstance(person, Person)
True

... and can do carpenter things:

>>> person.chop()
'chop, chop'

See ``roles.py`` for more examples.

Factories
=========

In most cases instances will require specific implementations of a certain role.
This can be done by decorating the specific role implementations with the
``assignto()`` decorator.

>>> from roles import assignto
>>> @assignto(Person)
... class Biker(object):
...     __metaclass__ = RoleType
...     def bike(self):
...         return 'cycle, cycle'

>>> Biker(person)				# doctest: +ELLIPSIS
<Person+Carpenter+Biker object at 0x...>

Assigning to a different class instance doesn't work:

>>> class Cat(object):
...     pass
>>> Biker(Cat())				# doctest: +ELLIPSIS
Traceback (most recent call last):
  ...
NoRoleException: No role found for <class 'Cat'>


Releases
========

Releases can be found on:

  http://pypi.python.org/pypi/roles


Change Log
----------

0.3.0
-----

- Module works for Python 2.6 as well as Python 3.x. Doctests still run under 2.6.

Note that conversion of doctests is trivial with::

  $ 2to3 -d -w roles.py

0.2.0
-----

- Added psyco_optimize() for optimizing code with psyco.

0.1.0
-----

- Initial release: roles.py

