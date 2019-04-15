from subprocess import call
from enum import Enum, unique, auto
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

    def compile(self, build_dir: str, type: BinaryType, src_list: List[str], headers_dirs: List[str]) -> Tuple[int, List[str]]:
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        o_files = []

        for src in src_list:
            command = ['gcc', '-c']

            for header_dir in headers_dirs:
                command.append('-I{}'.format(header_dir))

            if type is BinaryType.DYNAMIC_LIBRARY:
                # Need to create macros in binary code.
                # See https://renenyffenegger.ch/notes/development/languages/C-C-plus-plus/GCC/options/f/pic/index
                command.append('-fPIC')
            command.append(src)
            command.append('-o')

            base, extension = os.path.splitext(src)

            if extension in GccWrapper.ALLOWED_CODE_EXTENSIONS:
                src = base + '.o'
            else:
                print('Warn: not allowed code file extension {} in file {}'.format(extension, src))

            file_path = os.path.join(build_dir, src)
            _ensure_directory_exists(file_path)

            command.append(file_path)
            o_files.append(file_path)

            code = call(command)
            if code:
                return code, []

        return 0, o_files

    def copy_header(self, build_dir: str, header_list: List[str]) -> Tuple[int, str]:
        headers_dir = os.path.join(build_dir, 'headers')
        for header in header_list:
            base, extension = os.path.splitext(header)
            if extension not in self.ALLOWED_HEADER_EXTENSIONS:
                print('Warn: not allowed header file extension {} in file {}'.format(extension, header))

            file_path = os.path.join(headers_dir, header)
            _ensure_directory_exists(file_path)

            shutil.copyfile(header, file_path)

        return 0, headers_dir

    def link(self, build_dir: str, type: BinaryType, out_name: str, o_files: List[str], libs: List[str]) -> Tuple[int, str]:
        if type is BinaryType.STATIC_LIBRARY:
            out_file = os.path.join(build_dir, self._resolve_out_name(type, out_name))
            command = ['ar', '-rcs', out_file, *o_files]
            return call(command), out_file

        elif type is BinaryType.DYNAMIC_LIBRARY:
            out_file = os.path.join(build_dir, self._resolve_out_name(type, out_name))
            command = ['gcc', '-shared', *o_files, '-o', out_file]
            return call(command), out_file

        elif type is BinaryType.EXECUTABLE:
            out_file = os.path.join(build_dir, self._resolve_out_name(type, out_name))
            command = ['gcc', *o_files, '-o', out_file]
            for lib in libs:
                ps = os.path.abspath(lib)
                dr = os.path.dirname(ps)
                bn = os.path.basename(ps)
                command.append('-L{}'.format(dr))
                command.append('-l:{}'.format(bn))
            return call(command), out_file

        else:
            raise NotImplementedError('Unknown type {}'.format(type))

    @staticmethod
    def _resolve_out_name(type: BinaryType, name: str):
        if os.name is 'posix':
            if type is BinaryType.STATIC_LIBRARY:
                return 'lib' + name + '.a'
            elif type is BinaryType.DYNAMIC_LIBRARY:
                return 'lib' + name + '.so'
            elif type is BinaryType.EXECUTABLE:
                return name
        else:
            if type is BinaryType.STATIC_LIBRARY:
                return 'lib' + name + '.lib'
            elif type is BinaryType.DYNAMIC_LIBRARY:
                return 'lib' + name + '.dll'
            elif type is BinaryType.EXECUTABLE:
                return name + '.exe'


def _ensure_directory_exists(file_path: str):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
