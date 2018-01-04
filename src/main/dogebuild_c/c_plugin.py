from dogebuild.plugin.interfaces import Plugin
from dogebuild_c.tasks import CompileTask


class CPlugin(Plugin):
    def __init__(
            self,
            sources,
            out_name=None,
    ):
        self.sources = sources
        self.out_name = out_name

    def get_active_tasks(self):
        return [
            CompileTask(
                sources=self.sources,
                out_file=self.out_name,
            ),
        ]


