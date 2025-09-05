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
from roadrunner.fn import banner, etype, relpath
from roadrunner.help import HelpItem, HelpOption, HelpProxy
from roadrunner.rr import Call, Pipeline, asset, renderTemplate
from roadrunner.tools.vcs import common
import roadrunner.modules.files
import roadrunner.modules.verilog
import roadrunner.modules.tcl
import roadrunner.modules.cpp

LOGNAME = "VCSSim"

DEFAULT_SIM_FLAGS = ["SIMULATION"] + common.DEFAULT_FLAGS
DEFAULT_SIM_DEFINES = ["SIMULATION"] + common.DEFAULT_DEFINES

HelpItem("command", (common.NAME, "sim"), "Run VCS simulation",[
    HelpOption("attribute", "check", "bool", "true", "Run the logchecker"),
    HelpProxy("module", ("files", "handleFiles")),
    HelpProxy("function", (common.NAME, "do_compile")),
    #HelpProxy("function", (common.NAME, "do_dpi")),
    HelpProxy("function", (common.NAME, "do_elab")),
    HelpProxy("function", (common.NAME, "do_sim")),
    HelpProxy("function", (common.NAME, "do_check"))
])
def cmd_sim(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(LOGNAME)
    log.info(banner("VCS Simulation"))
             
    wd = pipe.initWorkDir()

    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_SIM_FLAGS
    log.debug(f"flags:{flags}")
    fcfg = cfg.move(addFlags=set(flags))

    check = fcfg.get(".check", default=True, isType=bool)

    vars = roadrunner.modules.files.handleFiles(fcfg, wd, pipe)

    with pipe.inSequence(LOGNAME):
        do_compile(fcfg, wd, vrsn, pipe, vars)
        #do_dpi(fcfg, wd, pipe)
        do_elab(fcfg, wd, vrsn, pipe)

        do_sim(fcfg, wd, vrsn, pipe, vars)
        if check:
            do_check(wd, pipe)

    log.info(banner("/VCS Simulation", False))
    return 0

HelpItem("function", (common.NAME, "do_compile"), "run vlogan", [
    HelpOption("attribute", "flags", "list[str]", "ConfigContext Flags used"),
    HelpProxy("function", (common.NAME, "do_verilogFiles"))
])
def do_compile(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline, vars):
    etype((cfg,ConfigContext), (wd,Path), (vs,(str,None)), (pipe,Pipeline))
    log = logging.getLogger(LOGNAME)

    #files, env
    envfile = roadrunner.modules.verilog.writeEnvFile(wd, vars)

    #verilog
    do_verilogFiles(cfg, wd, vs, pipe, [relpath(envfile, wd)])

def opt_waves(cfg:ConfigContext) -> tuple[bool, bool]:
    log = logging.getLogger(LOGNAME)
    waves = cfg.get('.waves', mkList=True, default=[]) #fsdb or vcd
    usevcd = 'vcd' in waves
    usefsdb = ('fsdb' in waves) or usevcd #vcd need the fsdb first
    return usefsdb, usevcd

HelpItem("function", (common.NAME, "do_verilogFiles"), "gather HDL files and write them to command file", [
    HelpProxy("module", ("verilog", "includeFiles"))
])
def do_verilogFiles(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline, addFiles:str):
    etype((cfg,ConfigContext), (wd,Path), (vs,(str,None)), (pipe,Pipeline), (addFiles,list,Path))

    usegui = cfg.get('.gui', isType=bool, default=False)
    usefsdb, usevcd = opt_waves(cfg)
    lst = roadrunner.modules.verilog.includeFiles(cfg.move(), wd)

    params = [
        '-full64',  #enable 64-bit simulation
        '-sverilog', #enable systemverilog
        '-assert', 'svaext' #enable sv assertion extension for elaboration system tasks
    ]
    if usegui or usefsdb or usevcd: 
        params.append('-kdb')
    #-override_timescale=time_unit/time_precision   #override in all files
    #-timescale=time_unit/time_precision            #value for files that don't have
    #-u changes all character ???

    #if usefsdb:
    #    data = renderTemplate(Path('vcs') / "RRWaves.sv", {})
    #    with open(wd / "RRWaves.sv", "w") as fh:
    #        fh.write(data)
    #        addFiles += ["RRWaves.sv"]

    call = Call(wd, "vlogan", common.NAME, vs)
    call.addArgs(['vlogan'] + params)
    call.addArgs(map(str, addFiles))
    call.nextCmd()

    hist = []

    for itm in lst:
        args = []
        hasFile = False
        args += ['vlogan'] + params
        defs = itm.defines + DEFAULT_SIM_DEFINES
        incs = itm.path
        for d in defs:
            args.append(f"+define+{d}")
        for i in incs:
            args.append(f"+incdir+{i}")
        for fname in itm.v + itm.sv:
            key = (fname, defs, incs)
            if key in hist:
                continue
            hist.append(key)
            args.append(str(fname))
            hasFile = True
        if hasFile:
            call.addArgs(args)
            call.nextCmd()

    pipe.addCall(call)


HelpItem("function", (common.NAME, "do_elab"), "run xelab", [
    HelpOption("attribute", "toplevel", "str", None, "Top level module"),
])
def do_elab(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline):
    etype((cfg,ConfigContext), (wd,Path), (vs,(str,None)), (pipe,Pipeline))
    log = logging.getLogger(LOGNAME)

    toplevels = cfg.get(".toplevel", mkList=True)

    vpi = do_vpi(cfg, pipe, wd, vs)

    #+vcs+fsdbon    #write fsdb file of whole design
    # 
    #-sverilog      #systemverilog support
    #+vpi           #VPI enabled
    #+memcbk        #enabel callbacks doe memories and multidimentional arrays
    #+vcsd          #??
    #+vcs+dumparrays    #enable dumping memory and arrays
    #-vcd           #vcd file name
    #+vcdfile       #same
    #+vcs+dumpvars  #start vcd dump

    #cmd
    call = Call(wd, "elab", tool=common.NAME, version=vs)
    call.addArgs(['vcs'])
    call.addArgs(['-full64'])
    if len(vpi):
        call.addArgs(['+vpi'])
        for so,fn in vpi:
            call.addArgs(["-load", f"./{so}:{fn}"])
    call.addArgs(['-kdb'])          #needed for verdi?
    call.addArgs(['-debug_access+r'])
    #if usevcd or usefsdb:
    #    call.addArgs(['-debug_region=cell+encrypt']) #replacement for +memcbk +vcsd
    #    call.addArgs(['-sverilog', '+vpi', '+plusarg_save', '+vcs+dumparrays'])
    #if usevcd:
    #    call.addArgs(['+vcs+dumpvars?waves.vcd']) #automatic dumpvars start
    #if usefsdb or usevcd:
    #    call.addArgs(['+vcs+fsdbon'])
    call.addArgs(toplevels)

    pipe.addCall(call)

HelpItem("function", (common.NAME, "do_sim"), "run xsim", [
    HelpProxy("module", ("files", "share")),
    HelpOption("attribute", "gui", "bool", "false", "Start GUI"),
])
def do_sim(cfg:ConfigContext, wd:Path, vs:str, pipe:Pipeline, vars:dict):
    etype((cfg,ConfigContext), (wd,Path), (vs,(str,None)), (pipe,Pipeline))
    log = logging.getLogger(LOGNAME)

    roadrunner.modules.files.share(cfg, pipe)
 
    roadrunner.modules.tcl.writeEnvFile(wd, vars)

    usegui = cfg.get('.gui', isType=bool, default=False)
    usefsdb, usevcd = opt_waves(cfg)

    if usefsdb:
        with open(wd / "ucli.tcl", "w") as fh:
            print("dump -file waves.fsdb -type FSDB", file=fh)
            print("dump -add . -fsdb_opt +struct", file=fh)
            print("run", file=fh)

    call = Call(wd, 'vcsSim', tool=common.NAME, version=vs)
    call.addArgs(['./simv'])
    if usegui:
        call.addArgs(['-verdi'])
    if usefsdb:
        call.addArgs(['-ucli', '-i', 'ucli.tcl'])
    if usegui and usefsdb:
        log.warning("simultaneous GUI mode and DB dumping may have unexpected results")
    #if usefsdb or usevcd:
    #    call.addArgs(["+fsdbfile+waves.fsdb"])
    #    call.addArgs(['+vcs+dumparrays'])
    #if usevcd:
    #    #call.addArgs(['+vcs+dumpfile+waves.vcd', '+vcs+dumparrays'])
    pipe.addCall(call)

    if usevcd:
        call = Call(wd, "fsdb2vcd", tool=common.NAME, version=vs)
        call.addArgs(['fsdb2vcd', 'waves.fsdb', '-o', 'waves.vcd'])
        pipe.addCall(call)

    if usefsdb or usevcd:
        pipe.result()
    if usefsdb:
        pipe.export("waves.fsdb", group="fsdb")
    if usevcd:
        pipe.export("waves.vcd", group="vcd")

    return 0

HelpItem("function", (common.NAME, "do_check"), "run logcheck", [])
def do_check(wd:Path, pipe:Pipeline):
    with open(wd / "logcheck.py", "w") as fh:
        print(asset(Path('rr/logcheck.py')).source, file=fh)
    call = Call(wd, 'logcheck', "Python3")
    call.addArgs(['python3', 'logcheck.py', 'vcsSim.stdout'])
    pipe.addCall(call)

HelpItem("function", (common.NAME, "vpi"), "compile and link vpi files", [
    HelpProxy("module", ("cpp", "includeFiles"))
])
def do_vpi(cfg:ConfigContext, pipe:Pipeline, wd:Path, vs:str) -> list[Path]:
    log = logging.getLogger(common.NAME)

    libs = [] #(shared object, startup function)
    used = []

    call = Call(wd, "vpi", common.NAME, vs)
    for vnode in cfg.travers():
        node = vnode.real()
        try:
            vpiMod = node.move(".vpiModule")
        except PathNotExist:
            continue
        if node.pos() in used:
            continue
        used.append(node.pos())
        #startup FN
        startFn = vpiMod.get(".startup", isType=str)
        #gcc -w  -pipe -fPIC -O -I/opt/synopsys/vcs/V-2023.12/include    -c ../greeter.c
        name = str(node.pos()).replace(".", "_")[1:]
        libFile = f"vpi_{name}.so"
        call.addArgs(["gcc", "-w", "-fPIC", "-O", "-shared"])
        call.addArgs(["-o", libFile])
        call.addArgs(["-I", "$VCS_HOME/include"])
        for itm in roadrunner.modules.cpp.includeFiles(vpiMod, wd):
            for path in itm.path:
                call.addArgs([f'-I{path}'])
            for lib in itm.libpath:
                call.addArgs([f'-L{lib}'])
            for lib in itm.lib:
                call.addArgs([f'-l{lib}'])
            if itm.std is not None:
                call.addArgs([f'-std={itm.std}'])
            call.addArgs(list(map(str, itm.c)))
            call.addArgs(list(map(str, itm.cpp)))
        call.nextCmd()
        libs.append((libFile, startFn))
    if len(libs):
        pipe.addCall(call)
    return libs

