#!/usr/bin/env python
import os
import sys

parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)

cmd = "pdm run fast test"
print("-->", cmd)
if os.system(cmd) != 0:
    sys.exit(1)
print("Done.")
