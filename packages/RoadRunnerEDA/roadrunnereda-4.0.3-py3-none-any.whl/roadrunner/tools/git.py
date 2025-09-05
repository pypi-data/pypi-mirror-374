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
from roadrunner.fn import etype
from roadrunner.config import ConfigContext
from roadrunner.rr import Call, Pipeline, workdir_import


NAME = "Git"
DESCRIPTION = "clone git repositories into results"

def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger("NAME")
    wd = pipe.initWorkDir()
    with pipe.inCall(NAME):
        pipe.result()
        fcfg = cfg
        repo = fcfg.get(".repo", isType=str)
        branch = fcfg.get(".branch", default=None, isType=str)
        config = fcfg.get(".config", default=None, isOsPath=True)
        if config:
            log.info(f"Using config: {config}")
            configFile = workdir_import(wd, config, targetName=Path("RR"))
            pipe.export("RR", configFile.parent)

        call = Call(wd, "git", NAME, vrsn)
        call.addArgs(["git", "clone", repo, "result"])
        if branch:
            call.addArgs(["-b", branch])
        pipe.useCall(call)

    return 0