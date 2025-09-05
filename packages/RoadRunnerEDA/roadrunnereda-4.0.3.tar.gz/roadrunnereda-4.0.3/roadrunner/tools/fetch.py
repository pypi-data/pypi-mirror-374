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
from roadrunner.fn import etype
from roadrunner.config import ConfigContext
from roadrunner.rr import Call, Pipeline


NAME = "Fetch"
DESCRIPTION = "Fetch sources from online services"

GITLAB_DEFAULT_URL = "gitlab.com"
GITLAB_DEFAULT_REV = "main"
#   url: https://gitlab.barkhauseninstitut.org/scoha/bilib/-/archive/dev/bilib-dev.tar.gz
GITLAB_URL_TEMPL = "https://{baseUrl}/{owner}/{repo}/-/archive/{rev}/{repo}-{rev}.tar.gz"
# https://github.com/Barkhausen-Institut/bilib/archive/refs/heads/dev.zip
GITHUB_URL_TEMPL = "https://github.com/{owner}/{repo}/archive/refs/heads/{rev}.tar.gz"

def cmd_gitlab(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(NAME)
    wd = pipe.initWorkDir()
    fcfg = cfg
    baseUrl = fcfg.get(".url", default=GITLAB_DEFAULT_URL, isType=str)
    owner = fcfg.get(".owner", isType=str)
    repo = fcfg.get(".repo", isType=str)
    rev = fcfg.get(".rev", default=GITLAB_DEFAULT_REV, isType=str)
    url = GITLAB_URL_TEMPL.format(
        baseUrl=baseUrl,
        owner=owner,
        repo=repo,
        rev=rev
    )
    with pipe.inSequence(NAME):
        pipe.result()
        do_fetch(url, pipe, wd, vrsn)
    return 0

def cmd_github(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(NAME)
    wd = pipe.initWorkDir()
    fcfg = cfg
    owner = fcfg.get(".owner", isType=str)
    repo = fcfg.get(".repo", isType=str)
    rev = fcfg.get(".rev", default=GITLAB_DEFAULT_REV, isType=str)
    url = GITHUB_URL_TEMPL.format(
        owner=owner,
        repo=repo,
        rev=rev
    )
    with pipe.inSequence(NAME):
        pipe.result()
        do_fetch(url, pipe, wd, vrsn)

    return 0

def cmd_archive(cfg:ConfigContext, pipe:Pipeline, vrsn:str):
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    log = logging.getLogger(NAME)
    wd = pipe.initWorkDir()
    fcfg = cfg
    url = fcfg.get(".url", isType=str)
    pipe.result()
    do_fetch(url, pipe, wd, vrsn)
    return 0

def do_fetch(url:str, pipe:Pipeline, wd:Path, vs:str):
    log = logging.getLogger(NAME)
    call = Call(wd, "curl", NAME, vs)
    call.addArgs(["curl", url, "-o", "archive.tar.gz", "-L"])
    pipe.addCall(call)
    call = Call(wd, "tar", NAME, vs)
    call.addArgs(["tar", "-x", "-z", "-f", "archive.tar.gz", "-C", "result", "--strip-components", "1"])
    pipe.addCall(call)

    return 0

