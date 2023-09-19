<p align="center">
  <a href="https://fastapi.tiangolo.com"><img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI"></a>
  <a href="https://tortoise.github.io"><img src="https://avatars.githubusercontent.com/u/42678965" alt="TortoiseORM"></a>
</p>
<p align="center">
    <em>Toolkit for FastAPI+TortoiseORM projects to runserver/migration/lint ...</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fast-tort-cli" target="_blank">
    <img src="https://img.shields.io/pypi/v/fast-tort-cli?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fast-tort-cli" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fast-tort-cli.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://github.com/waketzheng/fast-tort-cli/actions?query=workflow:ci" target="_blank">
    <img src="https://github.com/waketzheng/fast-tort-cli/workflows/ci/badge.svg" alt="GithubActionResult">
</a>
<a href="https://coveralls.io/github/waketzheng/fast-tort-cli?branch=main" target="_blank">
    <img src="https://coveralls.io/repos/github/waketzheng/fast-tort-cli/badge.svg?branch=main" alt="Coverage Status">
</a>
</p>

---

**Documentation**: <a href="https://waketzheng.github.io/fast-tort-cli" target="_blank">https://waketzheng.github.io/fast-tort-cli</a>

**Source Code**: <a href="https://github.com/waketzheng/fast-tort-cli" target="_blank">https://github.com/waketzheng/fast-tort-cli</a>

## Requirements

Python 3.11+

## Installation

<div class="termy">

```console
$ pip install "fast-tort-cli[all]"
---> 100%
Successfully installed fast-tort-cli
```

## Usage

- Lint py code:
```bash
fast lint /path/to/file-or-directory
```
- Bump up version in pyproject.toml
```bash
fast bump
```
- Export requirement file and install `pip install -r `
```bash
fast sync
```
- Upgrade main/dev dependenices to latest version
```bash
fast upgrade
```
- Run unittest and report coverage
```bash
fast test
```
