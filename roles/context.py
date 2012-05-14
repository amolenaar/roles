"""
Context.
"""

from __future__ import absolute_import

from functools import wraps
import threading


__all__ = ['context', 'in_context']


class ManagedContext(object):

    def __init__(self, stack, ctx, bindings):
        self.stack = stack
        self.ctx = ctx
        self.bindings = bindings

    def __enter__(self):
        """
        Activate the context, bind roles to instances defined in the context.
        """
        ctx = self.ctx
        self.stack.append(self.ctx)
        for var, role in self.bindings.iteritems():
            role.assign(getattr(ctx, var))
        return ctx

    def __exit__(self, exc_type, exc_value, traceback):
        ctx = self.stack.pop()
        assert ctx is self.ctx
        for var, role in self.bindings.iteritems():
            role.revoke(getattr(ctx, var))


class CurrentContextManager(threading.local):

    def __init__(self):
        # Access dict directly, prevent __{gs}etattr__ from being called
        self.__dict__['__stack'] = []

    def __call__(self, ctxobj, **bindings):
        assert ctxobj, 'Should provide a context object'
        return ManagedContext(self.__dict__['__stack'], ctxobj, bindings)

    @property
    def current_context(self):
        return self.__dict__['__stack'][-1]

    def __getattr__(self, key):
        return getattr(self.current_context, key)

    def __setattr__(self, key, val):
        return setattr(self.current_context, key, val)


context = CurrentContextManager()
context.__dict__['__doc__'] = """
The default application wide context stack.

Put a new context class on the context stack. This functionality should
be called with the context class as first argument.

>>> class SomeContext(object):
...     pass # define some methods, define some roles
...     def execute(self):
...         with context(self):
...             pass # do something

Roles can be fetched from the context by calling ``context.name``.
Just like that.

You can provide additional bindings to be performed:

>>> from role import RoleType

>>> class SomeRole(object):
...     __metaclass__ = RoleType

>>> class SomeContext(object):
...     def __init__(self, data_object):
...         self.data_object = data_object
...     def execute(self):
...         with context(self, data_object=SomeRole):
...             pass # do something

Those bindings are applied when the context is entered (in this case immediately).
"""


def in_context(func):
    """
    Decorator for running methods in context. The context is the object (self).
    """
    @wraps(func)
    def in_context_wrapper(self, *args, **kwargs):
        with context(self):
            return func(self, *args, **kwargs)
    return in_context_wrapper


# vim:sw=4:et:ai
