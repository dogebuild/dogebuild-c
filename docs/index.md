# Quick start

## What is dogebuild-c?

Dogebuid-c is [dogebuild](https://github.com/dogebuild/dogebuild) plugin to build C++ projects


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
