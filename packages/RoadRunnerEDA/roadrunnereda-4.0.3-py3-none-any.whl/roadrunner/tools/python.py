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
from roadexec.fn import etype
from roadrunner.config import ConfigContext

import roadrunner.modules.files
import roadrunner.modules.python
from roadrunner.fn import banner
from roadrunner.help import HelpItem, HelpOption, HelpProxy
from roadrunner.rr import Pipeline, workdir_import, Call

NAME = "Python"

DEFAULT_FLAGS = ['Python']

HelpItem("tool", NAME, "runs python scripts")

HelpItem("command", (NAME, "run"), "run a script", [
       HelpOption("attribute", "flags", "list[str]", None, "additional flags to be used"),
       HelpOption("attribute", "script", "str", None, "inline python script to be executed (after the scriptFile if any)"),
       HelpOption("attribute", "scriptFile", "file", None, "python script to be invoked (before inline script if any)"),
       HelpProxy("module", ('py', 'includeModules'))
])
def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    logg = logging.getLogger(NAME)
    logg.info(banner("Python"))

    wd = pipe.initWorkDir()

    #flags
    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_FLAGS
    interactive = cfg.get('.interactive', isType=bool, default=False)
    logg.debug(f"using flags:{flags}")

    pipe.enterCall(NAME)
    fcfg = cfg.move(addFlags=set(flags))
    roadrunner.modules.files.share(fcfg, pipe)
    vars = roadrunner.modules.files.handleFiles(fcfg, wd, pipe)
    paths = roadrunner.modules.python.includeModules(fcfg, wd, pipe)

    paths.add(Path('.'))
    pypaths = list(paths)

    #script file to source at start
    scriptSource = fcfg.get(".scriptFile", isOsPath=True, default=None)
    if scriptSource:
        scriptFile = workdir_import(wd, scriptSource)
    else:
        scriptFile = None

    #script content
    scriptInline = fcfg.get(".script", isType=str, default=None)
    
    with open(wd / "rrenv.py", "w") as fh:
        print(f"# Environment", file=fh)
        print(roadrunner.modules.python.pythonVars(vars), file=fh)

    if scriptInline is None:
        script = scriptFile
    else:
        with open(wd / "inline.py", "w") as fh:
            #origin = cnf.get(".script").origin #TODO get origin from ConfigContext
            print("from rrenv import *", file=fh)
            if scriptFile:
                print(f"ScriptFile {scriptFile}")
                print(f"exec(open('{scriptFile}').read())")
            #print(f"# Script ({origin})", file=fh)
            print(f"# Script ()", file=fh)
            print(scriptInline, file=fh)

    script = scriptFile or Path("inline.py")

    args = fcfg.get('.args', mkList=True, default=[])

    call = Call(wd, "python", "Python3", vrsn)
    for key,val in vars.items():
        call.envSet(key, val)
    call.addArgs(["python3", '-u']) #no output buffering
    call.addArgs([str(script)])
    call.addArgs(args)
    call.envAddPaths('PYTHONPATH', pypaths)

    pipe.useCall(call, interactive)
    logg.info(banner("/Python", False))
    pipe.leave()

    return 0
