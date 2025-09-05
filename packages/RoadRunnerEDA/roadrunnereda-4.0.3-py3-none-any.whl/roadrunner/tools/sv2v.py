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

import logging
from pathlib import Path

from roadexec.fn import relpath
from roadrunner.config import ConfigContext
from roadrunner.fn import etype, uniqueExtend
from roadrunner.help import HelpItem, HelpOption, HelpProxy
from roadrunner.rr import Call, Pipeline
import roadrunner.modules.files
import roadrunner.modules.verilog

NAME = "Sv2v"
HelpItem("tool", NAME, "SystemVerilog to Verilog")

HelpItem("command", (NAME, "run"), "run the Sv2v tool", [
    HelpOption("attribute", "flags", "str", None, "flags to be used in the ConfigContext"),
    HelpOption("attribute", "result", "str", None, "named of the result to receive the converted files"),
    HelpProxy("module", ("verilog", "includeFiles")),
])
def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    wd = pipe.initWorkDir()
    pipe.enterCall(NAME)

    flags = cfg.get('.flags', mkList=True, default=[])
    fcfg = cfg.move(addFlags=set(flags))

    vars = roadrunner.modules.files.handleFiles(fcfg, wd, pipe)
    envfile = roadrunner.modules.verilog.writeEnvFile(wd, vars)

    lst = roadrunner.modules.verilog.includeFiles(fcfg.move(), wd)

    # sort verilog files
    svfiles = [relpath(envfile, wd)]
    vfiles = []
    defines = []
    includes = []
    for item in lst:
        uniqueExtend(svfiles, item.sv)
        uniqueExtend(vfiles, item.v)
        uniqueExtend(defines, item.defines)
        uniqueExtend(includes, item.path)

    # call convertion
    (wd / "sv2v").mkdir(exist_ok=True)
    converted = {}
    call = Call(wd, 'sv2v', NAME, vrsn)
    call.addArgs(['sv2v', '--write', 'adjacent'])
    for fname in svfiles:
        call.addArgs([str(fname)])
        converted[fname] = fname.with_suffix('.v')
    for inc in includes:
        call.addArgs(["-I", str(inc)])
    for d in defines:
        call.addArgs(["-D", d])
    pipe.useCall(call)

    # create result
    resultName = fcfg.get('.result', isType=str, default='sv2v')
    pipe.result(resultName)
    for fname in converted.values():
        pipe.export(str(fname), group="v")

    pipe.leave()
    return 0