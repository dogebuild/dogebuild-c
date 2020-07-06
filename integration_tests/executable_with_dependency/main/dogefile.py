from dogebuild_c.c_plugin import CPlugin, BinaryType
from dogebuild import dependencies, directory, doge

dependencies(doge(directory("../dependency")))

CPlugin(
    binary_type=BinaryType.EXECUTABLE, out_name="hello", src=["main.c",], src_dir=".",
)
