# Quick start

## What is dogebuild-c?

Dogebuid-c is [dogebuild](https://github.com/dogebuild/dogebuild) plugin to build C++ projects


## Creating project with tapas

The easiest way to create project is to use [tapas scaffold tool](https://github.com/tapas-scaffold-tool/tapas).

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

Example of siple hello world project available in [demo repository](https://github.com/dogebuild/dogebuild-c-demo/tree/master/hello-world).
