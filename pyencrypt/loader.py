import linecache
import os
import sys
import types
from importlib import abc, machinery
from importlib._bootstrap_external import _NamespacePath
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_loader
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

from pyencrypt.decrypt import decrypt_file, decrypt_key
from pyencrypt.license import check_license

_Path = Union[bytes, str]
sys.dont_write_bytecode = True

ENCRYPT_SUFFIX = ".pye"


def __dir__():
    return []


class Base:
    def __dir__(self) -> Iterable[str]:
        return []


def _make_key_provider(
    priv_shards=None,
    priv_seed=0,
    cipher_shards=None,
    cipher_seed=0,
):
    if not priv_shards or not cipher_shards:
        return lambda: None

    def _reassemble_key(shards, seed):
        out = bytearray()
        for idx, shard in enumerate(shards):
            mask = (seed + idx * 31) & 0xFF
            out.extend(b ^ mask for b in shard)
        return out.decode("utf-8")

    private_key = _reassemble_key(priv_shards, priv_seed)
    cipher_key = _reassemble_key(cipher_shards, cipher_seed)
    __n, __d = private_key.split("O", 1)
    aes_key = decrypt_key(cipher_key, int(__d), int(__n))

    del private_key, cipher_key, priv_shards, cipher_shards

    def _get_key():
        return aes_key

    return _get_key


def _build_loader_class(_get_key):

    class EncryptFileImporter(abc.MetaPathFinder, abc.Loader, Base):
        POSSIBLE_PATH = [
            Path(os.path.expanduser("~")) / ".licenses" / "license.lic",
            Path(os.path.abspath(__file__)).parent / "licenses" / "license.lic",
            Path(os.getcwd()) / "licenses" / "license.lic",
        ]

        def __init__(self, path) -> None:
            self.path = path or ""
            self.license = None
            self.license_path = None
            self._init_license_path()
            self.check()

        def _init_license_path(self) -> None:
            if self.license is False:
                return
            for path in self.POSSIBLE_PATH:
                if path.exists():
                    self.license_path = path
                    break

        def check(self) -> bool:
            if self.license is False:
                return False

            if self.license_path is None:
                raise Exception("Could not find license file.")

            check_license(self.license_path, _get_key())
            return True

        def get_filename(self, fullname: str) -> str:
            return self.path

        def get_source(self, fullname: str):
            return None

        def get_data(self, path: _Path) -> bytes:
            try:
                return Path(path).read_bytes()
            except Exception:
                return b""

        def exec_module(self, module: types.ModuleType) -> None:
            source = None
            try:
                source = bytearray(decrypt_file(Path(self.path), _get_key()))
                code = compile(bytes(source), self.path, "exec")
            except Exception:
                raise ImportError(f"Cannot load encrypted module: {self.path}")
            finally:
                if source is not None:
                    for _i in range(len(source)):
                        source[_i] = 0
                    del source
            exec(code, module.__dict__)

        @staticmethod
        def _cache_line(file_path):
            stat = os.stat(file_path)
            size, mtime = stat.st_size, stat.st_mtime
            linecache.cache[file_path] = (size, mtime, [], file_path)

        def find_spec(
            self,
            fullname: str,
            path: Optional[Sequence[_Path]],
            target: Optional[types.ModuleType] = None,
        ) -> Optional[ModuleSpec]:
            if path:
                filename = "{}{}".format(fullname.rsplit(".", 1)[-1], ENCRYPT_SUFFIX)
                if isinstance(path, _NamespacePath):
                    file_path = Path(path._path[0]) / filename
                else:
                    file_path = Path(path[0]) / filename
            else:
                for p in sys.path:
                    file_path = Path(p) / f"{fullname}{ENCRYPT_SUFFIX}"
                    if file_path.exists():
                        break
            file_path = file_path.absolute().as_posix()
            if not os.path.exists(file_path):
                return None

            self._cache_line(file_path)

            return spec_from_loader(name=fullname, loader=self.__class__(file_path), origin="origin-encrypt")

        def invalidate_caches(self):
            pass

    return EncryptFileImporter


# TODO: generate randomly AES Class
def _install():
    machinery.EXTENSION_SUFFIXES.append(ENCRYPT_SUFFIX)
    _LOADER_CLASS = _build_loader_class(_make_key_provider(None))
    sys.meta_path.insert(0, _LOADER_CLASS(None))


_install()
