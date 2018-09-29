from dogebuild.plugins import DogePlugin, DagContext


DAG_CONTEXT = DagContext()


class CPlugin(DogePlugin):
    NAME = 'c-plugin'

    def __init__(self):
        super(CPlugin, self).__init__(
            {
                'compile': self.compile,
            },
            DAG_CONTEXT
        )

    @DAG_CONTEXT.depends_on('nothong')
    def compile(self) -> int:
        print('hello from c-plugin')
        return 1

