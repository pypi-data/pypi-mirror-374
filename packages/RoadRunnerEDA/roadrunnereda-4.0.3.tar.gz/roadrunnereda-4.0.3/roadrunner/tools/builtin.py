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
import pathlib
import re
import time
from typing import Iterator

from roadrunner.lua import LuaCtxt
import roadrunner.tools as tools
from roadrunner.config import ConfigContext, ConfigEnv, ConfigNode, ConfigPath, LinkNotExist, Location, NotIteratable, Origin, PathNotExist, makeConfigFromFile, makeConfigFromManifest, makeConfigVal, parsePathOption, registerLuaHook
from roadrunner.fn import banner, etype, ctype, uniqueExtend
from roadrunner.help import HelpProxy, HelpItem, HelpOption, getHelp, iterHelp
from roadrunner.rr import Pipeline, PipelineItem, QueryArgs, command_name, workdir_name
import roadrunner.runner as runner 

from roadrunner.version import version_string

NAME = "BuiltIn"

BUILTIN_COMMANDS = ['jabberwocky', 'parallel', 'sequence', 'pool', 'single']

HelpItem("tool", NAME, "builtin functions")

def load(cfg:ConfigContext):
    registerLuaHook(cfg, "wocky", burbelHook)
    registerLuaHook(cfg, "result", resultHook)
    registerLuaHook(cfg, "get", getHook)
    pass

HelpItem("query", (NAME, "jabberwocky"), "prints the jabberocky poem", [
    HelpOption("flag", ("--long", "-l"), desc="print the long version of the poem"),
    HelpOption("flag", ("--fail", "-f"), desc="return a failing exit code from the query"),
    HelpOption("flag", ("--noret", "-n"), desc="return None from the query")
])
def query_jabberwocky(cfg:ConfigContext) -> int:
    log = logging.getLogger(NAME)
    with QueryArgs(cfg) as args:
        args.addflag('--long', '-l')
        args.addflag('--fail', '-f')
        args.addflag('--noret', '-n', help="do not return an int")
    for line in jabberwocky(args.long):
        log.info(line)
    ret = 0
    if args.fail:
        log.warning("query will fail as requested by cmdline")
        ret = -1
    if args.noret:
        log.warning("query will not return an int as requested by cmdline")
        ret = None
    return ret

HelpItem("command", (NAME, "jabberwocky"), "writes the jabberwocky poem into a file", [
    HelpOption("attribute", "long", "bool", "False", "writes to long version"),
    HelpOption("attribute", "fail", "bool", "False", "return a failing exitcode (-1)"),
    HelpOption("attribute", "noret", "bool", "False", "return nothing (None)")
])
def cmd_jabberwocky(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(NAME)
    wd = pipe.initWorkDir()
    long = cfg.get(".long", isType=bool, default=False)
    fail = cfg.get(".fail", isType=bool, default=False)
    noret = cfg.get(".noret", isType=bool, default=False)
    with open(wd / "jabberwocky.txt", "w") as fh:
        for line in jabberwocky(long):
            print(line, file=fh)
    ret = 0
    if fail:
        log.warn("query will fail as requested by attribute")
        ret = -1
    if noret:
        log.warn("query will not return an int as requested by attribute")
        ret = None
    return ret

def jabberwocky(long:bool=False) -> Iterator[str]:
    yield "Twas brillig, and the slithy toves"
    yield "Did gyre and gimble in the wabe;"
    yield "All mimsy were the borogoves,"
    yield "And the mome raths outgrabe."
    if not long:
        return
    yield ""
    yield "Beware the Jabberwock, my son!"
    yield "The jaws that bite, the claws that catch!"
    yield "Beware the Jubjub bird, and shun"
    yield "The frumious Bandersnatch!"
    yield ""
    yield "He took his vorpal sword in hand:"
    yield "Long time the manxome foe he sought --"
    yield "So rested he by the Tumtum tree,"
    yield "And stood awhile in thought."
    yield ""
    yield "And, as in uffish thought he stood,"
    yield "The Jabberwock, with eyes of flame,"
    yield "Came whiffling through the tulgey wood,"
    yield "And burbled as it came!"
    yield ""
    yield "One, two! One, two! And through and through"
    yield "The vorpal blade went snicker-snack!"
    yield "He left it dead, and with its head"
    yield "He went galumphing back."
    yield ""
    yield "And, has thou slain the Jabberwock?"
    yield "Come to my arms, my beamish boy!"
    yield "O frabjous day! Callooh! Callay!"
    yield "He chortled in his joy."
    yield ""
    yield "Twas brillig, and the slithy toves"
    yield "Did gyre and gimble in the wabe;"
    yield "All mimsy were the borogoves,"
    yield "And the mome raths outgrabe."
    return

def burbelHook(cfg:ConfigContext, lua:LuaCtxt):
    lua.addVariables({
        "wocky": "burbel burbel - burbel burbel"
    })

HelpItem("query", (NAME, "help"), "prints info about the available tools", [
    HelpOption("flag", "tool", "str", desc="select a tool for more detailed info"),
    HelpOption("flag", "sub", "str", desc="select a command/query for more detailed info"),
    HelpOption("flag", ("--cmd", "-c"), desc="show command if there is also a query with the selected name")
])
def query_help(cfg:ConfigContext) -> int:
    with QueryArgs(cfg) as args:
        args.addstr("tool", nargs="?")
        args.addstr("sub", nargs="?")
        args.addflag("--cmd", "-c")
    if args.sub:
        subInfo(args.tool, args.sub, args.cmd)
    elif args.tool:
        toolInfo(args.tool)
    else:
        listTools()
    return 0

def listTools():
    log = logging.getLogger(NAME)
    log.info(banner("Tools"))
    for itm in iterHelp("tool"):
        tool = itm.scope[0]
        msg = tool
        if itm.desc:
            msg += f" - {itm.desc}"
        queries = [itm.scope[1] for itm in iterHelp("query", (tool,))]
        if queries != []:
            msg += f"\n  queries: {', '.join(queries)}"
        cmds = [itm.scope[1] for itm in iterHelp("command", (tool,))]
        if cmds != []:
            msg += f"\n  commands: {', '.join(cmds)}"
        for l in msg.split('\n'):
            log.info(l)
    log.info(banner("Tools", False))

def toolInfo(tool:str):
    etype((tool, str))
    log = logging.getLogger(NAME)
    log.info(banner("ToolInfo"))
    itm = getHelp("tool", (tool,))
    msg = tool
    if itm and itm.desc:
        msg += f" - {itm.desc}"
    firstQuery = True
    for itm in iterHelp("query", (tool,)):
        if firstQuery:
            msg += "\n  queries:"
            firstQuery = False
        msg += f"\n    {itm.scope[1]}"
        if itm.desc:
            msg += f" - {itm.desc}"
    firstCmd = True
    for itm in iterHelp("command", (tool,)):
        if firstCmd:
            msg += "\n  commands:"
            firstCmd = False
        msg += f"\n    {itm.scope[1]}"
        if itm.desc:
            msg += f" - {itm.desc}"
    for l in msg.split('\n'):
        log.info(l)
    log.info(banner("ToolInfo", False))
        
def subInfo(tool:str, sub:str, cmd:bool):
    etype((tool, str), (sub, str), (cmd, bool))
    #try query
    if not cmd and queryInfo(tool, sub):
        return
    if commandInfo(tool, sub):
        return
    logging.getLogger(NAME).warn(f"no info for tool:{tool} sub:{sub}")

def queryInfo(tool:str, sub:str) -> bool:
    log = logging.getLogger(NAME)
    etype((tool, str), (sub, str))
    itm = getHelp("query", (tool, sub))
    if not itm:
        return False
    #if not, try command
    log.info(banner("Query Info"))
    msg = f"{'.'.join(itm.scope)}"
    if itm.desc:
        msg += f" - {itm.desc}"
    for opt in itm:
        msg += f"\n  {' '.join(opt.names)}"
        if opt.valType:
            msg += f" ({opt.valType})"
        if opt.default:
            msg += f" default:{opt.default}"
        if opt.desc:
            msg += f" - {opt.desc}"
    for l in msg.split('\n'):
        log.info(l)
    log.info(banner("Query Info", False))
    return True

def commandInfo(tool:str, sub:str) -> bool:
    log = logging.getLogger(NAME)
    etype((tool, str), (sub, str))
    itm = getHelp("command", (tool, sub))
    if not itm:
        return False
    #if not, try command
    log.info(banner("Command Info"))
    msg = f"{'.'.join(itm.scope)}"
    if itm.desc:
        msg += f" - {itm.desc}"
    log.info(msg)
    def getoptions(itm):
        opts = []
        for opt in itm:
            if isinstance(opt, HelpProxy):
                uniqueExtend(opts, getoptions(opt))
                continue
            else:
                uniqueExtend(opts, [opt])
        return opts
    for opt in getoptions(itm):
        msg = f"  {' '.join(opt.names)}"
        if opt.valType:
            msg += f" ({opt.valType})"
        if opt.default:
            msg += f" default:{opt.default}"
        if opt.desc:
            msg += f" - {opt.desc}"
        log.info(msg)
    log.info(banner("Command Info", False))
    return True

HelpItem("query", (NAME, "getval"), "retrieves a value from the config space and prints it as python value", [
    HelpOption("flag", "--mklist", desc="puts a primitive value in a list before returning"),
    HelpOption("flag", "--path", desc="retrieves value as system path - as tuple of location and name"),
    HelpOption("flag", "--type", "str", desc="value will be type checked against this type"),
    HelpOption("flag", "pararms", "str", desc="config path to retrieve (can be specified multiple times)")
])
TYPES = {
    'int': int,
    'str': str,
    'bool': bool
}
def query_getval(cfg:ConfigContext) -> int:
    log = logging.getLogger(NAME)
    log.info(banner("Config Getter"))
    b_mklist, b_path, s_type = False, False, None
    with QueryArgs(cfg) as args:
        args.addflag('--mklist')
        args.addflag('--path')
        args.addstr('--type', nargs='?')
        args.addstr('params', nargs='*', default=':')
    if args.mklist:
        b_mklist = True
    if args.path:
        b_path = True
    if args.type:
        s_type = TYPES[args.type]
    for v in args.params:
        val = cfg.get(v, mkList=b_mklist, isOsPath=b_path, isType=s_type)
        if b_path:
            val = f"{val[0]}/{val[1]}"
        log.info(f"({v}):{val}")
    log.info(banner("Config Getter", False))
    return 0

HelpItem("query", (NAME, "get"), "get part of the config space and dumps it", [
    HelpOption("flag", "path", "str", desc="config path to the root node of the dumped subtree")
])
def query_get(cfg:ConfigContext) -> int:
    log = logging.getLogger(NAME)
    log.info(banner("Config Getter"))
    with QueryArgs(cfg) as args:
        args.addstr('path')
        args.addstr('poke', nargs='*')
    for p in args.poke:
        ctx = cfg.move(p)
        ctx.node.delegate(ctx.env)
    root = cfg.move(args.path)
    root.node.delegate(root.env)
    for line in root.dump():
        log.info(line)
    log.info(banner("Config Getter", False))
    return 0

REX_TOOL = r'(\w+)(\.\w+)?(:[\w\.<>=]+)?'

def parseTool(cfg:ConfigContext) -> tuple[str, str, str]:
    etype((cfg, ConfigContext))
    log = logging.getLogger(NAME)
    toolDesc = cfg.get(".tool", isType=str)
    #try to get everthing from toolDesc
    m = re.match(REX_TOOL, toolDesc)
    if not m:
        raise RuntimeError(f"tool Attribute wrong:{toolDesc}")
    toolMain = m[1]
    toolFn = m[2] and m[2][1:]     #remove first caracter if not None
    toolVersion = m[3] and m[3][1:]
    #see if anything is in .function
    raw = cfg.get(".function", None, isType=str)
    if raw:
        if toolFn:
            log.warn("specified function as 'function' and part of 'tool'")
        toolFn = raw
    #see if anything in .version
    raw = cfg.get(".version", None, isType=str)
    if raw:
        if toolVersion:
            log.warn("specified version as 'version' and part of 'tool'")
        toolVersion = raw
    #builtins
    bifn = None
    if (toolMain, toolVersion) == (None, None):
        bifn = toolFn
    if (toolFn, toolVersion) == (None, None):
        bifn = toolMain
    if bifn in BUILTIN_COMMANDS:
        toolMain = NAME
        toolFn = bifn
    #default funciton
    if toolFn is None:
        toolFn = 'run'
    return toolMain, toolFn, toolVersion

def command_run(cfg:ConfigContext, pipe:Pipeline) -> int:
    etype((cfg, ConfigContext), (pipe, Pipeline))
    log = logging.getLogger(NAME)
    toolMain, toolFn, toolVersion = parseTool(cfg)
    log.debug(f"parsig tool name from config:{toolMain} fn:{toolFn} v:{toolVersion}")
    commandFunction = tools.getcmd(toolMain, toolFn)
    #run
    ret = commandFunction(cfg, pipe, toolVersion)
    if not ctype((ret, int)):
        raise RuntimeError(f"command did not return an int - tool:{toolMain} fn:{toolFn} env:{toolVersion} ret:{ret}")
    return ret

def invoke(cmdlink:ConfigContext):
    log = logging.getLogger(NAME)
    #find the tool
    cmdnode = cmdlink.real()
    wd = workdir_name(cmdnode)
    cn = command_name(cmdnode)
    log.debug(f"working dir is:{wd}")
    pipe = Pipeline(wd, cn)
    #name = str(cmdnode.pos()[-1])[1:] #last item from path without leading '.'
    #log.debug(f"toplevel task name:{name}")
    #pipe.enter(name, "sequence")
    ret = command_run(cmdnode, pipe)
    if ret < 0:
        log.warning(f"cmd:({cmdnode.pos()}) preparation returned:{ret} - exiting")
        return ret
    #pipe.leave()
    pipe.commit()
    #runner
    if (wd / pipe.SCRIPTNAME).exists():
        if ret != 0:
            log.warning("query returned non zero:{ret} - will be overridden by execution")
        return runner.run(cmdnode)
    elif wd.exists():
        log.warning(f"result directory is ready:{dir}")
        return ret
    else:
        log.debug(f"no result dir and no script - nothing to do")
        return ret
    #end

HelpItem("query", (NAME, "invoke"), "execute a command node. This is the main funtionallity of RoadRunner.", [
    HelpOption("flag", "command", "str", desc="config path the (command) node to be executed")
])
def query_invoke(cfg:ConfigContext) -> int:
    log = logging.getLogger(NAME)
    with QueryArgs(cfg) as args:
        args.addstr('command')
        args.add("--tail", "-t", type=str, nargs='?', action="append", help="print stdout and stderr of one or more calls to stdout")
        args.add("--stdout", type=str, action="append", help="print stdout of one or more calls to stdout")
        args.add("--stderr", type=str, action="append", help="print stderr of one or more calls to stdout")
    #parse args
    path, opts = parsePathOption(":" + args.command)
    cmdArgs = []
    if args.tail is not None:
        for itm in args.tail:
            cmdArgs += ["--tail", itm] if itm is not None else ["--tail"]
    if args.stdout is not None:
        for itm in args.stdout:
            cmdArgs += ["--stdout", itm]
    if args.stderr is not None:
        for itm in args.stderr:
            cmdArgs += ["--stderr", itm]
    if len(cmdArgs):
        cfg.set(":_run.runArgs", cmdArgs, create=True)
    cmdnode = cfg.move(path, opts)
    return invoke(cmdnode)

RunTypes = {
    "parallel": PipelineItem.CommandMode.PARALLEL,
    "sequence": PipelineItem.CommandMode.SEQUENCE
}

def cmd_group(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    return run(cfg, pipe, "group")

def cmd_parallel(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    return run(cfg, pipe, "parallel")

def cmd_sequence(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    return run(cfg, pipe, "sequence")

def cmd_single(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    return run(cfg, pipe, "single")

def run(cfg:ConfigContext, pipe:Pipeline, typ:str) -> int:
    etype((cfg, ConfigContext), (pipe, Pipeline))
    log = logging.getLogger(NAME)
    log.info(banner(f"Scan"))
    pipe.initWorkDir()
    scan(cfg, pipe, typ)
    log.info(banner(f"Scan", False))
    return 0

def scan(cfg:ConfigContext, pipe:Pipeline, name:str, level=1):
    etype((cfg, ConfigContext), (pipe, Pipeline))
    log = logging.getLogger("group")
    real = cfg.real()
    # is it a command node (and not a 'Runner' command)
    tool = parseTool(cfg)
    if tool[0] != NAME or tool[1] not in RunTypes:
        log.debug(f"pipepos:{pipe.getPos()} level:{level}")
        #remove the first two pipe levels because they are just the initial command and the initial grouping
        pipepos = ".".join(pipe.curr[1:] + [name]) #FIXME should pipe.curr be fetched with method?
        log.info(f"{'--'*level} Command    pos:{real.pos()} pipe:{pipepos}")
        pipe.enter(name, PipelineItem.CommandMode.SINGLE, Path(pipepos))
        command_run(cfg, pipe)
        pipe.leave()
        return

    mode = None
    # mode from function
    if tool[1] is not None:
        mode = tool[1]
    #mode from .group
    group = cfg.get(".group", default=None, isType=str)
    if group:
        if mode:
            log.warning(f".group attribute overrides tool function in {cfg.pos()}")
        mode = group
    if mode is None:
        raise Exception(f"no Runner mode in {cfg.pos()}")

    log.info(f"{'--'*level} {mode}    {real.pos()}")

    assert mode in RunTypes, "group mode is not a valid RunType"

    #create the group
    pipe.enter(name, RunTypes[mode])

    #descend
    count = 0
    for key,node in cfg:
        #ignore magic
        if key in ['group', 'tool']:
            continue
        scan(node, pipe, key, level+1) #f"{count}{key}")
        count += 1

    #finish this group
    pipe.leave()

HelpItem("query", (NAME, "version"), "put roadrunners version")
def query_version(cfg:ConfigContext) -> int:
    log = logging.getLogger(NAME)
    log.info(f"RoadRunner {version_string()}")
    return 0


def pathSuggest(cfg:ConfigContext, cpath:str) -> int:
    path = ConfigPath(cpath)
    sug = []
    log = logging.getLogger(NAME)
    #remove trailing "."
    tail = cpath.endswith(".")
    #check if path this is already a path
    log.debug(f"path:({path}), tail:({tail})")
    try:
        ncfg = cfg.move(str(path))
    except PathNotExist:
        log.debug(f"not a full path")
        ncfg = None
    #remove slug from path
    if ncfg is None:
        _, slug = path.getElement(-1)
        path = str(path[:-1])
    else:
        slug = ""
    #again, check if path exists - die other wise
    try:
        ncfg = cfg.move(str(path))
    except PathNotExist:
        log.debug(f"path not found")
        return []
    #self suggest (only if trail is "")
    if not tail and slug == "":
        p = str(ncfg.pos())
        sug.append(p)
        log.debug(f"self suggestion:{p}")
    #suggest children
    children = [ncfg]
    try:
        while len(children) == 1:
            ncfg = children[0]
            children = []
            for key,node in ncfg:
                if not key.startswith(slug):
                    continue
                children.append(node)
                p = str(node.pos())
                log.debug(f"suggestion child:{p}")
                sug.append(p)
            slug = ""
    except NotIteratable:
        pass
    log.debug(f"suggestions:{len(sug)}")
    return sug

def query_tab(cfg:ConfigContext) -> int:
    log = logging.getLogger(NAME)
    log.info(banner(f"Tab Completer"))
    log.info("to use this query as bash completer set console logging (:_setup.log.level._console) to at least:warn.")
    log.info("  Also it is advised to disable file logging (:_setup.log.logFileEnabled).")
    log.info("  To install bash completion source (bin/rrcomplete) in a terminal.")
    log.info(banner(f"Suggestions"))
    log.debug(f"args:{cfg.get('._run.args')}")
    try:
        with QueryArgs(cfg) as args:
            args.addstr('command')
            args.addstr('input', nargs='?')
        #alreaddy a full path?
        cpath = ":" + (args.input if args.input is not None else "")

        for sug in pathSuggest(cfg, cpath):
            print(f"{sug[1:]}")
    except Exception:
        log.info("something went wrong - no suggestions")

    log.info(banner(f"Tab Completer", False))
    return 0

def findLatestResult(name:str, resultDir:Path) -> str:
    latest = None
    latestName = None
    for itm in resultDir.iterdir():
        split = itm.name.split('.')
        if len(split) < 2 or split[0] != name:
            continue
        try:
            tme = time.strptime(split[1], f"%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
        if latest is None or tme > latest:
            latest = tme
            latestName = '.'.join(split[1:])
    return latestName

def query_result(cfg:ConfigContext) -> int:
    with QueryArgs(cfg) as args:
        args.addstr('name')
        args.addstr('cmd')
        args.addstr('result', nargs='?')
        args.addflag('--latest')

    resultDir = Path(cfg.get(":_setup.result_base"))
    resultName = args.name
    if args.cmd == 'select':
        resSel = args.result
        if args.latest:
            resSel = findLatestResult(resultName, resultDir)
        if resSel is None:
            return -1
        dest = resultDir / resultName
        source = Path(f"{resultName}.{resSel}")
        if dest.is_symlink():
            dest.unlink()
        dest.symlink_to(source)
        return 0
    else:
        return -1
    
class ConfigResult(ConfigNode):
    NAME = "ConfigResult"
    def __init__(self, cmdNode:ConfigNode):
        etype((cmdNode, ConfigNode))
        super().__init__(cmdNode)
        self.key = '__result'
        self.parent = cmdNode
        self.cmd = cmdNode
        self.cacheNode = None
        self.cacheName = None

    def __repr__(self) -> str:
        return f"ConfigResult({self.cmd.getPath()})"
    
    def delegate(self, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        etype((env, ConfigEnv))
        log = logging.getLogger(NAME)
        #get result root
        cfg = ConfigContext(self, env=env)
        resultRoot = pathlib.Path(cfg.get(":_setup.result_base"))
        #get command name
        ccfg = ConfigContext(self.cmd, env=env)
        cmdName = command_name(ccfg)
        if self.cacheName != cmdName or self.cacheNode is None:
            #compile result directory
            resultDir = resultRoot / cmdName
            if not resultDir.exists():
                raise LinkNotExist(f"the result:{cmdName} cannot be found", env, self)
            log.debug(f"found result dir:{resultDir}")
            #load result - signal node
            resultNode = makeConfigVal({
                'isResult': True
            }, location=Location(resultRoot))
            resultNode.isFileRoot = True
            #try to load RR
            resultRR = resultDir / "RR"
            if resultRR.exists():
                log.debug(f"found result RR:{resultRR}")
                rrNode = makeConfigFromFile(resultRR) 
                resultNode.merge(rrNode, env)
            #try to load manifest
            resultManifest = resultDir / "manifest.ini"
            if resultManifest.exists():
                log.debug(f"found result manifest:{resultManifest}")
                manifesNode = makeConfigFromManifest(resultManifest)
                resultNode.merge(manifesNode, env)
            #finalize result node
            resultNode.setParent(self.parent, '__result')
            self.cacheName = cmdName
            self.cacheNode = resultNode
        return env, self.cacheNode

    def export(self) -> str:
        return f"~{self.desc}"
    
    def dump(self) -> tuple[str,list[str]]:
        val = f"~{self.desc}"
        if self.node:
            slug, lst = self.node.dump()
            val += " # " + slug
        else:
            lst = []
        return val, lst


def resultHook(cfg:ConfigContext, lc:LuaCtxt):
    res = ConfigResult(cfg.node)
    lc.addVariables({
        "result": res
    })

def getHook(cfg:ConfigContext, lc:LuaCtxt):
    lc.addVariables({
        "get": lambda x: cfg.get(x)
    })
