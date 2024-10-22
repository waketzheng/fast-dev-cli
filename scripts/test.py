#!/usr/bin/env python
import os
import subprocess
import sys
from pathlib import Path

work_dir = Path(__file__).parent.resolve().parent
if Path.cwd() != work_dir:
    os.chdir(str(work_dir))

cmds = """
pdm run coverage run -m pytest
pdm run coverage combine .coverage*
pdm run coverage report -m
""".strip().splitlines()

for cmd in cmds:
    print("-->", cmd)
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        sys.exit(1)
