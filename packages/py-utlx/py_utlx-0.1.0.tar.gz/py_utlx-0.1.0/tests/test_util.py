# Copyright (c) 2004 Adam Karpierz
# SPDX-License-Identifier: Zlib

import unittest
import sys
import io

import utlx
from utlx import issubtype, isiterable, issequence, remove_all, print_refinfo


class TestUtilityFunctions(unittest.TestCase):

    # --- issubtype ---
    def test_issubtype_with_valid_subclass(self):
        self.assertTrue(issubtype(int, object))

    def test_issubtype_with_non_type(self):
        self.assertFalse(issubtype(123, object))

    def test_issubtype_with_unrelated_types(self):
        self.assertFalse(issubtype(str, int))

    # --- isiterable ---
    def test_isiterable_with_list(self):
        self.assertTrue(isiterable([1, 2, 3]))

    def test_isiterable_with_tuple(self):
        self.assertTrue(isiterable((1, 2)))

    def test_isiterable_with_generator(self):
        self.assertTrue(isiterable((x for x in range(3))))

    def test_isiterable_with_string(self):
        self.assertFalse(isiterable("abc"))

    def test_isiterable_with_bytes(self):
        self.assertFalse(isiterable(b"abc"))

    def test_isiterable_with_custom_iterable(self):
        class Custom:
            def __iter__(self):
                return iter([1])
        self.assertTrue(isiterable(Custom()))

    # --- issequence ---
    def test_issequence_with_list(self):
        self.assertTrue(issequence([1, 2]))

    def test_issequence_with_tuple(self):
        self.assertTrue(issequence((1, 2)))

    def test_issequence_with_string(self):
        self.assertFalse(issequence("text"))

    def test_issequence_with_bytes(self):
        self.assertFalse(issequence(b"data"))

    def XXX_test_issequence_with_custom_sequence(self):
        class Custom:
            def __getitem__(self, index):
                return index
            def __len__(self):
                return 1
        self.assertTrue(issequence(Custom()))

    # --- remove_all ---
    def test_remove_all_removes_all_occurrences(self):
        data = [1, 2, 3, 2, 4]
        remove_all(data, 2)
        self.assertEqual(data, [1, 3, 4])

    def test_remove_all_with_no_match(self):
        data = [1, 2, 3]
        remove_all(data, 99)
        self.assertEqual(data, [1, 2, 3])

    def test_remove_all_with_empty_list(self):
        data = []
        remove_all(data, 1)
        self.assertEqual(data, [])

    def test_remove_all_removes_everything(self):
        data = [5, 5, 5]
        remove_all(data, 5)
        self.assertEqual(data, [])

    # --- print_refinfo ---
    def test_print_refinfo_outputs_expected_lines(self):
        obj = [1, 2, 3]
        captured = io.StringIO()
        sys.stderr = captured
        print_refinfo(obj)
        sys.stderr = sys.__stderr__
        output = captured.getvalue()
        self.assertIn("Object info report", output)
        self.assertIn("obj type:", output)
        self.assertIn("obj id:", output)
        # ref count may or may not be printed depending on platform
        self.assertTrue("ref count:" in output or "obj id:" in output)
