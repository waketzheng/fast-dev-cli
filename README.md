<p align="center">
  <img src="https://fastdevcli.waketzheng.top/img/logo-margin/logo-teal.png" alt="FastDevCli">
</p>
<p align="center">
    <em>Toolkit for python code lint/test/bump ...</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fast-dev-cli" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fast-dev-cli.svg" alt="Supported Python versions">
</a>
<a href="https://pypi.org/project/fast-dev-cli" target="_blank">
    <img src="https://img.shields.io/pypi/v/fast-dev-cli?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://github.com/waketzheng/fast-dev-cli/actions?query=workflow:ci" target="_blank">
    <img src="https://github.com/waketzheng/fast-dev-cli/workflows/ci/badge.svg" alt="GithubActionResult">
</a>
<a href="https://coveralls.io/github/waketzheng/fast-dev-cli?branch=main" target="_blank">
    <img src="https://coveralls.io/repos/github/waketzheng/fast-dev-cli/badge.svg?branch=main" alt="Coverage Status">
</a>
<a href="https://github.com/python/mypy" target="_blank">
    <img src="https://img.shields.io/badge/mypy-100%25-brightgreen.svg" alt="Mypy Coverage">
</a>
<a href="https://github.com/PyCQA/bandit" target="_blank">
    <img src="https://img.shields.io/badge/security-bandit-orange.svg" alt="security: bandit">
</a>
<a href="https://github.com/astral-sh/ruff" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
</a>
</p>

---

**Source Code**: <a href="https://github.com/waketzheng/fast-dev-cli" target="_blank">https://github.com/waketzheng/fast-dev-cli</a>

**English** | [中文](./README.zh.md)

## Requirements

Python 3.10+

## Installation

<div class="termy">

```bash
pip install fast-dev-cli
```
*Will install: fast-dev-cli emoji typer ruff mypy bumpversion2 pytest coverage*

</div>

## Usage

- Lint py code:
```bash
fast lint [/path/to/file-or-directory]
```
- Check only
```bash
fast check
```
- Bump up version in pyproject.toml
```bash
fast bump patch  # 0.1.0 -> 0.1.1
fast bump minor  # 0.1.0 -> 0.2.0
fast bump major  # 0.1.0 -> 1.0.0
fast bump <part> --commit # bump version and run `git commit`
```
- Run unittest and report coverage
```bash
fast test
```
- Export requirement file and install `pip install -r `
```bash
fast sync
```
- Upgrade main/dev dependencies to latest version (only for poetry project)
```bash
fast upgrade
```
- Start a fastapi server in development mode
```bash
fast dev
```
- Publish to pypi
```bash
fast upload
```
*Note: all command support the `--dry` option*
