from pathlib import Path

from dogebuild_c.c_plugin import CPlugin

CPlugin(
    out_name='helloworlder',
    src=[
        Path('helloworlder.c'),
    ],
    headers=[
        Path('helloworlder.h'),
    ],
    test_src=[
        Path('test.c'),
    ]
)
