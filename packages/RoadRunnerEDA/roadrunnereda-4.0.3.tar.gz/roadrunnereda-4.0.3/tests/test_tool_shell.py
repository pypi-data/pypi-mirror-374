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

class TestExec(unittest.TestCase):
    PATH=Path('tests/work/shell')
    def test_inline(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            tr.main(['invoke', 'inline'])
            with open(tr.tmp / "rrun/cmds/inline/script.stdout", "r") as fh:
                data = fh.readlines()
            exp = [
                "Hallo Welt!\n",
            ]
            self.assertListEqual(exp, data)

    def test_stages(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            tr.main(['invoke', 'simple'])
            with open(tr.tmp / "rrun/cmds/simple/script.stdout", "r") as fh:
                data = fh.readlines()
            exp = [
                "running stage 1: one\n",
                "this is script one\n",
                "running stage 2: three\n",
                "this is script three\n",
                "running stage 3: four\n",
                "this is script four\n",
                "done\n",
            ]
            self.assertListEqual(exp, data)
