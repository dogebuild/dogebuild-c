import nox
import os


LINE_LENGTH = 120

STYLE_TARGETS = [
    "dogebuild_c",
    "integration_tests",
    "noxfile.py",
    "setup.py",
]

FLAKE8_IGNORE = [
    "E203",
    "E231",
    "W503",
]


@nox.session()
@nox.parametrize(
    "directory",
    ["simple_static_library", "simple_dinamic_library", "simple_executable", "executable_with_dependency/main",],
)
def tests(session, directory):

    session.install("../dogebuild")  # Parametrize after releasing stable version of main dogebuild tool
    session.install(".")

    session.cd(os.path.join("integration_tests", directory))
    session.run("doge", "run")


@nox.session
def style(session):
    session.install("flake8", "black", "isort")

    session.run("black", "--version")
    session.run("black", "--check", "--target-version", "py38", "--line-length", f"{LINE_LENGTH}", *STYLE_TARGETS)

    session.run("flake8", "--version")
    session.run(
        "flake8",
        "--max-line-length",
        f"{LINE_LENGTH}",
        "--extend-ignore",
        ",".join(FLAKE8_IGNORE),
        "--show-source",
        *STYLE_TARGETS,
    )
