from dogebuild_c.c_plugin import CPlugin, BinaryType
from dogebuild import dependencies, folder

dependencies(
    folder('../dependency')
)

CPlugin(
    binary_type=BinaryType.EXECUTABLE,
    out_name='hello',
    src=[
        'main.c',
    ],
)
