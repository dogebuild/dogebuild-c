from dogebuild_c.c_plugin import CPlugin

CPlugin(
    out='helloworlder',
    src_dir='.',
    src=[
        'helloworlder.c',
    ],
    headers=[
        'helloworlder.h',
    ],
    test_src_dir=',',
    test_src=[
        'test.c',
    ]
)
