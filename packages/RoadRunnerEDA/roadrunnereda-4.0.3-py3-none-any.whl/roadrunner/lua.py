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
import importlib.resources
import logging
import re

import lupa

REX_ORIGIN = r'\[string "[\w<>]+"\]:(\d+):'
LOGNAME = "lua"

@dataclass
class LuaSnippet:
    source:str          #source code
    origin:str          #soruce name (file name)
    line:int            #source line
    template:bool=False #eplua template with inlined lua expressions
    program:bool=False  #use execute() instead of eval
    condition:bool=False #will always evaluate to a boolean value

    def error(self, errmsg:str):
        def reline(m):
            line = int(m.group(1))
            return f"{self.origin}:{self.line + line - 2}:" #substract 1 for the 'funtion ...' added by compile() and 1 because lines start counting at 1, so adding two line numbers has a off by one
        if self.origin is not None:
            errmsg2 = re.sub(REX_ORIGIN, reline, errmsg)
            msg = f"LUA Error in snippet @:{self.origin}:{self.line}\n{errmsg2}"
        else:
            msg = f"LUA Error:\n{errmsg}"
        raise LuaError(msg)

class LuaFunc:
    def __init__(self, func, snip:LuaSnippet):
        self.func = func
        self.snip = snip

    def call(self):
        try:
            if self.snip.template:
                ret = self.func(self.snip.source)
            else:
                ret = self.func()
            if ret is None and self.snip.condition == False:
                errmsg = "Lua evaluated to None"
            elif isinstance(ret, tuple) and ret[0] == None and isinstance(ret[1], str):
                errmsg = ret[1]
            else:
                errmsg = None
        except lupa.LuaError as err:
            errmsg = str(err)
        if errmsg:
            self.snip.error(errmsg)
        val = strip(ret)
        if self.snip.condition:
            val = bool(val)
        return val
    
    def start(self):
        args = self.snip.source if self.snip.template else []
        cr = self.func.coroutine(*args)
        return LuaCorot(cr, self)

class LuaCorot:
    def __init__(self, corot, func:LuaFunc):
        self.func = func
        self.corot = corot
        self.stopped = False

    def tick(self, arg=None):
        errmsg = None
        ret = None
        try:
            ret = self.corot.send(arg)
        except lupa.LuaError as err:
            errmsg = str(err)
        except StopIteration:
            self.stopped = True
        if errmsg is not None:
            self.func.snip.error(errmsg)
        val = strip(ret)
        return val

class LuaCtxt:
    def __init__(self):
        self.lua = lupa.LuaRuntime()
        #we are not allowed to use the rr package in lua so we have to load this by hand
        libdir = importlib.resources.files("roadrunner.assets") / "lua"
        self.lua.globals()['package']['path'] = f"{libdir}/?.lua"
        self.lua.globals()['print'] = self.luaPrint
        self.lua.execute('etlua = require "etlua"')

    def luaPrint(self, line):
        log = logging.getLogger(LOGNAME)
        log.info(line)

    #adds and processes variables
    def addVariables(self, vars:dict[str,any]):
        assert isinstance(vars, dict)
        luaGlobals = self.lua.globals()
        add = []
        addDyn = []
        lastError = None
        #remove variables from globals that will be added now
        for kkey,val in vars.items():
            if kkey[0] == '?':
                key = kkey[1:]
                isWeak = True
            else:
                key = kkey
                isWeak = False
            isDef = key in luaGlobals
            #need to add var
            if not isDef or not isWeak:
                if isinstance(val, LuaSnippet):
                    addDyn.append((key,val))
                else:
                    add.append((key,val))
            #need to remove var
            if not isWeak and isDef:
                del luaGlobals[key]
        #add new variables
        for key,val in add:
            luaGlobals[key] = luafy(self.lua, val)
        #add dynamic values until everything settles
        for _ in range(100):
            alive = False
            for key,val in addDyn:
                rendered = self.run(val)
                if key not in luaGlobals or luaGlobals[key] != rendered:
                    alive = True
                luaGlobals[key] = rendered
            if not alive:
                break
        else:
            raise LuaError(f"Lua runtime could not be created - variables recursive dependence? - lastError:{lastError}")

    def compile(self, snip:LuaSnippet) -> LuaFunc:
        if snip.template:
            source = "function(tpl)\n  return etlua.render(tpl)\nend"
        elif snip.program:
            source = "function()\n" + snip.source + "\nend"
        else:
            source = f"function()\n  return {snip.source}\nend"
        try:
            fn = self.lua.eval(source)
        except lupa.LuaSyntaxError as err:
            snip.error(str(err))
        return LuaFunc(fn, snip)

    def run(self, snip:LuaSnippet):
        func = self.compile(snip)
        return func.call()

def strip(luaval):
    #if luaval is None:
    #    return None
    if lupa.lua_type(luaval) == 'table':
        dd = {}
        for key,val in luaval.items():
            dd[key] = strip(val)
        #check if its a list
        if all(isinstance(k, int) for k in dd.keys()):
            return [dd[k] for k in sorted(dd.keys())]

        #check if its a str dict
        if all(isinstance(k, str) for k in dd.keys()):
            return dd
        raise Exception("error parsing lua return value")
    #if type(luaval) in [str, int, bool]:
    #    return luaval
    if type(luaval) is list:
        return [strip(x) for x in luaval]
    #return anything that is not an lua internal thing
    if lupa.lua_type(luaval) == None:
        return luaval
    raise Exception(f"unable to convert type:{type(luaval)} luatype:{lupa.lua_type(luaval)}")

def luafy(lua, val):
    if isinstance(val, list):
        lst = [luafy(lua, x) for x in val]
        return lua.table_from(lst)
    elif isinstance(val, dict):
        dd = {x: luafy(lua, y) for x,y in val.items()}
        return lua.table_from(dd)
    else:
        return val

class LuaError(Exception):
    pass
