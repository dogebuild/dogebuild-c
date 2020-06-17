# dogebuild-c

[![Build Status](https://travis-ci.com/dogebuild/dogebuild-c.svg?branch=master)](https://travis-ci.com/dogebuild/dogebuild-c)
[![PyPI version](https://badge.fury.io/py/dogebuild-c.svg)](https://badge.fury.io/py/dogebuild-c)
[![Documentation Status](https://readthedocs.org/projects/dogebuild-c/badge/?version=latest)](https://dogebuild-c.readthedocs.io/en/latest/?badge=latest)


C language plugin for dogebuild

## Install dogebuild c plugin

Install dogebuild c plugin via pip:

```shell script
pip install dogebuild-c
``` 

Dogebuild will be installed as a dependency.

## Creating project with tapas

The easiest way to create project is to use [tapas scaffold tool](https://github.com/tapas-scaffold-tool/tapas).
To install tapas use pip:

```shell script
pip install tapas
```

And then run tapas and follow instructions:

```shell script
tapas dogebuild-c <target-dir>
```

## Manually creating project

Create `dogefile.py` and fill it with following code:

```python
from pathlib import Path

from dogebuild_c.c_plugin import CPlugin, BinaryType


CPlugin(
    binary_type=BinaryType.EXECUTABLE,
    out_name="executable_name",
    src=Path("src").glob('**/*.c'),
    headers=Path("src").glob('**/*.h'),
)
```

Create directory `src` and put all your source code files into that.

## Building project

To build project run dogebuild in project directory:

```shell script
doge build
```

To build and run project run:

```shell script
doge run
```

## Next steps

Advanced documentation for dogebuild available in [readthedocs](https://dogebuild.readthedocs.io).

Advanced documentation for dogebuild c plugin available in [readthedocs](https://dogebuild-c.readthedocs.io).
 