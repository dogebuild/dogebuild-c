from dogebuild_c.c_plugin import CPlugin, BinaryType

CPlugin(
    type=BinaryType.DYNAMIC_LIBRARY,
    out='helloworlder',
    src=[
        'helloworlder.c',
    ],
    headers=[
        'helloworlder.h',
    ],
    test_src=[
        'test.c',
    ]
)
