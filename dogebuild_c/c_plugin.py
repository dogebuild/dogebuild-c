from subprocess import call
import os
import shutil
from typing import List, Tuple, Dict

from dogebuild.plugins import DogePlugin
from dogebuild.common import files
from dogebuild_c.gcc_wrapper import GccWrapper, BinaryType


class CPlugin(DogePlugin):
    NAME = 'c-plugin'

    def __init__(self, **kwargs):
        super(CPlugin, self).__init__()

        self.gcc = GccWrapper()

        self.add_task('compile', self.compile, phase='sources')

        self.add_task('test', self.test, phase='test')
        self.add_dependency('test', ['compile'])

        self.add_task('link', self.link, phase='build')
        self.add_dependency('link', ['test'])

        self.add_task('run', self.run, phase='run')
        self.add_dependency('run', ['link'])

        self.add_task('clean', self.clean, phase='clean')

        self.src_dir = kwargs.get('src_dir', 'src')
        self.src = files(self.src_dir, kwargs.get('src', []), kwargs.get('src_exclude'))
        self.headers = files(self.src_dir, kwargs.get('headers', []), kwargs.get('headers_exclude'))
        self.out = kwargs.get('out', 'a')
        self.out_file = None
        self.type = kwargs.get('type', BinaryType.STATIC_LIBRARY)
        self.build_dir = kwargs.get('build_dir', 'build')

        self.test_src_dir = kwargs.get('test_src_dir', 'test')
        self.test_main_exclude = files(self.src_dir, kwargs.get('test_main_exclude', []))
        self.test_src = files(self.test_src_dir, kwargs.get('test_src', []), kwargs.get('test_src_exclude'))
        self.test_headers = files(self.test_src_dir, kwargs.get('test_headers', []), kwargs.get('test_headers_exclude'))
        self.test_out = kwargs.get('test_out', 'test')
        self.test_build_dir = kwargs.get('test_build_dir', 'test_build')

        self.o_files = []

    def compile(self) -> Tuple[int, Dict[str, List[str]]]:
        dependencies_headers = []
        for dependency in self.dependencies + self.test_dependencies:
            dependencies_headers += map(
                lambda p: os.path.join(dependency.folder, p),
                dependency.artifacts.get('headers_directory', [])
            )

        code, o_files = self.gcc.compile(self.build_dir, self.type, self.src, dependencies_headers)
        if code:
            return code, {}
        else:
            self.o_files = o_files
            return 0, {'o_files': o_files}

    def test(self) -> Tuple[int, Dict[str, List[str]]]:
        if len(self.test_src) == 0:
            return 0, {}

        self.gcc.copy_header(self.build_dir, self.headers)

        dependencies_headers = []
        for dependency in self.dependencies + self.test_dependencies:
            dependencies_headers += map(lambda p: os.path.join(dependency.folder, p), dependency.artifacts.get('headers_directory', []))

        dependencies_library = []
        for dependency in self.dependencies + self.test_dependencies:
            dependencies_library += map(lambda p: os.path.join(dependency.folder, p), dependency.artifacts.get('static_library', []))

        code, test_o_files = self.gcc.compile(self.test_build_dir, BinaryType.EXECUTABLE, self.test_src, [os.path.join(self.build_dir, 'headers')] + dependencies_headers)
        if code:
            return code, {}

        # Fixme
        exclude_o_files = []
        for src in self.src:
            if src in self.test_main_exclude:
                base, extension = os.path.splitext(src)
                if extension in GccWrapper.ALLOWED_CODE_EXTENSIONS:
                    src = base + '.o'
                file_path = os.path.join(self.build_dir, src)
                exclude_o_files.append(file_path)

        code, test_out_file = self.gcc.link(self.test_build_dir, BinaryType.EXECUTABLE, self.test_out, list(set(self.o_files) - set(exclude_o_files)) + test_o_files, dependencies_library)
        if code:
            return code, {}

        return call([test_out_file]), {'test_executable': [test_out_file]}

    def link(self) -> Tuple[int, Dict[str, List[str]]]:
        libs = []
        if self.type is BinaryType.EXECUTABLE:
            for dependency in self.dependencies + self.test_dependencies:
                libs += map(
                    lambda p: os.path.join(dependency.folder, p),
                    dependency.artifacts.get('static_library', [])
                )

        code, out_file = self.gcc.link(self.build_dir, self.type, self.out, self.o_files, libs)
        if code:
            return code, {}

        self.out_file = out_file

        headers_directory = []
        if self.type in [BinaryType.STATIC_LIBRARY, BinaryType.DYNAMIC_LIBRARY]:
            _, headers_directory = self.gcc.copy_header(self.build_dir, self.headers)

        if self.type is BinaryType.EXECUTABLE:
            artifact = {'executable': [out_file]}
        elif self.type is BinaryType.STATIC_LIBRARY:
            artifact = {'static_library': [out_file]}
        elif self.type is BinaryType.DYNAMIC_LIBRARY:
            artifact = {'dynamic_library': [out_file]}
        else:
            raise NotImplementedError()

        return 0, dict(artifact, headers_directory=[headers_directory])

    def run(self) -> Tuple[int, Dict[str, List[str]]]:
        if self.type is BinaryType.EXECUTABLE:
            command = [self.out_file]
            return call(command), {'executable': [self.out_file]}
        else:
            self.logger.warning('Type {} is not executable'.format(self.type))
            return 0, {}

    def clean(self) -> Tuple[int, Dict[str, List[str]]]:
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        if os.path.exists(self.test_build_dir):
            shutil.rmtree(self.test_build_dir)

        return 0, {}
