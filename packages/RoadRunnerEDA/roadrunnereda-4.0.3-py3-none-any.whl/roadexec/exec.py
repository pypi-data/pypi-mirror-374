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

from __future__ import annotations
import configparser
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import threading

import roadexec
from roadexec.fn import IniConfig, NotIniConfig, banner, clone, etype, mkFile
from roadexec.proc import Proc
from roadexec.shares import ShareGate, Shares

ENV_BLANK = "#!/usr/bin/env bash\nsource $1" #script to be used for not defined tools

@dataclass
class CallItem:
    name: str
    script: Path
    abortOnError: bool
    interactive: bool

#things to add to the WD
# must specify exactly one of source, content or share
@dataclass
class LinkItem:
    name: Path              #path to the file in the WD
    source: Path=None       #path to the file to link to
    symlink: bool=False     #use symlink if linking
    content: str=None       #content of the file
    mode: int=None          #mode of the file
    mkdir: bool=True        #create the directory of name
    share: str=None         #name of the share to link to

@dataclass
class ResultItem:
    pattern: str
    base: Path
    dest: Path
    group: str

@dataclass
class ReturnValue:
    name:str
    value:int
    ignored:bool
    def __str__(self):
        return f"{self.name}:{self.value}{' (ignored)' if self.ignored else ''}"
    def isFail(self) -> bool:
        return self.value != 0 and not self.ignored

class ExecMode(Enum):
    INVALID = 0
    CALL = 1
    SEQUENCE = 2
    PARALLEL = 3
    POOL = 4

class ExecAbort(Exception):
    pass

class Exec:
    links:list[LinkItem]
    def __init__(self, name:str, parent:Exec, dir:Path=None):
        etype((name, str), (parent, (Exec, None)))
        #hierarchy
        self.name = name
        if parent is not None:
            parent._addChild(self)
        self.parent = parent
        self.children = [] #must be ordered
        #files
        self.dir = dir #directory this exec is in relative to parent
        self.links = []
        #shares
        if self.parent is None:
            self.shares = Shares()
        else:
            self.shares = ShareGate(self.parent.shares, self.dir)
        #execution
        self.mode = ExecMode.INVALID
        self.thread = None
        self.returnValue = None
        self.finished = threading.Event()
        self.interrupted = False
        self.procTail = None
        #call
        self.proc = None
        self.call = None #CallItem
        #results
        self.resultManifest = None
        self.results = []

    def _addChild(self, child:Exec):
        etype((child, Exec))
        self.children.append(child)

    def getWd(self) -> Path:
        if self.parent is None:
            return Path(".")
        if self.dir is None:
            return self.parent.getWd()
        else:
            return self.parent.getWd() / self.dir

    def getPos(self) -> str:
        if self.parent is None:
            return self.name
        else:
            return f"{self.parent.getPos()}.{self.name}"

    #find a tool that is defined in the config
    # returns the desired tool name and the one that was selected
    def selecttool(self, config:IniConfig, tool:str, version=None) -> tuple[str,str]:
        etype((config, IniConfig), (tool, str), (version, (str,None)))
        log = logging.getLogger(self.getPos())
        #toolName
        toolName = f"{tool}"
        if version is not None:
            toolName += f":{version}"
        #toolSel
        if config.hasSection(toolName):
            toolSel = toolName
        elif config.hasSection(tool):
            toolSel = tool
        elif config.hasSection("blank"):
            toolSel = "blank"
        else:
            toolSel = None
        return toolName, toolSel

    #create a tool invokation script an return its position
    def loadtool(self, config:IniConfig, tool:str, version=None):
        etype((config, IniConfig), (tool, str), (version, (str,None)))
        log = logging.getLogger(self.getPos())
        log.debug(f"loading tool:{tool} version:{version}")
        #toolName
        toolName, toolSel = self.selecttool(config, tool, version)
        if toolName != toolSel:
            log.warning(f"cannot find Env:({toolName}) using:({toolSel})")
        #check 
        if toolSel is None:
            script = ENV_BLANK
        elif config.hasValue(toolSel, "exec"):
            script = config.get(toolSel, "exec", esc=True)
        else:
            script = None
        if toolSel is None:
            sfile = None
        elif config.hasValue(toolSel, "execFile"):
            sfile = config.get(toolSel, "execFile", path=True) #FIXME this should be relative to the config file
        else:
            sfile = None
        assert [script, sfile].count(None) == 1,f"Environment:{toolSel} must define exactly one of script:{script} sfile:{sfile}"
        #
        toolScript = toolName.replace(':', '_') + ".sh"
        fname = Path("env") / toolScript
        li = LinkItem(fname, source=sfile, content=script, mode=0o755)
        self.links.append(li)

    def loadfile(self, config:IniConfig, name, tool, att, version=None):
        etype((config, IniConfig), (tool, str), (att, str), (version, (str,None)))
        toolName, toolSel = self.selecttool(config, tool, version)
        if toolSel is None:
            raise NotIniConfig(f"cannot find suitable env for:{toolName} loading attr:{att}")
        src = config.get(toolSel, att, path=True)
        dir = self.getWd() / "env"
        dest = dir / name
        li = LinkItem(dest, source=src)
        self.links.append(li)

    def setCall(self, name:str, script:Path, abortOnError:bool, interactive:bool):
        assert self.mode is ExecMode.INVALID, "mode already set"
        assert self.children == [], "already children registered"
        self.call = CallItem(
            name=name,
            script=script,
            abortOnError=abortOnError,
            interactive=interactive
        )
        self.mode = ExecMode.CALL

    def expose(self, file:Path, name:str=None):
        if name is None:
            name = str(file)
        self.shares.expose(file, name)

    def discover(self, file:Path, name:str=None):
        if name is None:
            name = str(file)
        li = LinkItem(file, share=name, symlink=True)
        self.links.append(li)
    
    def interrupt(self):
        self.interrupted = True
        #interrupt children
        for child in self.children:
            child.interrupt()
        #interrupt call
        try:
            self.proc.interrupt()
        except AttributeError:
            pass

    def result(self, resultDir:Path):
        etype((resultDir, Path))
        li = LinkItem("result", resultDir, symlink=True)
        self.links.append(li)
        self.resultManifest = {}
 
    def export(self, pattern:str, base:Path, dest:Path, group:str):
        etype((pattern,str), (base,(Path,None)), (dest,(Path,None)), (group,(str,None)))
        if base is None:
            base = Path("")
        if dest is None:
            dest = Path("")
        if group is None:
            group = "default"
        self.results.append(ResultItem(pattern, base, dest, group))

    def start(self):
        self.thread = threading.Thread(target=self.run, name=f"Exec:{self.getPos()}")
        self.thread.start()

    def run(self):
        log = logging.getLogger(self.getPos())
        try:
            self._createLinks()
            if self.mode == ExecMode.CALL:
                self._runCall()
            elif self.mode == ExecMode.SEQUENCE:
                self._runSequence()
            elif self.mode == ExecMode.PARALLEL:
                self._runParallel()
            else:
                assert False, "invalid mode"
            self._exportResults()
        except ExecAbort:
            log.error(f"Aborting Exec:{self.getPos()}")
        self.finished.set()

    def _createLinks(self):
        log = logging.getLogger(self.getPos())
        log.debug("setting Exec Env Links")
        #create Links
        for item in self.links:
            dest = self.getWd() / item.name
            assert [item.source, item.content, item.share].count(None) == 2, f"must specify exactly one of source:{item.source}, content:{item.content} or share:{item.share}"
            if item.source is not None:
                mkFile(dest, item.source, mode=item.mode, mkdir=item.mkdir, symlink=item.symlink)
            elif item.content is not None:
                mkFile(dest, mode=item.mode, mkdir=item.mkdir, symlink=item.symlink)
                with open(dest, "w") as fh:
                    print(item.content, file=fh)
            elif item.share is not None:
                try:
                    share = self.shares.discover(item.share)
                    mkFile(dest, share, mode=item.mode, mkdir=item.mkdir, symlink=item.symlink)
                except roadexec.shares.NotExposed:
                    raise ExecAbort(f"share Link:{item.share} has not been exposed")

    def _exportResults(self):
        log = logging.getLogger(self.getPos())
        result = Path("result")
        for item in self.results:
            base = self.getWd()
            if item.base:
                base = base / item.base
            for source in base.glob(item.pattern):
                fname = source.relative_to(base)
                dest = result / item.dest / fname
                dest.parent.mkdir(exist_ok=True, parents=True)
                log.info(f"export result {source} -> {dest}")
                clone(source, dest)
                if item.group not in self.resultManifest:
                    self.resultManifest[item.group] = []
                self.resultManifest[item.group].append(str(fname))
        if self.resultManifest is not None:
            mani = configparser.ConfigParser()
            mani.add_section("manifest")
            for group,files in self.resultManifest.items():
                mani['manifest'][group] = "\n".join(files)
            with open(result / "manifest.ini", "w") as fh:
                mani.write(fh)

    def _runCall(self):
        log = logging.getLogger(self.getPos())
        log.info(banner(self.getPos()))
        if self.call.interactive:
            log.info("Start Interactive Console")
        p = Proc([self.call.script], self.getWd(), self.name, interactive=self.call.interactive, tail=self.procTail)
        self.proc = p
        ret = p.finish()
        self.returnValue = ReturnValue(self.call.name, ret, not self.call.abortOnError)
        if self.returnValue.isFail():
            p.logTick(end=True, errTail=True)
        log.info(banner(self.getPos(), False))
        if ret != 0 and self.call.abortOnError:
            raise ExecAbort(f"call:{self.call.name} returned:{ret}")
        if self.interrupted:
            raise ExecAbort("interrupted")

    def _runSequence(self):
        log = logging.getLogger(self.getPos())
        log.debug(f"group run start {self.getPos()}")
        good = True
        for sub in self.children:
            sub.start()
            sub.finished.wait()
            if self.interrupted:
                raise ExecAbort("interrupted")
            if sub.returnValue is None or (sub.returnValue.value != 0 and sub.returnValue.ignored == False):
                good = False
                break
        self.returnValue = ReturnValue(self.name, 0 if good else 1, False)
        log.debug(f"group run end {self.getPos()}")
        
    def _runParallel(self):
        log = logging.getLogger(self.getPos())
        log.debug(f"group run start {self.getPos()}")
        for sub in self.children:
            sub.start()
        good = True
        for sub in self.children:
            sub.finished.wait()
            if self.interrupted:
                raise ExecAbort("interrupted")
            if sub.returnValue is None or (sub.returnValue.value != 0 and sub.returnValue.ignored == False):
                good = False
        self.returnValue = ReturnValue(self.name, 0 if good else 1, False)
        log.debug(f"group run end {self.getPos()}")

    def status(self) -> dict[str,any]:
        dd = {}
        if self.dir is not None:
            dd['dir'] = self.getWd()
        if self.call is not None:
            dd['script'] = self.call.script
        if self.proc is not None:
            if self.proc.fStdout is not None:
                dd['stdout'] = self.proc.fStdout
            if self.proc.fStderr is not None:
                dd['stderr'] = self.proc.fStderr
            if self.proc.process is not None:
                dd['pids'] = ", ".join([str(p.pid) for p in self.proc.process])
        dd['finished'] = self.finished.is_set()
        if self.returnValue:
            dd['return'] = self.returnValue.value
            if self.returnValue.ignored:
                dd['ignore'] = True
        return dd
    
    def tail(self, val:str):
        assert val in ['stdout', 'stderr', 'both'], "invalid tail value - must be stdout|stderr|both"
        self.procTail = val

class Status:
    def __init__(self, root:Exec, fname:Path):
        etype((root, Exec), (fname, Path))
        self.root = root
        self.status = configparser.ConfigParser()
        self.fname = fname

    def update(self):
        def walk(ex:Exec):
            yield ex.getPos(), ex.status()
            for sub in ex.children:
                yield from walk(sub)
        for sect, vals in walk(self.root):
            if sect not in self.status:
                self.status[sect] = {}
            for key,val in vals.items():
                self.status[sect][key] = str(val)
    
    def write(self):
        with open(self.fname, "w") as fh:
            self.status.write(fh)




