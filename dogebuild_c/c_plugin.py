from subprocess import run
import shutil
from typing import List, Tuple, Dict, Union
from pathlib import Path

from dogebuild.plugins import DogePlugin
from dogebuild_c.gcc_wrapper import GccWrapper, BinaryType


class CPlugin(DogePlugin):
    NAME = "c-plugin"

    def __init__(
        self,
        *,
        src: List[Union[Path, str]],
        headers: List[Union[Path, str]] = None,
        src_dir: Union[Path, str] = "src",
        binary_type: BinaryType = BinaryType.STATIC_LIBRARY,
        out_name: str = "a",
        build_dir: Union[Path, str] = Path("build"),
        test_src: List[Union[Path, str]] = None,
        test_headers: List[Union[Path, str]] = None,
        test_out_name: str = "test",
        test_build_dir: Union[Path, str] = Path("test_build"),
        test_src_exclude: List[Union[Path, str]] = None,
    ):
        super(CPlugin, self).__init__(artifacts_to_publish=CPlugin.binary_type_to_artifacts_list(binary_type))

        self.gcc = GccWrapper()

        self.add_task(self.compile, phase="sources")
        self.add_task(self.test, phase="test", depends=["compile"])
        self.add_task(self.link, phase="build", depends=["test"])
        self.add_task(self.run, phase="run", depends=["link"])
        self.add_task(self.clean, phase="clean")

        self.src = list(map(lambda x: Path(x).resolve(), src))
        self.headers = list(map(lambda x: Path(x).resolve(), headers if headers is not None else []))
        self.src_dir = Path(src_dir).resolve()
        self.binary_type = binary_type
        self.out_name = out_name
        self.build_dir = Path(build_dir)

        self.test_src = list(map(lambda x: Path(x).resolve(), test_src if test_src is not None else []))
        self.test_headers = list(map(lambda x: Path(x).resolve(), test_headers if test_headers is not None else []))
        self.test_out_name = test_out_name
        self.test_build_dir = Path(test_build_dir).resolve()
        self.test_src_exclude = list(
            map(lambda x: Path(x).resolve(), test_src_exclude if test_src_exclude is not None else [])
        )

    def compile(self, headers_directory) -> Tuple[int, Dict[str, List[Path]]]:
        code, o_files = self.gcc.compile(self.build_dir, self.binary_type, self.src, headers_directory)
        if code:
            return code, {}
        else:
            return 0, {"o_files": o_files}

    def test(self, o_files, headers_directory, static_library) -> Tuple[int, Dict[str, List[Path]]]:
        if len(self.test_src) == 0:
            return 0, {}

        self.gcc.copy_headers(self.src_dir, self.headers, self.build_dir)
        code, test_o_files = self.gcc.compile(
            self.test_build_dir, BinaryType.EXECUTABLE, self.test_src, [self.build_dir / "headers"] + headers_directory
        )
        if code:
            return code, {}

        # Fixme
        exclude_o_files = []
        for src in self.src:
            if src in self.test_src_exclude:
                if src.suffix in GccWrapper.ALLOWED_CODE_EXTENSIONS:
                    file_path = self.build_dir / src.with_suffix(".o")
                    exclude_o_files.append(file_path)

        code, test_out_file = self.gcc.link(
            self.test_build_dir,
            BinaryType.EXECUTABLE,
            self.test_out_name,
            list(set(o_files) - set(exclude_o_files)) + test_o_files,
            static_library,
        )
        if code:
            return code, {}

        result = run([str(test_out_file)])
        return result.returncode, {"test_executable": [test_out_file]}

    def link(self, o_files, static_library) -> Tuple[int, Dict[str, List[Path]]]:
        libs = []
        if self.binary_type is BinaryType.EXECUTABLE:
            libs += static_library

        code, out_file = self.gcc.link(self.build_dir, self.binary_type, self.out_name, o_files, libs)
        if code:
            return code, {}

        if self.binary_type in [BinaryType.STATIC_LIBRARY, BinaryType.DYNAMIC_LIBRARY]:
            self.gcc.copy_headers(self.src_dir, self.headers, self.build_dir)

        if self.binary_type is BinaryType.EXECUTABLE:
            artifact = {"executable": [out_file.resolve()]}
        elif self.binary_type is BinaryType.STATIC_LIBRARY:
            artifact = {"static_library": [out_file.resolve()]}
        elif self.binary_type is BinaryType.DYNAMIC_LIBRARY:
            artifact = {"dynamic_library": [out_file.resolve()]}
        else:
            raise NotImplementedError()

        return 0, dict(artifact, headers_directory=[(self.build_dir / "headers").resolve()])

    def run(self, executable) -> Tuple[int, Dict[str, List[Path]]]:
        if self.binary_type is BinaryType.EXECUTABLE:
            result = run([str(executable[0])])
            return result.returncode, {}
        else:
            self.logger.warning(f"Type {self.binary_type} is not executable")
            return 0, {}

    def clean(self) -> Tuple[int, Dict[str, List[str]]]:
        if self.build_dir.exists() and self.build_dir.is_dir():
            shutil.rmtree(self.build_dir)
        if self.test_build_dir.exists() and self.test_build_dir.is_dir():
            shutil.rmtree(self.test_build_dir)

        return 0, {}

    @staticmethod
    def binary_type_to_artifacts_list(binary_type: BinaryType):
        if binary_type is BinaryType.EXECUTABLE:
            return ["executable"]
        elif binary_type is BinaryType.STATIC_LIBRARY:
            return ["static_library", "headers_directory"]
        elif binary_type is BinaryType.DYNAMIC_LIBRARY:
            return ["dynamic_library", "headers_directory"]
        else:
            raise Exception(f"Unknown binary type {binary_type}")
