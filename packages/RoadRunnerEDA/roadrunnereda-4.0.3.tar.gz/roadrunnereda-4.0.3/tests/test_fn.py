#!/usr/bin/env python3

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import roadrunner.fn as fn

class TestEtype(unittest.TestCase):
    def test_etype(self):
        self.assertTrue(fn.etype(("hallo", str)))
        self.assertTrue(fn.etype((None, (str, None))))
        self.assertTrue(fn.etype(("hallo", (None, str))))
        self.assertTrue(fn.etype((None, None)))
        self.assertTrue(fn.etype(("hallo", None)))
        with self.assertRaises(TypeError):
            fn.etype(("hallo", int))
        with self.assertRaises(TypeError):
            fn.etype((None, int))
        with self.assertRaises(TypeError):
            fn.etype(("hallo", (int, None)))

    def test_etype_list(self):
        lst = [1, 3, 4]
        lst2 = [1, 3, "hallo"]
        lst3 = [1, 3, None]
        self.assertTrue(fn.etype((lst, None, int)))
        self.assertTrue(fn.etype((lst, list, int)))
        with self.assertRaises(TypeError):
            fn.etype((lst, None, str))
        with self.assertRaises(TypeError):
            fn.etype((lst2, None, int))
        self.assertTrue(fn.etype((lst2, list, (int, str))))
        with self.assertRaises(TypeError):
            fn.etype((lst3, None, (int, str)))

    def test_etype_tuple(self):
        tup = (1,2,3)
        self.assertTrue(fn.etype((tup, tuple, int)))
        with self.assertRaises(TypeError):
            fn.etype((tup, list, int))
        
    def test_etype_set(self):
        st = {1,2,3}
        self.assertTrue(fn.etype((st, set, int)))
        with self.assertRaises(TypeError):
            fn.etype((st, list, int))

    def test_etype_dict(self):
        dct = {1:2, 3:4}
        dct2 = {1:2, 3:"hallo"}
        self.assertTrue(fn.etype((dct, dict, int, int)))
        with self.assertRaises(TypeError):
            fn.etype((dct, dict, str, int))
        with self.assertRaises(TypeError):
            fn.etype((dct, dict, int, str))
        with self.assertRaises(TypeError):
            fn.etype((dct, dict, str, str))
        self.assertTrue(fn.etype((dct2, dict, int, (int, str))))

class TestCtype(unittest.TestCase):
    def test_ctype(self):
        self.assertFalse(fn.ctype(("hallo", int)))

class TestBanner(unittest.TestCase):
    def test_banner(self):
        self.assertEqual("--==---------------------------hallo----------------------------==--", fn.banner("hallo"))
        self.assertEqual("--==                          (hallo)                           ==--", fn.banner("hallo", False))

class TestCleardir(unittest.TestCase):
    def test_cleardir(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "test").mkdir()
            (tmp / "test2").mkdir()
            (tmp / "test/file1").touch()
            (tmp / "file2").touch()
            fn.cleardir(tmp)
            files = list(tmp.iterdir())
            self.assertEqual(0, len(files))
            
class TestMkFile(unittest.TestCase):
    def test_simple(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "file1"
            dest = tmp / "foo/bar/file1"
            source.touch()
            fn.mkFile(dest, source)
            self.assertTrue(dest.exists())
            self.assertTrue(dest.is_file())

    def test_symlink(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "file1"
            dest = tmp / "foo/bar/file1"
            source.touch()
            fn.mkFile(dest, source, symlink=True)
            self.assertTrue(dest.exists())
            self.assertTrue(dest.is_symlink())
            self.assertTrue(dest.is_file())

    def test_unlink(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "file1"
            dest = tmp / "foo/bar/file1"
            source.touch()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.touch()
            self.assertFalse(os.path.samefile(source, dest))
            fn.mkFile(dest, source)
            self.assertTrue(dest.exists())
            self.assertTrue(dest.is_file())
            self.assertFalse(dest.is_symlink())
            self.assertFalse(os.path.samefile(source, dest))

    def test_copy(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "file1"
            dest = tmp / "foo/bar/file1"
            source.touch()
            fn.mkFile(dest, source, hardlink=False, copy=True)
            self.assertTrue(dest.exists())
            self.assertTrue(dest.is_file())
            self.assertFalse(dest.is_symlink())
            self.assertFalse(os.path.samefile(source, dest))

    def test_mkLink(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "file1"
            dest = tmp / "foo/bar/file1"
            source.touch()
            fn.mkLink(dest, source)
            self.assertTrue(dest.exists())
            self.assertTrue(dest.is_file())

    def test_mkSymlink(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "file1"
            dest = tmp / "foo/bar/file1"
            source.touch()
            fn.mkSymlink(dest, source)
            self.assertTrue(dest.exists())
            self.assertTrue(dest.is_symlink())
            self.assertTrue(dest.is_file())

class TestClonedir(unittest.TestCase):
    def test_simple(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            f1 = "foo/bar"
            f2 = "braak"
            for fr in [f1, f2]:
                fp = tmp / "source" / fr
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.touch()
            fn.clonedir(tmp / "source", tmp / "dest")
            for fr in [f1, f2]:
                fp = tmp / "dest" / fr
                self.assertTrue(fp.exists())
                self.assertTrue(fp.is_file())

class TestRelpath(unittest.TestCase):
    def test_relpath(self):
        try:
            with TemporaryDirectory() as tmpdir:
                cwd = Path.cwd()
                tmp = Path(tmpdir)
                os.chdir(tmp)
                destDir = tmp / "foo/bar"
                destDir.mkdir(parents=True)
                startDir = Path("foo")
                rel = fn.relpath(destDir, startDir)
                self.assertEqual(rel, Path("bar"))
        finally:
            os.chdir(cwd)


class TestUniqueExtend(unittest.TestCase):
    def test_simple(self):
        baseList = ['foo', 'bar', 'blub']
        extendList = ['braak', 'bar']
        fn.uniqueExtend(baseList, extendList)
        self.assertEqual(baseList, ['foo', 'bar', 'blub', 'braak'])

class TestIniConfig(unittest.TestCase):
    def test_init(self):
        ini = fn.IniConfig()
        self.assertIsInstance(ini, fn.IniConfig)

class TestConfigParse(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn.configParse("section:value = 17"), ("section", "value", "17"))
        self.assertEqual(fn.configParse("section.sub:val.u = braak_dont"), ("section.sub", "val.u", "braak_dont"))

    def test_loglevel(self):
        self.assertEqual(fn.configParse("root = debugging", log=True), ("loglevel", "root", "debugging"))
        self.assertEqual(fn.configParse("test.blubber=1", log=True), ("loglevel", "test.blubber", "1"))
