#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

work_dir = Path(__file__).parent.resolve().parent
if Path.cwd() != work_dir:
    os.chdir(str(work_dir))

CMD = "pdm run coverage run -m pytest"
COMBINE = "pdm run coverage combine .coverage*"
REPORT = "pdm run coverage report -m"


def remove_outdate_files(start_time: float) -> None:
    for file in work_dir.glob(".coverage*"):
        if file.stat().st_mtime < start_time:
            file.unlink()
            print(f"Removed outdate file: {file}")


def run_command(cmd: str, shell=False) -> None:
    print("-->", cmd, flush=True)
    r = subprocess.run(cmd if shell else shlex.split(cmd), shell=shell)
    r.returncode and sys.exit(1)


def combine_result_files(shell=COMBINE) -> None:
    to_be_combine = [i.name for i in work_dir.glob(".coverage.*")]
    if to_be_combine:
        if sys.platform == "win32":
            if work_dir.joinpath(".coverage").exists():
                shell = shell.replace("*", " ")
            else:
                shell = shell.replace(".coverage*", "")
            shell += " ".join(to_be_combine)
        run_command(shell, True)


started_at = time.time()
run_command(CMD)
remove_outdate_files(started_at)
combine_result_files()
run_command(REPORT)
