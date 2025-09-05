# Copyright (c) 2018 Adam Karpierz
# SPDX-License-Identifier: Zlib

from ctypes.wintypes import HMODULE
from pathlib import Path

__all__ = ('dll_path', 'python_dll_path')


def dll_path(handle: HMODULE | int) -> Path | None:
    """Retrieves the fully qualified path for the file that contains the specified module.

    The module must have been loaded by the current process.
    """
    import ctypes as ct
    from ctypes.wintypes import HMODULE, LPWSTR, DWORD
    MAX_PATH = 520
    GetModuleFileName = ct.windll.kernel32.GetModuleFileNameW
    GetModuleFileName.argtypes = HMODULE, LPWSTR, DWORD
    GetModuleFileName.restype  = DWORD
    buf = ct.create_unicode_buffer(MAX_PATH)
    # print("LENNNN", len(buf))
    result = GetModuleFileName(handle, buf, len(buf))
    dll_path = buf.value
    # print("@@@@@@@@@@@", handle, result, dll_path)
    return (Path(dll_path) if handle != 0 and result != 0
            and dll_path and Path(dll_path).exists() else None)


def python_dll_path() -> Path | None:
    """Retrieves the fully qualified path for the file that contains Python dll module.

    The module must have been loaded by the current process.
    """
    import ctypes as ct
    return dll_path(ct.pythonapi._handle)


del HMODULE
