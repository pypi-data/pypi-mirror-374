import logging
from pathlib import Path
import pprint
from roadrunner.config import ConfigContext, PathNotExist
from roadrunner.fn import etype, banner, uniqueExtend
from roadrunner.rr import Pipeline, asset, workdir_import
from roadrunner.modules.tcl import tclVal
import roadrunner.rr as rr
from roadrunner.tools.vivado import common
import roadrunner.modules.verilog
import roadrunner.modules.stages

SYNTH_STEPS = {
    'synth': Path("vivado/synth.tcl"),
    'opt': Path("vivado/opt.tcl"),
    'place': Path("vivado/place.tcl"),
    'physopt': Path("vivado/physopt.tcl"),
    'route': Path("vivado/route.tcl"),
    'write': Path("vivado/write.tcl")
}

LOGNAME = "VivadoSynth"

def cmd_ip(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(LOGNAME)

    log.info(banner("Vivado IP"))

    wd = pipe.initWorkDir()

    vars = {
        'ipName': cfg.get(".name", isType=str),
        'ipPart': cfg.get(".part", isType=str),
        'ipBoard': cfg.get(".board", isType=str, default=""),
        'ipType': cfg.get('.typ', isType=str)
    }
    
    log.info(f"IP name:{vars['ipName']} part:{vars['ipPart']} board:{vars['ipBoard']} type:{vars['ipType']}")

    props = {}
    for key,val in cfg.move('.properties').leafs():
        props[key[1:]] = tclVal(val)
        log.info(f"Property: {key[1:]} = ({val})")
    vars['properties'] = props

    vars['xilinxFeatures'] = tclVal(cfg.get(".xilinxFeatures", mkList=True, default=[]))
    vars['xilinxLibs'] = tclVal(cfg.get(".libs", mkList=True, default=[]))

    tpl = asset(Path("vivado/ipgen.tcl"))
    lua = cfg.lua()
    lua.addVariables(vars)
    content = lua.run(tpl)
    
    with open(pipe.cwd() / "ipgen.tcl", "w") as fh:
        print(content, file=fh)

    call = rr.Call(wd, "ipgen", common.NAME, vrsn)
    call.addArgs(['vivado', '-mode', 'batch'])
    call.addArgs(['-source', "ipgen.tcl"])
    with pipe.inCall(common.NAME):
        pipe.useCall(call)

        pipe.result()
        pipe.export(vars['ipName'], Path('.')) #FIXME, cannot wok really
        pipe.export('RR', Path('.'))

    log.info(banner("/Vivado IP", False))

    return 0

def cmd_synth(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(LOGNAME)

    log.info(banner("Vivado Synth"))

    wd = pipe.initWorkDir()

    part = cfg.get(".part", isType=str)
    board = cfg.get(".board", isType=str, default="")
    toplevel = cfg.get(".toplevel", isType=str)
    incremental = cfg.get(".incremental", isType=bool, default=False)
    check = cfg.get(".check", default=True, isType=bool)

    fcfg = cfg.move(addFlags={'SYNTHESIS'})

    #verilog files
    lst = roadrunner.modules.verilog.includeFiles(fcfg.move(), wd)
    vars = {
        'part': part,
        'board': board,
        'toplevel': toplevel,
        'buildInc': incremental
    }
    nodes = []
    for item in lst:
        node = {
            'verilog': [tclVal(f) for f in item.v],
            'systemVerilog': [tclVal(f) for f in item.sv],
            'defines': [tclVal(f) for f in item.defines],
            'path': [tclVal(f) for f in item.path],
        }
        nodes.append(node)
    vars['sources'] = nodes

    #options
    opts = []
    xpmLibs = []
    for itm in fcfg.travers():
        vals = itm.get(".xilinxFeatures", default=[], mkList=True)
        uniqueExtend(opts, vals)
    if 'useXPMMem' in opts:
        uniqueExtend(xpmLibs, ['XPM_MEMORY'])
    vars['XPMLibraries'] = xpmLibs

    #IP
    xciList = []
    for itm in fcfg.move(addFlags=roadrunner.modules.verilog.CONFIG_FLAGS).travers():
        uniqueExtend(xciList, itm.get('.ip', mkList=True, default=[], isOsPath=True))

    ipList = []
    for itm in xciList:
        ipList.append(workdir_import(wd, itm))
        workdir_import(wd, (itm[0], itm[1].with_suffix('.xml')))
        workdir_import(wd, (itm[0], itm[1].with_suffix('.dcp')))
    vars['ip'] = ipList

    constrList = []
    for itm in fcfg.travers():
        try:
            ccfg = itm.move('.constraints')
        except PathNotExist:
            continue
        for key,iitm in ccfg:
            if iitm.isDict():
                props = {}
                fname = iitm.get(".file", isOsPath=True)
                options = iitm.get(".xilinxFeatures", mkList=True, default=[])
                if "notSynth" in options:
                    props["USED_IN_SYNTHESIS"] = "false"
                #TODO read a propoerties dict
                constrList.append({
                    'file': str(workdir_import(wd, fname)),
                    'properties': props
                })
            else:
                fname = iitm.get(isOsPath=True)
                constrList.append({
                    'file': str(workdir_import(wd, fname)),
                    'properties': {}
                })
    vars['constraints'] = constrList    

    log.info(f"Synth on part:{part} board:{board}")
    log.info(f"vars:{vars}")

    maintpl = asset(Path("vivado/impl.tcl"))
    stages = roadrunner.modules.stages.Stages(maintpl, ".tcl")
    for name,fpath in SYNTH_STEPS.items():
        stages.setStage(name, asset(fpath))
    try:
        scfg = cfg.move(".stages")
    except PathNotExist:
        scfg = None
    if scfg is not None:
        stages.loadConfig(scfg)

    lua = cfg.lua()
    lua.addVariables(vars)
    scriptDir = Path("synth")
    (wd / scriptDir).mkdir(exist_ok=True)
    main = stages.render(wd, scriptDir, lua)

    call = rr.Call(wd, "impl", common.NAME, vrsn)
    call.addArgs(['vivado', '-mode', 'batch'])
    call.addArgs(['-source', str(main)])
    pipe.enterCall(common.NAME)
    pipe.addCall(call)

    #check logs
    if check:
        snip = asset(Path('rr/logchecker.py'))
        rules = [{
            'pattern': "All user specified timing constraints are met.",
            'occur': 1
        },{
            'pattern': "Timing constraints are not met.",
            'occur': 0
        }]
        lua = cfg.lua()
        lua.addVariables({'rules': pprint.pformat(rules, sort_dicts=False)})
        raw = lua.run(snip)
        with open(wd / "logchecker.py", "w") as fh:
            print(raw, file=fh)
        call = rr.Call(wd, 'logchecker', "Python3")
        call.addArgs(['python3', 'logchecker.py', 'routed_timing.rpt'])
        pipe.addCall(call)

    pipe.leave()

    log.info(banner("/Vivado Synth", False))

    return 0
