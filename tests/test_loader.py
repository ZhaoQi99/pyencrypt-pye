import pytest
from pathlib import Path
import shutil
from pyencrypt.encrypt import *
from constants import AES_KEY


@pytest.fixture(scope='module')
def python_file(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('file')
    path = tmp_path / 'aaa.py'
    path.touch()
    path.write_text("""\
def main():
    return 'hello world'
    """)
    new_path = path.with_suffix('.pye')
    encrypt_file(path, AES_KEY, new_path=new_path)
    path.unlink()
    cipher_key, d, n = encrypt_key(AES_KEY)
    generate_so_file(cipher_key, d, n, tmp_path)
    loader_path = list((tmp_path / 'encrypted').glob('loader.cpython-*-*.so'))[0]
    shutil.copy(loader_path, tmp_path)
    shutil.rmtree(tmp_path / 'encrypted')
    return new_path


def test_python_file_with_sys_path(python_file: Path, monkeypatch):
    monkeypatch.syspath_prepend(python_file.parent.as_posix())
    import loader
    from aaa import main
    assert main() == 'hello world'


@pytest.fixture(scope='module')
def python_package(tmp_path_factory):
    pkg_path = tmp_path_factory.mktemp('package')
    path = pkg_path / 'bbb'
    path.mkdir()
    (path / '__init__.py').touch()
    path /= 'ccc.py'
    path.touch()
    path.write_text("""\
def main():
    return 'hello world'
    """)
    new_path = path.with_suffix('.pye')
    encrypt_file(path, AES_KEY, new_path=new_path)
    path.unlink()
    cipher_key, d, n = encrypt_key(AES_KEY)
    generate_so_file(cipher_key, d, n, pkg_path)
    loader_path = list((pkg_path / 'encrypted').glob('loader.cpython-*-*.so'))[0]
    shutil.copy(loader_path, pkg_path)
    shutil.rmtree(pkg_path / 'encrypted')
    return pkg_path


def test_python_package(python_package: Path, monkeypatch):
    monkeypatch.syspath_prepend(python_package.as_posix())
    import loader
    from bbb.ccc import main
    assert main() == 'hello world'


def test_python_package_without_init_file(tmp_path_factory):
    pkg_path = tmp_path_factory.mktemp('package')
    path = pkg_path / 'aaa'
    path.mkdir()
    path /= 'bbb.py'
    path.touch()
    path.write_text("""\
def main():
    return 'hello world'
    """)
    new_path = path.with_suffix('.pye')
    encrypt_file(path, AES_KEY, new_path=new_path)
    path.unlink()
    cipher_key, d, n = encrypt_key(AES_KEY)
    generate_so_file(cipher_key, d, n, pkg_path)
    loader_path = list((pkg_path / 'encrypted').glob('loader.cpython-*-*.so'))[0]
    shutil.copy(loader_path, pkg_path)
    shutil.rmtree(pkg_path / 'encrypted')
    import loader
    from bbb.ccc import main