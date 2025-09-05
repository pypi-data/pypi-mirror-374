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
from roadrunner.config import ConfigContext, PathNotExist
from roadrunner.fn import relpath,  etype
from roadrunner.help import HelpItem, HelpOption, HelpProxy
from roadrunner.rr import Call, Pipeline, asset, renderTemplate, workdir_import
import roadrunner.modules.files
import roadrunner.modules.cpp
import roadrunner.modules.verilog


NAME = "Icarus"
HelpItem("tool", NAME, "Icarus Verilog")

PYTHON_ENV = "Python3" #this is the nameof the python tool for logcheck

DEFAULT_SIM_FLAGS = ['SIMULATION', 'ICARUS', 'VPI']

HelpItem("command", (NAME, "compile"), "compile verilog files to a form that can be executed by vvp", [
    HelpOption("attribute", "result", "str", None, "named of the result to receive the simulation environment"),
    HelpOption("attribute", "flags", "str", None, "flags to be used in the ConfigContext"),
    HelpProxy("module", ("files", "share")),
    HelpProxy("function", (NAME, "compile"))
])
def cmd_compile(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    wd = pipe.initWorkDir()

    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_SIM_FLAGS
    fcfg = cfg.move(addFlags=set(flags))

    with pipe.inSequence(NAME):
        roadrunner.modules.files.share(fcfg, pipe)

        vpi = do_compile(fcfg, wd, vrsn, pipe)
        pipe.result()
        pipe.export("sim.vvp", group="vvp")
        if vpi:
            pipe.export("sim.vpi", group="vpi")

    return 0

HelpItem("command", (NAME, "sim"), "run a pre-compiled simulation", [
    HelpOption("attribute", "flags", "str", None, "flags to be used in the ConfigContext"),
    HelpOption("attribute", "check", "bool", "true", "run the simulation log checker"),
    HelpOption("attribute", "using", "tree", None, "simulation to use - this could be a result loader from a compile call"),
    HelpOption("attribute", "using.vvp", "file", None, "vvp file to use"),
    HelpOption("attribute", "using.vpi", "file", None, "vpi file to use"),
    HelpProxy("module", ("files", "share")),
])
def cmd_sim(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    wd = pipe.initWorkDir()

    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_SIM_FLAGS
    fcfg = cfg.move(addFlags=set(flags))


    vvpName = workdir_import(wd, fcfg.get(".sim.vvp", isOsPath=True))
    try:
        vpiName = workdir_import(wd, fcfg.get(".sim.vpi", isOsPath=True))
    except PathNotExist:
        vpiName = []

    check = cfg.get(".check", default=True, isType=bool)

    with pipe.inSequence(NAME):
        roadrunner.modules.files.share(fcfg, pipe)
        do_run(wd, vrsn, pipe, vvpName, vpiName, check)

    return 0

HelpItem("command", (NAME, "run"), "compile and run a simulation", [
    HelpOption("attribute", "flags", "str", None, "flags to be used in the ConfigContext"),
    HelpOption("attribute", "check", "bool", "true", "run the simulation log checker"),
    HelpProxy("module", ("files", "share")),
    HelpProxy("function", (NAME, "compile"))
])
def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    wd = pipe.initWorkDir()

    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_SIM_FLAGS
    fcfg = cfg.move(addFlags=set(flags))

    with pipe.inSequence(NAME):
        roadrunner.modules.files.share(fcfg, pipe)

        vpi = do_compile(fcfg, wd, vrsn, pipe)

        check = cfg.get(".check", default=True, isType=bool)

        do_run(wd, vrsn, pipe, Path("sim.vvp"), vpi, check)

    return 0

HelpItem("function", (NAME, "compile"), "gather (systemverilog) files and compile then to vvp", [
    HelpProxy("module", ("files", "handleFiles")),
    HelpProxy("function", (NAME, "verilogFiles")),
    HelpOption("attribute", "toplevel", "str", None, "toplevel module name"),
])
def do_compile(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline):
    etype((cfg,ConfigContext), (wd,Path), (vs,(str,None)), (pipe,Pipeline))

    vars = roadrunner.modules.files.handleFiles(cfg, wd, pipe)
    envfile = roadrunner.modules.verilog.writeEnvFile(wd, vars)

    #-o output file
    #-f -c command file
    #-D macro
    #-m VPI module to load
    #-s toplevel
    #-y library module search path
    #.sft system function table for vpi

    do_VerilogFiles(cfg, wd, vs, pipe, [relpath(envfile, wd)])

    vpiMods = do_vpi(cfg, pipe, vs)

    toplevel = cfg.get(".toplevel")

    #compile
    call = Call(wd, 'iverilog', NAME, vs)
    call.addArgs(['iverilog'])
    call.addArgs(['-u'])            #separate compilation units
    call.addArgs(['-g2012'])        #use 2012 standard
    call.addArgs(['-o', 'sim.vvp']) #output file
    call.addArgs(['-c', 'verilogFiles.cmd']) #command file
    call.addArgs(['-s', toplevel])
    pipe.addCall(call)
    return vpiMods

def do_run(wd:Path, vs:str, pipe:Pipeline, vvp:Path, vpi:list[str], check:bool=True):
    etype((wd,Path), (vs,(str,None)), (pipe,Pipeline), (vvp,Path), (vpi,list,str), (check,bool))
    #run
    call = Call(wd, 'vvp', NAME, vs)
    call.addArgs(['vvp'])
    call.addArgs(['-n']) #$stop is like $finish
    call.addArgs(['-M', '.'])
    for vm in vpi:
        call.addArgs(['-m', vm])
    call.addArgs([str(vvp)])
    pipe.addCall(call, abortOnError=False)
    #check logs
    if check:
        snip = asset(Path('rr/logcheck.py'))
        with open(wd / "logcheck.py", "w") as fh:
            print(snip.source, file=fh)
        call = Call(wd, 'logcheck', PYTHON_ENV)
        call.addArgs(['python3', 'logcheck.py', 'vvp.stdout'])
        pipe.addCall(call)

HelpItem("function", (NAME, "verilogFiles"), "gather verilog files and create a command file for iverilog", [
    HelpProxy("module", ("verilog", "includeFiles")),
    HelpOption("attribute", "timescale", "str", None, "set the Icarus timescale directive - for sources that don't do that"),
])
def do_VerilogFiles(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline, addFiles:list=[]):
    etype((cfg,ConfigContext), (wd,Path), (vs,(str,None)), (pipe,Pipeline), (addFiles, list, Path))

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

    #preprocessing
    with open(wd / "verilogFiles.cmd", "w") as fh:
        if timescale is not None:
            print(f"+timescale+{timescale}", file=fh)
        call = Call(wd, f"iverilog.prep", NAME, vs)
        for fname,defs,incs in files:
            suffix = fname.suffix
            dname = fname.with_suffix('.pre' + suffix)
            call.addArgs(['iverilog'])
            call.addArgs(['-E']) #preprocess only
            call.addArgs(['-o', str(dname)])
            for d in defs:
                call.addArgs([f"-D{d}"])
            for i in incs:
                call.addArgs([f"-I{i}"])
            call.addArgs([str(fname)])
            call.nextCmd()
            print(str(dname), file=fh)   
        pipe.addCall(call)

HelpItem("function", (NAME, "vpi"), "compile and link vpi files", [
    HelpProxy("module", ("cpp", "includeFiles"))
])
def do_vpi(cfg:ConfigContext, pipe:Pipeline, vs:str) -> list[str]:
    log = logging.getLogger(NAME)
    wd = pipe.cwd()

    vpiMods = []
    used = []

    call = Call(wd, f"vpi", NAME, vs)
    for itm in cfg.travers():
        #see if there is a vpiModule defined here
        try:
            vpiMod = itm.move(".vpiModule")
        except PathNotExist:
            continue
        realPos = itm.real().pos()
        if realPos in used:
            continue
        used.append(realPos)
        #generate name
        name = str(itm.real().pos()).replace(".", "_")[1:]
        log.info(f"found VPI Module:{name} @:{vpiMod.real().path()}")
        #startup function
        startFn = vpiMod.get(".startup", isType=str)
        #generate entry point
        entryFile = Path(f"vpi{name}/entry.c")
        log.debug(f"generate vpi entry for startFn:{startFn} in {entryFile}")
        (wd / entryFile).parent.mkdir(parents=True, exist_ok=True)
        with open(wd / entryFile, "w") as fh:
            print(renderTemplate(Path("icarus/vpiEntry.c"), {"startupCall": startFn}), file=fh)
        #source files
        call.addArgs(["iverilog-vpi"])
        call.addArgs([str(entryFile)])
        for fitm in roadrunner.modules.cpp.includeFiles(vpiMod, wd):
            for path in fitm.path:
                call.addArgs([f'-I{path}'])
            for lib in fitm.libpath:
                call.addArgs([f'-L{lib}'])
            for lib in fitm.lib:
                call.addArgs([f'-l{lib}'])
            if fitm.std is not None:
                call.addArgs([f'-std={fitm.std}'])
            call.addArgs(list(map(str, fitm.c)))
            call.addArgs(list(map(str, fitm.cpp)))
            call.addArgs([f"--name={name}"])
            call.nextCmd()
        #register mod
        vpiMods.append(name)
    if len(vpiMods):
        pipe.addCall(call)

    return vpiMods
