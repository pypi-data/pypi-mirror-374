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

from dataclasses import dataclass
import logging
from pathlib import Path
from roadexec.fn import etype
from roadrunner.config import BadValue, ConfigContext, NoValue, PathNotExist
from roadrunner.lua import LuaCtxt, LuaSnippet


NAME = "stages"
LOGNAME = "stages"

#cmd:
#  tool: StageShell
#  stages:
#    prepare: false #don't run the prepare standard phase
#    build:
#      scriptFile: build.sh
#      after: prepare
#    test: true
#  
#

class Stages:
    templates: dict[str,LuaSnippet] #must contain a main template
    stages: list[str] #ordered list of stages to run
    fileExt: str #file extension to name the generated scripts
    def __init__(self, mainTpl:LuaSnippet, ext:str):
        self.templates = {'main': mainTpl}
        self.disables = set()
        self.stages = []
        self.fileExt = ext

    def setStage(self, name:str, tpl:LuaSnippet=None, enable:bool=None, idx:int=None):
        etype((name, str), (tpl, (None,LuaSnippet)), (enable, (None,bool)), (idx,(None,int)))
        log = logging.getLogger(LOGNAME)
        if tpl is not None:
            log.debug(f"stage:{name} set tpl!")
            self.templates[name] = tpl
        if name == 'main':
            return
        if (idx is not None) and name in self.stages:
            self.stages.remove(name)
        if name not in self.stages:
            if idx is None:
                log.debug(f"stage:{name} add stage at the end")
                self.stages.append(name)
            else:
                log.debug(f"stage:{name} add stage at pos:{idx}")
                self.stages.insert(idx, name)
        if enable is not None:
            if enable and name in self.disables:
                log.debug(f"stage:{name} enable!")
                self.disables.remove(name)
            elif not enable and name not in self.disables:
                log.debug(f"stage:{name} disable!")
                self.disables.add(name)

    def render(self, wd:Path, dest:Path, lua:LuaCtxt):
        etype((dest, Path), (lua, LuaCtxt))
        assert 'main' in self.templates, "stages need a 'main' stage"
        scripts = {stage: str(dest / f'{stage}{self.fileExt}') for stage in self.stages}
        log = logging.getLogger(LOGNAME)
        log.debug(f"rendering stages:{self.stages}")
        lua.addVariables({
            'stages': [x for x in self.stages if x not in self.disables],
            'scripts': scripts
        })
        #render stages
        for stage, tpl in self.templates.items():
            with open(wd / dest / f'{stage}{self.fileExt}', "w") as fh:
                fh.write(lua.run(tpl))
        return dest / f'main{self.fileExt}'

    def loadConfig(self, cfg:ConfigContext):
        log = logging.getLogger(LOGNAME)
        log.debug(f"load stage config from:{cfg.pos()}")
        for key, ncfg in cfg:
            raw = cfg.get(".")
            if self.loadConfigStageBool(key, ncfg):
                continue
            if self.loadConfigStagePath(key, ncfg):
                continue
            if self.loadConfigStageSet(key, ncfg):
                continue
            ncfg.error(f"stage:{key} cannot read definition")

    def loadConfigStageBool(self, key:str, cfg:ConfigContext) -> bool: 
        log = logging.getLogger(LOGNAME)
        try:
            switch = cfg.get(".", isType=bool)            
        except (PathNotExist, BadValue):
            return False
        log.debug(f"stage:{key} load enable:{switch}")
        self.setStage(key, enable=switch)
        return True

    def loadConfigStagePath(self, key:str, cfg:ConfigContext) -> bool:
        log = logging.getLogger(LOGNAME)
        try:
            fpos = cfg.get(".", isOsPath=True)
        except (PathNotExist, BadValue):
            return False
        fname = (fpos[0].path / fpos[1])
        log.debug(f"stage:{key} load from:{fname}")
        data = fname.read_text()
        self.setStage(key, data)
        return True

    def loadConfigStageSet(self, key:str, cfg:ConfigContext) -> bool:
        log = logging.getLogger(LOGNAME)
        #load scriptFile
        fpos = cfg.get(".scriptFile", isOsPath=True, default=None)
        if fpos:
            fname = (fpos[0].path / fpos[1])
            log.debug(f"stage:{key} load from:{fname}")
            data = LuaSnippet(fname.read_text(), fname, 0, template=True)
        else:
            data = None
        #load inline script
        raw = cfg.get(".script", isType=str, default=None)
        if raw:
            if data is not None:
                log.warning(f"stage:{key} defines both a scriptFile and an inline script")
            log.debug(f"stage:{key} load from inline:{cfg.pos()}")
            ori = cfg.move(".script").origin()
            data = LuaSnippet(raw, ori.file, ori.line, template=True)
        #load enbale
        switch = cfg.get(".enable", isType=bool, default=None)
        #TODO allow specification with before/after on stages that are not yet loaded
        pos = None
        before = cfg.get(".before", isType=str, default=None)
        try:
            if before:
                pos = self.stages.index(before)
        except ValueError:
            raise BadValue(f"stage:{key} cannot be set before:{before} - does not exist", cfg.env, cfg.node)
        after = cfg.get(".after", isType=str, default=None)
        try:
            if after:
                pos = self.stages.index(after) + 1
        except ValueError:
            raise BadValue(f"stage:{key} cannot be set after:{after} - does not exist", cfg.env, cfg.node)
        if data is None and switch is None and pos is None:
            return False
        self.setStage(key, tpl=data, enable=switch, idx=pos)
        return True

