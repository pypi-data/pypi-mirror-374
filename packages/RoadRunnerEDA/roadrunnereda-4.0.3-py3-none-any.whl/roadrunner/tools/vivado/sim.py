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
from roadrunner.config import ConfigContext, Location, PathNotExist
from roadrunner.fn import etype, banner, uniqueExtend, relpath
from roadrunner.help import HelpItem, HelpOption, HelpProxy
from roadrunner.rr import Call, Pipeline, asset, workdir_import
import roadrunner.modules.files
import roadrunner.modules.verilog
import roadrunner.modules.vhdl
import roadrunner.modules.tcl
from roadrunner.tools.vivado import common

LOGNAME = "VivSim"

DEFAULT_SIM_DEFINES = ["SIMULATION", "DPI"] + common.DEFAULT_DEFINES
DEFAULT_SIM_FLAGS = ["SIMULATION", "DPI"] + common.DEFAULT_FLAGS

HelpItem("command", (common.NAME, "sim"), "Run Vivado Simulation", [
    HelpOption("attribute", "check", "bool", "true", "Run the logchecker"),
    HelpProxy("module", ("files", "handleFiles")),
    HelpProxy("function", (common.NAME, "do_compile")),
    HelpProxy("function", (common.NAME, "do_dpi")),
    HelpProxy("function", (common.NAME, "do_elab")),
    HelpProxy("function", (common.NAME, "do_sim")),
    HelpProxy("function", (common.NAME, "do_check"))
])
def cmd_sim(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(LOGNAME)
    log.info(banner("Vivado Simulation"))
             
    wd = pipe.initWorkDir()


    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_SIM_FLAGS
    log.debug(f"compile config flags:{flags}")
    fcfg = cfg.move(addFlags=set(flags))

    check = fcfg.get(".check", default=True, isType=bool)

    vars = roadrunner.modules.files.handleFiles(fcfg, wd, pipe)

    with pipe.inSequence(common.NAME):
        do_compile(fcfg, wd, vrsn, pipe, vars)
        do_dpi(fcfg, wd, vrsn, pipe)
        do_elab(fcfg, wd, pipe)

        do_sim(fcfg, wd, vrsn, pipe, vars)
        if check:
            do_check(wd, vrsn, pipe)

    log.info(banner("/Vivado Simulation", False))
    return 0

HelpItem("command", (common.NAME, "xcompile"), "Run Vivado Simulation Compile", [
    HelpOption("attribute", "result", "str", "Result directory"),
    HelpProxy("module", ("files", "handleFiles")),
    HelpProxy("function", (common.NAME, "do_compile")),
    HelpProxy("function", (common.NAME, "do_dpi")),
    HelpProxy("function", (common.NAME, "do_elab"))
])
def cmd_xcompile(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(LOGNAME)
    log.info(banner("Vivado Simulation"))

    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_SIM_FLAGS
    log.debug(f"compile config flags:{flags}")
    fcfg = cfg.move(addFlags=set(flags))

    wd = pipe.initWorkDir()

    with pipe.inSequence(common.NAME):
        vars = roadrunner.modules.files.handleFiles(fcfg, wd, pipe)

        do_compile(fcfg, wd, vrsn, pipe, vars)
        do_dpi(fcfg, wd, vrsn, pipe)
        do_elab(fcfg, wd, pipe)

        pipe.result()
        pipe.export("xsim.dir")

    log.info(banner("/Vivado Simulation", False))
    return 0

HelpItem("command", (common.NAME, "xsim"), "Run a precompiled Vivado Simulation", [
    HelpOption("attribute", "check", "bool", "true", "Run the logchecker"),
    HelpOption("attribute", "using", "tree", "load a result with simulation files"),
    HelpProxy("function", (common.NAME, "do_sim")),
    HelpProxy("function", (common.NAME, "do_check"))
])
def cmd_xsim(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(LOGNAME)
    log.info(banner("Vivado Simulation"))

    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_SIM_FLAGS
    log.debug(f"compile config flags:{flags}")
    fcfg = cfg.move(addFlags=set(flags))

    wd = pipe.initWorkDir()
    check = fcfg.get(".check", default=True, isType=bool)
    vars = roadrunner.modules.files.handleFiles(fcfg, wd, pipe)

    result = fcfg.get(".using.files", isOsPath=True)
    workdir_import(wd, result, targetDir=Path("."))

    do_sim(fcfg, wd, vrsn, pipe, vars)
    if check:
        do_check(wd, vrsn, pipe)

    log.info(banner("/Vivado Simulation"))
    return 0

HelpItem("function", (common.NAME, "do_compile"), "run xvlog", [
    HelpOption("attribute", "flags", "list[str]", "ConfigContext Flags used"),
    HelpProxy("function", (common.NAME, "do_verilogFiles"))
])
def do_compile(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline, vars):
    etype((cfg,ConfigContext), (wd,Path), (vs,str), (pipe,Pipeline))
    log = logging.getLogger(LOGNAME)

    #files, env
    envfile = roadrunner.modules.verilog.writeEnvFile(wd, vars)

    #verilog
    do_verilogFiles(cfg, wd, pipe, [relpath(envfile, wd)])
    call = Call(wd, 'xvlog', common.NAME, vs)
    call.addArgs(['xvlog', '--prj', 'xvlog.prj'])
    pipe.addCall(call)

    #vhdl - skip
    do_vhdlFiles(cfg, wd, pipe)
    call = Call(wd, 'xvhdl', common.NAME, vs)
    call.addArgs(['xvhdl', '--prj', 'xvhdl.prj'])
    pipe.addCall(call)

HelpItem("function", (common.NAME, "gatherOptions"), "gather Vivado specific options",[
    HelpOption("attribute", "xilinxFeatures", "list[str]", None, "Vivado options"),
    HelpOption("attribute", "libs", "list[str]", None, "Vivado libraries"),
    HelpOption("attribute", "dpi_libpath", "list[str]", None, "DPI library paths")
])
def gatherOptions(cfg:ConfigContext):
    options = []
    libs = []
    dpi = []
    for itm in cfg.move(addFlags=roadrunner.modules.verilog.CONFIG_FLAGS).travers():
        uniqueExtend(options, itm.get('.xilinxFeatures', mkList=True, default=[]))
        uniqueExtend(libs, itm.get('.xilinxLibs', mkList=True, default=[]))
        uniqueExtend(dpi, itm.get('.dpi_libpath', mkList=True, default=[]))
    etype((options,list,str), (libs,list,str))
    return options, libs, dpi

HelpItem("function", (common.NAME, "do_verilogFiles"), "gather HDL files and write them to project file", [
    HelpProxy("module", ("verilog", "includeFiles")),
    HelpProxy("function", (common.NAME, "gatherOptions"))
])
def do_verilogFiles(cfg:ConfigContext, wd:Path, pipe:Pipeline, addFiles:list[Path]):
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline), (addFiles,list,Path))

    lst = roadrunner.modules.verilog.includeFiles(cfg.move(), wd)

    options, _, __ = gatherOptions(cfg)

    files = []

    if 'useGlbl' in options:
        fname = pipe.loadfile('Vivado', 'glbl', 'glbl.v')
        files += [('verilog', fname, [], [])]

    for fname in addFiles:
        typ = "sv" if fname.suffix == '.sv' else "verilog"
        files += [(typ, fname, [], [])]

    for itm in lst:
        defs = itm.defines + DEFAULT_SIM_DEFINES
        incs = itm.path
        files += [('sv', fname, defs, incs) for fname in itm.sv]
        files += [('verilog', fname, defs, incs) for fname in itm.v]
        #files += [('vhdl', fname, defs, incs) for fname in rr.workdir_import(wd, itm['vhdl'])]

    #remove duplicates
    tmp = files
    files = []
    for itm in tmp:
        if itm not in files:
            files.append(itm)

    #xvlog
    with open(wd / "xvlog.prj", "w") as fh:
        for typ,fname,defs,incs in files:
            if typ not in ['sv', 'verilog']:
                continue
            line = f"{typ} work {fname}"
            for d in defs:
                line += f" -d {d}"
            for i in incs:
                line += f" -i {i}"
            print(line, file=fh)

HelpItem("function", (common.NAME, "do_vhdlFiles"), "gather HDL files and write them to project file", [
    HelpProxy("module", ("vhdl", "includeFiles")),
    HelpProxy("function", (common.NAME, "gatherOptions"))
])
def do_vhdlFiles(cfg:ConfigContext, wd:Path, pipe:Pipeline, addFiles:list[Path]=[]):
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline), (addFiles,(list,None),Path))

    lst = roadrunner.modules.vhdl.includeFiles(cfg.move(), wd)

    options, _, __ = gatherOptions(cfg)

    files = []

    for fname in addFiles:
        files += [(fname, [], [])]

    for itm in lst:
        defs = itm.defines + DEFAULT_SIM_DEFINES
        incs = itm.path
        files += [(fname, defs, incs) for fname in itm.vhdl]

    #remove duplicates
    tmp = files
    files = []
    for itm in tmp:
        if itm not in files:
            files.append(itm)

    #xvlog
    with open(wd / "xvhdl.prj", "w") as fh:
        for fname,defs,incs in files:
            line = f"vhdl work {fname}"
            print(line, file=fh)

HelpItem("function", (common.NAME, "do_dpi"), "run xsc", [
    HelpProxy("module", ("cpp", "includeFiles"))
])
def do_dpi(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline):
    etype((cfg,ConfigContext), (wd,Path), (vs,str), (pipe,Pipeline))
    log = logging.getLogger(LOGNAME)

    lst = roadrunner.modules.cpp.includeFiles(cfg.move(), wd)
    if lst == []:
        log.info("No DPI files items found - skip")
        return 0

    sources = []
    libs = []
    libpaths = []
    paths = []
    std = None
    for itm in lst:
        uniqueExtend(sources, map(str, itm.c))
        uniqueExtend(sources, map(str, itm.cpp))
        uniqueExtend(libs, map(str, itm.lib))
        uniqueExtend(paths, map(str, itm.path))
        uniqueExtend(libpaths, map(str, itm.libpath))
        if itm.std is not None:
            if std is not None and itm.std != std:
                log.warning("multiple different C standards defined - using first found")
            else:
                std = itm.std

    if len(sources) == 0:
        log.info("No DPI files found - skip")
        return 0

    call = Call(wd, "xsc", common.NAME, vs)
    call.addArgs(["xsc"])
    call.addArgs(sources)
    for path in paths:
        call.addArgs(['-gcc_compile_options', f'-I{path}'])
    for lib in libpaths:
        call.addArgs(['-gcc_link_options', f'-L{lib}'])
    for lib in libs:
        call.addArgs(['-gcc_link_options', f'-l{lib}'])
    if std is not None:
        call.addArgs(['-gcc_compile_options', f'-std={std}'])

    pipe.addCall(call)

HelpItem("function", (common.NAME, "do_elab"), "run xelab", [
    HelpOption("attribute", "toplevel", "str", None, "Top level module"),
    HelpProxy("function", (common.NAME, "gatherOptions")),
    HelpOption("attribute", "optimize", "int", None, "Optimization level"),
    HelpOption("attribute", "params", "list[str]", None, "Generic parameters passed to the top level module")
])
def do_elab(cfg:ConfigContext, wd:Path, pipe:Pipeline):
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline))
    log = logging.getLogger(LOGNAME)

    toplevels = cfg.get(".toplevel", mkList=True)
    options, libs, _ = gatherOptions(cfg)
    optimize = cfg.get('.optimize', default=None, isType=int)
    params = cfg.get('.params', mkList=True, default=[])

    dpiLibs = ['dpi'] if (wd / 'xsim.dir/work/xsc/dpi.so').exists() else []

    if 'useGlbl' in options:
        toplevels.append('glbl')
    if 'useXPMMem' in options:
        libs.append('xpm')

    #cmd
    call = Call(wd, "xelab", tool=common.NAME)
    call.addArgs(['xelab'])
    for l in dpiLibs:
        call.addArgs(['-sv_lib', l])
    if optimize is not None:
        call.addArgs([f'-O{optimize}'])
    call.addArgs(['--relax', '--incr', '--debug', 'typical'])
    for lib in libs:
        call.addArgs(['-L', lib])
    call.addArgs(['--snapshot', 'rrun.snap'])
    for par in params:
        call.addArgs(['-generic_top', str(par)])
    call.addArgs(toplevels)

    pipe.addCall(call)

HelpItem("function", (common.NAME, "do_sim"), "run xsim", [
    HelpProxy("module", ("files", "share")),
    HelpProxy("function", (common.NAME, "gatherOptions")),
    HelpOption("attribute", "gui", "bool", "false", "Start GUI"),
    HelpOption("attribute", "view", "str", None, "View file for Vivado to setup the viewport"),
])
def do_sim(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline, vars:dict):
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline), (vs, (None,str)))
    log = logging.getLogger(LOGNAME)

    roadrunner.modules.files.share(cfg, pipe)
 
    _, __, dpiLibs = gatherOptions(cfg)

    roadrunner.modules.tcl.writeEnvFile(wd, vars)

    usegui = cfg.get('.gui', default=None)
    view = cfg.get('.view', default=None, isOsPath=True)

    if view is not None:
        view_file = workdir_import(wd, view)


    call = Call(wd, 'xsim', tool=common.NAME, version=vs)
    if len(dpiLibs):
        call.setenv('LD_LIBRARY_PATH', ":".join([str(x) for x in dpiLibs]))
    call.addArgs(['xsim', 'rrun.snap'])
    if usegui:
        call.addArgs(['-gui'])
        if view:
            call.addArgs(['-view', view_file])
    else:
        call.addArgs(['--runall'])

    pipe.addCall(call)
    return 0

HelpItem("function", (common.NAME, "do_check"), "run logcheck", [])
def do_check(wd:Path, pipe:Pipeline):
    with open(wd / "logcheck.py", "w") as fh:
        print(asset(Path('rr/logcheck.py')).source, file=fh)
    call = Call(wd, 'logcheck', common.PYTHON_ENV)
    call.addArgs(['python3', 'logcheck.py', 'xsim.stdout'])
    pipe.addCall(call)
