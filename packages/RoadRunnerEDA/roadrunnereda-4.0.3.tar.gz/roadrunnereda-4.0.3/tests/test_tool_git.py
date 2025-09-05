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
import subprocess

import roadrunner.run as run

class TestExec(unittest.TestCase):
    PATH=Path('tests/work/git')
    def test_simple(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'simple'])
            self.assertEqual(ret, 0)
            with open(tr.tmp / "rrun/cmds/simple/Git.stderr", "r") as fh:
                data = fh.readlines()
            exp = "Cloning into 'result'...\n"
            self.assertIn(exp, data)

    def test_branch(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'branch'])
            self.assertEqual(ret, 0)
            cp = subprocess.run(["git", "-C", f"{tr.tmp}/rres/branch", "branch"], capture_output=True)
            self.assertEqual(cp.stdout.decode('utf-8'), "* v3\n")

    def test_config(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'config'])
            self.assertEqual(ret, 0)
            ctnt = (tr.tmp / "rres/config/RR").read_text()
            self.assertEqual(ctnt, "value: 42\n")

    def test_config2(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'config2'])
            self.assertEqual(ret, 0)
            ctnt = (tr.tmp / "rres/config2/RR").read_text()
            self.assertEqual(ctnt, "value: 42\n")


