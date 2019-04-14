from subprocess import call
from dogebuild.plugins import DogePlugin
import os
import shutil
from typing import List, Tuple

from dogebuild_c.gcc_wrapper import GccWrapper, BinaryType


class CPlugin(DogePlugin):
    NAME = 'c-plugin'

    def __init__(self, **kwargs):
        super(CPlugin, self).__init__()

        self.gcc = GccWrapper()

        self.add_task('compile', self.compile, phase='compile')

        self.add_task('test', self.test, phase='test')
        self.add_dependency('test', ['compile'])

        self.add_task('link', self.link, phase='link')
        self.add_dependency('link', ['test'])

        self.add_task('run', self.run, phase='run')
        self.add_dependency('run', ['link'])

        self.add_task('clean', self.clean, phase='clean')

        self.out = kwargs.get('out', 'a')
        self.out_file = None
        self.test_out = kwargs.get('test_out', 'test')
        self.src = kwargs.get('src')
        self.headers = kwargs.get('headers', [])
        self.test_src = kwargs.get('test_src', [])
        self.type = kwargs.get('type', BinaryType.STATIC_LIBRARY)
        self.build_dir = kwargs.get('build_dir', 'build')
        self.test_build_dir = kwargs.get('test_build_dir', 'test_build')
        self.o_files = []
        self.test_exclude = kwargs.get('test_exclude', [])

    def compile(self) -> int:
        code, o_files = self.gcc.compile(self.build_dir, self.type, self.src, [])
        if code:
            return code
        else:
            self.o_files = o_files
            return 0

    def test(self) -> int:
        if len(self.test_src) == 0:
            return 0

        self.gcc.copy_header(self.build_dir, self.headers)

        code, test_o_files = self.gcc.compile(self.test_build_dir, BinaryType.EXECUTABLE, self.test_src, [os.path.join(self.build_dir, 'headers')])
        if code:
            return code

        # Fixme
        exclude_o_files = []
        for src in self.src:
            if src in self.test_exclude:
                base, extension = os.path.splitext(src)
                if extension in GccWrapper.ALLOWED_CODE_EXTENSIONS:
                    src = base + '.o'
                file_path = os.path.join(self.build_dir, src)
                exclude_o_files.append(file_path)

        code, test_out_file = self.gcc.link(self.test_build_dir, list(set(self.o_files) - set(exclude_o_files)) + test_o_files, self.test_out, BinaryType.EXECUTABLE)
        if code:
            return code

        return call([test_out_file])

    def link(self) -> int:
        code, out_file = self.gcc.link(self.build_dir, self.o_files, self.out, self.type)
        if code:
            return code

        self.out_file = out_file

        if self.type in [BinaryType.STATIC_LIBRARY, BinaryType.DYNAMIC_LIBRARY]:
            self.gcc.copy_header(self.build_dir, self.headers)

        return 0

    def run(self) -> int:
        if self.type is BinaryType.EXECUTABLE:
            command = [self.out_file]
            return call(command)
        else:
            print('Type {} is not executable'.format(self.type))
            return 0

    def clean(self):
        shutil.rmtree(self.build_dir)
        shutil.rmtree(self.test_build_dir)
