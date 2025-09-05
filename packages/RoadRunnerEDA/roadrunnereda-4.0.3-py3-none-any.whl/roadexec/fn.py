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

import configparser
import re
import shutil
import stat
from typing import Iterable, Union
import os
from pathlib import Path
import logging

#checks if the type of a variable is correct
# takes tuples of (varibale, types, [[keyTypes], valTypes])
# types can be a tuple of types that are allowed and also None
# if a variable is list, tuple or set the values are checked against the valTypes
# same with dicts and keyTypes and valTypes
def etype(*args) -> bool:
    for idx,tup in enumerate(args):
        #break up tuple
        if len(tup) == 2:
            var,varTup = tup
            keyTup, valTup = None, None
        elif len(tup) == 3:
            var,varTup,valTup = tup
            keyTup = None
        elif len(tup) == 4:
            var,varTup,keyTup,valTup = tup
        else:
            raise ValueError(f"wrong number of arguments:{len(tup)}")
        ##### make sets
        def makeSet(tup):
            if tup is None:
                return None, False
            if not isinstance(tup, tuple):
                return (tuple(), True) if tup is None else ((tup,), False)
            return tuple(filter(lambda x: x is not None, tup)), None in tup
        varTypes, varNone = makeSet(varTup)
        keyTypes, keyNone = makeSet(keyTup)
        valTypes, valNone = makeSet(valTup)
        #check
        def check(var, types, none):
            if none and var is None:
                return
            if types is None or isinstance(var, types):
                return 
            raise TypeError(f"wrong type:{type(var)} != {types} in argument #{idx}")
        check(var, varTypes, varNone)
        #check iteratables
        if isinstance(var, (list, tuple, set)) and valTypes is not None:
            for val in var:
                check(val, valTypes, valNone)
        if isinstance(var, dict):
            for key,val in var.items():
                check(key, keyTypes, keyNone)
                check(val, valTypes, valNone)
    return True

def ctype(*args):
    try:
        return etype(*args)
    except TypeError:
        return False

def banner(title, head=True):
    if head:
        return f"--=={title:-^60}==--"
    else:
        tmp = f"({title})"
        return f"--=={tmp:^60}==--"

def cleardir(path):
    "remove all files from directory"
    for itm in path.iterdir():
        if itm.is_dir():
            shutil.rmtree(itm)
        else:
            itm.unlink()

def mkFile(path:Path, target:Path=None, mode:int=None, mkdir:bool=True, unlink:bool=True,
           hardlink:bool=False, symlink:bool=False, copy:bool=True):
    "set file attributes, may even create a hard or symlink"
    etype((path, Path), (target, (Path, None)), (mode, (int, None)), (mkdir, bool), (unlink, bool),
          (hardlink, bool), (symlink, bool), (copy, bool))
    log = logging.getLogger("mkFile")
    log.debug(f"mkfile:{path} target:{target} mode:{mode} mkdir:{mkdir} unlink:{unlink} hardlink:{hardlink} symlink:{symlink} copy:{copy}")
    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    if unlink and (path.exists() or path.is_symlink()):
        path.unlink()
    if target is None:
        path.touch()
    else:
        done = False
        if symlink:
            try:
                os.symlink(target, path)
                done = True
            except OSError:
                pass
        if hardlink and not done:
            try:
                os.link(target, path)
                done = True
            except OSError:
                pass
        if copy and not done:
            try:
                shutil.copyfile(target, path)
                done = True
            except OSError:
                pass
        if not done:
            raise Exception(f"cannot create file:{path} from:{target}"
                            f"{' (sym)' if symlink else ''}"
                            f"{' (hard)' if hardlink else ''}"
                            f"{' (copy)' if copy else ''}"
            )
    if mode:
        path.chmod(mode)

def mkLink(path:Path, target:Path, mode:int=None, mkdir:bool=True, unlink:bool=True):
    "create a hardlink"
    mkFile(path, target, mode, mkdir, unlink, True, False, True)

def mkSymlink(path:Path, target:Path, mode:int=None, mkdir:bool=True, unlink:bool=True):
    "create a symlink"
    mkFile(path, target, mode, mkdir, unlink, False, True, False)

def cpFile(path:Path, target:Path, mode:int=None, mkdir:bool=True, unlink:bool=True):
    "copy a file"
    mkFile(path, target, mode, mkdir, unlink, False, False, True)

def clonedir(source:Path, dest:Path):
    "copy a tree - but do it with hardlinks"
    etype((source, Path), (dest, Path))
    shutil.copytree(source, dest, copy_function=clonedirCopy, dirs_exist_ok=True)
    #make directories writeable
    def mkwr(path:Path):
        mode = path.stat().st_mode
        mode |= stat.S_IRWXU
        path.chmod(mode)
        for itm in path.iterdir():
            if itm.is_dir():
                mkwr(itm)
    mkwr(dest)

def clonedirCopy(source, dest):
    etype((source, str), (dest, str))
    cpFile(Path(dest), Path(source))

def clonefile(source:Path, dest:Path):
    "link a file - make directories as needed"
    cpFile(dest, source)
    # etype((source, Path), (dest, Path))
    # dest.parent.mkdir(exist_ok=True, parents=True)
    # linkfile(source, dest)

def clone(source:Path, dest:Path):
    "copy directory of file"
    etype((source, Path), (dest, Path))
    if source.is_dir():
        clonedir(source, dest)
    else:
        clonefile(source, dest)

#needs to use os.path.relpath because Path.relative_to work differently
# https://docs.python.org/3/library/pathlib.html -> footnote 1
def relpath(path:Path, start:Path):
    "return path relative to start"
    etype((path, Path), (start, Path))
    relatived = os.path.relpath(path, start)
    pathed = Path(relatived)
    return pathed

def uniqueExtend(base:list, ext:Iterable):
    etype((base, list), (ext, Iterable))
    for itm in ext:
        if itm not in base:
            base.append(itm)

class IniConfigParserSpec(configparser.ConfigParser):
    def getPath(self, group, attr) -> Path:
        return Path(self.get(group, attr))
    def getEsc(self, group, attr) -> str:
        raw = self.get(group, attr)
        return bytes(raw, "utf-8").decode("unicode_escape")

class IniConfig:
    CONFIG_FILES = [
        "/etc/roadrunner/config.ini",
        "~/.config/roadrunner/config.ini"
    ]
    DEFAULTS = {
        "loglevel": {
        },
        "logging": {
            "formatConsole": "%(threadName)-14s | %(message)s",
            "formatFile": "%(asctime)s | %(levelname)-8s | %(threadName)-14s | %(message)s (%(name)s)",
            "levelConsole": "INFO",
            "levelFile": "DEBUG"
        }
    }
    LOGNAME = "Config"

    def __init__(self):
        log = logging.getLogger(self.LOGNAME)
        self.config = IniConfigParserSpec(interpolation=None)
        for group,vars in self.DEFAULTS.items():
            for key,val in vars.items():
                self.set(group, key, val)
        expanded = [Path(x).expanduser() for x in self.CONFIG_FILES]
        self.config.read(expanded)

    def hasSection(self, section:str) -> bool:
        etype((section, str))
        return section in self.config

    def hasValue(self, group:str, attr:str) -> bool:
        try:
            self.get(group, attr)
            return True
        except NotIniConfig:
            return False

    def get(self, group:str, attr:str, path:bool=False, esc:bool=False) -> str:
        etype((group, str), (attr, str))
        try:
            if path:
                return self.config.getPath(group, attr)
            elif esc:
                return self.config.getEsc(group, attr)
            else:
                return self.config.get(group, attr)
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass
        raise NotIniConfig(f"Config cannot find g:{group} a:{attr}")
    
    def iter(self, group:str):
        if group not in self.config:
            return
        for key,val in self.config[group].items():
            yield key, val
    
    def set(self, group:str, key:str, val:str) -> str:
        etype((group, str), (key, str), (val, str))
        if group not in self.config:
            self.config[group] = {}
        self.config.set(group, key, val)


class NotIniConfig(Exception):
    pass

REX_CONFIG = r'([\w\.]+):([\w\.]+)\s*=\s*([\w\/\-\._]+)'
def configParse(itm:str, log:bool=False) -> tuple[str, str, str]:
    if log:
        m = re.match(REX_CONFIG, "loglevel:" + itm)
    else:
        m = re.match(REX_CONFIG, itm)
    if m is None:
        raise Exception(f"cannot parse setup item:{itm}")
    section = m.group(1)
    key = m.group(2)
    value = m.group(3)
    return section, key, value

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
