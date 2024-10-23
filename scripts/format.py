#!/usr/bin/env python
import os
import shlex
import subprocess
import sys
from pathlib import Path

work_dir = Path(__file__).parent.resolve().parent
if Path.cwd() != work_dir:
    os.chdir(str(work_dir))

cmd = "pdm run fast lint"
r = subprocess.run(shlex.split(cmd), env=dict(os.environ, SKIP_MYPY="1"))
sys.exit(None if r.returncode == 0 else 1)
