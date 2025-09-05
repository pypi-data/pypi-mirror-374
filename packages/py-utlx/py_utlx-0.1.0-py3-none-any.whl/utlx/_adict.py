# Copyright (c) 2012 Adam Karpierz
# SPDX-License-Identifier: Zlib

from typing import Any
from typing_extensions import Self
from collections.abc import Iterable
from collections import defaultdict

__all__ = ('adict', 'defaultadict')


class __adict:

    class __AttributeAndKeyError(AttributeError, KeyError):
        __doc__ = AttributeError.__doc__

    def __getattr__(self, name: str) -> Any:
        """Attribute access"""
        try:
            return self.__getitem__(name)
        except KeyError as exc:
            raise self.__AttributeAndKeyError(*exc.args) from None

    def __setattr__(self, name: str, value: Any) -> None:
        """Attribute assignment"""
        try:
            self.__setitem__(name, value)
        except KeyError as exc:
            raise self.__AttributeAndKeyError(*exc.args) from None

    def __delattr__(self, name: str) -> None:
        """Attribute deletion"""
        try:
            self.__delitem__(name)
        except KeyError as exc:
            raise self.__AttributeAndKeyError(*exc.args) from None


class adict(__adict, dict[Any, Any]):

    @classmethod
    def fromkeys(cls, seq: Iterable[Any], value: Any = None) -> Self:
        self = super().fromkeys(seq, value)
        return cls(self)

    def copy(self) -> Self:
        return self.__class__(self)


class defaultadict(__adict, defaultdict[Any, Any]):

    @classmethod
    def fromkeys(cls, seq: Iterable[Any], value: Any = None) -> Self:
        self = super().fromkeys(seq, value)
        return cls(self.default_factory, self)  # type: ignore[attr-defined]

    def copy(self) -> Self:
        return self.__class__(self.default_factory, self)


del Self, Iterable, defaultdict
