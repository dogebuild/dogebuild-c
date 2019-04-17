from dogebuild_c.c_plugin import CPlugin, BinaryType
from dogebuild.dependencies import dependencies, folder

dependencies(
    folder('../dependency')
)

CPlugin(
    type=BinaryType.EXECUTABLE,
    out='hello',
    src_dir='.',
    src=[
        'main.c',
    ],
)
