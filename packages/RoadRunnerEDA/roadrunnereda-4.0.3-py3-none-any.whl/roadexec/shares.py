import configparser
from pathlib import Path
import logging

from roadexec.fn import etype, relpath

NAME = "shares"

class Shares:
    store:dict[str,Path]
    def __init__(self):
        self.store = {}
    
    def expose(self, file:Path, name:str):
        etype((name, str), (file, Path))
        log = logging.getLogger(NAME)
        if name in self.store:
            log.warn(f"overwriting share:{name}")
        self.store[name] = file
        log.debug(f"expose ({name}) -> ({file})")

    def discover(self, name:str) -> Path:
        etype((name, str))
        log = logging.getLogger(NAME)
        if name not in self.store:
            raise RuntimeError(f"share{name} is not defined")
        try:
            val = self.store[name]
            log.debug(f"discover ({name}) -> ({val})")
            return val
        except KeyError:
            pass
        raise NotExposed
    
class ShareGate(Shares):
    def __init__(self, shares:Shares, offset:Path):
        etype((shares, Shares), (offset, (Path, None)))
        self.shares = shares
        self.offset = offset or Path(".")
        log = logging.getLogger(NAME)
        log.debug(f"create share gate off:({self.offset})")

    def expose(self, file:Path, name:str):
        etype((name, str), (file, Path))
        log = logging.getLogger(NAME)
        log.debug(f"gate expose off:({self.offset}) ({name}) -> ({file})")
        self.shares.expose(self.offset / file, name)

    def discover(self, name:str) -> Path:
        etype((name, str))
        log = logging.getLogger(NAME)
        path = self.shares.discover(name)
        norm = relpath(path, self.offset)
        log.debug(f"gate discover off:({self.offset}) ({name}) -> ({path})({norm})")
        return norm

# class FileShares:
#     def __init__(self, fileName:Path, prefix:Path, offset:Path):
#         etype((fileName, Path), (prefix, Path), (offset, Path))
#         self.fname = fileName
#         self.offset = offset
#         self.prefix = prefix
#         self.config = configparser.ConfigParser()
#         self.config.read(fileName)
#         if 'shares' not in self.config:
#             self.config['shares'] = {}

#     def saveFile(self):
#         with open(self.fname, "w") as fh:
#             self.config.write(fh)

#     def expose(self, file:Path, name:str):
#         self.config['shares'][name] = str(self.prefix / file)
#         self.saveFile()
    
#     def discover(self, name:str):
#         try:
#             return self.offset / self.config['shares'][name]
#         except KeyError:
#             raise NotExposed(name)

# def load():
#     sharesFile = Path("shares.ini")
#     if not sharesFile.exists():
#         raise RuntimeError("shares.ini not found")
#     if not sharesFile.is_symlink():
#         raise RuntimeError("shares.ini should be a symlink")
#     realDir = sharesFile.readlink().parent.absolute()
#     cwd = Path.cwd()
#     prefix = cwd.relative_to(realDir)
#     offset = realDir.relative_to(cwd)
#     return Shares(sharesFile, prefix, offset)

class NotExposed(Exception):
    pass
