import nox
import os


@nox.session(python=['3.6'])
@nox.parametrize(
    'directory',
    [
        'simple_static_library',
        'simple_dinamic_library',
        'simple_executable',
    ]
)
def tests(session, directory):

    session.install('../dogebuild')  # Parametrize after releasing stable version of main dogebuild tool
    session.install('.')

    session.cd(os.path.join('integration_tests', directory))
    session.run('doge', 'run_plugin', 'run')
