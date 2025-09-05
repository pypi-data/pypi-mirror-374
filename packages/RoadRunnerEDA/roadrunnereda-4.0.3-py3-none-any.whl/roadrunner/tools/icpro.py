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
from pathlib import Path
from roadrunner import fn, rr
from roadrunner.config import ConfigContext, Location
import roadrunner.modules.files
import roadrunner.modules.verilog
from roadrunner.rr import Pipeline


UNIT_VERILOG_PATH = "units/{unit}/source/rtl/verilog"
UNIT_SVERILOG_PATH = "units/{unit}/source/rtl/systemverilog"
UNIT_VHDL_PATH = "units/{unit}/source/rtl/vhdl"
UNIT_INCLUDE_PATH = "units/{unit}/source/rtl/header"
UNIT_C_PATH = "units/{unit}/source/behavioral/c"
UNIT_PYTHON_PATH = "units/{unit}/source/python"

EXPORT_PATH = "rr"

NAME = "ICPro"
DESCRIPTION = "icpro project exporter"

GENUS_FLAGS_DEFAULT = ["SYNTHESIS", "RACYICS", "ICPRO"]
GENUS_UNIT_DIR = "units/{unit}/rtl2gds/genus"
GENUS_FILELIST_FILE = "addons/{unit}.design.tcl"
GENUS_DEFINES_FILE = "defines.tcl"

def cmd_genus(cfg:ConfigContext, pipe:Pipeline):
    log = logging.getLogger("ICPro")

    wd = pipe.initWorkDir()
    roadrunner.modules.files.share(cfg, pipe)

    flags = cfg.get('.flags', mkList=True, default=[]) + GENUS_FLAGS_DEFAULT
    log.info(f"flags:{flags}")
    fcfg = cfg.move(addFlags=set(flags))
    pathMap = fcfg.get(".pathMap")
    vFiles = roadrunner.modules.verilog.includeFiles(fcfg, wd)
    
    files_sv = export_files(wd, vFiles, 'sv')
    files_v = export_files(wd, vFiles, 'v')
    #files_vhdl = export_files(wd, vFiles)
    files_inc = export_files(wd, vFiles, 'path')

    #unit name to synth
    unit = fcfg.get(".unit", isType=str)

    #write filelist file
    with open(wd / 'filelist.tcl', "w") as fh:
        print(f"set HDL_SEARCH_PATHS [list \\", file=fh)
        for _, fname in files_inc:
            print(f"\t$ICPRO_DIR/{fname} \\", file=fh)
        print("]\n\nset VERILOG_SRC_LIST [list \\", file=fh)
        for _, fname in files_v:
            print(f"\t$ICPRO_DIR/{fname} \\", file=fh)
        print("]\n\nset SYSVERILOG_SRC_LIST [list \\", file=fh)
        for _, fname in files_sv:
            print(f"\t$ICPRO_DIR/{fname} \\", file=fh)
        print("]\n\nset VHDL_SRC_LIST [list \\", file=fh)
        #for _, fname in files_vhdl:
        #    print(f"\t$ICPRO_DIR/{fname} \\", file=fh)
        print("]", file=fh)

    #gather defines and paths
    defines = []
    paths = []
    for itm in vFiles:
        defines.extend(itm.defines)
        paths.extend(itm.path)

    #write defines into a tcl file
    with open(wd / 'defines.tcl', "w") as fh:
        print("%I dont't know where to put the global defines for a genus synthesis run", file=fh)
        defs = [x.strip() for x in set(defines)]
        print("set DEFINES = {", file=fh, end="")
        print(" ".join(defs), file=fh, end="")
        print("}", file=fh)

    rd = Path('result')
    ud = Path(GENUS_UNIT_DIR.format(unit=unit))
    dirs = []
    with open(wd / 'export.sh', 'w') as fh:
        print("#Verilog", file=fh)
        for source, dest in files_v:
            copyFile(fh, dirs, source, rd / dest)
        print("#SystemVerilog", file=fh)
        for source, dest in files_sv:
            copyFile(fh, dirs, source, rd / dest)
#        print("#VHDL", file=fh)
#        for source, dest in files_vhdl:
#            copyFile(fh, dirs, source, rd / dest)
        print("#include", file=fh)
        for source, dest in files_inc:
            copyFile(fh, dirs, source, rd / dest)
        print("#filelist", file=fh)
        copyFile(fh, dirs, "filelist.tcl", rd / ud / GENUS_FILELIST_FILE.format(unit=unit))
        copyFile(fh, dirs, "defines.tcl", rd / ud / GENUS_DEFINES_FILE.format(unit=unit))

    call = rr.Call(wd, 'exportFiles', 'Bash')
    call.addArgs(['sh', 'export.sh'])

    pipe.runCall(call)
    return 0


# NCSIM_TESTCASE_DIR = "units/{unit}/simulation/ncsim/{testcase}"
# NCSIM_SOURCES_RTL_TEMPLATE = "icpro/ncsim_rtl.Makefile"
# NCSIM_SOURCES_RTL_FILE = "Makefile.rtl.sources"
# NCSIM_FLAGS_DEFAULT = ["SIMULATION", "RACYICS", "ICPRO", "VPI"] #technically ncsim also supports DPI but that soes not play well with SiCo
# NCSIM_VARS_FILE = "Makefile.var"
# NCSIM_VARS_TEMPLATE = "icpro/ncsim_var.Makefile"

# def cmd_ncsim(cnf:ConfigNode, pipe:Pipeline):
#     log = logging.getLogger("ICPro")

#     wd = rr.workdir_init(pipe.cwd())
#     share(cnf, pipe)
#     paths = cnf.getval(".pathMap")

#     flags = cnf.getval('.flags', mklist=True, default=[]) + NCSIM_FLAGS_DEFAULT
#     log.info(f"flags:{flags}")
#     tags = flags + ['include', 'inc']
#     attrs = {'path': True, 'sv': True, 'v': True, 'vhdl': True, 'define': False,
#         'c': True}
#     dd = rr.gather(cnf, tags, attrs.keys(), flags, path=attrs, united=True)

#     files_sv = export_files(wd, dd['sv'], paths, UNIT_SVERILOG_PATH)
#     files_v = export_files(wd, dd['v'], paths, UNIT_VERILOG_PATH)
#     files_vhdl = export_files(wd, dd['vhdl'], paths, UNIT_VHDL_PATH)
#     files_inc = export_files(wd, dd['path'], paths, UNIT_INCLUDE_PATH)
#     files_c = export_files(wd, dd['c'], paths, UNIT_C_PATH)

#     #unit name to simulate
#     unit = cnf.getval(".unit")
#     testcase = cnf.getval(".testcase")
#     toplevel = cnf.getval(".toplevel")
#     log.info(f"unit:{unit} testcase:{testcase} toplevel:{toplevel}")

#     rd = pathlib.Path('result')

#     td = pathlib.Path(NCSIM_TESTCASE_DIR.format(unit=unit, testcase=testcase))

#     #env files
#     vars = roadrunner.mod.files.gather_env_files(cnf, wd, tags)
#     print(f"vars:{vars}")
#     files_vars = []
#     for var in vars.values():
#         if (wd / var).exists():
#             files_vars.append((var, td / var.name))
#     fname = roadrunner.mod.verilog.write_env_file(wd, vars)
#     source = fn.relpath(fname, wd)
#     files_sv.insert(0, (source, td / source))

#     #write RTL makefile
#     def makeMakefileList(lst):
#         strlst = [f"    $(ICPRO_DIR)/{x} \\" for _, x in lst]
#         return "\n".join(strlst)
#     with open(wd / "sources.rtl.Makefile", "w") as fh:
#         print(rr.template(NCSIM_SOURCES_RTL_TEMPLATE).format(
#             toplevel=toplevel,
#             v_files=makeMakefileList(files_v),
#             sv_files=makeMakefileList(files_sv),
#             vhdl_files=makeMakefileList(files_vhdl),
#             c_files=makeMakefileList(files_c)
#         ), file=fh)

#     #write VARS makefile
#     defines = []
#     for d in dd['define']:
#         defines.append(f"IRUN_OPTS += -define {d.strip()}")
#     with open(wd / "Makefile.var", "w") as fh:
#         print(rr.template(NCSIM_VARS_TEMPLATE).format(
#             testcase=testcase,
#             defines="\n".join(defines)
#         ), file=fh)

#     #make shares.yaml
#     shares = roadexec.shares.Shares(wd / "shares.yaml", Path(".."))
#     shares.expose(Path("SiCo.sock"), "SiCo.sock")

#     #exporter
#     dirs = []
#     with open(wd / "export.sh", "w") as fh:
#         print("#Verilog", file=fh)
#         for source, dest in files_v:
#             copyFile(fh, dirs, source, rd / dest)
#         print("#SystemVerilog", file=fh)
#         for source, dest in files_sv:
#             copyFile(fh, dirs, source, rd / dest)
#         print("#VHDL", file=fh)
#         for source, dest in files_vhdl:
#             copyFile(fh, dirs, source, rd / dest)
#         print("#C", file=fh)
#         for source, dest in files_c:
#             copyFile(fh, dirs, source, rd / dest)
#         print("#include paths", file=fh)
#         for source, dest in files_inc:
#             copyFile(fh, dirs, source, rd / dest)
#         print("#misc", file=fh)
#         for source, dest in files_vars:
#             copyFile(fh, dirs, source, rd / dest)
#         copyFile(fh, dirs, "sources.rtl.Makefile", rd / td / NCSIM_SOURCES_RTL_FILE.format(unit=unit))
#         copyFile(fh, dirs, "Makefile.var", rd / td / NCSIM_VARS_FILE.format(unit=unit))
#         copyFile(fh, dirs, "shares.yaml", rd / td / "shares.yaml")

#     pipe.configDefault('Bash', 'bin', 'bash $@') #FIXME load the default from somewhere
#     call = rr.Call(wd, 'exportFiles', ('Bash', 'bin'))
#     call.addArgs(['export.sh'])

#     pipe.runCall(call)

#     #parallel command
#     do_parallel(cnf, pipe, rd / td, paths)

# def do_parallel(cnf:ConfigNode, pipe:Pipeline, tcDir:Path, pathMap:dict):
#     wd = pipe.cwd()
#     try:
#         cmdNode = cnf.get(".parallel").resolve()
#     except PathNotExist:
#         return
#     cmdWd = wd / "parallel"
#     cmdWd.mkdir(exist_ok=True)
#     cmdPipe = Pipeline(cmdWd)
#     rr.command_run(cmdNode, cmdPipe)
#     cmdDir, cmdFile = cmdPipe.commit()
#     print(f"parallel dir:{cmdDir} file:{cmdFile}")

#     resultDir = Path('result')

#     #copy/link files
#     dirs = []
#     with open(wd / "export.sh", "a") as fh:
#         print("#parallel command", file=fh)
#         def walk(loc:Path):
#             if loc.is_dir():
#                 for itm in loc.iterdir():
#                     walk(itm)
#             else:
#                 source = loc.relative_to(wd)
#                 dest = tcDir / "parallel" / loc.relative_to(cmdWd)
#                 real = dispatchFile(loc, pathMap, cmdDir, resultDir)
#                 copyFile(fh, dirs, source, dest, real)
#         walk(cmdWd)


#create commands to copy a file from source to dest
# also creates a command to make the destination directory
def copyFile(fh, dirs:list, source:Path, dest:Path):
    #dont copy static files
    if source is None:
        return
    #create directories
    if dest.parent not in dirs:
        dirs.append(dest.parent)
        print(f"mkdir -p {dest.parent}", file=fh)
    #copy
    print(f"cp -r -T {source} {dest}", file=fh)

# #returns location for the file
# def dispatchFile(fname:Path, pathMap:dict, source:Path, dest:Path) -> Path:
#     log = logging.getLogger("ICPro")
#     relPath = fname.relative_to(source)
#     nodeStr = relPath.parts[0]
#     #don't patch roadexec infrastructure
#     if nodeStr in ['calls', 'tools'] or len(relPath.parts) <= 1:
#         return
#     localPath = relPath.relative_to(Path(nodeStr))
#     ext = fname.suffix
#     try:
#         templ = {
#             '.py': UNIT_PYTHON_PATH,
#             '.pyc': UNIT_PYTHON_PATH,
#         }[ext]
#     except KeyError:
#         log.info(f"unknown file type - keeping file local:{fname}")
#         return None
#     unit = mapUnit(nodeStr, pathMap)
#     if unit is None:
#         log.info(f"cannot determine unit - keep file local {fname} in {source}")
#         return None
#     real = dest / Path(templ.format(unit=unit)) / localPath
#     #log.info(f"dispatch file:{fname} -> real:{real}")
#     return real


def mapUnit(directory:str, map:dict) -> str:
    log = logging.getLogger("ICPro")
    unitname = None
    for slug, unit in map.items():
        if directory.startswith(slug):
            if unitname is not None:
                log.warning(f"multiple units defined for dir:{directory} old:{unitname} new:{unit}")
            unitname = unit
    return unitname


def export_files(wd:Path, lst:list[roadrunner.modules.verilog.FileItem], attr:str):
    exports = []
    log = logging.getLogger("ICPro")
    for itm in lst:
        for filep in getattr(itm, attr):
            if not itm.static:
                target = Path(EXPORT_PATH) / filep
                source = filep
                log.debug(f"export dynamic {source} -> {target}")
            else:
                target = filep
                source = None
                log.debug(f"export static {target}")
            if target not in [x[1] for x in exports]:
                exports.append((source, target))
    return exports

