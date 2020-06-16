from setuptools import setup, find_packages

setup(
    name="dogebuild-c",
    version="0.1.0",
    description="C language dogebuild plugin",
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
