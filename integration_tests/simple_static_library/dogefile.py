from pathlib import Path

from dogebuild_c.c_plugin import CPlugin

CPlugin(
    out_name="helloworlder",
    src=[Path("helloworlder.c"),],
    src_dir=".",
    headers=[Path("helloworlder.h"),],
    test_src=[Path("test.c"),],
)
