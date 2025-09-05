# Copyright (c) 2012 Adam Karpierz
# SPDX-License-Identifier: Zlib

import typing
from typing import Any
from collections.abc import Iterable, Sequence
try:
    from System import String  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    String = str

__all__ = ('issubtype', 'isiterable', 'issequence', 'remove_all',
           'print_refinfo')


def issubtype(x: Any, t: Any) -> bool:
    return isinstance(x, type) and issubclass(x, t)


def isiterable(x: Any) -> bool:
    return (isinstance(x, (Iterable, typing.Iterable))
            and not isinstance(x, (bytes, str, String)))


def issequence(x: Any) -> bool:
    return (isinstance(x, (Sequence, typing.Sequence))
            and not isinstance(x, (bytes, str, String)))


def remove_all(seq: list[Any], value: Any) -> None:
    seq[:] = (item for item in seq if item != value)


def print_refinfo(obj: Any) -> None:
    import sys

    def typename(obj: Any) -> Any:
        try:
            return obj.__class__.__name__
        except AttributeError:
            pass
        try:
            return type(obj).__name__
        except AttributeError:
            pass
        return "???"

    ref_count = ((sys.getrefcount(obj) - 2)
                 if hasattr(sys, "getrefcount") else None)

    print("Object info report",            file=sys.stderr)
    print("    obj type: ", typename(obj), file=sys.stderr)
    print("    obj id:   ", id(obj),       file=sys.stderr)
    if ref_count is not None:
        print("    ref count:", ref_count, file=sys.stderr)
