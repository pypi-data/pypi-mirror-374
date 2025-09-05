#!/usr/bin/env python3

from pathlib import Path
import tempfile
import unittest
from roadrunner.config import ConfigContext, ConfigError, Location, makeConfigFromStr
from roadrunner.run import UnitTestRunner
import roadrunner.run as run
import roadrunner.tools.builtin as builtin

class TestQuery_jabberwocky(unittest.TestCase):
    def test_jabberwocky(self):
        with UnitTestRunner() as utr:
            with self.assertLogs('root', 'INFO') as cm:
                utr.main(['jabberwocky'])
            exp = [
                'INFO:BuiltIn:Twas brillig, and the slithy toves',
                'INFO:BuiltIn:Did gyre and gimble in the wabe;',
                'INFO:BuiltIn:All mimsy were the borogoves,',
                'INFO:BuiltIn:And the mome raths outgrabe.'
            ]
            for e in exp:
                self.assertIn(e, cm.output)

    def test_query_fail(self):
        with UnitTestRunner(dir=Path('tests/work/builtin')) as utr:
            self.assertEqual(utr.main(['jabberwocky']), 0)
            self.assertEqual(utr.main(['jabberwocky', '--fail']), -1)
            with self.assertRaises(RuntimeError):
                utr.main(['jabberwocky', '--noret'])

    def test_cmd_fail(self):
        with UnitTestRunner(dir=Path('tests/work/builtin')) as utr:
            self.assertEqual(utr.main(['jubjub']), 0)
            self.assertEqual(utr.main(['jubjub_fail']), -1)
            with self.assertRaises(RuntimeError):
                utr.main(['jubjub_noret'])

class TestQuery_help(unittest.TestCase):
    def test_help(self):
        with UnitTestRunner() as utr:
            with self.assertLogs('root', "INFO") as cm:
                utr.main(['help'])
            self.assertIn('INFO:BuiltIn:  commands: jabberwocky', cm.output)

    def test_toolInfo(self):
        with UnitTestRunner() as utr:
            with self.assertLogs('root', "INFO") as cm:
                utr.main(['help', 'BuiltIn'])
            self.assertIn('INFO:BuiltIn:    getval - retrieves a value from the config space and prints it as python value', cm.output)

class TestQuery_getval(unittest.TestCase):
    def test_getval(self):
        with UnitTestRunner(dir=Path('tests/work/builtin')) as utr:
            with self.assertLogs('root', "INFO") as cm:
                utr.main(['getval', ':monkey', ':somefile'])
                utr.main(['getval', ':sub.source', '--path'])
                utr.main(['getval', ':number', '--type', 'int'])
            self.assertIn('INFO:BuiltIn:(:monkey):mandrill', cm.output)
            self.assertIn('INFO:BuiltIn:(:somefile):somefile.txt', cm.output)
            self.assertIn('INFO:BuiltIn:(:sub.source):sub/code.c', cm.output)
            with self.assertRaises(ConfigError):
                utr.main(['--dontcatch', 'getval', ':number', '--type', 'str'])

class TestQuery_get(unittest.TestCase):
    def test_get(self):
        with UnitTestRunner() as utr:
            with self.assertLogs('root', 'INFO') as cm:
                utr.main(['--dir', 'tests/work/builtin', 'get', ':monkey'])
            self.assertIn('INFO:BuiltIn:.monkey # mandrill', cm.output)

class TestQuery_tab(unittest.TestCase):
    def test_tab(self):
        with UnitTestRunner(dir=Path('tests/work/tab')) as utr:
            #complete
            with self.assertLogs('BuiltIn', 'DEBUG') as cm:
                utr.main(['tab', 'rr', 'so'])
            self.assertIn('DEBUG:BuiltIn:suggestions:5', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.node', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.node2', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.now', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo', cm.output)
            #trailing dot
            with self.assertLogs('BuiltIn', 'DEBUG') as cm:
                utr.main(['tab', 'rr', 'some.'])
            self.assertIn('DEBUG:BuiltIn:suggestions:4', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.node', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.node2', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.now', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo', cm.output)
            #single child dive
            with self.assertLogs('BuiltIn', 'DEBUG') as cm:
                utr.main(['tab', 'rr', 'some.f'])
            self.assertIn('DEBUG:BuiltIn:suggestions:6', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar.wheel', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar.wheel.one', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar.wheel.two', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar.wheel.three', cm.output)
            #self suggestion
            with self.assertLogs('BuiltIn', 'DEBUG') as cm:
                utr.main(['tab', 'rr', 'some.foo'])
            self.assertIn('DEBUG:BuiltIn:suggestions:6', cm.output)
            self.assertIn('DEBUG:BuiltIn:self suggestion:.some.foo', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar.wheel', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar.wheel.one', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar.wheel.two', cm.output)
            self.assertIn('DEBUG:BuiltIn:suggestion child:.some.foo.bar.wheel.three', cm.output)

class TestLuaHook(unittest.TestCase):
    def test_simple(self):
        with UnitTestRunner(dir=Path('tests/work/builtin')) as utr:
            with self.assertLogs('root', 'INFO') as cm:
                utr.main(['getval', ':hook'])
            self.assertIn('INFO:BuiltIn:(:hook):The Jabberwocky says burbel burbel - burbel burbel', cm.output)   

class TestResult(unittest.TestCase):
    PATH = Path('tests/work/builtin')
    def test_simple(self):
        with UnitTestRunner(dir=self.PATH) as utr:
            self.assertEqual(utr.main(['invoke', 'makeResult']), 0)
            self.assertEqual(utr.main(['invoke', 'useResult']), 0)

    def test_cmdFromResult(self):
        with UnitTestRunner(dir=self.PATH) as utr:
            self.assertEqual(utr.main(['invoke', 'reactiveResult']), 0)
            self.assertEqual(utr.main(['invoke', 'cmdFromResult']), 0)
            with open(utr.tmp / "rrun/cmds/reactiveResult.__result.cmd/script.stdout", "r") as fh:
                data = fh.readlines()
            exp = [
                "Hallo Welt\n",
            ]
            self.assertListEqual(exp, data)

    def test_doubleindirect(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'indirect2'])
            self.assertEqual(ret, 0)
            file = (utr.tmp / "rres/makeResult/RR")
            self.assertTrue(file.is_file())
            self.assertEqual(file.read_text(), "target: 93\n")

class TestGetHook(unittest.TestCase):
    def test_simple(self):
        with UnitTestRunner(dir=Path('tests/work/builtin')) as utr:
            self.assertEqual(utr.main(['invoke', 'hooksTest']), 0)
            data = (utr.tmp / "rrun/cmds/hooksTest/script.stdout").read_text().splitlines()
            exp = ["wocky: burbel burbel - burbel burbel", "getter: foo", "num: 20"]
            for term in exp:
                self.assertIn(term, data)


class TestTool(unittest.TestCase):
    def test_parse(self):
        rr = """
          test1:
            tool: Hammer
          test2:
            tool: Gun.fire
          test3:
            tool: File:v23
          test4:
            tool: Spoon.handle:brass
        """
        node = makeConfigFromStr(rr, Location("test_tool_buildin.py"))
        cfg = ConfigContext(node)
        self.assertEqual(builtin.parseTool(cfg.move(".test1")), ("Hammer", "run", None))
        self.assertEqual(builtin.parseTool(cfg.move(".test2")), ("Gun", "fire", None))
        self.assertEqual(builtin.parseTool(cfg.move(".test3")), ("File", "run", "v23"))
        self.assertEqual(builtin.parseTool(cfg.move(".test4")), ("Spoon", "handle", "brass"))


class TestCommandRunner(unittest.TestCase):
    PATH = Path('tests/work/builtin')
    def test_parallel(self):
        """test that two command can run parallel"""
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'parallel'])
            self.assertEqual(ret, 0)

    def test_sequence(self):
        """test that two command can run sequentially"""
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'sequence'])
            self.assertEqual(ret, 0)

    def test_multilevel(self):
        """test that a multilevel grouping creates distinct WDs for everyone"""
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'dynamic.merge'])
            self.assertEqual(ret, 0)
            for b in [1, 2]:
                br = {1: "one", 2: "two"}
                for t in ["One", "Two"]:
                    fpath = (utr.tmp / f"rrun/cmds/dynamic.merge/branch{b}.task{t}/script.stdout")
                    self.assertEqual(fpath.read_text(), f"task {t.lower()} -- branch {br[b]}\n") 

    def test_invokoption(self):
        """test that options are read from commandline"""
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'paramTask+par~12'])
            self.assertEqual(ret, 0)
            fpath = (utr.tmp / f"rrun/cmds/paramTask+par~12/script.stdout")
            self.assertEqual(fpath.read_text(), f"parameter par:12\n") 

        