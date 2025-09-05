# Copyright (c) 2004 Adam Karpierz
# SPDX-License-Identifier: Zlib

import unittest
import types

import utlx
from utlx import public, private


class TestPublicPrivate(unittest.TestCase):

    def setUp(self):
        # We create a temporary module for testing
        self.module = types.ModuleType("testmod")
        self.module.__dict__["__all__"] = []

    def test_public_decorator_adds_to___all__(self):
        @public
        def sample(): return 1
        self.assertIn("sample", __all__)

    def test_public_function_form_adds_single_name(self):
        result = public(test_func=lambda: 42)
        self.assertEqual(result(), 42)
        self.assertIn("test_func", __all__)
        self.assertTrue(callable(test_func))

    def test_public_function_form_adds_multiple_names(self):
        result = public(a=lambda: 1, b=lambda: 2)
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0](), 1)
        self.assertEqual(result[1](), 2)
        self.assertIn("a", __all__)
        self.assertIn("b", __all__)

    def test_public_decorator_raises_on_kwargs(self):
        with self.assertRaises(AssertionError):
            public(lambda: 1, x=2)

    def test_private_removes_from___all__(self):
        @public
        def hidden(): return "secret"
        self.assertIn("hidden", __all__)
        private(hidden)
        self.assertNotIn("hidden", __all__)

    def XXX_test___all___must_be_list(self):
        __all__ = "not a list"
        with self.assertRaises(TypeError):
            public(test=lambda: 1)

    def test_private_does_nothing_if_name_not_in___all__(self):
        def ghost(): return "boo"
        private(ghost)  # Should not raise
        self.assertNotIn("ghost", __all__)
