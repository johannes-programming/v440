import argparse
import os
from collections.abc import Iterable
from pathlib import Path
import glob

__all__ = ["main", "run"]

def get_absfiles(filepatterns: Iterable[str]) -> list[str]:
    absfile: str
    absfiles: list[str]
    file: str
    pattern: str
    absfiles = list()
    for pattern in filepatterns:
        for file in glob.iglob(pattern, recursive=True):
            absfile = os.path.abspath(file)
            if absfile in absfiles:
                continue
            if os.path.isfile(absfile):
                absfiles.append(absfile)
    return absfiles

def main(args:list[str] = None, /) -> None:
    parser:argparse.ArgumentParser
    parser=argparse.ArgumentParser(fromfile_prefix_chars="@")
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("filepatterns", default=[], nargs="*")
    kwargs = vars(parser.parse_args(args))
    run(*kwargs.pop("filepatterns"), **kwargs)

def run(*filepatterns:str, reverse:bool=False) -> None:
    absfiles:list[str]
    absfiles=get_absfiles(filepatterns)
    for absfile in absfiles:
        sort_lines_in_file(absfile, reverse=reverse)

def sort_lines_in_file(file_path: str, *, reverse: bool = False) -> None:
    path = Path(file_path)
    with path.open("r") as file:
        lines = file.readlines()
    lines.sort(reverse=reverse)
    with path.open("w") as file:
        file.writelines(lines)