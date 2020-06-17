from os import path
from setuptools import setup, find_packages


project_directory = path.abspath(path.dirname(__file__))


def load_from(file_name):
    with open(path.join(project_directory, file_name), encoding="utf-8") as f:
        return f.read()


setup(
    name="dogebuild-c",
    version=load_from("dogebuild_c/dogebuild_c.version").strip(),
    description="C language dogebuild plugin",
    long_description=load_from("README.md"),
    long_description_content_type="text/markdown",
    author="Kirill Sulim",
    author_email="kirillsulim@gmail.com",
    license="MIT",
    url="https://github.com/dogebuild/dogebuild-c",
    packages=find_packages(include=["dogebuild*",]),
    test_suite="tests",
    install_requires=["dogebuild",],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
    keywords="dogebuild builder",
)
