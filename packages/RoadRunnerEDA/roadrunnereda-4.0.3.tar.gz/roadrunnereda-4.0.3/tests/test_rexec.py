from pathlib import Path
import unittest

from roadrunner import run


class TestTool(unittest.TestCase):
    PATH=Path('tests/work/roadexec')
    def test_simple(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            ret = tr.main(['invoke', 'test'])
            self.assertEqual(ret, 0)

