import os
import sys
import types
from importlib import abc
from importlib.machinery import ModuleSpec
import importlib.util
from pathlib import Path
from typing import Sequence, Union
from pyencrypt.decrypt import *
import traceback

_Path = Union[bytes, str]
sys.dont_write_bytecode = True

PRIVATE_KEY = ''
CIPHER_KEY = ''

PRIVATE_N,PRIVATE_D = PRIVATE_KEY.split('O',1)
AES_KEY = decrypt_key(CIPHER_KEY, int(PRIVATE_N), int(PRIVATE_D))

class EncryptFileLoader(abc.SourceLoader):
    def __init__(self,path) -> None:
        self.path = path or ''

    def get_filename(self, fullname: str) -> _Path:
        return f"{fullname.rsplit('.',1)[-1]}.pye"

    def get_data(self, path: _Path) -> bytes:
        try:
            return decrypt_file(Path(self.path),AES_KEY)
        except Exception:
            traceback.print_exc()
            return b''


class EncryptFileFinder(abc.MetaPathFinder):
    def find_spec(self, fullname: str, path: Sequence[_Path], target: types.ModuleType = None) -> ModuleSpec:
        if path:
            file_path = Path(path[0]) / f'{fullname.rsplit(".",1)[-1]}.pye'
        else:
            file_path = f'{fullname}.pye'
        if not os.path.exists(file_path):
            return None
        loader = EncryptFileLoader(file_path)
        return importlib.util.spec_from_loader(name=fullname, loader=loader, origin='origin-encrypt')


sys.meta_path.append(EncryptFileFinder())
