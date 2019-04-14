from dogebuild_c.c_plugin import CPlugin

CPlugin(
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
