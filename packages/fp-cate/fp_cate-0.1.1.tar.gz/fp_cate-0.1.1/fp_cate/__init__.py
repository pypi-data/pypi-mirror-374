from .type_class import Tp
from .type_classes import Semigroup, Functor
from .utils import identity, assert_and, expr, compose

lst = Tp([Functor, Semigroup], (1, 2, 3))

# fmt: off
__all__ = [
    "Semigroup", "Functor",
    "identity", "assert_and", "expr", "compose",
    "lst"
]
# fmt: on
