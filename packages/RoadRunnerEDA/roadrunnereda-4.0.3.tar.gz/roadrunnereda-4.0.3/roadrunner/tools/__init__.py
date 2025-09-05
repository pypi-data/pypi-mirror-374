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

import importlib
import logging
import pkgutil
from roadrunner.config import ConfigContext
from roadrunner.fn import etype

#load tools
tools = {}
for modinfo in pkgutil.iter_modules(__path__):
    mod = importlib.import_module("." + modinfo.name, __package__)
    if hasattr(mod, 'NAME'):
        if mod.NAME in tools:
            logging.getLogger('RR').warning(f"overwrite tool: {mod.NAME}")
        tools[mod.NAME] = mod
    else:
        del mod

def loadtools(cfg:ConfigContext):
    for _,tool in tools.items():
        if hasattr(tool, 'load'):
            tool.load(cfg)

def getcmd(name:str, fn:str='run') -> callable:
    try:
        return getattr(tools[name], "cmd_" + fn)
    except KeyError:
        raise ToolException(f"tool:{name}.{fn} not found")

def getquery(name:str) -> callable:
    etype((name, str))
    fn = None
    for tool in tools.values():
        if hasattr(tool, "query_" + name):#
            if fn:
                logging.getLogger("RR").warning(f"multiple tools provide query:{name}")
            fn = getattr(tool, "query_" + name)
    if fn is None:
        raise ToolException(f"query:{name} not found")
    return fn

class ToolException(Exception):
    pass