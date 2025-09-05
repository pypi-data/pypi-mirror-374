# Copyright (c) 2012 Adam Karpierz
# SPDX-License-Identifier: Zlib

from typing import Protocol, Any
from collections.abc import Callable, Sequence
import subprocess

class RunType(Protocol):

    def __call__(self, *args: Any, start_terminal_window: bool = False,
                 **kwargs: Any) -> subprocess.CompletedProcess[str | bytes]: ...

    CompletedProcess: type

    PIPE:    int
    STDOUT:  int
    DEVNULL: int

    SubprocessError:    type
    TimeoutExpired:     type
    CalledProcessError: type

    SafeString: type

    split_kwargs: Callable[[dict[str, Any], Sequence[str]],
                           tuple[dict[str, Any], dict[str, Any]]]

run: RunType
