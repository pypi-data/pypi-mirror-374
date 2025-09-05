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

class TestSim(unittest.TestCase):
    PATH = Path('tests/work/icarus')
    def test_sim(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'sim'])
            self.assertEqual(ret, 0)

    def test_simFail(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'simFail'])
            self.assertEqual(ret, 1)

    def test_simIgnoreFail(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'simIgnoreFail'])
            self.assertEqual(ret, 0)

    def test_compileSim(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'compile'])
            self.assertEqual(ret, 0)
            ret = utr.main(['--dontcatch', 'invoke', 'xsim'])
            self.assertEqual(ret, 0)

    def test_sepCompileUnits(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'sepCompileUnit'])
            self.assertEqual(ret, 0)

    def test_flags(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'compileFlags'])
            self.assertEqual(ret, 0)

    def test_includes(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'sim_inc'])
            self.assertEqual(ret, 0)

    def test_vpi(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'vpi'])
            self.assertEqual(ret, 0)
            data = (utr.tmp / "rrun/cmds/vpi/calls/vpi.sh").read_text()
            lines = data.splitlines()
            self.assertEqual(lines.count("iverilog-vpi \\"), 2) #two vpi compiles, because greeter is doubled

