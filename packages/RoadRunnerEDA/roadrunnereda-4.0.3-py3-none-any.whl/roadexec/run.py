from __future__ import annotations
import argparse

from configparser import ConfigParser
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import selectors
import sys
import threading
import time

from roadexec.exec import Exec, ExecMode, Status
from roadexec.fn import banner, IniConfig, configParse, loggingLevelInt

class RunEnv:
    result: Path
    def __init__(self, glob, pipe, env):
        self.config = IniConfig()
        self.root = None
        self.result = None
        self.args = []
        self.pipe = pipe

        self.readEnv(env)
        self.readGlobal(glob)
        self.readArgs()
        self.initLogging()

        logging.getLogger("roadexec").info(banner("RoadExec"))

    def readArgs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--loglevel", '-l', type=str, action="append", help="set loglevel - short for -s loglevel:<scope>=<val>")
        parser.add_argument("--setup", "-s", type=str, action="append", help="set config values")
        parser.add_argument("--dry", "-d", action="store_true", help="do not run anything")
        parser.add_argument("--tail", "-t", type=str, nargs='?', action="append", help="print stdout and stderr of one or more calls to stdout")
        parser.add_argument("--stdout", type=str, action="append", help="print stdout of one or more calls to stdout")
        parser.add_argument("--stderr", type=str, action="append", help="print stderr of one or more calls to stdout")
        args = parser.parse_args(self.args)
        if args.setup is not None:
            for cmd in args.setup:
                section, key, value = configParse(cmd)
                self.config.set(section, key, value)
        if args.loglevel is not None:
            for cmd in args.loglevel:
                section, key, value = configParse(cmd, log=True)
                self.config.set(section, key, value)
        if args.tail is not None:
            for scope in args.tail:
                if scope is None:
                    scope = "*"
                self.config.set("tail", scope, "both")
        if args.stdout is not None:
            for scope in args.stdout:
                if scope is None:
                    scope = "*"
                self.config.set("tail", scope, "stdout")
        if args.stderr is not None:
            for scope in args.tail:
                if scope is None:
                    scope = "*"
                self.config.set("tail", scope, "stderr")
        self.config.set("run", "dry", str(args.dry))

    def readEnv(self, env:dict):
        self.name = env['cmdName']

    def readGlobal(self, glob):
        if "resultDir" in glob:
            self.config.set("RoadExec", "resultDir", glob["resultDir"])
        self.isMain = glob['isMain']
        if self.isMain:
            self.args += sys.argv[1:]
        elif "args" in glob:
            self.args += glob["args"]
        else:
            self.args = []

    def initLogging(self):
        #basic levels
        for scope,val in self.config.iter("loglevel"):
            level = loggingLevelInt(val)
            logging.getLogger(scope).setLevel(level)
            print(f"logging set {scope} -> {level}")
        #output
        root = logging.getLogger()
        if root.hasHandlers():
            return
        #console output
        root.setLevel(logging.DEBUG)
        fmt = self.config.get("logging", "formatConsole")
        lvl = self.config.get("logging", "levelConsole")
        formatter = logging.Formatter(fmt)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(loggingLevelInt(lvl))
        root.addHandler(handler)
        #file logging
        fmt = self.config.get("logging", "formatFile")
        lvl = self.config.get("logging", "levelFile")
        formatter = logging.Formatter(fmt)
        handler = RotatingFileHandler("rrun.log", maxBytes=0, backupCount=5)
        handler.setFormatter(formatter)
        handler.setLevel(loggingLevelInt(lvl))
        handler.doRollover()
        root.addHandler(handler)

    def readPipeline(self):
        def gen(curr, source):
            wdir = Path(source["workdir"]) if "workdir" in source else None
            ex = Exec(source["name"], curr, wdir)
            matchLen = 0
            for key,val in self.config.iter("tail"):
                if source["name"].startswith(key) or key == '*':
                    matchLen = len(key)
                    matchVal = val
            if matchLen > 0:
                ex.tail(matchVal)
            if "envs" in source:
                for env in source["envs"]:
                    ex.loadtool(self.config, env)
            if "files" in source:
                for tool, att, dest in source["files"]:
                    ex.loadfile(self.config, dest, tool, att)
            if "expose" in source:
                for raw in source["expose"]:
                    lst = raw.split(':')
                    pth = Path(lst[0])
                    name = lst[1] if len(lst) > 1 else None
                    ex.expose(pth, name)
            if "discover" in source:
                for raw in source["discover"]:
                    lst = raw.split(':')
                    pth = Path(lst[0])
                    name = lst[1] if len(lst) > 1 else None
                    ex.discover(pth, name)
            if "result" in source:
                ex.result(self.getResult())
            if "export" in source:
                for exp in source["export"]:
                    base = Path(exp["base"]) if "base" in exp else None
                    dest = Path(exp["dest"]) if "dest" in exp else None
                    group = exp["group"] if "group" in exp else None
                    ex.export(exp["pattern"], base, dest, group)
            if "script" in source:
                aoe = source['abortOnError'] if 'abortOnError' in source else True
                interactive = source['interactive'] if 'interactive' in source else False
                ex.setCall(source["name"], Path(source["script"]), abortOnError=aoe, interactive=interactive)
            if "parallel" in source:
                ex.mode = ExecMode.PARALLEL
                for item in source["parallel"]:
                    gen(ex, item)
            if "sequence" in source:
                ex.mode = ExecMode.SEQUENCE
                for item in source["sequence"]:
                    gen(ex, item)
            if "command" in source:
                ex.mode = ExecMode.SEQUENCE
                gen(ex, source['command'])
            return ex
        #
        self.root = gen(None, self.pipe)

    def getResult(self) -> Path:
        rdir = Path(self.config.get("RoadExec", "resultDir"))
        self.result = rdir / self.name
        return self.result

    def mkResult(self):
        if self.result is not None:
            self.result.mkdir(parents=True, exist_ok=True)

    def run(self):
        log = logging.getLogger("roadexec")

        #execution thread
        if self.config.get("run", "dry") == "True":
            log.info("Dry run, no execution")
            ret = 0
        else:
            self.execute()
            try:
                ret = self.root.returnValue.value
            except AttributeError:
                ret = -1
        log.info(banner("RoadExec", False))
        return ret

    def execute(self):
        log = logging.getLogger("roadexec")
        self.readPipeline()

        def statusDaemon(status:Status, stop:threading.Event):
            while not stop.wait(1.0):
                status.update()
                status.write()
            status.update()
            status.write()
        status = Status(self.root, Path("status.ini"))
        statusStop = threading.Event()
        statusThread = threading.Thread(target=statusDaemon, args=(status, statusStop), name="statusDaemon")
        statusThread.start()
        
        self.mkResult()
        self.root.start()
        while True:
            try:
                self.root.finished.wait()
                break
            except KeyboardInterrupt: #TODO exit strategy if thing don't work
                log.info("Interruption by User")
                self.root.interrupt()

        statusStop.set()
        statusThread.join()
        log.info("return value summary:")
        def dump(itm, indent=0):
            lines = []
            if itm.returnValue is None:
                val = "None"
            else:
                val = str(itm.returnValue.value)
                if itm.returnValue.ignored:
                    val += " (ignored)"
            lines.append(("  " * indent) + f"{itm.name} -> {val}")
            for child in itm.children:
                lines += dump(child, indent+1)
            return lines
        for itm in dump(self.root):
            log.info(itm)
        
        if self.root.returnValue is None:
            return -1
        elif self.root.returnValue.ignored:
            return 0
        else:
            return self.root.returnValue.value
    
    def exit(self, ret):
        if self.isMain:
            sys.exit(ret)

