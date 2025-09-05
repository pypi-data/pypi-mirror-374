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
from roadrunner.config import ConfigContext, ConfigPath, PathNotExist
from roadrunner.fn import relpath,  etype
from roadrunner.help import HelpItem, HelpOption, HelpProxy
from roadrunner.rr import Call, Pipeline, asset, renderTemplate, workdir_import
import roadrunner.modules.files
import roadrunner.modules.cpp
import roadrunner.modules.verilog

NAME = "Slang"
HelpItem("tool", NAME, "Slang SystemVerilog compiler")

DEFAULT_FLAGS = ['SLANG']

HelpItem("command", (NAME, "run"), "compile verilog files", [
    HelpOption("attribute", "flags", "str", None, "flags to be used in the ConfigContext"),
    HelpProxy("function", (NAME, "compile"))
])
def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    wd = pipe.initWorkDir()

    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_FLAGS
    fcfg = cfg.move(addFlags=set(flags))

    do_compile(fcfg, wd, vrsn, pipe)

    return 0

HelpItem("function", (NAME, "compile"), "gather (systemverilog) files and compile them", [
    HelpProxy("function", (NAME, "verilogFiles")),
    HelpOption("attribute", "toplevel", "str", None, "toplevel module name"),
])
def do_compile(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline):
    etype((cfg,ConfigContext), (wd,Path), (vs,(str,None)), (pipe,Pipeline))

    envfile = roadrunner.modules.verilog.writeEnvFile(wd, {})
    cmdFile = do_VerilogFiles(cfg, wd, pipe, [relpath(envfile, wd)])

    toplevel = cfg.get(".toplevel")
    timescale = cfg.get(".timescale", default="1ns/1ns", isType=str)

    #compile
    call = Call(wd, 'slang', NAME, vs)
    call.addArgs(['slang'])
    call.addArgs(['--timescale', timescale])
    call.addArgs(['-f', str(cmdFile)]) #command file or is it -C?
    call.addArgs(['--top', toplevel])
    pipe.addCall(call)
    return 0

HelpItem("function", (NAME, "verilogFiles"), "gather verilog files and create a command file for slang", [
    HelpProxy("module", ("verilog", "includeFiles")),
    HelpOption("attribute", "timescale", "str", None, "set the timescale directive - for sources that don't do that"),
])
def do_VerilogFiles(cfg:ConfigContext, wd:Path, pipe:Pipeline, addFiles:list=[]):
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline), (addFiles, list, Path))

    lst = roadrunner.modules.verilog.includeFiles(cfg.move(), wd)

    #override timescale
    timescale = cfg.get(".timescale", default=None, isType=str)

    files = []

    #addFiles without defines or includes
    for fname in addFiles:
        files.append((fname, [], []))

    for itm in lst:
        defs = itm.defines
        incs = itm.path
        files += [(fname, defs, incs) for fname in itm.sv]
        files += [(fname, defs, incs) for fname in itm.v]

    #remove duplicates
    tmp = files
    files = []
    for itm in tmp:
        if itm not in files:
            files.append(itm)

    #compile units
    cud = Path("comp_units")
    (wd / cud).mkdir(exist_ok=True)

    cmdFile = "command.cmd"
    with open(wd / cmdFile, "w") as fh:
        if timescale is not None:
            print(f"--timescale={timescale}", file=fh)
        for fname,defs,incs in files:
            cmdName = fname.with_suffix('.cmd')
            cmdDir = fname.parent
            fileName = fname.name
            with open(wd / cmdName, "w") as fc:
                for d in defs:
                    print(f"-D{d}", file=fc)
                for i in incs:
                    print(f"-I{relpath(i, cmdDir)}", file=fc)
                print(str(fileName), file=fc)   
            print(f"-C {cmdName}", file=fh)

    return cmdFile

