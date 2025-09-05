from typing import Any
from collections.abc import Callable

__all__ = ["Semigroup", "Functor"]


def _call_op(a: Any, b: Any, op: str) -> Any:
    return getattr(a, f"__{op}__")(b)


class Semigroup:
    """
    A semigroup should satify:
      * Associativity
      * Unit
      * Multiplication

    Default operation is '+' so that it works with numbers, strings, lists, tuples, etc.
    """

    @staticmethod
    def validate_type(prototype: Any, op: str = "add") -> None:
        Type = type(prototype)
        ident = Type()

        assert _call_op(_call_op(ident, prototype, op), ident, op) == _call_op(
            ident, _call_op(prototype, ident, op), op
        ), f"Type does not satisfy associativity for op ${op}"
        assert (
            _call_op(ident, prototype, op) == prototype
            and _call_op(prototype, ident, op) == prototype
        ), "Type does not satisfy unit"
        assert _call_op(prototype, _call_op(prototype, prototype, op), op) == _call_op(
            _call_op(prototype, prototype, op), prototype, op
        ), f"Type does not satisfy multiplication for op ${op}"

    def __init__(self, op: str = "add") -> None:
        self.op = op

    def __add__(self, other: "Semigroup") -> "Semigroup":
        assert type(self) is type(other) and other.op == self.op
        return type(self)(_call_op(self, other, self.op))


class Functor:
    """
    A functor should satisfy:
      * Identity
      * Composition

    Works with lists, tuples, sets, etc.
    """

    @staticmethod
    def validate_type(prototype: Any) -> None:
        base_cls = type(prototype)
        assert (
            base_cls(map(lambda x: x, prototype)) == prototype
        ), "Type does not satisfy identity"

    def fmap(self, func: Callable) -> "Functor":
        return type(self)(map(func, self))  # pyright: ignore

    def __or__(self, func: Callable) -> "Functor":
        return self.fmap(func)
