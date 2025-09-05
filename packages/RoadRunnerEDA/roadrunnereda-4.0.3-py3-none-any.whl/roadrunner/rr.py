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

from importlib.abc import Traversable
import argparse
from contextlib import contextmanager
from enum import Enum
import importlib.resources
import logging
from pathlib import Path
import pprint
import shutil
from typing import Iterable

from roadrunner.config import ConfigContext, Location
from roadrunner.fn import etype, cleardir, clone
from roadrunner.lua import LuaCtxt, LuaSnippet

class QueryArgs(argparse.Namespace):
    def __init__(self, cnf:ConfigContext):
        etype((cnf, ConfigContext))
        self._cnf = cnf
        self._parser = argparse.ArgumentParser()
    
    def __enter__(self):
        return self

    def __exit__(self, _, __, ___):
        self.parse()

    def parse(self):
        if self._parser is None:
            logging.getLogger("RR").warning("command arg parser closed")
            return
        ags = self._cnf.get(':_run.args', mkList=True)
        etype((ags, list, str))
        self._parser.parse_args(ags, self)
        self._parser = None

    def add(self, *args, **kwargs):
        if self._parser is None:
            logging.getLogger("RR").warning("command arg parser closed")
            return
        self._parser.add_argument(*args, **kwargs)

    def addstr(self, *names, **kwargs):
        self.add(*names, type=str, **kwargs)

    def addflag(self, *names, **kwargs):
        self.add(*names, action="store_true", **kwargs)

class Call:
    CALL_DIR = Path("calls")
    ENV_DIR = Path("env")
    def __init__(self, workdir:Path, name:str, tool:str, version:str=None):
        etype((workdir, Path), (name, str), (tool, str), (version, (str,None)))
        self.workdir = workdir
        self.name = name
        self.env = {}
        self.args = []
        self.cmds = []    #list of args
        self.tool = tool
        if version:
            self.tool += ":" + version

    def nextCmd(self):
        self.cmds.append(self.args)
        self.args = []

    def addArgs(self, args:Iterable):
        etype((args, Iterable, str))
        self.args += args

    def envSet(self, var:str, val:any):
        etype((var, str))
        self.env[var] = val

    def envAddPaths(self, var:str, paths:Iterable[Path]):
        etype((var, str), (paths, Iterable, Path))
        if var not in self.env:
            self.env[var] = "$" + var
        for path in paths:
            self.env[var] += ":" + str(path)

    def commit(self) -> str:
        if len(self.args):
            self.nextCmd()
        dir = self.workdir / self.CALL_DIR
        file = f"{self.name}.sh"
        dir.mkdir(exist_ok=True)
        with open(dir / file, "w") as fh:
            #shebang
            cmd = self.ENV_DIR / (self.tool.replace(':', '_') + ".sh")
            print(f"#!{cmd}", file=fh)
            #abort on error
            if len(self.cmds) > 1:
                print("set -e", file=fh)
            #environment
            for key,var in self.env.items():
                print(f"{key}={var}", file=fh)
            #commands
            for args in self.cmds:
                print(" \\\n".join(args), file=fh)
                print("", file=fh)
        (dir / file).chmod(0o755)
        return self.CALL_DIR / file

class PipelineItem:
    class CommandMode(Enum):
        SINGLE = 0
        SEQUENCE = 1
        PARALLEL = 2
        CALL = 4
        
    def __init__(self, name:str):
        etype((name, str))
        self.name = name
        self.sub:dict[str,PipelineItem] = {}
        self.workdir:Path = None
        self.workdirInited:bool = False
        self.commandValid:bool = False
        #attributes
        self.tools:list[str] = []
        self.mode:PipelineItem.CommandMode = None
        self.links:list[tuple[str,str,str]] = []
        self.call:tuple[Path,bool,bool] = None
        self.expose:list[tuple[Path,str]] = []
        self.discover:list[tuple[Path,str]] = []
        self.result:bool = False
        self.export:list[tuple[str,Path,Path,str]] = []

    def render(self) -> dict:
        log = logging.getLogger(f"{PipelineItem}:{self.name}")
        dd = {'name': self.name}
        if self.workdir is not None:
            dd["workdir"] = str(self.workdir)
        if len(self.tools):
            dd["envs"] = self.tools
        if len(self.links):
            dd["files"] = self.links
        if len(self.expose):
            dd["expose"] = []
            for path, name in self.expose:
                val = str(path)
                if name is not None:
                    val += ":" + name
                dd["expose"].append(val)
        if len(self.discover):
            dd["discover"] = []
            for path, name in self.discover:
                val = str(path)
                if name is not None:
                    val += ":" + name
                dd["discover"].append(val)
        if self.result:
            dd["result"] = True
        if len(self.export):
            dd['export'] = []
            for pattern, base, dest, group in self.export:
                exp = {"pattern": pattern}
                if base is not None:
                    exp["base"] = str(base)
                if dest is not None:
                    exp["dest"] = str(dest)
                if group is not None:
                    exp["group"] = group
                dd['export'].append(exp)
        if self.mode == self.CommandMode.CALL:
            dd["script"] = str(self.call[0])
            if self.call[1] == False:
                dd["abortOnError"] = False
            if self.call[2] == True:
                dd["interactive"] = True
        elif self.mode == self.CommandMode.PARALLEL:
            dd['parallel'] = [sub.render() for sub in self.sub.values()]
        elif self.mode == self.CommandMode.SEQUENCE:
            dd['sequence'] = [sub.render() for sub in self.sub.values()]
        elif self.mode == self.CommandMode.SINGLE:
            nsub = len(self.sub)
            assert nsub < 2, "single mode requires exactly one subitem"
            if nsub:
                dd['command'] = next(iter(self.sub.values())).render()
        else:
            log.warning("PipelineItem: no mode set")
        return dd

class Pipeline:
    SCRIPTNAME = "rrun.py"
    def __init__(self, workdir:Path, cmdName:str):
        etype((workdir, Path), (cmdName, str))
        self.root = PipelineItem("root")
        self.root.workdir = workdir
        self.root.mode = PipelineItem.CommandMode.SINGLE
        self.curr = []
        self.cmdName = cmdName

    def getPos(self) -> str:
        return ".".join(self.curr)

    def enter(self, name:str, mode:PipelineItem.CommandMode, workdir:Path=None):
        etype((name, str), (mode, PipelineItem.CommandMode), (workdir, (Path,None)))
        pli = PipelineItem(name)
        self.getCurr().sub[name] = pli
        self.curr.append(name)
        pli.mode = mode
        pli.workdir = workdir

    def enterSequence(self, name:str):
        self.enter(name, PipelineItem.CommandMode.SEQUENCE)

    def enterParallel(self, name:str):
        self.enter(name, PipelineItem.CommandMode.PARALLEL)

    def enterCall(self, name:str):
        self.enter(name, PipelineItem.CommandMode.CALL)

    @contextmanager
    def inSequence(self, name:str):
        try:
            self.enterSequence(name)
            yield
        finally:
            self.leave()

    @contextmanager
    def inParallel(self, name:str):
        try:
            self.enterParallel(name)
            yield
        finally:
            self.leave()

    @contextmanager
    def inCall(self, name:str):
        try:
            self.enterCall(name)
            yield
        finally:
            self.leave()

    def leave(self):
        #TODO some sanity checks on the current item mode
        self.curr.pop()

    def getCurr(self) -> PipelineItem:
        tmp = self.root
        for part in self.curr:
            tmp = tmp.sub[part]
        return tmp

    def cwd(self) -> Path:
        pth = self.root.workdir
        tmp = self.root
        for part in self.curr:
            tmp = tmp.sub[part]
            if tmp.workdir is not None:
                pth /= tmp.workdir
        return pth
    
    def initWorkDir(self, clear:bool=False) -> Path:
        etype((clear, bool))
        #create if not exist
        path = self.cwd()
        path.mkdir(parents=True, exist_ok=True)
        #clear
        if clear:
            cleardir(path)
        self.getCurr().workdirInited = True
        return path

    def loadenv(self, tool:str):
        etype((tool, str))
        #TODO make sure config default is included from tool's definition
        self.getCurr().tools.append(tool)

    def loadfile(self, tool:str, attribute:str, dest:str) -> Path:
        etype((tool, str), (attribute, str), (dest, str))
        self.getCurr().links.append((tool, attribute, dest))
        return Path('env') / dest

    def run(self, name:str, script:Path, abortOnError:bool=True, interactive:bool=False):
        etype((name, str), (script, Path), (abortOnError, bool), (interactive, bool))
        self.enter(name, "call")
        self.call(script, abortOnError, interactive)
        self.leave()

    def call(self, script:Path, abortOnError:bool=True, interactive:bool=False):
        etype((script, Path), (abortOnError, bool), (interactive, bool))
        pli = self.getCurr()
        if pli.mode != PipelineItem.CommandMode.CALL:
            logging.getLogger("RR").warning("set call in non call mode pipeline item")
        pli.call = (script, abortOnError, interactive)

    def expose(self, file:Path, name:str=None):
        etype((file, Path), (name, (str, None)))
        self.getCurr().expose.append((file, name))

    def discover(self, file:Path, name:str=None):
        etype((file, Path), (name, (str, None)))
        self.getCurr().discover.append((file, name))

    def result(self):
        self.getCurr().result = True

    #schedule one or more files to be copied to the result dir
    # pattern - glob pattern to select files
    # base - path in the commands WD to apply the pattern on
    # dest - base path in result dir
    # group - section in results manifest.ini for copied files
    def export(self,  pattern:str, base:Path=None, dest:Path=None, group:str=None):
        etype((pattern,str), (base,(Path,None)), (dest,(Path,None)), (group,(str,None)))
        self.getCurr().export.append((pattern, base, dest, group))

    def commit(self) -> bool: #workdir prepared
        log = logging.getLogger('RR')
        self.curr = []
        dd = self.root.render()
        if 'command' not in dd:
            return False
        for key in dd:
            if key not in ['name', 'workdir', 'command']:
                log.warning(f"pipeline root contains unexpected attribute:{key} which will not be used")
        root = self.getCurr()
        #build wd script
        if not root.workdirInited:
            self.initWorkDir()
        file = root.workdir / self.SCRIPTNAME
        ddstr = pprint.pformat(dd['command'], sort_dicts=False)
        envstr = pprint.pformat({'cmdName': self.cmdName})
        #format everything
        data = renderTemplate(Path("rr") / self.SCRIPTNAME, {
            "pipeline": ddstr, "env": envstr
        })
        with open(file, "w") as fh:
            print(data, file=fh)
        file.chmod(0o755)
        deployRoadExec(root.workdir)
        return root.workdirInited

    def addCall(self, call:Call, interactive:bool=False, abortOnError:bool=True):
        self.enterCall(call.name)
        self.useCall(call, interactive, abortOnError)
        self.leave()

    #use Call in an already opened CALL item
    def useCall(self, call:Call, interactive:bool=False, abortOnError:bool=True):
        etype((call, Call), (interactive, bool))
        script = call.commit()
        self.loadenv(call.tool)
        self.call(script, interactive=interactive, abortOnError=abortOnError)

def command_name(cfg:ConfigContext) -> str:
    etype((cfg, ConfigContext))
    opts = cfg.get(".options", mkList=True, default=[])
    return cfg.uid(set(opts))

def workdir_name(cfg:ConfigContext) -> Path:
    etype((cfg, ConfigContext))
    name = command_name(cfg)
    rname = name.replace('#', '_')
    return Path(cfg.get(":_setup.workdir_base", isType=str)) / "cmds" / rname

def workdir_import(workdir:Path, file:tuple[Location,Path], targetDir:Path=None, targetName:Path=None, baseDir:Path=None) -> Path:
    etype((workdir,Path), (file,tuple), (targetDir,(Path,None)), (targetName,(Path,None)), (baseDir,(Path,None)))
    etype((file[0],Location), (file[1],Path))
    location, fname = file
    stat = location.static
    dirSlug = str(location).replace('/', '_') if targetDir is None else str(targetDir)
    fileSlug = str(fname).replace('..', '_') if targetName is None else str(targetName)
    if fileSlug[0] == '/':
        fileSlug = fileSlug[1:]
    filePath = Path(fileSlug)
    dirPath = Path(dirSlug)
    offsetDir = dirPath if baseDir is None else(baseDir / dirPath)
    relativeDest = offsetDir / filePath
    dest = workdir / relativeDest
    if not stat:
        try:
            clone(location / fname, dest)
        except FileNotFoundError:
            raise NotAFile(location, fname, dest)
        return relativeDest
    else:
        return location / fname #original file 

def workdir_import_list(workdir:Path, file:list[tuple[Location,Path]], targetDir:list[Path]=None, targetName:list[Path]=None, baseDir:Path=None) -> list[Path]:
    etype((workdir,Path), (file,list,tuple), (targetDir,(list,None),(Path,None)), (targetName,(list,None),(Path,None)), (baseDir,(Path,None)))
    for f in file:
        etype((f[0],Location), (f[1],Path))
    if targetDir is None:
        targetDir = [None] * len(file)
    if targetName is None:
        targetName = [None] * len(file)
    baseDir = [baseDir] * len(file)
    ret = []
    for f,td,tn,bs in zip(file, targetDir, targetName, baseDir):
        ret.append(workdir_import(workdir,f,td,tn,bs))
    return ret

def resultBase(cfg:ConfigContext) -> Path:
    etype((cfg, ConfigContext))
    return Path(cfg.get(":_setup.result_base", isType=str))

def asset(path:Path) -> LuaSnippet:
    etype((path, Path))
    trav = importlib.resources.files("roadrunner.assets")
    cont = trav / path
    content =  cont.read_text()
    return LuaSnippet(content, str(cont), 0, template=True)

def renderTemplate(path:Path, vars:dict[str,any]):
    tpl = asset(path)
    lua = LuaCtxt()
    lua.addVariables(vars)
    return lua.run(tpl)

def deployRoadExec(dir:Path):
    etype((dir, Path))
    def walk(dir:Path, trav:Traversable):
        etype((dir,Path), (trav,Traversable))
        if trav.is_file():
            with importlib.resources.as_file(trav) as mfile:
                shutil.copyfile(mfile, dir / mfile.name)
        else: #directory
            subdir = dir / trav.name
            subdir.mkdir(exist_ok=True)
            for item in trav.iterdir():
                walk(subdir, item)
    rexec = importlib.resources.files("roadexec")
    walk(dir, rexec)
    psutil = importlib.resources.files("psutil")
    walk(dir, psutil)

class RRError(Exception):
    pass

class NotAFile(RRError):
    def __init__(self, location:Location, fname:Path, dest:Path):
        etype((location, Location), (fname, Path), (dest, Path))
        self.location = location
        self.fname = fname
        self.dest = dest

    def __str__(self):
        return f"not a file: {self.location} # {self.fname} -> {self.dest}"