# Fast Dev CLI

开发工具合辑:

经常会需要执行`ruff format xxx.py && ruff check --fix xxx.py && mypy xxx.py`
一开始是使用lint.sh脚本来简化操作，实际使用中发现不够灵活，于是诞生了这个工具库。
由于Pycharm/Vscode用的少，平时一般在终端和服务器码代码，所以fast lint命令极大地方便了我对代码规范的追求。

[English](./README.md) | **中文**

## 要求

Python3.9及其以上版本

*注：如需在3.8中使用，下载源码、删除所有类型注解、然后从源码安装即可*

## 安装

- 全量安装
```bash
pip install fast-dev-cli
```
*会同时安装emoji、typer、ruff、mypy、pytest、coverage、bumpversion2等日常开发工具包*

- 最小化安装
```bash
pip install fastdevcli-slim
```
*只依赖typer/emoji(适用于只使用tag和sync/upload/upgrade命令的情况)*

## 使用
### 代码格式化
1. 使用ruff对当前目录下的所有Python文件进行格式化/导入排序/删除多余import，如果没报错再用mypy进行静态检查
```bash
fast lint
# 相当于执行：ruff format . && ruff check --extend-select=I,B,SIM --fix . && dmypy run .
```
- 注：dmypy run会启动一个后台进程来加速mypy检查

2. 对单个文件进行格式化和静态检查
```bash
fast lint /path/to/xxx.py
```
3. 对某个目录里的所有Python文件进行格式化和静态检查
```bash
fast lint /path/to/directory/
```
4. 示例
```bash
fast lint conftest.py tortoise-orm/ tests/
```
### 代码规范检查
```bash
fast check
```
*与fast lint的不同是：只做检查，不修改原文件*

### 升级版本号
- 升级小版本，如：0.1.5 -> 0.1.6
```bash
fast bump patch
```
- 升级中版本，如：0.1.5 -> 0.2.0
```bash
fast bump minor
```
- 升级大版本，如：0.1.5 -> 1.0.0
```bash
fast bump major
```
- 升级版本并提交commit
```bash
fast bump <part> --commit
```

### 执行单元测试，并打印覆盖率
```bash
fast test
```
### 导出依赖文件，并使用pip安装所有依赖
- 适用于某些poetry install会报错，或无法直接用poetry install的情况
```bash
fast sync --save
```
### 升级poetry管理的所有依赖包至最新版本
poetry update有时只会升级依赖包的小版本，如：sqlmodel==0.0.18 -> sqlmodel==0.0.19

而fast upgrade则会连大版本也升级，如：python-dotenv="^0.19.2" -> python-dotenv="^1.0.1"
```bash
fast upgrade
```

### 启动fastapi调试服务（只适用于fastapi>=0.111.0）
- 默认使用8000端口和127.0.0.1主机
```bash
fast dev
# 相当于执行fastapi dev
```
- 使用其他端口
```bash
fast dev 8001
```
- 指定要启动的文件
```bash
fast dev file_with_app.py
```
- 同时修改端口和主机
```bash
fast dev my_app.py --port=9000 --host=0.0.0.0
```

### 发布软件包到pypi

```bash
fast upload
```
**注：所有命令均支持`--dry`参数，即只打印命令，不实际执行**

## 许可证

[MIT](./LICENSE)
