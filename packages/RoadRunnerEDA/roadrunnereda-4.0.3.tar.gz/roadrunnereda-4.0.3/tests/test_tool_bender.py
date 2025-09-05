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
    PATH=Path('tests/work/bender')
    def test_simple(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            tr.main(['invoke', 'checkout'])
            tr.main(['invoke', 'import'])
            with open(tr.tmp / "rres/import/RR", "r") as fh:
                data = fh.readlines()
            exp = [
                "        - .bender/git/checkouts/common_cells-ef73fb619e9c374f/src/edge_propagator_rx.sv\n",
                "      path:\n",
                "        - .bender/git/checkouts/common_cells-ef73fb619e9c374f/include\n",
                "    - sv:\n",
                "        - .bender/git/checkouts/apb-5224435a7135763a/src/apb_pkg.sv\n",
                "        - .bender/git/checkouts/apb-5224435a7135763a/src/apb_intf.sv\n",
                "        - .bender/git/checkouts/apb-5224435a7135763a/src/apb_err_slv.sv\n",
                "        - .bender/git/checkouts/apb-5224435a7135763a/src/apb_regs.sv\n",
                "        - .bender/git/checkouts/apb-5224435a7135763a/src/apb_cdc.sv\n"
            ]
            self.assertListEqual(exp, data[123:132])

    def test_subdir(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            tr.main(['invoke', 'checkout2'])
            tr.main(['invoke', 'importDir'])
            with open(tr.tmp / "rres/importDir/RR", "r") as fh:
                data = fh.readlines()
            exp = [
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_bus_compare.sv\n',
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_cdc_dst.sv\n',
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_cdc_src.sv\n',
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_cut.sv\n',
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_delayer.sv\n',
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_demux_simple.sv\n',
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_dw_downsizer.sv\n',
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_dw_upsizer.sv\n',
                '        - .bender/git/checkouts/axi-a612f580cfee89bc/src/axi_fifo.sv\n'
            ]
            self.assertListEqual(exp, data[141:150])

    def test_target(self):
        with run.UnitTestRunner(dir=self.PATH) as tr:
            tr.main(['invoke', 'checkout'])
            tr.main(['invoke', 'importTarget'])
            with open(tr.tmp / "rres/importTarget/RR", "r") as fh:
                data = [x.strip() for x in fh.readlines()]
            exp = '- hw/test/axi_reorder_compare.sv'
            self.assertIn(exp, data)

