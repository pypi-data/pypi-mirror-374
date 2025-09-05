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
import unittest

import roadrunner.run as run

#class TestRunner(unittest.TestCase):
#    PATH=Path('tests/work/local')
#    def test_simple(self):
#        with run.UnitTestRunner(dir=self.PATH) as tr, self.assertLogs('roadexec', 'DEBUG') as tl:
#            ret = tr.main(['invoke', 'simple'])
#        self.assertEqual(ret, 0)
#        self.assertIn(['INFO:lua:Hallo Welt!'], tl.output)
