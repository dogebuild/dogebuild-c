from subprocess import call
from enum import Enum, unique, auto
from dogebuild.plugins import DogePlugin
import os
import shutil


@unique
class BinaryType(Enum):
    STATIC_LIBRARY = auto()
    DYNAMIC_LIBRARY = auto()
    EXECUTABLE = auto()


class CPlugin(DogePlugin):
    NAME = 'c-plugin'

    def __init__(self, **kwargs):
        super(CPlugin, self).__init__()

        self.add_task('compile', self.compile, phase='compile')

        self.add_task('run', self.run, phase='run')
        self.add_dependency('run', ['compile'])

        self.add_task('clean', self.clean, phase='clean')

        self.out = kwargs.get('out', 'a')
        self.src = kwargs.get('src')
        self.headers = kwargs.get('headers', [])
        self.type = kwargs.get('type', BinaryType.STATIC_LIBRARY)
        self.build_dir = kwargs.get('build_dir', 'build')

    def compile(self) -> int:

        if not os.path.exists(self.build_dir):
            os.mkdir(self.build_dir)

        if self.type is BinaryType.STATIC_LIBRARY:
            command = ['gcc']

            o_files = []

            for src in self.src:
                command.append('-c')
                command.append(src)
                command.append('-o')

                if src.endswith('.c'):
                    src = src[:-2] + '.o'

                file_path = os.path.join(self.build_dir, src)
                dir_path = os.path.dirname(file_path)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                command.append(file_path)
                o_files.append(file_path)

            code = call(command)
            if code:
                return code

            out_file = os.path.join(self.build_dir, CPlugin._resolve_out_name(self.type, self.out))
            command = ['ar', '-rcs', out_file, *o_files]
            code = call(command)
            if code:
                return code

            for header in self.headers:
                file_path = os.path.join(self.build_dir, 'headers', header)
                dir_path = os.path.dirname(file_path)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                shutil.copyfile(header, file_path)

            return 0

        elif self.type is BinaryType.DYNAMIC_LIBRARY:
            command = ['gcc']

            o_files = []

            for src in self.src:
                command.append('-c')
                command.append('-fPIC')  # Need to create macros in binary code. See https://renenyffenegger.ch/notes/development/languages/C-C-plus-plus/GCC/options/f/pic/index
                command.append(src)
                command.append('-o')

                if src.endswith('.c'):
                    src = src[:-2] + '.o'

                file_path = os.path.join(self.build_dir, src)
                dir_path = os.path.dirname(file_path)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                command.append(file_path)
                o_files.append(file_path)

            code = call(command)
            if code:
                return code

            out_file = os.path.join(self.build_dir, CPlugin._resolve_out_name(self.type, self.out))
            command = ['gcc', '-shared', *o_files, '-o', out_file]
            code = call(command)
            if code:
                return code

            for header in self.headers:
                file_path = os.path.join(self.build_dir, 'headers', header)
                dir_path = os.path.dirname(file_path)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                shutil.copyfile(header, file_path)

            return 0

        elif self.type is BinaryType.EXECUTABLE:
            out_file = os.path.join(self.build_dir, CPlugin._resolve_out_name(self.type, self.out))
            command = ['gcc', *self.src, '-o', out_file]
            return call(command)
        else:
            raise NotImplementedError('Unknown type {}'.format(self.type))

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
