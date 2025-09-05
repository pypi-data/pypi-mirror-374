# Copyright (c) 2004 Adam Karpierz
# SPDX-License-Identifier: Zlib

import unittest

import utlx
from utlx import adict, defaultadict


class TestAdict(unittest.TestCase):

    def test_attribute_access(self):
        d = adict()
        d["x"] = 10
        self.assertEqual(d.x, 10)

    def test_attribute_assignment(self):
        d = adict()
        d.x = 20
        self.assertEqual(d["x"], 20)

    def test_attribute_deletion(self):
        d = adict(x=5)
        del d.x
        self.assertNotIn("x", d)

    def test_copy_returns_new_instance(self):
        d1 = adict(a=1, b=2)
        d2 = d1.copy()
        self.assertIsInstance(d2, adict)
        self.assertEqual(d2, d1)
        self.assertIsNot(d1, d2)

    def XXX_test_fromkeys_creates_instance(self):
        keys = ["a", "b"]
        d = adict.fromkeys(keys, 0)
        self.assertIsInstance(d, adict)
        self.assertEqual(d["a"], 0)
        self.assertEqual(d["b"], 0)

    def XXX_test_missing_attribute_raises(self):
        d = adict()
        with self.assertRaises(AttributeError):
            _ = d.missing


class TestDefaultAdict(unittest.TestCase):

    def test_default_factory_behavior(self):
        d = defaultadict(lambda: "default")
        self.assertEqual(d["missing"], "default")

    def test_attribute_access_and_assignment(self):
        d = defaultadict(lambda: 0)
        d.x = 100
        self.assertEqual(d["x"], 100)
        self.assertEqual(d.x, 100)

    def test_attribute_deletion(self):
        d = defaultadict(lambda: None, x=1)
        del d.x
        self.assertNotIn("x", d)

    def test_copy_preserves_factory(self):
        d1 = defaultadict(lambda: 42, a=1)
        d2 = d1.copy()
        self.assertIsInstance(d2, defaultadict)
        self.assertEqual(d2["missing"], 42)

    def XXX_test_fromkeys_creates_instance(self):
        d = defaultadict(lambda: "X").fromkeys(["a", "b"], "Y")
        self.assertIsInstance(d, defaultadict)
        self.assertEqual(d["a"], "Y")
        self.assertEqual(d["missing"], "X")

    def XXX_test_missing_attribute_raises(self):
        d = defaultadict(lambda: None)
        with self.assertRaises(AttributeError):
            _ = d.__getattr__("nonexistent")
