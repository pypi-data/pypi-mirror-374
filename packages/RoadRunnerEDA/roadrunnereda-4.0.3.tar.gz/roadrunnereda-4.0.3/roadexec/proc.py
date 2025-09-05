import logging
import os
import pathlib
import signal
import subprocess
import sys
import termios
import threading
import time

import psutil

class ProcLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[{self.extra['name']}] {msg}", kwargs

def procLogger(name):
    return ProcLoggerAdapter(logging.getLogger(name), {'name': name })

class Proc(object):
    UPDATE_CYCLE = 0.1
    def __init__(
        self, args, wd:pathlib.Path, name:str, toShell:bool=True,
        interactive:bool=False, tail:str=None, environ:dict=None
    ):
        self.killSequence = [
            #(signal, delay after signal)
            (None, None),           #run forever
            (signal.SIGINT, 3.0),   #first KeyboardInterrupt -> send SIGINT, wait...
            (signal.SIGINT, 0.5),   # double sigint
            (signal.SIGINT, 5.0),   # ...is important for some programs
            (signal.SIGTERM, 5.0),  # SIGTEM and SIGKILL with pause inbetween
            (signal.SIGKILL, 5.0)   # after last wait, RaodRunner will end and warn that a process was not killed
        ]
        self.log = procLogger(name)
        #cmd
        cmd = args
        #start process
        self.interactive = interactive
        self.fStdout = None #filename
        self.fStderr = None
        self.hStdout = None #log tail handle
        self.hStderr = None
        self.bStdout = ""   #log tail buffer
        self.bStderr = ""
        self.tStderr = tail in ['stderr', 'both'] #log tail modus
        self.tStdout = tail in ['stdout', 'both']
        self.phStdout = None    #process file handles
        self.phStderr = None
        if interactive:
            #save terminal state
            fn = sys.stdin.fileno()
            self.termattr = termios.tcgetattr(fn)
            #start process
            self.popen = subprocess.Popen(cmd, cwd=wd)
        else:
            if environ is not None:
                env = os.environ.copy()
                env.update(environ)
            else:
                env = None
            self.fStdout = wd / ('stdout' if name is None else f'{name}.stdout')
            self.fStderr = wd / ('stderr' if name is None else f'{name}.stderr')
            self.log.info(f"stdout:{self.fStdout} stderr:{self.fStderr}")
            self.phStdout = open(self.fStdout, 'w')
            self.phStderr = open(self.fStderr, 'w')
            self.popen = subprocess.Popen(
                cmd, cwd=wd, stdout=self.phStdout, stderr=self.phStderr,
                start_new_session=True, env=env
            )
        #
        self.process = [psutil.Process(self.popen.pid)]
        self.name = name
        self.intEvent = threading.Event()

    def __del__(self):
        if self.popen.returncode is None:
            self.log.error("SubProcess was not terminated - please investigate")
        #restore term
        if self.interactive:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.termattr)
            except ValueError: #already closed
                pass
        #close still open files
        if self.hStderr:
            self.hStderr.close()
        if self.hStdout:
            self.hStdout.close()

    def _update_process(self):
        for proc in self.process:
            try:
                for child in proc.children(recursive=True):
                    if child not in self.process:
                        self.process.append(child)
                        self.log.debug(f"new child process: {child.pid}")
            except psutil.NoSuchProcess:
                pass
        alive = []
        for proc in self.process:
            if proc.is_running():
                alive.append(proc)
            else:
                self.log.debug(f"child disappeared: {proc.pid}")
        self.process = alive

    def signal(self, sig):
        self._update_process()
        for p in self.process:
            try:
                p.send_signal(sig)
            except psutil.NoSuchProcess:
                pass

    def finish(self):
        killIter = iter(self.killSequence)
        killStep = True
        killTime = None
        while True:
            if killTime and killTime < time.time():
                killStep = True
            if killStep:
                try:
                    sig, delay = next(killIter)
                except StopIteration:
                    self.log.warn("kill sequence end")
                    break
                if sig:
                    self.log.info(f"signal:{sig.name} next in:{delay}")
                    self.signal(sig)
                killTime = time.time() + delay if delay else None
                killStep = False
            self._update_process()
            if self.popen.returncode is None and self.popen.poll() is not None:
                self.log.debug("main subprocess exited")
                #if killTime is None: #TODO: why start kill sequence when main proc is gone
                #    killStep = True
            if len(self.process) == 0:
                self.log.debug("all childs gone - break")
                break
            delay = max(0, 1.0 if killTime is None else killTime - time.time())
            delay = min(self.UPDATE_CYCLE, delay)
            if self.intEvent.wait(timeout=delay):
                self.intEvent.clear()
                self.log.debug("got interrupt - killStep!")
                killStep = True
            self.logTick()
            #time.sleep(0.5)
        self.popen.poll()
        self.logTick(end=True)
        #restore term
        if self.interactive:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.termattr)
        #
        return self.popen.returncode

    def interrupt(self):
        self.intEvent.set()

    def logTick(self, end=False, errTail=False):
        if errTail:
            self.log.info("Error tail (-10):")
        if self.tStderr or errTail:
            tailLines = []
            if self.hStderr is None:
                self.hStderr = open(self.fStderr, 'r')
            while True:
                raw = self.hStderr.read()
                self.bStderr += raw
                if raw == "":
                    break
                lines = self.bStderr.splitlines()
                for line in lines if end else lines[:-1]:
                    fmt = f"E:{line}"
                    if self.tStderr:
                        self.log.info(fmt)
                    tailLines.append(fmt)
                    tailLines = tailLines[-10:]
                if not end and len(lines) > 1:
                    self.bStderr = self.bStderr.splitlines(keepends=True)[-1]
            if errTail and not self.tStderr:
                for line in tailLines:
                    self.log.info(line)
        if self.tStdout or errTail:
            tailLines = []
            if self.hStdout is None:
                self.hStdout = open(self.fStdout, 'r')
            while True:
                raw = self.hStdout.read()
                self.bStdout += raw
                if raw == "":
                    break
                lines = self.bStdout.splitlines()
                for line in lines if end else lines[:-1]:
                    fmt = line
                    if self.tStderr:
                        self.log.info(fmt)
                    tailLines.append(fmt)
                    tailLines = tailLines[-10:]
                if not end and len(lines) > 1:
                    self.bStdout = self.bStdout.splitlines(keepends=True)[-1]
            if errTail and not self.tStdout:
                for line in tailLines:
                    self.log.info(line)
