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

import argparse
import re
from pathlib import Path
import tempfile

import roadrunner.log
from roadrunner.tasks import RootTask, Task, waitForTasks
import roadrunner.tools as tools
from roadrunner.config import ConfigContext, ConfigError, ConfigLeaf, Location, PathNotExist, makeConfigFromStr, makeConfigVal, makeConfigFromFile
from roadrunner.fn import etype, ctype
from roadrunner.rr import RRError
import os
import logging

CONFIG = {
    "_setup" : {
        "workdir_base": 'rrun',
        "result_base": 'rres',
    },
    "_run" : {
        "query": 'jabberwocky',
        "luaHooks": {},
    }
}

LOGNAME = 'rr'

# running the main roadrunner tool
def runRR(cfg:ConfigContext) -> int:
    log = logging.getLogger(LOGNAME)
    #load tools
    tools.loadtools(cfg)
    #task pool
    rtask = RootTask()
    #execute query
    queryCmd = cfg.get(":_run.query", isType=str)
    try:
        queryFn = tools.getquery(queryCmd)
    except (tools.ToolException, IndexError):
        #no query specified, defaulting to 'invoke'
        args = cfg.get(":_run.args", mkList=True, default=[])
        args.insert(0, queryCmd)
        queryCmd = "invoke"
        queryFn = tools.getquery(queryCmd)
        cfg.set(":_run.args", args)
        cfg.set(":_run.query", queryCmd)
    #run
    log.debug(f"running query:{queryCmd}")
    ret = queryFn(cfg)
    if not ctype((ret, int)):
        raise RuntimeError(f"query did not return an int - query:{queryCmd} ret:{ret}")
    if ret < 0:
        log.warning(f"query:({queryCmd}) returned:{ret}")
    rtask.retCode = ret
    #check tasks
    waitForTasks(rtask.childs)
    #task return values
    log.info("task summary")
    def walk(task:Task, indent:int=0):
        log.info(f"{'  '*indent}{task.name}: {task.retCode}")
        for child in task.childs:
            walk(child, indent+1)
    walk(rtask)
    return ret

# function that enters the working directory
#  loads the RR file
def enterDir(cfg:ConfigContext):
    etype((cfg, ConfigContext))
    log = logging.getLogger(LOGNAME)
    cd = Path.cwd()
    #change dir
    try:
        dir = cfg.get(":_run.dir")
        log.info(f"change dir:{dir}")
        os.chdir(dir)
    except PathNotExist:
        pass
    except FileNotFoundError:
        log.error(f"cannot enter directory:{dir} from:{cd}")
        raise
    #load RR
    try:
        node = makeConfigFromFile(Path('RR'))
        cfg.assimilate("", node, merge=True)
    except FileNotFoundError:
        logging.getLogger(LOGNAME).warning("no RR file not found")
    return cd

# parse commandline arguments and add them to the config
def parseArgs(cfg:ConfigContext, argStrs=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help="change to this directory before doing anything")
    parser.add_argument('--dontcatch', action="store_true", help='disables the catchall exception')
    parser.add_argument('--setup', '-s', type=str, action="append", help="set :_setup values")
    parser.add_argument('--loglevel', '-l', type=str, action="append", help="set loglevel - short for -s log.level.<scope>=<val>")
    parser.add_argument('query', type=str, default="query", help='query to do, can be omitted, then "invoke" subsided')
    parser.add_argument('params', type=str, nargs=argparse.REMAINDER, help='parameters for the query')
    args = parser.parse_args(argStrs)

    run = cfg.move(":_run")
    run.set(".query", args.query)
    run.set(".args", args.params)
    if args.dir is not None:
        run.set(".dir", args.dir)
    setup = cfg.move(":_setup")    
    if args.dontcatch:
        setup.set(".dontcatch", True)
    if args.setup is not None:
        for cmd in args.setup:
            scope, value = configParse(cmd)
            setup.set("." + scope, value, create=True)
    if args.loglevel is not None:
        for cmd in args.loglevel:
            scope, value = configParse(cmd)
            setup.set(".log.level." + scope, value, create=True)

REX_CONFIG = r'([\w\.]+)\s*=\s*([\w\/\-\._]+)'
def configParse(itm:str) -> tuple[str, any]:
    m = re.match(REX_CONFIG, itm)
    if m is None:
        raise Exception(f"cannot parse setup item:{itm}")
    scope = m.group(1)
    node = makeConfigFromStr(m.group(2), Location(f"cmdline:{itm}"))
    assert type(node) == ConfigLeaf
    value = node.value
    return scope, value

# create basic config
def makeConfig() -> ConfigContext:
    ctxt = ConfigContext(makeConfigVal(CONFIG))
    setup = ctxt.move(":_setup")
    roadrunner.log.configSetup(setup)
    return ctxt

# main function called from the commandline
def main(args:list[str]=None):
    log = logging.getLogger(LOGNAME)
    etype((args, (list, None, str)))
    cfg = makeConfig()
    parseArgs(cfg, args)
    oldDir = enterDir(cfg)
    setup = cfg.move(":_setup")
    roadrunner.log.initLogging(setup)
    nocatch = cfg.get(":_setup.dontcatch", isType=bool, default=False)
    try:
        ret = runRR(cfg)
    except ConfigError as ex:
        for line in ex.dump():
            log.error(line)
        if nocatch:
            raise
        ret = -1
    except RRError as ex:
        log.error(f"RRError:{ex}")
        ret = -1
    finally:
        os.chdir(oldDir)
    return ret

class UnitTestRunner:
    tmp:Path
    tmpDir:tempfile.TemporaryDirectory
    dir:Path
    def __init__(self, tmp:Path=None, dir:Path=None):
        etype((tmp, (Path, None)), (dir, (Path, None)))
        self.tmp = tmp
        self.tmpDir = None
        self.dir = dir

    def __enter__(self):
        if self.tmp is None:
            self.tmpDir = tempfile.TemporaryDirectory()
            self.tmp = Path(self.tmpDir.name)
        print(f"using tmp:{self.tmp}")
        return self
    
    def __exit__(self, _,__,___):
        if self.tmpDir is not None:
            self.tmpDir.cleanup()

    def main(self, cmd:list[str]):
        args = []
        args += [
            "--setup", f"workdir_base={self.tmp}/rrun",
            "--setup", f"result_base={self.tmp}/rres",
        ]
        if self.dir is not None:
            args += ["--dir", str(self.dir)]
        args += cmd
        return main(args)
