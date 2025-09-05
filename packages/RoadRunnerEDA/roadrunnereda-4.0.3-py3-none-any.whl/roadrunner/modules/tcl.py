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

from pathlib import Path

from roadrunner.fn import etype

RRENV_FILE = "RREnv.tcl"

def writeEnvFile(loc:Path, vars:dict) -> Path:
    etype((loc,Path), (vars,dict))
    fname = loc / RRENV_FILE
    with open(fname, "w") as fh:
        for name, var in vars.items():
            print(f"set {name} {tclVal(var)}", file=fh)
    return fname

def tclVal(val):
    if isinstance(val, list):
        return " ".join([f"{{{x}}}" for x in val])
    elif isinstance(val, bool):
        return f"{1 if val else 0}"
    elif val is None:
        return "{}"
    elif isinstance(val, str):
        return f'"{val}"'
    else:
        return f"{val}"

