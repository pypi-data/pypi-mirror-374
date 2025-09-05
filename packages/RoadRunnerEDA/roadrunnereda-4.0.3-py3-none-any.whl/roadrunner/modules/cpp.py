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
from pathlib import Path
from roadrunner.config import ConfigContext, ConfigPath
from roadrunner.fn import etype
from roadrunner.help import HelpItem, HelpOption
from roadrunner.rr import workdir_import_list

@dataclass
class FileItem:
    pos:ConfigPath
    c:list[Path]
    cpp:list[Path]
    defines:list[str]
    lib:list[Path]
    path:list[Path]
    libpath:list[Path]
    std:str

    # the position is the only thing that may be different
    def __eq__(self, other) -> bool:
        if self.c != other.c:
            return False
        if self.cpp != other.cpp:
            return False
        if self.defines != other.defines:
            return False
        if self.lib != other.lib:
            return False
        if self.path != other.path:
            return False
        if self.libpath != other.libpath:
            return False
        if self.std != other.std:
            return False
        return True

HelpItem("module", ("cpp", "includeFiles"), "Inlcude C++ files", [
    HelpOption("attribute", "c", "list[path]", None, "C source files"),
    HelpOption("attribute", "cpp", "list[path]", None, "C++ source files"),
    HelpOption("attribute", "defines", "list[str]", None, "C Defines"),
    HelpOption("attribute", "lib", "list[path]", None, "C libraries"),
    HelpOption("attribute", "libpath", "list[path]", None, "C library paths"),
    HelpOption("attribute", "path", "list[path]", None, "Include paths"),
    HelpOption("attribute", "std", "str", None, "C++ standard")
])
def includeFiles(cfg:ConfigContext, wd:Path):
    etype((cfg,ConfigContext), (wd,Path))
    files = []
    for itm in cfg.move(addFlags={'C'}).travers():
        c = workdir_import_list(wd, itm.get(".c", mkList=True, isOsPath=True, default=[]))
        cpp = workdir_import_list(wd, itm.get(".cpp", mkList=True, isOsPath=True, default=[]))
        defines = itm.get(".defines", mkList=True, default=[])
        lib = workdir_import_list(wd, itm.get(".lib", mkList=True, isOsPath=True, default=[])) #TODO: check if this is correct
        libpath = workdir_import_list(wd, itm.get(".libpath", mkList=True, isOsPath=True, default=[])) #TODO: check if this is correct
        inc = workdir_import_list(wd, itm.get(".path", mkList=True, isOsPath=True, default=[]),
                                  baseDir=Path("include"))
        incdirset = set()
        for i in inc:
            if i.is_dir() or (wd / i).is_dir():
                incdirset.add(i)
            else:
                incdirset.add(i.parent)
        incdirs = list(incdirset)
        std = itm.get(".std", default=None)
        pos = itm.pos()
        if all(x == [] for x in [c, cpp, defines, incdirs, lib, libpath]):
            continue
        files.append(FileItem(pos, c, cpp, defines, lib, incdirs, libpath, std))
    return files
