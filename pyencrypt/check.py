from importlib import abc
from importlib.machinery import ModuleSpec
from typing import Sequence, Union
import types
from importlib._bootstrap_external import _NamespacePath
from pathlib import Path
import os

_Path = Union[bytes, str]


class CheckFinder(abc.MetaPathFinder):
    def find_spec(self, fullname: str, path: Sequence[_Path],
                  target: types.ModuleType=None) -> ModuleSpec:
        if path:
            if isinstance(path, _NamespacePath):
                file_path = Path(
                    path._path[0]) / f'{fullname.rsplit(".",1)[-1]}.py'
            else:
                file_path = Path(path[0]) / f'{fullname.rsplit(".",1)[-1]}.py'
        else:
            file_path = f'{fullname}.py'
        if not os.path.exists(file_path):
            return None
        return None