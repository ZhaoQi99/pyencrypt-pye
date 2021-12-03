import os
import sys
import traceback
import types
from importlib import abc
from importlib._bootstrap_external import _NamespacePath
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_loader
from pathlib import Path
from typing import Iterable, Sequence, Union

from pyencrypt.decrypt import *

_Path = Union[bytes, str]
sys.dont_write_bytecode = True


class Base:
    def __dir__(self) -> Iterable[str]:
        return []


class EncryptFileLoader(abc.SourceLoader, Base):
    def __init__(self, path) -> None:
        self.path = path or ''
        self.__private_key = ''
        self.__cipher_key = ''

    def get_filename(self, fullname: str) -> str:
        return self.path

    def get_data(self, path: _Path) -> bytes:
        try:
            __n, __d = self.__private_key.split('O', 1)
            return decrypt_file(
                Path(path), decrypt_key(self.__cipher_key, int(__n), int(__d)))
        except Exception:
            traceback.print_exc()
            return b''


class EncryptFileFinder(abc.MetaPathFinder, Base):
    def find_spec(self,
                  fullname: str,
                  path: Sequence[_Path],
                  target: types.ModuleType = None) -> ModuleSpec:
        if path:
            if isinstance(path, _NamespacePath):
                file_path = Path(
                    path._path[0]) / f'{fullname.rsplit(".",1)[-1]}.pye'
            else:
                file_path = Path(path[0]) / f'{fullname.rsplit(".",1)[-1]}.pye'
        else:
            file_path = Path(f'{fullname}.pye')
        file_path = file_path.absolute().as_posix()
        if not os.path.exists(file_path):
            return None
        loader = EncryptFileLoader(file_path)
        return spec_from_loader(name=fullname,
                                loader=loader,
                                origin='origin-encrypt')


# TODO: generate randomly AES Class
sys.meta_path.append(EncryptFileFinder())
