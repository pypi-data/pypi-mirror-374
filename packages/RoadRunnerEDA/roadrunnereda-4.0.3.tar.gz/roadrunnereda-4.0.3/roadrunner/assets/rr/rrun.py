#! /usr/bin/env python3
from roadexec.run import RunEnv
isMain = __name__ == '__main__'
ex = RunEnv(globals(),
<%-pipeline%>,
<%-env%>)
ret = ex.run()
ex.exit(ret)