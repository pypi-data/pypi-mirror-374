####    ############
####    ############
####
####
############    ####
############    ####
####    ####    ####
####    ####    ####
############
############

from pathlib import Path
import tempfile
import unittest

import roadrunner.run as run

class TestShare(unittest.TestCase):
    PATH=Path('tests/work/python')
    def test_inline(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            tr.main(['invoke', 'inline'])
            with open(tr.tmp / "rrun/cmds/inline/message", "r") as fh:
                data = fh.readlines()
            exp = [
                "Hallo Welt!\n",
            ]
            self.assertListEqual(exp, data)

    def test_script(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            self.assertEqual(tr.main(['invoke', 'script']), 0)
            with open(tr.tmp / "rrun/cmds/script/message", "r") as fh:
                data = fh.readlines()
            exp = [
                "Hallo Welt!\n",
            ]
            self.assertListEqual(exp, data)

    def test_script_args(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'scriptArgs'])
            self.assertEqual(ret, 0)
            with open(utr.tmp / "rrun/cmds/scriptArgs/message", "r") as fh:
                data = fh.readlines()
            exp = [
                "Hallo User!\n",
            ]
            self.assertListEqual(exp, data)

    def test_files(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            tr.main(['invoke', 'files'])
            with open(tr.tmp / "rrun/cmds/files/message", "r") as fh:
                data = fh.readlines()
            exp = [
                "Hallo du kleiner Mandrill",
            ]
            self.assertListEqual(exp, data)

    def test_return_value(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            self.assertEqual(tr.main(['invoke', 'returnValue']), 0)

    def test_return_fail(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            self.assertEqual(tr.main(['invoke', 'returnFail']), 12)

    def test_default_flags(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            self.assertEqual(tr.main(['invoke', 'defaultFlags']), 0)

    def test_mods_files(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            self.assertEqual(tr.main(['invoke', 'moduleFile']), 0)

    def test_mods_dir(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            self.assertEqual(tr.main(['invoke', 'moduleDir']), 0)

    def test_envVariables(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            self.assertEqual(tr.main(['invoke', 'envVars']), 0)

    #it is not possible to test curses in a unittest
    #def test_curses(self):
    #    with run.UnitTestRunner(dir=Path('tests/test_py')) as tr:
    #        tr.main(['invoke', 'curses'])
    #        #I don't know how to test this - because is displaying an curses UI
    #    # so I guess if it manages to run without crashing, it's fine
    #    self.assertTrue(True)

