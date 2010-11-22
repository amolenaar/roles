Django DCI example
==================

The module account/tests.py contains an example of how the roles module can be
applied in Django. Since Django model classes have their own metaclass, roles
that are applied to model instances should inherit from
``roles.django.ModelRoleType``.

Cateats
-------

<modelinstance>.save() is using the class name to look up the table. This does
not work well with roles, since the class name is changed (role names are
applied). Quick solution is not to perform save() on instances playing some
role.

