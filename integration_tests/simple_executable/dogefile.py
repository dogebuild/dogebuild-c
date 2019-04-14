from dogebuild_c.c_plugin import CPlugin, BinaryType

CPlugin(
    type=BinaryType.EXECUTABLE,
    out='helloworlder',
    src=[
        'helloworlder.c',
        'main.c',
    ],
    headers=[
        'helloworlder.h',
    ],
    test_src=[
        'test.c',
    ],
    test_exclude=[
        'main.c',
    ],
)
