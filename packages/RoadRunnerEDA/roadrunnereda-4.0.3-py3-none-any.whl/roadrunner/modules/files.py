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
from roadrunner.config import ConfigContext, NotIteratable, PathNotExist
from pathlib import Path
import logging
from roadrunner.rr import Pipeline, workdir_import, workdir_import_list
from roadrunner.fn import etype, clone
from roadrunner.help import HelpItem, HelpOption

NAME = "Files"

logg = logging.getLogger(NAME)

HelpItem("module", (NAME, "handleFiles"), "import and export files to working directory", [
    HelpOption("attribute", "env", "dict[name|value]", None, "set variables"),
    HelpOption("attribute", "files", "dict[name|file|list[file]]", None, "import files an assign path to variables"),
    HelpOption("attribute", "import", "dict", None, desc="import bulks of files to working dir"),
    HelpOption("attribute", "import.pattern", "str", None, "glob pattern to include"),
    HelpOption("attribute", "import.base", "dir", None, "dir in source tree to use as base for globbing"),
    HelpOption("attribute", "import.dest", "dir", None, "dir in workdir to copy files to"),
    HelpOption("attribute", "export", "dict", None, desc="export files to result dir"),
    HelpOption("attribute", "export.pattern", "str", None, "glob pattern to use"),
    HelpOption("attribute", "export.base", "dir", None, "dir in working dir to use as base for globbing"),
    HelpOption("attribute", "export.dest", "dir", None, "dir in result dir to copy files to"),
    HelpOption("attribute", "export.group", "str", None, "group name to register files in result manifest")
])

def handleFiles(cfg:ConfigContext, wd:Path, pipe:Pipeline):
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline))
    vars = {}
    vars_origin = {}
    #files & env
    logg.debug(f"handle Files/Env @:{cfg.pos()}")
    for curr in cfg.travers():
        real = curr.real()
        #variables
        try:
            loc = {}
            for key,vcfg in curr.move(".env"):
                if key in vars:
                    logg.warn(f"Env var:{key} shadowed:{vars_origin[key]} by:{real.pos()}")
                vars_origin[key] = vcfg.pos()
                loc[key] = vcfg.get()
                logg.debug(f"Env var:{key} val:{loc[key]}")
            vars.update(loc)
        except PathNotExist:
            pass
        #files
        try:
            for key,vcfg in curr.move(".files"):
                files = vcfg.get(isOsPath=True)
                vars_origin[key] = vcfg.pos()
                if key in vars:
                    logg.warn(f"Env file:{key} shadowed:{vars_origin[key]} by:{real.pos()}")
                if isinstance(files, list):
                    fil = workdir_import_list(wd, files)
                    vars[key] = [str(f) for f in fil] #no posix paths
                else:
                    fil = workdir_import(wd, files)
                    vars[key] = str(fil) #no posix paths
                logg.debug(f"Env file:{key} val:{vars[key]}")
        except PathNotExist:
            pass
        #import
        def doImport(cfg:ConfigContext):
            log = logging.getLogger('modFiles')
            etype((cfg,ConfigContext))
            dest = cfg.get('.dest', default=".")
            base = cfg.get('.base', isOsPath=True)
            source = base[0] / base[1]
            log.info(f"importing from:{source} to:{wd / dest}")
            for itm in cfg.get('.pattern', mkList=True):
                count = 0
                for fitm in source.glob(itm):
                    log.debug(f"glob:{fitm}")
                    clone(fitm, wd / dest / fitm.name)
                    count += 1
                if count == 0:
                    log.warn(f"pattern:{itm} nohting imported")
                elif count == 1:
                    log.info(f"pattern:{itm} imported")
                else:
                    log.info(f"pattern:{itm} imported:{count} items")
        try:
            icfg = cfg.move(".import")
            if icfg.isList():
                for _,im in icfg:
                    doImport(im)
            else:
                doImport(icfg)
        except PathNotExist:
            pass
        #export
        def doExport(cfg:ConfigContext):
            etype((cfg,ConfigContext))
            pipe.result()
            base = cfg.get(".base", default=None)
            dest = cfg.get(".dest", default=None)
            group = cfg.get(".group", default=None)
            for pattern in cfg.get(".pattern", mkList=True):
                pipe.export(pattern, base and Path(base), dest and Path(base), group)
        try:
            result = cfg.get(".result", isType=str, default=None)
            ecfg = cfg.move(".export")
            if ecfg.isList():
                for _,ex in ecfg:
                    doExport(ex)
            else:
                doExport(ecfg)
        except PathNotExist:
            pass

    return vars

#converts a value to be printed into a bash script
def bash_val(val) -> str:
    if isinstance(val, list):
        return '(' + " ".join(bash_val(x) for x in val) + ')'
    elif isinstance(val, (str, Path)):
        return '"' + str(val) + '"'
    else:
        return str(val)

HelpItem("module", (NAME, "share"), "shares files with other commands", [
    HelpOption("attribute", "expose", "file|list[file]|dict[_|file]", None, "select files to be shared with other commands"),
    HelpOption("attribute", "discover", "file|list[file]|dict[_|file]", None, "selects exposed files from other commands to be used")
])
def share(cfg:ConfigContext, pipe:Pipeline):
    etype((cfg, ConfigContext), (pipe, Pipeline))
    #expose
    try:
        for _,itm in cfg.move(".expose"):
            pipe.expose(itm.get(isType=str))
    except NotIteratable: #not iteratable
        pipe.expose(Path(cfg.get(".expose", isType=str)))
    except PathNotExist:
        logging.getLogger(NAME).debug(".expose does not exists")
        pass
    #discover
    try:
        for key,itm in cfg.move(".discover"):
            pipe.discover(itm.get(isType=str), key)
    except NotIteratable: #not iteratable
        pipe.discover(Path(cfg.get(".discover", isType=str)))
    except PathNotExist:
        logging.getLogger(NAME).debug(".discover does not exists")
        pass

