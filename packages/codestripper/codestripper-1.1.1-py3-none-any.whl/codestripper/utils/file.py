import glob
import os
import logging
from pathlib import Path
from typing import Dict, Generator, Iterable, Set, Union, List


def get_working_directory(working_directory: Union[str, None]) -> str:
    if working_directory is not None:
        if os.path.isabs(working_directory):
            cwd = working_directory
        else:
            cwd = str(os.path.join(os.getcwd(), working_directory))
        Path(cwd).relative_to(os.getcwd())
        return cwd
    else:
        return os.getcwd()


class FileUtils:
    def __init__(self,
                 included: Iterable[str],
                 excluded: Union[Iterable[str], None] = None,
                 working_directory: Union[str, None] = None,
                 recursive: bool = True,
                 logger: str = "codestripper"
                 ) -> None:
        self.logger = logging.getLogger(f"{logger}.fileutils")
        self.included = included
        if excluded is None:
            self.excluded: Iterable[str] = []
        else:
            self.excluded = excluded
        self.recursive = recursive
        self.old_cwd = os.getcwd()
        self.cwd = get_working_directory(working_directory)

    def __get_normalized_files(self, file_names: Iterable[str], relative_to: Path, recursive=True) -> \
            Generator[str, None, None]:
        for file_name in file_names:
            path = os.path.join(self.cwd, file_name)
            for file in glob.glob(path, recursive=recursive):
                tmp = Path(file).relative_to(relative_to)
                if tmp.is_file():
                    yield str(tmp)

    def __convert_to_paths_set(self, file_names: Iterable[str], recursive=True) -> Set[str]:
        """Convert the file name(s) that are passed as CLI arguments to file paths (can contain GLOB)"""
        files = set()
        for file in self.__get_normalized_files(file_names, Path(self.cwd), recursive):
            files.add(file)
        return files

    def get_matching_files(self) -> Iterable[str]:
        """Get files that fulfill requirements, match included and do not match excluded"""
        os.chdir(self.cwd)
        included_files = self.__convert_to_paths_set(self.included, self.recursive)
        self.logger.debug(f"Included files are: {included_files}")

        excluded_files = self.__convert_to_paths_set(self.excluded, self.recursive)
        self.logger.debug(f"Excluded files are: {excluded_files}")
        os.chdir(self.old_cwd)
        return included_files - excluded_files
