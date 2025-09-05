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

from roadrunner.config import ConfigContext
import subprocess
import logging
import sys

from roadrunner.rr import Pipeline, workdir_name, resultBase
from roadrunner.tasks import taskPool

def run(cfg:ConfigContext) -> int:

    wd = workdir_name(cfg)
    rd = resultBase(cfg)
    ard = rd.absolute()

    args = [sys.executable, Pipeline.SCRIPTNAME]
    args += ["--setup", f"RoadExec:resultDir={ard}"]
    args += cfg.get(":_run.runArgs", isType=list, default=[])

    isRoot = taskPool().getCurrTask().isRoot()

    log = logging.getLogger("local")
    log.debug(f"running:{args} at:{wd}")
    stdio = None if isRoot else subprocess.DEVNULL
    cp = subprocess.run(
        cwd=wd,
        args=args,
        stdout=stdio,
        stderr=stdio
    )

    return cp.returncode
