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
from roadrunner.help import HelpItem, HelpOption
from roadrunner.rr import Pipeline, workdir_import

NAME = "py"
LOGNAME = "Python" #use the logger of the tool wrapper

HelpItem("module", (NAME, "includeModules"), "include python modules", [
    HelpOption("attribute", "pymod", "str|list[str]", None, "modules to include"),
])

def includeModules(cfg:ConfigContext, wd:Path, pipe:Pipeline) -> set[Path]:
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline))

    #
    log = logging.getLogger(LOGNAME)
    paths = set()
    log.debug(f"gathering modules from:{cfg.pos()} flags:{cfg.flags()}")
    for curr in cfg.travers():
        real = curr.real()
        log.debug(f"gather @:{real.pos()} flags:{real.flags()}")
        for mod in curr.get(".pymod", default=[], mkList=True, isOsPath=True):
            res = workdir_import(wd, mod)
            log.debug(f"gathered: {res}")
            path = str(res.parent)
            paths.add(path)
    return {Path(x) for x in paths}

def pythonVars(vars:dict) -> str:
    data = []
    for name,val in vars.items():
        data.append(f"{name}={val.__repr__()}")
    return "\n".join(data)

