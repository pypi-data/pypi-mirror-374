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

from roadrunner.config import ConfigContext
from roadrunner.help import HelpItem
from roadrunner.rr import Call, Pipeline
from roadrunner.tools import builtin
from roadrunner.tools.vivado import sim, synth, common

NAME = common.NAME
HelpItem("tool", NAME, "Xilinx Vivado")

cmd_sim = sim.cmd_sim
cmd_xcompile = sim.cmd_xcompile
cmd_xsim = sim.cmd_xsim
cmd_ip = synth.cmd_ip
cmd_synth = synth.cmd_synth

HelpItem("query", (NAME, "vivado"), "Start Vivado GUI")
def query_vivado(cfg:ConfigContext) -> int:
    cfg.set(".Vivado.tool", "Vivado.run", create=True)
    cmdnode = cfg.move(".Vivado")
    return builtin.invoke(cmdnode)

HelpItem("command", (NAME, "run"), "Start Vivado GUI")
def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    wd = pipe.initWorkDir()
    call = Call(wd, NAME, NAME, vrsn)
    call.addArgs(["vivado"])
    pipe.addCall(call, interactive=True)
    return 0
