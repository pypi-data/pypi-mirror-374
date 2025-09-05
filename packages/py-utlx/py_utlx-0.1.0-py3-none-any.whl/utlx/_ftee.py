# Copyright (c) 2018 Adam Karpierz
# SPDX-License-Identifier: Zlib

from typing import TextIO
from collections.abc import Generator
from os import PathLike
import sys
import io
import contextlib

__all__ = ('ftee',)


class _Tee(io.TextIOBase):

    def __init__(self, *files: TextIO) -> None:
        """Initializer"""
        self._files = files

    def close(self) -> None:
        super().close()
        self._files[0].flush()
        for f in self._files[1:]:
            f.close()

    def writable(self) -> bool:
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        return True

    def write(self, s: str) -> int:
        count: int = 0
        for f in self._files:
            count = f.write(s)
        return count

    def flush(self) -> None:
        for f in self._files:
            f.flush()


@contextlib.contextmanager
def ftee(*filenames: str | PathLike[str]) -> Generator[TextIO | _Tee, None, None]:
    stdout = sys.stdout
    files = [open(fname, "w") for fname in filenames]
    try:
        sys.stdout = _Tee(stdout, *files)
        yield sys.stdout
    finally:
        sys.stdout.close()
        sys.stdout = stdout


del TextIO, Generator, PathLike
del io, contextlib
