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
from typing import Iterable, Union
from roadrunner.fn import etype

class HelpOption:
    def __init__(self, typ:str, names:Union[tuple[str],str], valType:str=None, default:str=None, desc:str=None):
        etype((typ, str), (names, (tuple, str), str), (valType, (str, None)), (default, (str, None)), (desc, (str, None)))
        self.typ = typ
        self.names = names if isinstance(names, tuple) else (names,)
        self.valType = valType
        self.default = default 
        self.desc = desc

class HelpProxy:
    def __init__(self, typ:str, scope:Union[tuple[str],str]):
        etype((typ, str), (scope, (tuple, str), str))
        self.typ = typ
        self.scope = scope if isinstance(scope, tuple) else (scope,)

    def __iter__(self):
        itm = getHelp(self.typ, self.scope)
        if itm is not None:
            yield from itm
        else:
            logging.getLogger("RRHelp").warning(f"proxy for:{self.typ} scope:{self.scope} did not return anything")

helpDB = []

class HelpItem:
    def __init__(self, typ:str, scope:Union[tuple[str],str], desc:str, opt:list[Union[HelpOption,HelpProxy]]=None):
        etype((typ, str), (scope, (tuple, str), str), (opt, (list, None), (HelpOption, HelpProxy)))
        self.typ = typ
        self.scope = scope if isinstance(scope, tuple) else (scope,)
        self.desc = desc
        self.options = opt
        helpDB.append(self)

    def __iter__(self):
        if len(self.options):
            yield from self.options

def iterHelp(typ:str, scope:tuple[str]=None) -> Iterable[tuple[HelpItem, list]]:
    etype((typ, str), (scope, (tuple, None), str))
    for itm in helpDB:
        if itm.typ != typ:
            continue
        if scope is not None and itm.scope[:len(scope)] != scope:
            continue
        yield itm

def getHelp(typ:str, scope:tuple[str]) -> tuple[HelpItem, list]:
    it = iterHelp(typ, scope)
    try:
        return next(it)
    except StopIteration:
        return None
    
