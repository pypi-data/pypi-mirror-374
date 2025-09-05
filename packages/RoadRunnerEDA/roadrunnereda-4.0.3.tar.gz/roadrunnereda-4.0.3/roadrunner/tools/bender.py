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
from roadrunner.config import ConfigContext, Location
from roadrunner.fn import clone, etype
from roadrunner.help import HelpItem, HelpOption
from roadrunner.rr import Call, Pipeline, asset, workdir_import


NAME = "Bender"
HelpItem("tool", NAME, "Bender dependency manager")


HelpItem("command", (NAME, "run"), "import dependencies from a bender.yml to a result", [
    HelpOption("attribute", "benderDir", "path", None, "directory where to find the bender.yaml and bender.lock"),
    HelpOption("attribute", "targets", "list[str]", "[]", "list of or single target to pass to bender"),
    HelpOption("attriubte", "local", "list[str]", "[]", "glob patterns of files that belong to the bender repository itself and not to the dependencies")
])
def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    log = logging.getLogger(NAME)
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    wd = pipe.initWorkDir()

    benderDir = cfg.get(".benderDir", isOsPath=True)
    benderPath = benderDir[0] / benderDir[1]
    log.debug(f"benderDir:{benderPath}")

    targets = cfg.get(".target", default=[], mkList=True)
    log.debug(f"target: {targets}")

    for itm in cfg.get('.local', mkList=True, default=[]):
        count = 0
        for fitm in benderPath.glob(itm):
            log.debug(f"glob:{fitm}")
            clone(fitm, wd / fitm.name)
            count += 1
        if count == 0:
            log.warning(f"local:{itm} nohting imported")
        elif count == 1:
            log.info(f"local:{itm} imported")
        else:
            log.info(f"local:{itm} imported:{count} items")

    with pipe.inSequence(NAME):
        benderFile = (Location(benderPath), Path("Bender.yml"))
        workdir_import(wd, benderFile, targetDir=Path(""))
        benderLock = (Location(benderPath), Path("Bender.lock"))
        workdir_import(wd, benderLock, targetDir=Path(""))

        pipe.result()
        call = Call(wd, "checkout", NAME, vrsn)
        call.addArgs(["bender", "checkout"])
        pipe.addCall(call)

        baseCall = ["bender", "script", "template"]
        for tg in targets:
            baseCall += ["--target", tg]
        call = Call(wd, "genrr", NAME, vrsn)
        snip = asset(Path("bender/rr.tera"))
        with open(wd / "rr.tera", "w") as fh:
            fh.write(snip.source)
        call.addArgs(baseCall + ["--template", "rr.tera", ">", "result/RR"])
        pipe.addCall(call)

        call = Call(wd, "genex", NAME, vrsn)
        snip = asset(Path("bender/export.tera"))
        with open(wd / "export.tera", "w") as fh:
            fh.write(snip.source)
        call.addArgs(baseCall + ["--template", "export.tera", ">", "export.sh"])
        pipe.addCall(call)

        call = Call(wd, "export", NAME, vrsn)
        call.addArgs(['sh', 'export.sh'])
        pipe.addCall(call)

    return 0