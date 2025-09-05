# Copyright (c) 2016 Adam Karpierz
# SPDX-License-Identifier: Zlib

import unittest
import tempfile
import shutil
import os
import stat
import re
from pathlib import Path as StdPath

import utlx
from utlx.epath import Path


class TestPath(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.file = self.temp_dir / "test.txt"
        self.file.write_text("Hello World\nHello Python\n")

    def tearDown(self):
        shutil.rmtree(str(self.temp_dir), ignore_errors=True)

    def test_exists_and_mkdir(self):
        new_dir = self.temp_dir / "new"
        self.assertFalse(new_dir.exists())
        new_dir.mkdir()
        self.assertTrue(new_dir.exists())

    def test_rmdir_and_cleardir(self):
        subdir = self.temp_dir / "sub"
        subdir.mkdir()
        (subdir / "file.txt").write_text("data")
        subdir.cleardir()
        self.assertTrue(subdir.exists())
        self.assertEqual(list(subdir.iterdir()), [])
        subdir.rmdir()
        self.assertFalse(subdir.exists())

    def test_copy_and_move(self):
        dst = self.temp_dir / "copy.txt"
        copied = self.file.copy(dst)
        self.assertTrue(dst.exists())
        self.assertEqual(dst.read_text(), "Hello World\nHello Python\n")

        moved_path = self.temp_dir / "moved.txt"
        moved = copied.move(moved_path)
        self.assertTrue(moved_path.exists())
        self.assertFalse(dst.exists())
        self.assertEqual(moved.read_text(), "Hello World\nHello Python\n")

    def test_unlink_and_permission_handling(self):
        self.file.chmod(stat.S_IREAD)
        self.file.unlink()
        self.assertFalse(self.file.exists())

    def test_file_hash(self):
        hash_val = self.file.file_hash("md5")
        self.assertTrue(hasattr(hash_val, "hexdigest"))
        self.assertIsInstance(hash_val.hexdigest(), str)

    def test_dir_hash(self):
        hash_val = self.temp_dir.dir_hash("sha256")
        self.assertTrue(hasattr(hash_val, "hexdigest"))

    def test_unpack_archive(self):
        archive = self.temp_dir / "archive.zip"
        shutil.make_archive(str(archive.with_suffix("")), "zip", str(self.temp_dir))
        extract_dir = self.temp_dir / "extracted"
        archive.unpack_archive(extract_dir)
        self.assertTrue(extract_dir.exists())
        self.assertTrue((extract_dir / "test.txt").exists())

    def test_sed_inplace(self):
        self.file.sed_inplace("Hello", "Hi")
        content = self.file.read_text()
        self.assertIn("Hi World", content)
        self.assertIn("Hi Python", content)

    def test_chdir_and_pushd(self):
        original = StdPath.cwd()
        self.temp_dir.chdir()
        self.assertEqual(StdPath.cwd(), self.temp_dir)

        with self.temp_dir.pushd():
            self.assertEqual(StdPath.cwd(), self.temp_dir)
        self.assertEqual(StdPath.cwd(), self.temp_dir)

    def test_which(self):
        python_path = Path.which("python")
        self.assertIsNotNone(python_path)
        self.assertTrue(python_path.exists())

    def test_cleardir_on_symlink_raises(self):
        target = self.temp_dir / "target"
        target.mkdir()
        symlink = self.temp_dir / "link"
        symlink.symlink_to(target, target_is_directory=True)
        with self.assertRaises(NotADirectoryError):
            symlink.cleardir()

    def test_rmdir_on_nonexistent_path_does_nothing(self):
        ghost = self.temp_dir / "ghost"
        try:
            ghost.rmdir()
        except Exception as e:
            self.fail(f"rmdir raised {e} unexpectedly")

    def test_hardlink_to_not_supported(self):
        if not hasattr(os, "link"):
            with self.assertRaises(NotImplementedError):
                self.file.hardlink_to(self.temp_dir / "hard.txt")

    def test_unlink_missing_ok_false_raises(self):
        ghost = self.temp_dir / "ghost.txt"
        with self.assertRaises(FileNotFoundError):
            ghost.unlink(missing_ok=False)

    def test_file_hash_invalid_algorithm(self):
        with self.assertRaises(ValueError):
            self.file.file_hash("unknownhash")

    def test_dir_hash_empty_directory(self):
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()
        hash_val = empty_dir.dir_hash("md5")
        self.assertTrue(hasattr(hash_val, "hexdigest"))

    def test_sed_inplace_invalid_encoding(self):
        # Create a file with invalid UTF-8 bytes
        bad_file = self.temp_dir / "bad.txt"
        bad_file.write_bytes(b"\xff\xfe\xfd")
        try:
            bad_file.sed_inplace("x", "y")
        except Exception as e:
            self.fail(f"sed_inplace raised {e} unexpectedly")

    def test_unpack_archive_invalid_format(self):
        archive = self.temp_dir / "archive.zip"
        shutil.make_archive(str(archive.with_suffix("")), "zip", str(self.temp_dir))
        with self.assertRaises(shutil.ReadError):
            archive.unpack_archive(format="tar")

    def test_pushd_restores_directory_on_exception(self):
        original = StdPath.cwd()
        try:
            with self.temp_dir.pushd():
                raise RuntimeError("Simulated error")
        except RuntimeError:
            self.assertEqual(StdPath.cwd(), original)
