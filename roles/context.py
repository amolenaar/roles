
from functools import wraps, partial


class ctxman(object):

    def __init__(self, stack, ctx):
        self.stack = stack
        self.ctx = ctx

    def __enter__(self):
        self.stack.append(self.ctx)

    def __exit__(self, exc_type, exc_value, traceback):
        ctx = self.stack.pop()
        assert ctx is self.ctx


class CurrentContextManager(object):

    def __init__(self):
        self.__dict__['_stack'] = []
        
    def __call__(self, newctx):
        return ctxman(self._stack, newctx)

    @property
    def current_context(self):
        return self.__dict__['_stack'][-1]

    def __getattr__(self, key):
        return getattr(self.current_context, key)

    def __setattr__(self, key, val):
        return setattr(self.current_context, key, val)


context = CurrentContextManager()
context.__dict__['__doc__'] = """
The default application wide context stack.

Put a new context class on the context stack. This functionality should be called
with the context class as first argument.

>>> class SomeContext(object):
...     pass # define some methods, define some roles
...     def execute(self):
...         with context(self):
...             pass # do something

Roles can be fetched from the context by calling ``context.name``. Just like that.
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
