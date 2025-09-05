from roadrunner.config import ConfigContext
from pathlib import Path
import roadrunner.runner.local as local


def run(cfg:ConfigContext) -> int:
    return local.run(cfg)

