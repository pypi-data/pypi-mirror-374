from typing import Any

__all__ = ["Tp"]


def Tp(mixin_specs: list[type | tuple], prototype: Any) -> type:
    base_cls = type(prototype)

    mixin_bases = [spec[0] if isinstance(spec, tuple) else spec for spec in mixin_specs]
    name = base_cls.__name__ + "".join(c.__name__ for c in mixin_bases)
    bases = (base_cls,) + tuple(mixin_bases)

    def __new__(cls, *args, **kwargs):
        return base_cls.__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        base_cls.__init__(self, *args, **kwargs)
        for spec in mixin_specs:
            if isinstance(spec, tuple):
                mixin_cls, *mixin_args = spec
                mixin_cls.__init__(self, *mixin_args)
            else:
                spec.__init__(self)

    NewType = type(name, bases, {"__new__": __new__, "__init__": __init__})

    for spec in mixin_specs:
        mixin_cls = spec[0] if isinstance(spec, tuple) else spec
        mixin_args = spec[1:] if isinstance(spec, tuple) else []

        if hasattr(mixin_cls, "validate_type"):
            try:
                mixin_cls.validate_type(prototype, *mixin_args)
            except Exception as e:
                raise TypeError(
                    f"Validation failed for '{mixin_cls.__name__}' on base class '{base_cls.__name__}'. "
                    f"The base type does not satisfy the required laws."
                ) from e

    return NewType
