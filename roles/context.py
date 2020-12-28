"""Context."""


import threading
from functools import wraps

__all__ = ["context", "in_context"]


class ManagedContext:
    def __init__(self, stack, ctx, bindings):
        self.stack = stack
        self.ctx = ctx
        self.bindings = bindings

    def __enter__(self):
        """Activate the context, bind roles to instances defined in the
        context."""
        ctx = self.ctx
        self.stack.append(ctx)
        for var, role in self.bindings.items():
            role.assign(getattr(ctx, var))
        return ctx

    def __exit__(self, exc_type, exc_value, traceback):
        ctx = self.stack.pop()
        assert ctx is self.ctx
        for var, role in self.bindings.items():
            role.revoke(getattr(ctx, var))


class CurrentContextManager(threading.local):
    """
    The default application wide context stack.

    Put a new context class on the context stack. This functionality should
    be called with the context class as first argument.

    >>> class SomeContext:
    ...     pass # define some methods, define some roles
    ...     def execute(self):
    ...         with context(self):
    ...             pass # do something

    Roles can be fetched from the context by calling ``context.name``.
    Just like that.

    You can provide additional bindings to be performed:

    >>> from roles.role import RoleType

    >>> class SomeRole(metaclass=RoleType):
    ...     pass

    >>> class SomeContext:
    ...     def __init__(self, data_object):
    ...         self.data_object = data_object
    ...     def execute(self):
    ...         with context(self, data_object=SomeRole):
    ...             pass # do something

    Those bindings are applied when the context is entered (in this case immediately).
    """

    def __init__(self):
        # Access dict directly, prevent __{gs}etattr__ from being called
        self.__dict__["__stack"] = []

    def __call__(self, ctxobj, **bindings):
        assert ctxobj, "Should provide a context object"
        return ManagedContext(self.__dict__["__stack"], ctxobj, bindings)

    @property
    def current_context(self):
        try:
            return self.__dict__["__stack"][-1]
        except IndexError:
            return None

    def __getattr__(self, key):
        return getattr(self.current_context, key)

    def __setattr__(self, key, val):
        return setattr(self.current_context, key, val)


context = CurrentContextManager()


def in_context(func):
    """Decorator for running methods in context.

    The context is the object (self).
    """

    @wraps(func)
    def in_context_wrapper(self, *args, **kwargs):
        with context(self):
            return func(self, *args, **kwargs)

    return in_context_wrapper
