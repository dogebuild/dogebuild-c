# dogebuild-c

[![Build Status](https://travis-ci.com/dogebuild/dogebuild-c.svg?branch=master)](https://travis-ci.com/dogebuild/dogebuild-c)
[![PyPI version](https://badge.fury.io/py/dogebuild-c.svg)](https://badge.fury.io/py/dogebuild-c)
[![Documentation Status](https://readthedocs.org/projects/dogebuild-c/badge/?version=latest)](https://dogebuild-c.readthedocs.io/en/latest/?badge=latest)


C language plugin for dogebuild

## Dogefile example

```python
from pathlib import Path

from dogebuild_c.c_plugin import CPlugin, BinaryType


CPlugin(
    binary_type=BinaryType.EXECUTABLE,
    out_name="helloworlder",
    src=[Path("helloworlder.c"), Path("main.c"),],
    headers=[Path("helloworlder.h"),],
    test_src=[Path("test.c"),],
    test_src_exclude=[Path("main.c"),],
)

```
