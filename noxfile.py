import nox
import os


@nox.session()
@nox.parametrize(
    'directory',
    [
        'simple_static_library',
        'simple_dinamic_library',
        'simple_executable',
        'executable_with_dependency/main',
    ]
)
def tests(session, directory):

    session.install('../dogebuild')  # Parametrize after releasing stable version of main dogebuild tool
    session.install('.')

    session.cd(os.path.join('integration_tests', directory))
    session.run('doge', 'run')
