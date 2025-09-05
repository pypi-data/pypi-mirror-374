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
from roadrunner.config import ConfigContext, parsePathOption
from roadrunner.lua import LuaCtxt, LuaSnippet
from roadrunner.rr import Pipeline
from roadrunner.tasks import Task, taskPool, waitForTasks
from roadrunner.tools.builtin import invoke


NAME = "Flow"
DESCRIPTION = "Tool Flow Control"

def taskRun(cmd:str, cfg:ConfigContext):
    cpath, opts = parsePathOption(cmd)
    ccfg = cfg.move(cpath, opts)
    return invoke(ccfg)


def impLua(lua:LuaCtxt, cfg:ConfigContext):
    lua.addVariables({
        'task': lambda name, cmd: luaCreateTask(name, cmd, cfg, hold=False),
        'create': lambda name, cmd: luaCreateTask(name, cmd, cfg, hold=True),
        'release': luaStart,
        'depend': luaDepend,
        'status': luaStatus,
        'wait': luaWaitTask
    })

def luaCreateTask(name:str, cmd:str, cfg:ConfigContext, hold:bool) -> int:
    log = logging.getLogger(NAME)
    task = Task(name, taskRun, (cmd, cfg), hold=hold)
    tid = task.threadId()
    #log.info(f"created task:{tid} hold:{hold}")
    return tid
    
def luaStart(tid:int):
    tasks = taskPool()
    tsk = tasks.getTask(tid)
    if tsk.released.is_set():
        logging.getLogger(NAME).warning(f"staring task:{tid} that is already released")
    tsk.released.set()

def luaDepend(first:int, second:int):
    tasks = taskPool()
    ftsk = tasks.getTask(first)
    stsk = tasks.getTask(second)
    stsk.dependOn(ftsk)

def luaStatus(tsk:int):
    tasks = taskPool()
    task = tasks.getTask(tsk)
    return {
        'finished': task.isFinished(),
        'started': task.isStarted(),
        'released': task.isReleased(),
        'returnCode': task.retCode,
        'command': task.args[0]
    }
    
def luaWaitTask(tsk:int=None):
    tasks = taskPool()
    task = tasks.getTask(tsk)
    task.finished.wait()
      
def cmd_run(cfg:ConfigContext, _:Pipeline, __:str):
    log = logging.getLogger(NAME)
    raw = cfg.get(".script", isType=str)
    ori = cfg.move(".script").origin()
    snip = LuaSnippet(raw, ori.file, ori.line, program=True)
    #log.info(snip)
    lua = cfg.lua()
    impLua(lua, cfg)
    kern = lua.compile(snip)
    log.debug("Lua: enter script")
    kern.call()
    log.debug("Lua: return from script")
    return 0

def cmd_pool(cfg:ConfigContext, _:Pipeline, __:str):
    log = logging.getLogger(NAME)
    tsks:list[Task] = []
    for key,ccfg in cfg:
        if key == "tool":
            continue
        tsk = Task(key, invoke, (ccfg,))
        log.debug(f"add task to pool:{ccfg.pos()} uid:{ccfg.real().uid()} as:{tsk.threadId()}")
        tsks.append(tsk)
    #wait for taks to finish
    waitForTasks(tsks)
    ret = 0
    for task in tsks:
        ret |= task.retCode

    return ret

def cmd_sequence(cfg:ConfigContext, _:Pipeline, __:str):
    log = logging.getLogger(NAME)
    tsks:list[Task] = []
    last = None
    for key,ccfg in cfg:
        if key == "tool":
            continue
        tsk = Task(key, invoke, (ccfg,), hold=True)
        if last is not None:
            tsk.dependOn(last)
        tsk.released.set()
        last = tsk
        log.debug(f"add task to sequence:{ccfg.pos()} uid:{ccfg.real().uid()} as:{tsk.threadId()}")
        tsks.append(tsk)
    #wait for taks to finish
    waitForTasks(tsks)
    ret = 0
    for task in tsks:
        ret |= task.retCode

    return ret

