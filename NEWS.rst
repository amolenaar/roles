Change Log
==========

0.6.0
-----

- RoleType.played_by for easy use with `with` statement
- removed roles function and psyco optimizations.
- bug fixes and performance updates

0.5.0
-----

- Support for contexts (`with` statement).
- revoke on factories now works as expected.

0.4.0
-----

- Make the way a role is applied to an object pluggable. This means you can
  either apply the role to the original instance or create a clone, using the
  original instance dict.

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

