#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys

TOOL = ("pdm", "poetry", "uv")[0]
parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)


def run_and_echo(cmd, tool=TOOL, verbose=True):
    # type: (str, str, bool) -> int
    if tool:
        cmd = tool + " run " + cmd
    if verbose:
        print("--> " + cmd)
    return os.system(cmd)


if run_and_echo("fast check --skip-mypy", verbose=False) != 0:
    print("\033[1m Please run './scripts/format.py' to auto-fix style issues \033[0m")
    sys.exit(1)
package_name = os.path.basename(work_dir).replace("-", "_").replace(" ", "_")
if run_and_echo("mypy {} {}".format(package_name, "tests")) != 0:
    sys.exit(1)
if run_and_echo("bandit -r {}".format(package_name)) != 0:
    sys.exit(1)
print("Done. ✨ 🍰 ✨")
