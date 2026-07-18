#!/usr/bin/env -S just --justfile
set allow-duplicate-recipes

import? '.common-just/justfile'

system-info:
    @echo "This is an {{ arch() }} machine running on {{ os_family() }}"
    just --list

init:
    git submodule add https://github.com/waketzheng/python-backend-justfile .common-just
