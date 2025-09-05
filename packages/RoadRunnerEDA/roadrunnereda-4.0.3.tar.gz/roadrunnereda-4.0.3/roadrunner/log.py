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
import logging.handlers
import re
import sys
from pathlib import Path
import threading
from typing import Union

import roadrunner.config as config

CONFIG_SCOPE = ".log" #in :_setup
CONFIG_ORIGIN = config.Origin(22, 0, "log.py")
CONFIG_DEFAULT = {
    "logDir": "log",
    "logFileEnabled": True,
    "level": {
        "root": "DEBUG",
        "_console": "INFO",
        "_file": "DEBUG"
    },
    "tasks": {
        "root": "WARNING",
        "tasks": "INFO",
        "lua": "INFO"
    },
    "formatConsole": "%(threadName)-14s | %(message)s",
    "formatFile": "%(asctime)s | %(levelname)-8s | %(threadName)-14s | %(message)s (%(name)s)",
}

class ThreadFilter(logging.Filter):
    def __init__(self, tName:str, levels:dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tName = tName
        self.levels = levels

    def filter(self, record) -> bool:
        if record.threadName == self.tName:
            return True
        try:
            if record.levelno >= self.levels[record.name]:
                return True
        except KeyError:
            pass
        return False 

# add default logging config to config space
def configSetup(setup:config.ConfigContext):
    node = config.makeConfigVal(CONFIG_DEFAULT, CONFIG_ORIGIN)
    setup.assimilate(CONFIG_SCOPE, node, )

# def init logging as set in the config
def initLogging(setup:config.ConfigContext):
    cfg = setup.move(CONFIG_SCOPE)
    #log dir
    logDir = Path(setup.get(".workdir_base"), cfg.get(".logDir"))
    logFileEnabled = cfg.get(".logFileEnabled", isType=bool)
    if logFileEnabled:
        logDir.mkdir(parents=True, exist_ok=True)
    #basic levels 
    for scope,levelStr in cfg.get(".level", default={}).items():
        if scope[0] == '_':
            continue
        if scope == 'root':
            scope = None
        level = loggingLevelInt(levelStr)
        logging.getLogger(scope).setLevel(level)
    #task levels
    taskLevels = {}
    for key,val in cfg.get(".tasks").items():
        ival = loggingLevelInt(val)
        taskLevels[key] = ival
    #configure output
    root = logging.getLogger()
    #console logging
    formatter = logging.Formatter(cfg.get(".formatConsole"))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(loggingLevelInt(cfg.get(".level._console")))
    handler.addFilter(ThreadFilter(threading.current_thread().getName(), taskLevels))
    root.addHandler(handler)
    #file logging
    if logFileEnabled:
        formatter = logging.Formatter(cfg.get(".formatFile"))
        handler = logging.handlers.RotatingFileHandler(logDir / "roadrunner.log", maxBytes=0, backupCount=5)
        handler.setFormatter(formatter)
        handler.setLevel(loggingLevelInt(cfg.get(".level._file")))
        handler.doRollover()
        root.addHandler(handler)

#gets a loglevel integer from a string or int
REX_LEVEL = r'(\w+)(\+(\d+))?'
def loggingLevelInt(val:Union[str,int]) -> int:
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            pass
        m = re.match(REX_LEVEL, val)
        if m is None:
            raise Exception(f"cannot parse log level:{val} from string")
        name = m.group(1).lower()
        offstr = m.group(3)
        if offstr is not None:
            offset = int(offstr)
        else:
            offset = 0
        if name in ['debug', 'dbg', 'd']:
            base = logging.DEBUG
        elif name in ['info', 'i']:
            base = logging.INFO
        elif name in ['warn', 'warning', 'w']:
            base = logging.WARNING
        elif name in ['err', 'error', 'e']:
            base = logging.ERROR
        elif name in ['crit', 'critical', 'c']:
            base = logging.CRITICAL
        else:
            raise Exception(f"unknown logging level name:{name}")
        return base + offset
    raise Exception(f"cannot parse log level:{val} from:{type(val)}")

