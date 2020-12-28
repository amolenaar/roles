# Roles

Library for Role based development.

Pythonic implementation of the DCI (Data Context Interaction) pattern
(http://www.artima.com/articles/dci_vision.html).

The big difference with mixins is that this role is applied only to the subject
instance, not to the subject class (alas, a new class is constructed).

Roles can be assigned and revoked. Multiple roles can be applied to an
instance. Revocation can happen in any particular order.

Homepage: http://github.com/amolenaar/roles

Releases: http://pypi.python.org/pypi/roles


## Using Roles

As a basic example, consider a domain class:

```python
>>> class Person:
...     def __init__(self, name):
...         self.name = name
>>> person = Person("John")
```

The instance should participate in a collaboration in which it fulfills a
particular role:

```python
>>> from roles import RoleType
>>> class Carpenter(metaclass=RoleType):
...     def chop(self):
...          return "chop, chop"

```
Assign the role to the person:

```python
>>> Carpenter(person)				# doctest: +ELLIPSIS
<__main__.Person+Carpenter object at 0x...>
>>> person					# doctest: +ELLIPSIS
<__main__.Person+Carpenter object at 0x...>

```

The person is still a Person:

```python
>>> isinstance(person, Person)
True

```
... and can do carpenter things:

```python
>>> person.chop()
'chop, chop'

```

See [`roles.py`](http://github.com/amolenaar/roles/blob/master/roles.py) for more examples.

## Context

Roles make a lot of sense when used in a context. A classic example is the
money transfer example. Here two accounts are used and an amount of money is
transfered from one account to the other. So, one account playes the role of
source account and the other plays the role of target account.

An example can be found in [`example.py`](http://github.com/amolenaar/roles/blob/master/example.py).
