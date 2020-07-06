# Multimodule project

You can separate your project to several modules. 
For dogebuild multimodule project see [dogebuild documentation](https://dogebuild.readthedocs.io/en/latest/multimodule-project/).

## Multimodule project structure

Multimodule dogebuild-c project usually consist of some libraries modules and one or many executables:

```
project/
  library_1/
    src/
      ... library_1 sources ...
    dogefile.py
  library_2/
    src/
      ... library_2 sources ...
    dogefile.py
  main_executable/
    src/
      ... main executable sources ...
    dogefile.py
```

Dogefile for libraries is a standard static library dogefile:


```python
from pathlib import Path

from dogebuild_c.c_plugin import CPlugin, BinaryType


CPlugin(
    binary_type=BinaryType.STATIC_LIBRARY,
    out_name="library_1",
    src=Path("src").glob('**/*.c'),
    headers=Path("src").glob('**/*.h'),
)

```

Dogefile for main executable dependent on library should contain list of its dependencies:

```python
from pathlib import Path

from dogebuild import dependencies, directory, doge
from dogebuild_c.c_plugin import CPlugin, BinaryType

dependencies(
    doge(directory("../library_1")),
    doge(directory("../library_2")),
)

CPlugin(
    binary_type=BinaryType.EXECUTABLE,
    out_name="main",
    src=Path("src").glob('**/*.c'),
    headers=Path("src").glob('**/*.h'),
)
```

Dogefile for project is simple multimodule dogefile:

```python
from dogebuild import modules

modules(
    'library_1',
    'library_2',
    'main',
)
```

Example of multimodule project available in [demo repository](https://github.com/dogebuild/dogebuild-c-demo/tree/master/project-with-library).
