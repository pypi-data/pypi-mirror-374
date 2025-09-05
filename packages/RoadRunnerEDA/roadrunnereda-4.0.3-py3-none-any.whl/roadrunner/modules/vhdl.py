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
from roadrunner.config import ConfigContext
from roadrunner.rr import workdir_import_list
from dataclasses import dataclass
from pathlib import Path
from roadrunner.help import HelpItem, HelpOption

CONFIG_FLAGS = {'VHDL'}
LOGNAME = "VHDL"

@dataclass
class FileItem:
    vhdl:list[Path]
    defines:list[str]
    path:list[Path]
    static:bool
    
HelpItem("module", ("vhdl", "includeFiles"), "import verilog files", [
    HelpOption("attribute", "vhdl", "list[file]", None, "list of VHDL files"),
    HelpOption("attribute", "path", "list[dir]", None, "list of include paths"),
    HelpOption("attribute", "define", "list[str]", None, "list of defines"),
    HelpOption("attribute", "inc", "tree", None, "traversing the config tree")
])
def includeFiles(cfg:ConfigContext, wd:Path) -> list[FileItem]:
    log = logging.getLogger(LOGNAME)
    files = []
    for itm in cfg.move(addFlags=CONFIG_FLAGS).travers():
        log.debug(f"VHDL import from node:{itm.node} pos:{itm.pos()} - loc:{itm.location()!r}")
        v = workdir_import_list(wd, itm.get(".vhdl", mkList=True, isOsPath=True, default=[]))
        path = workdir_import_list(wd, itm.get(".path", mkList=True, isOsPath=True, default=[]),
                                    baseDir=Path("include"))
        incdirset = set()
        for i in path:
            if i.is_dir() or (wd / i).is_dir():
                incdirset.add(i)
            else:
                incdirset.add(i.parent)
        incdirs = list(incdirset)
        defines = itm.get(".define", mkList=True, default=[])
        static = itm.location().static
        if all(x == [] for x in [v, incdirs, defines]):
            continue
        files.append(FileItem(v, defines, incdirs, static))

    return files
