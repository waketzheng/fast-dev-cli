#!/usr/bin/env python
import os
import sys

parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)

if os.system("pdm run fast check") != 0:
    print("\033[1m Please run './scripts/format.py' to auto-fix style issues \033[0m")
    sys.exit(1)

package_name = os.path.basename(work_dir).replace("-", "_")
cmd = "pdm run bandit -r {}".format(package_name)
print("-->", cmd)
if os.system(cmd) != 0:
    sys.exit(1)
print("Done.")
