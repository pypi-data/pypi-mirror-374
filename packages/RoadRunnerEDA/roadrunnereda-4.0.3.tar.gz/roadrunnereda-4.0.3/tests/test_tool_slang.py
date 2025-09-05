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

class TestCall(unittest.TestCase):
    PATH=Path('tests/work/slang')
    def test_simple(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'simple'])
            self.assertEqual(ret, 0)

    def test_compileFlags(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'compileFlags'])
            self.assertEqual(ret, 0)

    def test_sepCompileUnits(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'sepCompileUnit'])
            self.assertEqual(ret, 0)

    def test_includes(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'includes'])
            self.assertEqual(ret, 0)

