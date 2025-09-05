from functools import reduce
from typing import TypeVar

__all__ = ["identity", "assert_and", "expr", "compose"]


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
