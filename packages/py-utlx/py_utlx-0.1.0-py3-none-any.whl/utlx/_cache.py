# Copyright (c) 2012 Adam Karpierz
# SPDX-License-Identifier: Zlib

from typing import TypeVar, TypeAlias, Any
from collections.abc import Callable

__all__ = ('cached', 'cached_property')

P = TypeVar("P", bound=object)
T = TypeVar("T")

AnyCallable: TypeAlias = Callable[..., Any]


def cached(method: AnyCallable) -> AnyCallable:
    """Decorator to simple cache method's result"""

    from functools import wraps

    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        key: int = hash(method)
        try:
            return self.__cache__[key]
        except KeyError:
            pass
        except AttributeError:
            self.__cache__ = {}
        self.__cache__[key] = result = method(self, *args, **kwargs)
        return result

    return wrapper


def cached_property(fget: Callable[[P], T] | None = None,
                    fset: Callable[[P, T], None] | None = None,
                    fdel: Callable[[P], None] | None = None,
                    doc: str | None = None) -> property:
    """Decorator to simple cache property attribute.

    fget
      function to be used for cached getting an attribute value
    fset
      function to be used for setting an attribute value
    fdel
      function to be used for del'ing an attribute
    doc
      docstring
    """
    return property(None if fget is None else cached(fget), fset, fdel, doc)


del P, T
del TypeVar, TypeAlias, Callable, AnyCallable
