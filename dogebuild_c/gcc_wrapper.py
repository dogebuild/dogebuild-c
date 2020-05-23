from logging import getLogger
from subprocess import run
from enum import Enum, unique, auto
from pathlib import Path
import os
import shutil
from typing import List, Tuple


@unique
class BinaryType(Enum):
    STATIC_LIBRARY = auto()
    DYNAMIC_LIBRARY = auto()
    EXECUTABLE = auto()


class GccWrapper:
    ALLOWED_CODE_EXTENSIONS = [
        '.c',
    ]

    ALLOWED_HEADER_EXTENSIONS = [
        '.h',
    ]

    def __init__(self):
        self.logger = getLogger('GccWrapper')
        self.binary = 'gcc'

    def compile(self, build_dir: Path, binary_type: BinaryType, source_files: List[Path], headers_dirs: List[Path]) -> Tuple[int, List[Path]]:
        """
        Compile all ALLOWED_CODE_EXTENSIONS files to corresponding .o files regarding directory structure
        :param build_dir: root of build directory
        :param binary_type: type of
        :param source_files: list of source files
        :param headers_dirs: list of headers directories
        :return: Tuple of binary return code and list of .o files
        """
        build_dir.mkdir(exist_ok=True, parents=True)

        o_files = []
        for src in source_files:
            command = [self.binary, '-c']

            for header_dir in headers_dirs:
                command.append(f'-I{header_dir}')

            if binary_type is BinaryType.DYNAMIC_LIBRARY:
                # Need to create macros in binary code.
                # See https://renenyffenegger.ch/notes/development/languages/C-C-plus-plus/GCC/options/f/pic/index
                command.append('-fPIC')
            command.append(src)
            command.append('-o')

            if src.suffix in GccWrapper.ALLOWED_CODE_EXTENSIONS:
                src = src.with_suffix('o')
            else:
                self.logger.warning(f'Not allowed code file extension .{src.suffix} of file {src}. File ignored.')

            o_file_path = build_dir / src
            o_file_path.parent.mkdir(exist_ok=True, parents=True)

            command.append(str(o_file_path))
            o_files.append(o_file_path)

            result = run(command)
            if result.returncode:
                return result.returncode, []

        return 0, o_files

    def copy_headers(self, build_dir: Path, header_list: List[Path]):
        """
        Copy headers with ALLOWED_HEADER_EXTENSIONS to build_dir subdirectory 'headers'.
        Useful when building libraries
        :param build_dir: build directory
        :param header_list: list of headers to copy
        :return: Tuple of ret
        """
        headers_dir = build_dir / 'headers'
        for header in header_list:
            if header.suffix not in self.ALLOWED_HEADER_EXTENSIONS:
                self.logger.warning(f'Not allowed header file extension {header.suffix} of file {header}')
                continue

            file_path = headers_dir / header
            file_path.parent.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(str(header), str(file_path))

    def link(self, build_dir: Path, binary_type: BinaryType, out_name: str, o_files: List[Path], libraries: List[Path]) -> Tuple[int, Path]:
        """
        Link object files with libraries to file with out_name based name
        :param build_dir:
        :param binary_type:
        :param out_name:
        :param o_files:
        :param libraries:
        :return:
        """
        if binary_type is BinaryType.STATIC_LIBRARY:
            out_file = build_dir / self._resolve_out_name(binary_type, out_name)
            command = ['ar', '-rcs', out_file, *o_files]
            result = run(command)
            return result.returncode, out_file

        elif binary_type is BinaryType.DYNAMIC_LIBRARY:
            out_file = build_dir / self._resolve_out_name(binary_type, out_name)
            command = [self.binary, '-shared', *o_files, '-o', out_file]
            result = run(command)
            return result.returncode, out_file

        elif binary_type is BinaryType.EXECUTABLE:
            out_file = build_dir / self._resolve_out_name(binary_type, out_name)
            command = [self.binary, *o_files, '-o', out_file]

            library_dirs = set()
            library_names = set()
            for lib in libraries:
                library_dirs.add(lib.resolve().parent)
                library_names.add(lib.name)

            for library_dir in library_dirs:
                command.append(f'-L{library_dir}')
            for library_name in library_names:
                command.append(f'-l:{libray_name}')
            return call(command), out_file

        else:
            raise NotImplementedError(f'Unknown type {binary_type}')

    @staticmethod
    def _resolve_out_name(binary_type: BinaryType, name: str):
        if os.name is 'posix':
            if binary_type is BinaryType.STATIC_LIBRARY:
                return 'lib' + name + '.a'
            elif binary_type is BinaryType.DYNAMIC_LIBRARY:
                return 'lib' + name + '.so'
            elif binary_type is BinaryType.EXECUTABLE:
                return name
        else:
            if binary_type is BinaryType.STATIC_LIBRARY:
                return 'lib' + name + '.lib'
            elif binary_type is BinaryType.DYNAMIC_LIBRARY:
                return 'lib' + name + '.dll'
            elif binary_type is BinaryType.EXECUTABLE:
                return name + '.exe'
