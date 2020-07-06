from dogebuild_c.c_plugin import CPlugin

CPlugin(
    out_name="helloworlder", src=["helloworlder.c",], headers=["helloworlder.h",], test_src=["test.c",], src_dir=".",
)
