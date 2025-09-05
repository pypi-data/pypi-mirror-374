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
    PATH = Path('tests/work/flow')
    #TODO actually test something
    def test_simple(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'simple'])
            self.assertEqual(ret, 0)

    def test_flagged(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'printnum'])
            self.assertEqual(ret, 0)
            msg1 = (utr.tmp / "rres/printnumber+one/msg").read_text()
            self.assertEqual(msg1, "The number is:1\n")
            msg2 = (utr.tmp / "rres/printnumber+two/msg").read_text()
            self.assertEqual(msg2, "The number is:2\n")

    def test_retval(self):
        with run.UnitTestRunner(dir=self.PATH) as utr, self.assertLogs('lua') as cm:
            ret = utr.main(['invoke', 'guess'])
        self.assertEqual(ret, 0)
        self.assertIn("INFO:lua:number is:137", cm.output)

    def test_pool(self):
        with run.UnitTestRunner(dir=self.PATH) as utr:
            ret = utr.main(['invoke', 'lists'])
            self.assertEqual(ret, 0)
            self.assertEqual((utr.tmp / "rres/square+num~3/product").read_text(), "3*3\n")
            self.assertEqual((utr.tmp / "rres/square+num~4/product").read_text(), "4*4\n")
            self.assertEqual((utr.tmp / "rres/square+num~5/product").read_text(), "5*5\n")


    