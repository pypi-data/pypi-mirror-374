from __future__ import annotations
from abc import ABC
from typing import TypeVar, ClassVar

class _MethodEnforcer(ABC):
    """
    Base that prevents overriding method names listed in __final_methods__.
    This is a runtime guard complementing @final (which is static/type-check only).
    """
    __final_methods__: ClassVar[set[str]] = set()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Gather final names from all bases
        inherited_finals: set[str] = set()
        for base in cls.mro()[1:]:
            inherited_finals |= getattr(base, "__final_methods__", set())
        # If this class defines any of those names, reject
        for name in inherited_finals:
            if name in cls.__dict__:
                raise TypeError(f"{cls.__name__} cannot override final method '{name}'")
