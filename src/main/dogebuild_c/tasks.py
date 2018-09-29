from subprocess import check_call

from dogebuild.plugin_old.interfaces import Task


class CompileTask(Task):
    def __init__(self, sources, out_file=None):
        self.input_files = sources
        self.out_file = out_file

    def run(self):
        command = ['clang']
        command.extend(self.input_files)
        if self.out_file:
            command.append('--output=' + self.out_file)

        check_call(command)

