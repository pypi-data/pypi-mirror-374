# Copyright (c) 2004 Adam Karpierz
# SPDX-License-Identifier: Zlib

import unittest
from unittest.mock import patch
import importlib

import utlx


class TestPlatform(unittest.TestCase):

    def reload_platform(self, platform_attrs=None, sys_attrs=None, os_attrs=None):
        """Helper function for reloading the module with mocked values."""
        patches = []
        if platform_attrs:
            patches.append(patch.multiple("platform", **platform_attrs))
        if sys_attrs:
            patches.append(patch.multiple("sys", **sys_attrs))
        if os_attrs:
            patches.append(patch.multiple("os", **os_attrs))

        for p in patches:
            p.start()
        from utlx import platform
        importlib.reload(platform)
        for p in reversed(patches):
            p.stop()
        return platform

    def test_is_windows_true_for_win32(self):
        platform = self.reload_platform(sys_attrs={"platform": "win32"}, platform_attrs={"win32_ver": lambda: ("10",)})
        self.assertTrue(platform.is_windows)

    def test_is_linux_true(self):
        platform = self.reload_platform(sys_attrs={"platform": "linux"}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_linux)

    def test_is_macos_true(self):
        platform = self.reload_platform(sys_attrs={"platform": "darwin"}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_macos)

    def test_is_bsd_true(self):
        platform = self.reload_platform(sys_attrs={"platform": "freebsd"}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_bsd)

    def test_is_sunos_true(self):
        platform = self.reload_platform(sys_attrs={"platform": "sunos"}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_sunos)

    def test_is_aix_true(self):
        platform = self.reload_platform(sys_attrs={"platform": "aix"}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_aix)

    def XXX_test_is_android_true(self):
        platform = self.reload_platform(sys_attrs={"getandroidapilevel": lambda: 33}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_android)

    def test_is_posix_true(self):
        platform = self.reload_platform(os_attrs={"name": "posix"}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_posix)

    def test_is_32bit_true(self):
        platform = self.reload_platform(sys_attrs={"maxsize": 2**32}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_32bit)

    def test_is_ucs2_true(self):
        platform = self.reload_platform(sys_attrs={"maxunicode": 0xFFFF}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_ucs2)

    def test_is_cpython_true(self):
        platform = self.reload_platform(platform_attrs={"python_implementation": lambda: "CPython", "win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_cpython)

    def test_is_pypy_true(self):
        platform = self.reload_platform(platform_attrs={"python_implementation": lambda: "PyPy", "win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_pypy)

    def test_is_ironpython_true(self):
        platform = self.reload_platform(platform_attrs={
            "python_implementation": lambda: "IronPython",
            "system": lambda: "CLI",
            "win32_ver": lambda: ("",)
        }, sys_attrs={"platform": "cli"})
        self.assertTrue(platform.is_ironpython)

    def XXX_test_is_wsl_true(self):
        platform = self.reload_platform(platform_attrs={"uname": lambda: type("Uname", (), {"release": "5.15.0-microsoft-standard"})(), "win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_wsl)

    def test_is_cygwin_true(self):
        platform = self.reload_platform(sys_attrs={"platform": "cygwin"}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_cygwin)

    def test_is_msys_true(self):
        platform = self.reload_platform(sys_attrs={"platform": "msys"}, platform_attrs={"win32_ver": lambda: ("",)})
        self.assertTrue(platform.is_msys)
