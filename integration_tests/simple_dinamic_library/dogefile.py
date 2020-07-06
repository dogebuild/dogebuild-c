from dogebuild_c.c_plugin import CPlugin, BinaryType

CPlugin(
    binary_type=BinaryType.DYNAMIC_LIBRARY,
    out_name="helloworlder",
    src=["helloworlder.c",],
    headers=["helloworlder.h",],
    test_src=["test.c",],
    src_dir=".",
)
