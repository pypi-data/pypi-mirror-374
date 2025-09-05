import logging
import re
import subprocess
import sys
import inspect
import pathlib

import roadrunner.fn

# major.minor.patch
# major - not backwards compatible changes
# minor - backwards compatible changes, features extension
# patch - bug fixes only
# -dev  - not hitting a release label exactly - meaning somewhere between versions

REX_GITVERSION = r'v([\d\.]+)(-[\w-]+)?'

version_file = pathlib.Path(__file__).parent / "version"

def version_string():
    label, isdev = gitlabel()
    with open(version_file, 'r') as fh:
        version_const = fh.read().strip()
    if label is not None and label.split('.')[0:2] != version_const.split('.')[0:2]:
        logging.getLogger('RR').warning(f"git label does not match const version - git:{label} const:{version_const}")
    return version_const + ('-dev' if isdev else '')

def gitlabel():
    try:
        cmd = ["git", "describe", "--tags"]
        cwd = getroot()
        raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, cwd=cwd)
        dec = raw.decode(sys.stdout.encoding).strip()
    except FileNotFoundError: #git not installed?
        return None, False
    except subprocess.CalledProcessError: #not a git repository
        return None, False
    m = re.match(REX_GITVERSION, dec)
    isdev = False if m.group(2) is None else True
    return m.group(1), isdev

def getroot():
    cframe = inspect.currentframe()
    cfile = inspect.getfile(cframe)
    cfile2 = pathlib.Path(cfile)
    cpath = cfile2.resolve()
    cdir = cpath.parents[1]
    return cdir
