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
from enum import Enum
import logging
import pathlib
from typing import Any, Callable, Iterable

from roadrunner.fn import ctype, etype
import re
import yaml

from roadrunner.lua import LuaCtxt, LuaSnippet, LuaError

LOGNAME = "config"

def makeConfigVal(raw, origin:Origin=None, location:Location=None) -> ConfigNode:
    etype((origin, (Origin, None)), (location, (Location, None)))
    if isinstance(raw, (int, bool)) or raw == '':
        return ConfigLeaf(raw, origin, location)
    elif isinstance(raw, str):
        if raw[0] == '=':
            return ConfigLink(raw, origin, location)
        elif raw[0] == '$':
            return ConfigScript(raw, origin, location)
        elif raw[0] == '+':
            return ConfigImport(raw, origin, location)
        else:
            return ConfigLeaf(raw, origin, location)
    elif isinstance(raw, dict):
        #check if it is a consitional dict
        cond = None
        for key in raw:
            if key == '__origins__':
                continue
            ncond = True if key[0] == '/' else False
            if cond is None:
                cond = ncond
            elif cond != ncond:
                raise Exception("dictionary is not pure")
        if cond:
            return ConfigCond(raw, origin, location)
        else:
            return ConfigDict(raw, origin, location)
    elif isinstance(raw, list):
        return ConfigList(raw, origin, location)
    else:
        raise Exception(f"cannot construct ConfigVal from:{type(raw)}")

class SafeLineLoader(yaml.loader.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep)
        lines = {}
        for key_node,val_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key not in mapping:
                raise Exception("cannot create mapping")
            lines[key] = Origin(key_node.start_mark.line+1, key_node.start_mark.column, key_node.start_mark.name)
        mapping['__origins__'] = lines
        return mapping

    def construct_sequence(self, node):
        lst = super(SafeLineLoader, self).construct_sequence(node)
        lines = []
        for itm_node in node.value:
            lines.append(Origin(itm_node.start_mark.line+1, itm_node.start_mark.column, itm_node.start_mark.name))
        if len(lines):
            lst.append(lines)
        return lst

def makeConfigFromFile(fname):
    etype((fname, pathlib.Path))
    with open(fname, "r") as fh:
        f_json = yaml.load(fh, Loader=SafeLineLoader)
    orig = Origin(0, 0, fname)
    loc = Location(fname.parent)
    return makeConfigVal(f_json, orig, loc)

def makeConfigFromStr(raw:str, location:pathlib.Path) -> ConfigNode:
    f_json = yaml.load(raw, Loader=SafeLineLoader)
    return makeConfigVal(f_json, location=location)

def makeConfigFromManifest(fname:pathlib.Path) -> ConfigNode:
    etype((fname, pathlib.Path))
    mani = configparser.ConfigParser()
    mani.read(fname)
    data = {}
    for key, val in mani.items('manifest'):
        lst = [v.strip() for v in val.split('\n')]
        if len(lst) == 1:
            lst = lst[0]
        data[key] = lst
    return makeConfigVal(data, origin=Origin(0, 0, fname), location=Location(fname.parent))

def writeConfigToFile(cnf:ConfigNode, fname):
    with open(fname, "w") as fh:
        fh.write(writeConfigToStr(cnf))

def writeConfigToStr(cnf:ConfigNode) -> str:
    return yaml.dump(cnf.export())

class NoValue(object):
    pass

class ConfigEnv:
    flags:dict[str,Option]
    hist:ConfigPath
    node:ConfigNode
    PATH_WIDTH = 40
    def __init__(self):
        self.pred = None # env derived from this env
        self.operation = ("Env", ) # (operation, [parameter, ...]) that created this env
        self.hist = ConfigPath('')
        self.flags = {}

    def derive(self, op:tuple[str, ...], move:ConfigPath=None, addFlags:set[Option]=None, remFlags:set[str]=None) -> ConfigEnv:
        etype((op, (tuple, str)), (move, (ConfigPath, None)), (addFlags, (set, None), Option), (remFlags, (set, None), str))
        env = ConfigEnv()
        env.pred = self
        env.operation = op
        env.hist = self.hist if move is None else (self.hist + move)
        env.flags = self.flags.copy()
        if addFlags:
            for fl in addFlags:
                env.flags[fl.key] = fl
        if remFlags:
            for key in remFlags:
                del env.flags[key]
        return env

    def __repr__(self):
        return f"ConfigEnv({self.hist}," + ",".join(self.flags) + ")"

    def optionsUid(self, sentinal:set=None) -> str:
        if sentinal is None:
            sentinal = set()
        flst:list[Option] = [opt for key,opt in self.flags.items() if key in sentinal]
        flst.sort(key=lambda x: x.key)
        #TODO escape +
        return "+".join([str(x) for x in flst])

    def dump(self) -> list[str]:
        msg = [f"{self} - trace:"]
        curr = self
        while curr:
            msg.append(curr.dumpLine())
            curr = curr.pred
        return msg

    def dumpLine(self) -> str:
        try:
            pathStr = str(self.hist)
        except:
            pathStr = "EXCP"
        opStr = " ".join(self.operation) or "NOOP"
        return f"  @{pathStr:{self.PATH_WIDTH}} - {opStr}"

class ConfigNode:
    NAME = "ConfigNode"
    def __init__(self, raw:ConfigNode=None, origin:Origin=None, location:Location=None):
        etype((origin, (Origin, None)), (location, (Location, None)))
        if isinstance(raw, ConfigNode):
            self.origin = origin or raw.origin
            self.location = location or raw.location
            self.parent = raw.parent
            self.key = raw.key
            self.isFileRoot = raw.isFileRoot
        else:
            self.location = location
            self.origin = origin
            self.parent = None
            self.key = None
            self.isFileRoot = False

    def clone(self, origin:Origin=None, location:Location=None):
        return self.__class__(self, origin, location)

    def items(self, env:ConfigEnv) -> Iterable[tuple[str,ConfigEnv]]:
        denv, dnode = self.delegate(env)
        if denv is not None:
            yield from dnode.items(denv)
            return
        raise NotIteratable

    #when cold is true the delegate will only be returned if alread loaded
    def delegate(self, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        return None,None #default is not delegating

    def getId(self) -> int:
        return id(self)
    
    def getRoot(self, file=False) -> ConfigNode:
        curr = self
        while curr.parent is not None:
            #file root
            if file and curr.isFileRoot:
                return curr
            curr = curr.parent
        return curr
    
    def getChild(self, key:str, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        etype((key, str), (env, ConfigEnv))
        denv, dnode = self.delegate(env)
        if denv:
            return dnode.getChild(key, denv)
        raise ChildError(f"cannot get child of {self.NAME}", env, self)

    def setChild(self, key:str, val:ConfigNode, env:ConfigEnv):
        etype((key, str), (val, ConfigNode), (env, ConfigEnv))
        denv, dnode = self.delegate(env)
        if denv is not None:
            return dnode.setChild(key, val, env)
        raise ChildError("cannot get child of {self.NAME}", env, self)

    def getValue(self, env:ConfigEnv) -> any:
        etype((env, ConfigEnv))
        denv, dnode = self.delegate(env)
        if denv is not None:
            return dnode.getValue(denv)
        raise BadValue(f"cannot get value of {self.NAME}", env, self)
    
    def merge(self, other:ConfigNode, env:ConfigEnv, overwrite:bool=False):
        etype((other, ConfigNode), (env, ConfigEnv))
        denv, dnode = self.delegate(env)
        if denv is not None:
            return dnode.merge(other, env, overwrite)
        raise BadValue(f"cannot merge {self.NAME}", env, self)

    def getLocation(self, env:ConfigEnv) -> Location:
        denv, dnode = self.delegate(env)
        if denv is not None:
            return dnode.getLocation(denv)
        return self.location

    def setParent(self, node:ConfigNode, key:str):
        self.parent = node
        self.key = key
    
    def getPath(self) -> ConfigPath:
        if self.parent is None:
            return ConfigPath("")
        if self.key is None:
            raise TreeCorrupt(f"cannot build name - partent key is None", None, self)
        return self.parent.getPath() + ConfigPath(f".{self.key}")

    def getLua(self, env:ConfigEnv) -> LuaCtxt:
        etype((env, ConfigEnv))
        lc = LuaCtxt()
        #vars
        def addVars(node:ConfigNode):
            if node.parent:
                addVars(node.parent)
            lc.addVariables(node.getVars())
        addVars(self)
        #env flags
        dd = {opt.key: True if opt.val is None else opt.val for opt in env.flags.values()}
        lc.addVariables(dd)
        #call hooks
        cfg = ConfigContext(self, env=env)
        try:
            for key,icfg in cfg.move(":_run.luaHooks"):
                val:callable = icfg.get(".")
                val(cfg, lc)
        except (PathNotExist, ChildError):
            pass
        return lc

    def getVars(self) -> dict[str,LuaSnippet|ConfigLink|str|int|bool]:
        return {}

    def __repr__(self) -> str:
        return f"{self.NAME}({self.getId()})"

    def dump(self) -> tuple[str,list[str]]:
        return self.NAME, []
    
    def export(self):
        raise Exception(f"cannot export {self.NAME}")
    
class ConfigLeaf(ConfigNode):
    NAME = "ConfigLeaf"
    def __init__(self, raw:str|int|bool|ConfigLeaf, origin:Origin=None, location:Location=None):
        etype((raw, (str, int, bool, ConfigLeaf)))
        super().__init__(raw, origin, location)
        if isinstance(raw, ConfigLeaf):
            self.value = raw.value
        else:
            self.value = raw
    
    def getValue(self, env:ConfigEnv) -> any:
        if isinstance(self.value, str):
            lua = self.getLua(env)
            file = None if self.origin is None else self.origin.file
            line = None if self.origin is None else self.origin.line
            snip = LuaSnippet(self.value, file, line, template=True)
            return lua.run(snip)
        return self.value

    def merge(self, other:ConfigLeaf, env:ConfigEnv, overwrite:bool=False):
        etype((other, ConfigLeaf), (env, ConfigEnv))
        if overwrite:
            self.value = other.value

    def __repr__(self) -> str:
        return f"ConfigLeaf({self.value})"

    def dump(self) -> tuple[str,list[str]]:
        if isinstance(self.value, str) and "\n" in self.value:
            lst = self.value.split("\n")
            if lst[-1] == "":
                lst.pop()
            return "|", lst
        return str(self.value), []

    def export(self) -> str:
        return self.value

class ConfigList(ConfigNode):
    store:list[ConfigNode]
    NAME = "ConfigList"
    def __init__(self, raw:list|ConfigList, origin:Origin=None, location:Location=None):
        etype((raw, (list, ConfigList)), (origin, (Origin, None)), (location, (Location, None)))
        super().__init__(raw, origin, location)
        self.store = []
        if isinstance(raw, ConfigList):
            for value in raw.store:
                self.setChild('#', value.clone(), ConfigEnv())
        elif isinstance(raw, list):
            try:
                assert isinstance(raw[-1][0], Origin)
                origins = raw[-1]
                values = raw[:-1]
            except (IndexError, AssertionError, KeyError, TypeError):
                origins = [origin] * len(raw)
                values = raw
            for value,ori in zip(values,origins):
                self.setChild('#', makeConfigVal(value, ori, location), ConfigEnv())

    def items(self, env:ConfigEnv) -> Iterable[tuple[str,ConfigEnv,ConfigNode]]:
        etype((env, ConfigEnv))
        for idx,child in enumerate(self.store):
            denv = env.derive("index", move=ConfigPath("." + str(idx)))
            yield str(idx), denv, child

    def merge(self, other:ConfigList, env:ConfigEnv, overwrite:bool=False):
        if overwrite == True:
            raise UnsupportedError("List merge cannot do overwrite", env, self)
        etype((other, ConfigList))
        for val in other.store:
            self.setChild('#', val.clone(), env)

    def getChild(self, key:str, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        etype((key, str), (env, ConfigEnv))
        try:
            idx = int(key)
        except ValueError:
            raise PathNotExist("list index must be int", env)
        newEnv = env.derive(("ListChild", key), move=ConfigPath("." + key))
        return newEnv, self.store[idx]
    
    def getValue(self, env:ConfigEnv) -> any:
        return [child.getValue(env) for child in self.store]

    def setChild(self, key:str, node:ConfigNode, env:ConfigEnv):
        etype((key, str), (node, ConfigNode))
        if key == '#': #append
            self.store.append(node)
            node.setParent(self, str(len(self.store)-1))
            return
        try:
            idx = int(key)
        except ValueError:
            raise BadValue("index in a list must be an integer", env, self)
        if idx in self.store:
            self.store[idx].setParent(None, None)
        self.store[idx] = node
        node.setParent(self, str(idx))
    
    def __repr__(self) -> str:
        return f"ConfigList(len:{len(self)})"
    
    def export(self) -> list:
        return [child.export() for child in self.store]
    
    def dump(self) -> tuple[str,list[str]]:
        ret = []
        for child in self.store:
            slug, lst = child.dump()
            ret += ["- " + slug]
            ret += ["  " + x for x in lst]
        return "", ret
    
    def __len__(self) -> int:
        return len(self.store)

class ConfigDict(ConfigNode):
    store:dict[str,ConfigNode]
    NAME="ConfigDict"
    def __init__(self, raw, origin:Origin=None, location:Location=None):
        etype((origin, (Origin, None)), (location, (Location, None)), (raw, (ConfigDict, dict)))
        #load location
        if isinstance(raw, dict):
            stat = bool(raw['_static']) if '_static' in raw else False
            if '_location' in raw:
                location = Location(raw['_location'], static=stat)
            elif '_static' in raw:
                location = Location(raw['_static'], static=stat)
            elif stat:
                location = Location(location, static=stat)
        #
        super().__init__(raw, origin, location)
        #
        self.store = {}
        if isinstance(raw, dict):
            oris = raw['__origins__'] if '__origins__' in raw else {}            
            for key,val in raw.items():
                if key == '__origins__':
                    continue
                ori = oris[key] if key in oris else origin
                self.setChild(key, makeConfigVal(val, ori, location), ConfigEnv())
        elif isinstance(raw, ConfigDict):
            for key,val in raw.store.items():
                self.setChild(key, val.clone(), ConfigEnv())
        else:
            raise BadValue(f"cannot create ConfigDict from {type(raw)}")            

    def items(self, env:ConfigEnv) -> Iterable[tuple[str,ConfigEnv,ConfigNode]]:
        etype((env, ConfigEnv))
        for key,child in self.store.items():
            nenv = env.derive(("iterChild", key), move=ConfigPath("." + key))
            yield key, nenv, child

    def getChild(self, key:str, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        try:
            val = self.store[key]
        except KeyError:
            raise PathNotExist(f"child:{key} does not exist", env, self)
        newEnv = env.derive(("DictChild", key), move=ConfigPath("." + key))
        return newEnv, val
    
    def getValue(self, env:ConfigEnv) -> any:
        return {key:child.getValue(env) for key,child in self.store.items()}
    
    def setChild(self, key:str, node:ConfigNode, _:ConfigEnv):
        etype((key, str), (node, ConfigNode))
        if key in self.store:
            self.store[key].setParent(None, None)
        self.store[key] = node
        node.setParent(self, key)

    def __repr__(self) -> str:
        return f"ConfigDict(size:{len(self.store)})"

    def merge(self, other:ConfigDict, env:ConfigEnv, overwrite=True):
        etype((other, ConfigDict))
        for key,val in other.store.items():
            try:
                self.store[key].merge(val, env, overwrite)
            except KeyError:
                cpy = val.clone()
                self.setChild(key, cpy, env) #add copy of val
                cpy.setParent(self, key)

    def getVars(self) -> dict[str,LuaSnippet|ConfigLink|str|int|bool]:
        if 'vars' not in self.store:
            return {}
        dd = {}
        for name,node in self.store['vars'].store.items():
            if isinstance(node, ConfigLeaf):
                if isinstance(node.value, str):
                    file = None if self.origin is None else self.origin.file
                    line = None if self.origin is None else self.origin.line
                    dd[name] = LuaSnippet(node.value, file, line, template=True)
                else:
                    dd[name] = node.value
            elif isinstance(node, ConfigLink):
                dd[name] = node
            else:
                raise BadValue("vars must be defined directly as Leafs or Links", None, self)
        return dd        

    #return you own slug and a list of lines from the children
    def dump(self) -> tuple[str,list[str]]:
        ret = []
        for key, child in self.store.items():
            slug, lst = child.dump()
            ret += [f"{key}: " + slug]
            ret += ["  " + x for x in lst]
        return "", ret

    def export(self) -> dict:
        return {key:child.export() for key,child in self.store.items()}

class ConfigCond(ConfigNode):
    NAME = "ConfigCond"
    parts:list[tuple[LuaSnippet,ConfigNode]]
    def __init__(self, raw:dict|ConfigCond, origin:Origin=None, location:Location=None):
        etype((origin, (Origin, None)), (location, (Location, None)), (raw, (dict, ConfigCond)))
        super().__init__(raw, origin, location)
        self.parts = []
        self.mode = None
        #
        if isinstance(raw, ConfigCond):
            for cond,node in raw.parts:
                self.addPart(cond, node.clone())
            self.mode = raw.mode
        else:
            oris = raw['__origins__'] if '__origins__' in raw else {} 
            for key,val in raw.items():
                if key == '__origins__':
                    continue
                if key[0:2] == '/#':
                    newMode = 'list'
                    rkey = key[2:]
                elif key[0:2] == '/?':
                    newMode = 'single'
                    rkey = key[2:]
                elif key == '/default':
                    newMode = None
                    rkey = key[1:]
                else:
                    newMode = 'merge'
                    rkey = key[1:]
                if newMode is not None and self.mode is not None and newMode != self.mode:
                    raise Exception("parse error - condition is not pure")
                if self.mode is None:
                    self.mode = newMode
                assert key[0] == '/'
                ori = oris[key] if key in oris else origin
                file = None if ori is None else ori.file
                line = None if ori is None else ori.line
                snip = LuaSnippet(rkey, file, line, condition=True)
                self.addPart(snip, makeConfigVal(val, ori, location))
        assert self.mode is not None

    def addPart(self, condition:LuaSnippet, node:ConfigNode):
        self.parts.append((condition, node))

    def delegate(self, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        lua = self.getLua(env)
        lua.addVariables({'default': True})
        if self.mode == 'list':
            accu = ConfigList([], self.origin, self.location)
        else:
            accu = None
        for condition, node in self.parts:
            res = lua.run(condition)
            if res:
                if self.mode == 'list':
                    accu.setChild('#', node.clone(), None)
                elif self.mode == 'merge':
                    if accu is None:
                        accu = node.clone()
                    else:
                        try:
                            accu.merge(node, env)
                        except TypeError:
                            raise BadValue("ConfigCondition resolved to incompatible types", env, self)
                elif self.mode == 'single':
                    accu = node.clone()
                    break
        if accu is None:
            raise BadValue("ConfigCondition resolved to an empty value", env, self)
        else:
            accu.setParent(self.parent, self.key)
        return env, accu

    def export(self) -> dict:
        return {"/" + cond.source:node.export() for cond,node in self.parts}  

    def __repr__(self) -> str:
        return "ConfigCond()"     
    
    def dump(self) -> tuple[str,list[str]]:
        ret = []
        for cond, node in self.parts:
            slug, lst = node.dump()
            ret += [f"/{cond.source}: " + slug]
            ret += ["  " + x for x in lst]
        return "", ret

class ConfigLink(ConfigNode):
    NAME = "ConfigLink"
    FLAG_REX = r'(\+|-)(\w+)'
    def __init__(self, raw:str|ConfigLink, origin:Origin, location:Location):
        etype((origin, (Origin, None)), (location, (Location, None)), (raw, (str, ConfigLink)))
        super().__init__(raw, origin, location)
        if isinstance(raw, ConfigLink):
            self.path = raw.path
            self.addFlags = raw.addFlags
            self.remFlags = raw.remFlags
            return
        assert raw[0] == '='
        path, flags = parsePathOption(raw[1:])
        self.path = path
        self.addFlags = flags
        self.remFlags = set()

    def __repr__(self) -> str:
        desc = str(self.path)
        for opt in self.addFlags:
            desc += f"+{opt}"
        return f"Link({desc})"

    def delegate(self, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        etype((env, ConfigEnv))
        targetEnv, targetNode = self.path.follow(env, self, "LinkFollow")
        if self.addFlags != set() or self.remFlags != set():
            param = ""
            param += " " + " ".join([f"+{x}" for x in self.addFlags])
            param += " " + " ".join([f"-{x}" for x in self.remFlags])
            flaggedEnv = targetEnv.derive(("LinkFlags", param), addFlags=self.addFlags, remFlags=self.remFlags)
        else:
            flaggedEnv = targetEnv
        return flaggedEnv, targetNode

    def dump(self) -> tuple[str,list[str]]:
        val = f"={self.path}"
        for flag in self.addFlags:
            val += f"+{flag}"
        for flag in self.remFlags:
            val += f"-{flag}"
        return (val, [])

    def export(self) -> str:
        flags = [f"+{f}" for f in self.addFlags] + [f"-{f}" for f in self.remFlags]
        return f"={self.path}{''.join(flags)}"

class ConfigImport(ConfigNode):
    NAME = "ConfigImport"
    def __init__(self, raw:str|ConfigImport, origin:Origin, location:Location):
        etype((origin, (Origin, None)), (location, (Location, None)), (raw, (str, ConfigImport)))
        super().__init__(raw, origin, location)
        #######
        if isinstance(raw, ConfigImport):
            self.path = raw.path
        else: #string
            assert raw[0] == '+'
            if raw[1:] == '+':
                self.path = None
            elif raw[1] == '#':
                self.path = pathlib.Path(raw[2:])
            else:
                self.path = pathlib.Path(raw[1:]) / "RR"
        self.node = None #lasy loading

    def delegate(self, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        if self.node is None:
            if self.path is None:
                self.path = pathlib.Path(self.key) / "RR"
            try:
                dd = makeConfigFromFile(self.location / self.path)
            except FileNotFoundError:
                raise LinkNotExist(f"File not found:{self.path}", env, self)
            dd.setParent(self.parent, self.key)
            dd.isFileRoot = True
            self.node = dd
        return env, self.node

    def dump(self) -> tuple[str,list[str]]:
        val = str(self.path)
        if self.node:
            slug, lst = self.node.dump()
            val += " # " + slug
        else:
            lst = []
        return val, lst
    
    def export(self) -> str:
        if self.path is None or self.path == pathlib.Path(self.key) / "RR":
            return "+_"
        elif self.path.name == "RR":
            return f"+{self.path.parent}"
        else:
            return f"+#{self.path}"

class ConfigScript(ConfigNode):
    NAME = "ConfigScript"
    def __init__(self, raw:str, origin:Origin, location:Location):
        etype((origin, (Origin, None)), (location, (Location, None)), (raw, (str, ConfigScript)))
        super().__init__(raw, origin, location)
        if isinstance(raw, ConfigScript):
            self.source = raw.source
            return
        assert raw[0] == '$'
        file = None if self.origin is None else self.origin.file
        line = None if self.origin is None else self.origin.line
        if raw[1] == '$':
            self.source = LuaSnippet(raw[2:], file, line, program=True)
        else:
            self.source = LuaSnippet(raw[1:], file, line)

    def delegate(self, env:ConfigEnv) -> tuple[ConfigEnv, ConfigNode]:
        lua = self.getLua(env)
        return env, makeConfigVal(lua.run(self.source))
    
    def export(self):
        if self.source.program:
            return f"$${self.source.source}"
        else:
            return f"${self.source.source}"
        
    def dump(self) -> tuple[str,list[str]]:
        return "<script>", []

class ConfigRaw(ConfigNode):
    def __init__(self, raw:any, origin:Origin, location:Location):
        etype((origin, (Origin, None)), (location, (Location, None)))
        if isinstance(raw, ConfigRaw):
            super().__init__(raw, origin=origin, location=location)
            self.raw = raw.raw
        else:
            super().__init__(None, origin=origin, location=location)
            self.raw = raw

    def getValue(self, env):
        return self.raw
    
    def __repr__(self):
        return f"ConfigRaw({self.raw})"
    
    def export(self):
        raise Exception("ConfigRaw is gernerally not exportable")

    def dump(self) -> tuple[str,list[str]]:
        return str(self.raw), []

class ConfigContext:
    INCLUDES = ["inc", "include"]
    def __init__(self, node:ConfigNode, flags:set[str]=None, env:ConfigEnv=None):
        etype((node, ConfigNode), (flags, (set, None)), (env, (ConfigEnv, None)))
        self.node = node
        if env:
            assert flags is None, "cannot set flags when env is given at Context Creation"
            self.env = env
        else:
            self.env = ConfigEnv().derive(("ContextCreate",), addFlags=flags)

    def __eq__(self, other:ConfigContext) -> bool:
        etype((other, ConfigContext))
        return self.node == other.node and self.env == other.env
    
    def move(self, cpath:str=None, addFlags:set[Option|str]=None, remFlags:set[str]=None) -> ConfigContext:
        etype((cpath,(str,ConfigPath,None)), (addFlags,(set,None),(Option,str)), (remFlags,(set,None),str))
        if isinstance(cpath, ConfigPath):
            path = cpath
        elif cpath is None:
            path = ConfigPath("")
        else: #str
            path = ConfigPath(cpath)
        nenv, nnode = path.follow(self.env, self.node, "Move")
        if addFlags is not None:
            addOptions = {Option.mkOption(x) for x in addFlags}
        else:
            addOptions = None
        if addOptions is not None or remFlags is not None:
            nnenv = nenv.derive(("MoveFlags",), addFlags=addOptions, remFlags=remFlags)
        else:
            nnenv = nenv
        return ConfigContext(nnode, env=nnenv)
    
    def __iter__(self) -> Iterable[tuple[str,ConfigContext]]:
        for key,ienv,child in self.node.items(self.env):
            yield key, ConfigContext(child, env=ienv)

    def leafs(self) -> Iterable[tuple[str,any]]:
        def desc(ctx:ConfigContext, path:str):
            try:
                for key,child in ctx:
                    npath = path + "." + key
                    yield from desc(child, npath)
            except NotIteratable:
                yield path, ctx.get()
        yield from desc(self, "")

    def travers(self, first_descend:None=True) -> Iterable[ConfigContext]:
        log = logging.getLogger(LOGNAME)
        def walk(cfg:ConfigContext, hist=[]):
            #don't visit a node twice
            for h in hist:
                if h == cfg:
                    return
            hist.append(cfg)
            #iterate over current node
            cfgs = []
            isList = None
            for key,icfg in cfg:
                #is it a list?
                if isList is None:
                    try:
                        x = int(key)
                        isList = True
                    except ValueError:
                        isList = False
                #ok iterate
                if isList or key in self.INCLUDES:
                    cfgs.append(icfg)
            #yield node pre
            if not isList and not first_descend:
                log.debug(f"yield pre node:@{cfg.pos()} flags:{cfg.flags()}")
                yield cfg
            #descend
            for icfg in cfgs:
                yield from walk(icfg, hist)
            #yield node post
            if not isList and first_descend:
                log.debug(f"yield post node:@{cfg.pos()} flags:{cfg.flags()}")
                yield cfg
        yield from walk(self)

    def get(self, cpath:str=None, default:any=NoValue, mkList:bool=False, isOsPath:bool=False, isType:type=None):
        etype((cpath, (str,None)), (mkList,bool), (isOsPath,bool), (isType,(type,None)))
        if cpath is None:
            cpath = ""
        try:
            path = ConfigPath(cpath)
            env, node = path.follow(self.env, self.node, "CtxtGet")
            raw = node.getValue(env)
            if isOsPath:
                assert isType is None, "isOsPath and isType cannot be used together"
                if isinstance(raw, list):
                    locations = [itm.getLocation(env) for _,_,itm in node.items(env)]
                    raw = [(loc, pathlib.Path(path)) for loc,path in zip(locations,raw)]
                elif isinstance(raw, str):
                    location = node.getLocation(env)
                    raw = (location, pathlib.Path(raw))
                else:
                    raise BadValue(f"node value must be str or list of str for isOsPath mode, but is:{type(raw)}", env, node)
            if mkList and not isinstance(raw, list):
                raw = [raw]
            if isType is not None and not isinstance(raw, isType):
                raise BadValue(f"node value is not a {isType} but {type(raw)}", env, node)
            return raw
        except (PathNotExist, ChildError):
            if default is NoValue:
                raise
            else:
                return default
            
    def set(self, cpath:str, value:any, create:bool=False, merge:bool=False):
        node = makeConfigVal(value)
        self.assimilate(cpath, node, create, merge)

    def assimilate(self, cpath:str, node:ConfigNode, create:bool=False, merge:bool=False):
        etype((cpath, str), (create, bool), (node, ConfigNode))
        path = ConfigPath(cpath)
        if len(path) == 0:
            if not merge:
                raise BadValue("cannot set root node without merge", self.env, self.node)
            self.node.merge(node, self.env)
            return
        if create:
            self.assertPath(path)
        pEnv, pNode = path[:-1].follow(self.env, self.node, "CtxtSet")
        fn, key = path.getElement(-1)
        if fn != ConfigPathFunction.SELECT:
            raise BadValue("for setting values only the select modifier (.) is supported", pEnv, pNode)
        if merge:
            try:
                _, old = pNode.getChild(key, pEnv)
                new = old.clone()
                new.merge(node, pEnv)
            except PathNotExist:
                new = node
        else:
            new = node
        pNode.setChild(key, new, pEnv)

    def assertPath(self, path:ConfigPath):
        node = self.node
        env = self.env
        for idx in range(len(path)-1):
            try:
                env, node = path[idx].follow(env, node, "CtxtAssertPath")
                continue
            except PathNotExist:
                pass
            fn, key = path.getElement(idx)
            nfn, nextKey = path.getElement(idx+1)
            if fn != ConfigPathFunction.SELECT or nfn != ConfigPathFunction.SELECT:
                raise Exception("cannot auto create Path - only select (.) is supported")
            try:
                _ = True if nextKey == '#' else int(nextKey) #check if nextKey is '#' or an int
                value = makeConfigVal(list())
            except ValueError:
                value = makeConfigVal(dict())
            if isinstance(node, ConfigDict):
                try:
                    node.getChild(key, env)
                    raise ChildError("cannot auto create Path - key already exists", env, node)
                except PathNotExist:
                    pass
                node.setChild(key, value, env)
            elif isinstance(node, ConfigList):
                try:
                    node.getChild(key, env)
                    raise ChildError("cannot auto create Path - index already exists", env, node)
                except PathNotExist:
                    pass
                node.setChild(key, value)
            else:
                raise BadValue("cannot auto create Path - parent must be Dict or List", env, node)
            
    def dump(self) -> list[str]:
        slug, lst = self.node.dump()
        return [str(self.node.getPath()) + " # " + slug] + lst
    
    def pos(self) -> ConfigPath:
        return self.node.getPath()
    
    def path(self) -> ConfigPath:
        return self.env.hist
    
    def real(self) -> ConfigContext:
        cenv, cnode = self.env, self.node
        while cnode is not None:
            nenv, nnode = cenv, cnode
            cenv, cnode = nnode.delegate(nenv)
        if nnode is self.node:
            return self
        return ConfigContext(nnode, env=nenv)
    
    def location(self) -> Location:
        return self.node.getLocation(self.env)

    def origin(self) -> Origin:
        return self.node.origin
    
    def isList(self) -> bool:
        return isinstance(self.node, ConfigList)
    
    #FIXME must delegate to node - othewise a CondConfigDict is not detected
    def isDict(self) -> bool:
        return isinstance(self.node, ConfigDict)
    
    def flags(self) -> dict[str,Option]:
        return self.env.flags
    
    def error(self, msg:str):
        raise ContextError(msg, self.env, self.node)
    
    def lua(self) -> LuaCtxt:
        return self.node.getLua(self.env)
    
    def uid(self, sentinal:set=None) -> str:
        msg = str(self.pos())[1:]
        flags = self.env.optionsUid(sentinal)
        if flags != '':
            msg += "+" + flags
        return msg

class Location():
    def __init__(self, path, static=False):
        if isinstance(path, str):
            self.path = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            self.path = path
        elif isinstance(path, Location):
            self.path = path.path
        else:
            self.path = None
        assert path is not None
        self.static = static

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return f"Loc{'s' if self.static else ''}('{str(self.path)}')"

    def __truediv__(self, other):
        return self.path / other

    def __eq__(self, other: object) -> bool:
        return self.path == other.path and self.static == other.static

class Origin():
    def __init__(self, line, column, f=None):
        self.line = line
        self.column = column
        self.file = f

    def __repr__(self):
        return f"Ori({self.file}:{self.line}:{self.column})"

    def __str__(self):
        return f"{self.file}:{self.line}"
    
    def __eq__(self, other:Origin) -> bool:
        return self.line == other.line and self.column == other.column and self.file == other.file

#path string
# list of (fn, value)
# functions: . : ; $
#   . - use current node
#   : - use root node
#   ; - use currents file's root node
#   $ - use variable
# parameter to nodes:
# "" - do nothing
# str - select child by index or key
# # - append to list - only for setting
# . - select parent

class ConfigPathFunction(Enum):
    NOOP = 0
    SELECT = 1
    ROOT = 2
    FILE = 3
    VAR = 4
    UP = 5

class ConfigPath:
    REX_ELEM = r"([\.:;\$])([\w#]*)"
    def __init__(self, path:str|list[tuple[str, str]]):
        etype((path, (str, list))) 
        self.steps = []
        if isinstance(path, str):
            self.parse(path)
        else:
            for tup in path:
                self.eTuple(tup)
            self.steps = path

    @classmethod
    def cTuple(cls, tup:tuple[ConfigPathFunction,str]):
        try:
            return cls.eTuple(tup)
        except (InvalidPath, TypeError):
            return False

    @classmethod
    def eTuple(cls, tup:tuple[ConfigPathFunction,str]) -> bool:
        etype((tup, tuple), (tup[0], ConfigPathFunction), (tup[1], (str,None)))
        if len(tup) != 2:
            raise InvalidPath(f"invalid ConfigPath tuple:{tup} - not len 2")
        fn, param = tup
        if fn in [ConfigPathFunction.NOOP, ConfigPathFunction.ROOT, ConfigPathFunction.FILE, ConfigPathFunction.UP]:
            if param is not None:
                raise InvalidPath(f"tuple with fn:{fn} must have None param but has:{param}")
        elif fn in [ConfigPathFunction.SELECT, ConfigPathFunction.VAR]:
            if not ctype((param, str)):
                raise InvalidPath(f"tuple with fn:{fn} must have str param but has:{param} ({type(param)})")

    def parse(self, path:str):
        etype((path, str))
        pos = 0
        openDelim = False
        for itm in re.finditer(self.REX_ELEM, path):
            delim = itm[1]
            arg = itm[2]
            #create steps
            if delim == ':':
                self.steps.append((ConfigPathFunction.ROOT, None))
                doSelect = True
            elif delim == ';':
                self.steps.append((ConfigPathFunction.FILE, None))
                doSelect = True
            elif delim == '.':
                if openDelim:
                    self.steps.append((ConfigPathFunction.UP, None))
                doSelect = True
            elif delim == '$':
                self.steps.append((ConfigPathFunction.VAR, arg))
                doSelect = False
            else:
                raise ConfigPathError(f"unknwon delim:{delim}")
            if doSelect:
                if arg == '':
                    openDelim = True
                else:
                    self.steps.append((ConfigPathFunction.SELECT, arg))
                    openDelim = False
            #forward ho!
            sp = itm.span()
            if sp[0] != pos:
                raise ConfigPathError(f"invalid path:{path} - gap @:{pos}-{sp[0]}")
            pos = sp[1]
        if pos != len(path):
            raise ConfigPathError(f"invalid path:{path} - gap @:{pos}-{len(path)}")

    def __str__(self):
        msg = ""
        isOpenDelim = False #means that an delim has been aded but no arg - a SELECT has to be be collapsed
        for fn,param in self.steps:
            if fn == ConfigPathFunction.FILE:
                msg += ';'
                isOpenDelim = True
            elif fn == ConfigPathFunction.ROOT:
                msg += ":"
                isOpenDelim = True
            elif fn == ConfigPathFunction.SELECT:
                if not isOpenDelim:
                    msg += '.'
                msg += param
                isOpenDelim = False
            elif fn == ConfigPathFunction.UP:
                if not isOpenDelim:
                    msg += '.'
                msg += '.'
                isOpenDelim = True
            elif fn == ConfigPathFunction.VAR:
                msg += f'${param}'
            else:
                raise InvalidPath(f"bad contains unknown fn:{fn} param:{param}")
        return msg
    
    def __repr__(self):
        return f"CPath('{str(self)}')"
    
    def __getitem__(self, idx):
        if isinstance(idx, int):
            return ConfigPath([self.steps[idx]])
        elif isinstance(idx, slice):
            if idx.step is not None:
                raise Exception("slice step not supported in ConfigPath")
            return ConfigPath(self.steps[idx.start:idx.stop])
        else:
            raise Exception("invalid index type")
        
    def __add__(self, other:ConfigPath) -> ConfigPath:
        etype((other, ConfigPath))
        return ConfigPath(self.steps + other.steps)

    def __len__(self) -> int:
        return len(self.steps)
    
    def __eq__(self, other:ConfigPath) -> bool:
        return self.steps == other.steps

    def getElement(self, idx:int) -> tuple[str, str]:
        etype((idx, int))
        return self.steps[idx]

    def reduced(self) -> ConfigPath:
        steps = []
        for fn,param in self.steps:
            if fn == ConfigPathFunction.UP:
                if len(steps) and steps[-1][0] == ConfigPathFunction.SELECT:
                    steps.pop()
                else:
                    steps.append((fn,param))
            elif fn == ConfigPathFunction.ROOT:
                steps = [(fn,param)]
            elif fn in [ConfigPathFunction.SELECT, ConfigPathFunction.VAR]:
                steps.append((fn,param))
            elif fn == ConfigPathFunction.FILE:
                if len(steps) == 0 or steps[-1][0] != ConfigPathFunction.FILE:
                    steps.append((fn,param))
            else:
                raise InvalidPath(f"bad contains unknown fn:{fn} param:{param}")
        return ConfigPath(steps)

    def follow(self, env:ConfigEnv, node:ConfigNode, fn:str='_') -> tuple[ConfigEnv, ConfigNode]:
        etype((env,ConfigEnv), (node,ConfigNode), (fn,str))
        env = env.derive(("Follow", fn, str(self)))
        startNode = node
        for fn,par in self.steps:
            if fn == ConfigPathFunction.ROOT:
                newNode = node.getRoot()
                newEnv = env.derive(("Root",), move=ConfigPath(":"))
            elif fn == ConfigPathFunction.FILE:
                newNode = node.getRoot(file=True)
                newEnv = env.derive(("FileRoot",), move=ConfigPath(";"))
            elif fn == ConfigPathFunction.VAR:
                lua = node.getLua(env)
                file = None if node.origin is None else node.origin.file
                line = None if node.origin is None else node.origin.line
                snip = LuaSnippet(par, file, line)
                val = lua.run(snip)
                tenv = env.derive(("Var", par), move=ConfigPath(f"${par}"))
                if not isinstance(val, ConfigNode):
                    raise InvalidName(f"variable:{par} does not resolve to a ConfigNode but:{type(val)}", tenv, startNode)
                newEnv, newNode = val.delegate(tenv)
            elif fn == ConfigPathFunction.UP:
                if node.parent is None:
                    raise InvalidPath(f"cannot go up from root node", env, node)
                newNode = node.parent
                newEnv = env.derive(("Up",), move=ConfigPath(".."))
            elif fn == ConfigPathFunction.SELECT:
                newEnv, newNode = node.getChild(par, env)
            else:
                raise InvalidPath(f"invalid path modifier:{fn}")
            env = newEnv
            node = newNode
        return env, node

class Option:
    def __init__(self, key:str, val:int|float|bool|None=None):
        etype((key, str), (val, (int,float,None,bool)))
        self.key = key
        self.val = val

    def __hash__(self):
        return hash((self.key, self.val))

    def __eq__(self, other:Option):
        return self.key == other.key and self.val == other.val

    def __str__(self) -> str:
        msg = self.key
        if self.val is not None:
            lua = LuaCtxt()
            snip = LuaSnippet("tostring(val)", "config.py:Option:__str__", 4)
            lua.addVariables({'val': self.val})
            strVal = lua.run(snip)
            msg += "~" + strVal
        return msg
    
    def __repr__(self) -> str:
        return f"Op({self.key}:{self.val})"
    
    @classmethod
    def fromStr(self, raw:str) -> Option:
        parts = raw.split('~')
        key = parts[0]
        if len(parts) <= 1:
            value = None
        elif parts[1] == 'true':
            value = True
        elif parts[1] == 'false':
            value = False
        else:
            lua = LuaCtxt()
            snip = LuaSnippet("tonumber(val)", "config.py:Option:__str__", 4)
            lua.addVariables({'val': parts[1]})
            try:
                value = lua.run(snip)
            except LuaError:
                raise OptionError("option string cannot be parsed")
            etype((value, (int, float)))
        return Option(key, value)

    @classmethod
    def mkOption(cls, raw:Option|str) -> Option:
        etype((raw, (Option,str)))
        if isinstance(raw, Option):
            return Option(raw.key, raw.val)
        else:
            return Option.fromStr(raw)

def parsePathOption(raw:str) -> tuple[ConfigPath, set[Option]]:
    etype((raw, str))
    parts =raw.split('+')
    opts = {Option.mkOption(x) for x in parts[1:]}
    return  ConfigPath(parts[0]), opts

class ConfigError(Exception):
    REASON = "Error"
    DESCRIPTION = None
    def __init__(self, msg, env:ConfigEnv, node:ConfigNode):
        self.msg = msg
        self.node = node
        self.env = env

    def __str__(self):
        return f"{self.REASON}: {self.msg}"
    
    def dump(self) -> list[str]:
        msg = [str(self)]
        if self.node is not None:
            try:
                path = self.node.getPath()
            except:
                path = "PATH EXCP"
            msg.append(f"  {self.node}\n    @{path}")
        if self.env is not None:
            msg += [f"  {x}" for x in self.env.dump()]
        return msg

class InvalidPath(ConfigError):
    REASON = "InvalidPath"
    DESCRIPTION = "The path at hand contains invalid parts (not int or str) or points to an invalid loaction like above the root node"

class InvalidName(ConfigError):
    REASON = "InvalidName"
    DESCRIPTION = "The string at hand is not a correctly formated path"

class PathNotExist(ConfigError):
    REASON = "PathNotExist"
    DESCRIPTION = "Some part of the path points to an non-existing child"

class LinkNotExist(ConfigError):
    REASON = "LinkNotExist"
    DESCRIPTION = "The target of the link does not exist, e.g. the config node or the file to be loaded"

class BadValue(ConfigError):
    REASON = "BadValue"
    DESCRIPTION = "A bad value has been used, like a str to access a list"

class TreeCorrupt(ConfigError):
    REASON = "TreeCorrupt"
    DESCRIPTION = "Something in the config tree is wrong that should not be"

class ChildError(ConfigError):
    REASON = "ChildError"
    DESCRIPTION = "Problem with child access, like accessing child in leaf node or indexing list beyond its size"

class LinkError(ConfigError):
    REASON = "LinkError"
    DESCRIPTION = "Bad usage of a link like trying to set the child of a Link"

class UnsupportedError(ConfigError):
    REASON = "UnsupportedError"
    DESCRIPTION = "Something cannot be done, maybe only yet"

class ContextError(ConfigError):
    REASON = "ContextError"
    DESCRIPTION = "Application level error"

class NotIteratable(Exception):
    pass

class ConfigPathError(Exception):
    pass

class OptionError(Exception):
    pass

def registerLuaHook(cfg:ConfigContext, name:str, func:callable):
    etype((cfg, ConfigContext), (name, str), (func, Callable))
    rawNode = ConfigRaw(func, None, None)
    cfg.assimilate(f":_run.luaHooks.{name}", rawNode)
