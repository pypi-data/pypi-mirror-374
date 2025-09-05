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
import threading
from typing import Callable

from roadrunner.fn import etype


LOGNAME = "tasks"

class Task:
    depends:list["Task"]
    def __init__(self, name:str, fn:Callable, args:tuple, hold:bool=False):
        etype((name, str), (fn, Callable))
        self.name = name    
        self.fn = fn        #function to call
        self.args = args    #args to call
        self.retCode = None
        self.predecessors = [] # tasks to wait before starting
        self.thread = threading.Thread(target=self.exec, name=f"{LOGNAME}.{self.name}")
        self.childs = []    #tasks created from this one
        self.created = threading.Event()
        self.finished = threading.Event()
        self.released = threading.Event() #hold released
        self.started = threading.Event() #start fn
        if not hold:
            self.released.set()
        self.thread.start()
        taskPool().getCurrTask().childs.append(self)

    def isRoot(self) -> bool:
        return False

    def __str__(self) -> str:
        msg = f"Task({self.name}"
        if self.retCode is not None:
            msg += ",r:" + str(self.retCode)
        msg += ")"
        return msg

    def isFinished(self) -> bool:
        return self.retCode is not None

    def isReleased(self):
        return self.released.is_set()

    def isStarted(self):
        return self.started.is_set()

    def exec(self):
        log = logging.getLogger(LOGNAME)
        taskPool()._register(self)
        self.created.set()
        log.info(f"task:{self.name} created")
        self.released.wait()
        log.debug(f"task:{self.name} released")
        waitForTasks(self.predecessors)
        log.debug(f"task:{self.name} predecessors finished")
        self.started.set()
        ret = self.fn(*self.args)
        log.info(f"task:{self.name} finish with code:{ret}")
        self.retCode = -1 if ret is None else ret
        self.finished.set()

    def threadId(self):
        self.created.wait()
        return self.thread.ident
    
    def dependOn(self, pred:"Task"):
        if self.released.is_set():
            logging.getLogger(LOGNAME).warning(f"add predecessor to task:{self.threadId()} that is already started")
        self.predecessors.append(pred)

def waitForTasks(tasks:list["Task"]):
    for task in tasks:
        task.finished.wait()

class RootTask(Task):
    def __init__(self):
        self.name = "root"    
        self.retCode = None
        self.childs = []    #tasks created from this one
        self.thread = threading.currentThread()
        self.finished = threading.Event()
        self.created = threading.Event()
        taskPool()._register(self)
        self.created.set()

    def isRoot(self) -> bool:
        return True

class TaskPool:
    def __init__(self):
        self.tasks = {} #threading.ident -> Task
        self.lock = threading.Lock()

    def getCurrTask(self) -> Task:
        log = logging.getLogger(LOGNAME)
        tid = threading.get_ident()
        with self.lock:
            return self.tasks[tid]
    
    def getTask(self, tid:int) -> Task:
        log = logging.getLogger(LOGNAME)
        with self.lock:
            return self.tasks[tid]

    def _register(self, task:Task):
        log = logging.getLogger(LOGNAME)
        tid = task.thread.ident
        with self.lock:
            self.tasks[tid] = task

poolInst:TaskPool = TaskPool()
def taskPool() -> TaskPool:
    return poolInst
