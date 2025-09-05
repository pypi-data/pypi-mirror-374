from functools import reduce, partial
from typing import TypeVar
from inspect import signature, _empty

__all__ = ["identity", "assert_and", "expr", "compose", "curry", "Filter", "State"]


def identity(x):
    return x


T = TypeVar("T")


def assert_and(cond: bool, expr: T, msg: str | None = "Assertion failed") -> T:
    """Works like assert but returns expr when cond is True"""
    assert cond, msg
    return expr


def expr(*args):
    """Evaluates and returns the last argument"""
    return args[-1]


def compose(*funcs):
    """Composes multiple functions into a single function"""
    return reduce(lambda f, g: lambda x: f(g(x)), funcs, identity)


# from https://stackoverflow.com/a/78149460
def curry(f):
    def inner(*args, **kwds):
        new_f = partial(f, *args, **kwds)
        params = signature(new_f, follow_wrapped=True).parameters
        if all(params[p].default != _empty for p in params):
            return new_f()
        else:
            return curry(new_f)

    return inner


class Filter:
    def __init__(self, func):
        self.func = func

    def __rmatmul__(self, iterable):
        return type(iterable)(filter(self.func, iterable))


class State:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def update(self, **kwargs) -> "State":
        new_state = self.__dict__.copy()
        return State(**new_state, **kwargs)

    def __repr__(self):
        return (
            "Ctx {\n"
            + "\n".join(f"  {k}={v}" for k, v in self.__dict__.items())
            + "\n}"
        )
