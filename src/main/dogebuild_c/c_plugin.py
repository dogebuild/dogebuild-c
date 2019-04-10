from subprocess import call
from enum import Enum, unique, auto
from dogebuild.plugins import DogePlugin
import os


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

        self.out = kwargs.get('out', 'a')
        self.src = kwargs.get('src')
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

            command = ['ar', '-rcs', CPlugin._resolve_out_name(self.type, self.out), *o_files]

            return call(command)

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

            command = ['gcc', '-shared', *o_files, '-o', CPlugin._resolve_out_name(self.type, self.out)]

            return call(command)
        elif self.type is BinaryType.EXECUTABLE:
            command = ['gcc', '-o', CPlugin._resolve_out_name(self.type, self.out), *self.src]
            return call(command)
        else:
            raise NotImplementedError('Unknown type {}'.format(self.type))

    def run(self) -> int:
        if self.type is BinaryType.EXECUTABLE:
            command = ['./' + CPlugin._resolve_out_name(self.type, self.out)]
            return call(command)
        else:
            print('Type {} is not executable'.format(self.type))
            return 1

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
