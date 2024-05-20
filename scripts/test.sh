#!/usr/bin/env bash

set -e
pdm run coverage run -m pytest
pdm run coverage combine .coverage*
pdm run coverage report -m
