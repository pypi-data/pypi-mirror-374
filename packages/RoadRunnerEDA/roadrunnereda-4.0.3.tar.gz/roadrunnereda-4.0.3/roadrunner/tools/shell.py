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
import roadrunner.fn as fn
from roadrunner.modules.stages import Stages
import roadrunner.rr as rr
from roadrunner.config import ConfigContext
from roadrunner.rr import Pipeline
from roadrunner.modules.files import share, handleFiles, bash_val
from roadrunner.help import HelpOption, HelpItem, HelpProxy

NAME = "Shell"

HelpItem("tool", NAME, "calling shell scripts")


HelpItem("command", (NAME, "run"), "run a inline defined shell script", [
    HelpOption("attribute", "script", "str", None, "the bash script to be executed"),
    HelpProxy("module", ("files", "share")),
    HelpProxy("module", ("files", "files")),
    HelpOption("attribute", "inc", "tree", None, "hierarchical traversal of source tree")
])
def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    fn.etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    logg = logging.getLogger(NAME)
    logg.info(fn.banner(f"Shell"))
    
    wd = pipe.initWorkDir()
    pipe.enterCall("script")
    logg.debug(f"wd:{wd}")

    share(cfg, pipe)

    #collect variables
    vars = handleFiles(cfg.move(addFlags={NAME}), wd, pipe)

    #script content
    script = cfg.get(".script", isType=str)
    with open(wd / "script", "w") as fh:
        print(f"# Environment", file=fh)
        for name,val in vars.items():
            print(f"{name}={bash_val(val)}", file=fh)
        #origin = cnf.get(".script").origin
        #print(f"# Script ({origin})", file=fh)
        print("# Script", file=fh)
        print(script, file=fh)

    call = rr.Call(wd, 'script', "Shell", vrsn)
    call.addArgs(['bash', 'script'])
    pipe.useCall(call)
    pipe.leave()

    logg.info(fn.banner("Shell", False))
    return 0

def cmd_stages(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    fn.etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    logg = logging.getLogger(NAME)
    logg.info(fn.banner(f"Shell (stages)"))
    
    wd = pipe.initWorkDir()
    logg.debug(f"wd:{wd}")

    scfg = cfg.move(".stages")

    snip = rr.asset(Path("shell/mainStage.sh"))
    stages = Stages(snip, ".sh")
    stages.loadConfig(scfg)
    stagesDir = Path("stages")
    (wd / stagesDir).mkdir(exist_ok=True)
    lua = cfg.lua()
    mainPath = stages.render(wd, stagesDir, lua)

    call = rr.Call(wd, 'script', "Shell", vrsn)
    call.addArgs(['bash', str(mainPath)])
    pipe.addCall(call)

    logg.info(fn.banner("Shell (stages)", False))
    return 0
