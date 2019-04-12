from subprocess import call
from enum import Enum, unique, auto
from dogebuild.plugins import DogePlugin
import os
import shutil
from typing import List, Tuple


@unique
class BinaryType(Enum):
    STATIC_LIBRARY = auto()
    DYNAMIC_LIBRARY = auto()
    EXECUTABLE = auto()


class CPlugin(DogePlugin):
    NAME = 'c-plugin'

    ALLOWED_CODE_EXTENSIONS = [
        '.c',
    ]

    ALLOWED_HEADER_EXTENSIONS = [
        '.h',
    ]

    def __init__(self, **kwargs):
        super(CPlugin, self).__init__()

        self.add_task('compile', self.compile, phase='compile')

        self.add_task('link', self.link, phase='link')
        self.add_dependency('link', ['compile'])

        self.add_task('run', self.run, phase='run')
        self.add_dependency('run', ['link'])

        self.add_task('clean', self.clean, phase='clean')

        self.out = kwargs.get('out', 'a')
        self.src = kwargs.get('src')
        self.headers = kwargs.get('headers', [])
        self.type = kwargs.get('type', BinaryType.STATIC_LIBRARY)
        self.build_dir = kwargs.get('build_dir', 'build')
        self.o_files = []

    def compile(self) -> int:
        code, o_files = self._compile(self.build_dir, self.src, self.type)
        if code:
            return code
        else:
            self.o_files = o_files
            return 0

    def link(self) -> int:
        code = self._link(self.build_dir, self.o_files, self.out, self.type)
        if code:
            return code

        if self.type in [BinaryType.STATIC_LIBRARY, BinaryType.DYNAMIC_LIBRARY]:
            self._copy_header(self.build_dir, self.headers)

        return 0

    def run(self) -> int:
        if self.type is BinaryType.EXECUTABLE:
            out_file = os.path.join('.', self.build_dir, CPlugin._resolve_out_name(self.type, self.out))
            command = [out_file]
            return call(command)
        else:
            print('Type {} is not executable'.format(self.type))
            return 1

    def clean(self):
        shutil.rmtree(self.build_dir)

    @staticmethod
    def _compile(build_dir: str, src_list: List[str], type: BinaryType) -> Tuple[int, List[str]]:
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        command = ['gcc']

        o_files = []

        for src in src_list:
            command.append('-c')
            if type is BinaryType.DYNAMIC_LIBRARY:
                # Need to create macros in binary code.
                # See https://renenyffenegger.ch/notes/development/languages/C-C-plus-plus/GCC/options/f/pic/index
                command.append('-fPIC')
            command.append(src)
            command.append('-o')

            base, extension = os.path.splitext(src)

            if extension in CPlugin.ALLOWED_CODE_EXTENSIONS:
                src = base + '.o'
            else:
                print('Warn: not allowed code file extension {} in file {}'.format(extension, src))

            file_path = os.path.join(build_dir, src)
            CPlugin._ensure_directory_exists(file_path)

            command.append(file_path)
            o_files.append(file_path)

        return call(command), o_files

    @staticmethod
    def _copy_header(build_dir: str, header_list: List[str]):
        for header in header_list:
            base, extension = os.path.splitext(header)
            if extension not in CPlugin.ALLOWED_HEADER_EXTENSIONS:
                print('Warn: not allowed header file extension {} in file {}'.format(extension, header))

            file_path = os.path.join(build_dir, 'headers', header)
            CPlugin._ensure_directory_exists(file_path)

            shutil.copyfile(header, file_path)

    @staticmethod
    def _link(build_dir: str, o_files: List[str], out_name: str, type: BinaryType) -> int:
        if type is BinaryType.STATIC_LIBRARY:
            out_file = os.path.join(build_dir, CPlugin._resolve_out_name(type, out_name))
            command = ['ar', '-rcs', out_file, *o_files]
            return call(command)

        elif type is BinaryType.DYNAMIC_LIBRARY:
            out_file = os.path.join(build_dir, CPlugin._resolve_out_name(type, out_name))
            command = ['gcc', '-shared', *o_files, '-o', out_file]
            return call(command)

        elif type is BinaryType.EXECUTABLE:
            out_file = os.path.join(build_dir, CPlugin._resolve_out_name(type, out_name))
            command = ['gcc', *o_files, '-o', out_file]
            return call(command)

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

    @staticmethod
    def _ensure_directory_exists(file_path: str):
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

