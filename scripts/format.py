#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys

parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)

cmd = "pdm run fast lint --skip-mypy"
if os.system(cmd) != 0:
    sys.exit(1)
