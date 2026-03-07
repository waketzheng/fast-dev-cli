<p align="center">
  <img src="https://raw.githubusercontent.com/waketzheng/fast-dev-cli/main/img/logo-teal.png" alt="FastDevCli">
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
<a href="https://github.com/microsoft/pyright" target="_blank">
    <img src="https://img.shields.io/badge/pyright-checked-brightgreen.svg" alt="Pyright Checked">
</a>
<a href="https://github.com/astral-sh/ty" target="_blank">
    <img src="https://img.shields.io/badge/ty-checked-brightgreen.svg" alt="ty Checked">
</a>
<a href="https://github.com/astral-sh/ruff" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
</a>
<a href="https://pdm-project.org/en/latest/" target="_blank">
    <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>
<a href="https://github.com/PyCQA/bandit" target="_blank">
    <img src="https://img.shields.io/badge/security-bandit-orange.svg" alt="security: bandit">
</a>
</p>

---

**Source Code**: <a href="https://github.com/waketzheng/fast-dev-cli" target="_blank">https://github.com/waketzheng/fast-dev-cli</a>

---

fast-dev-cli is a command line tool to make it easy to:
- Bump version
- Lint code
- Serve api
- Display version
- Install deps

## `fastdevcli-slim`

⚠️ Do not install this package. ⚠️

This package, `fastdevcli-slim`, does nothing other than depend on `fast-dev-cli`.

There used to be a slimmed-down version of fast-dev-cli called `fastdevcli-slim`, which didn't include the dependencies `rich` and `shellingham`, and use `typer-slim` instead of `typer`.

However, since version 0.22.0, we have stopped supporting this, and `fastdevcli-slim` now simply installs (all of) fast-dev-cli.

If you want to disable Rich globally, you can set an environmental variable `TYPER_USE_RICH` to `False` or `0`.

The only reason this package exists is as a migration path for old projects that used to depend on `fastdevcli-slim`, so that they can get the latest version of `fast-dev-cli`.

You **should not** install this package.

Install instead:

```bash
pip install fast-dev-cli
```

This package is deprecated and will stop receiving any updates and published versions.

## License

This project is licensed under the terms of the MIT license.
