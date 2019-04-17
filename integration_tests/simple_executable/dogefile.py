from dogebuild_c.c_plugin import CPlugin, BinaryType

CPlugin(
    type=BinaryType.EXECUTABLE,
    out='helloworlder',
    src_dir='.',
    src=[
        'helloworlder.c',
        'main.c',
    ],
    headers=[
        'helloworlder.h',
    ],
    test_src_dir='.',
    test_src=[
        'test.c',
    ],
    test_main_exclude=[
        'main.c',
    ],
)
