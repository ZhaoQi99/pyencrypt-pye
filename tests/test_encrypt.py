import os
from pathlib import Path
import shutil
import sys

import pytest
from pyencrypt.encrypt import can_encrypt, encrypt_file, encrypt_key, generate_so_file
from pyencrypt.generate import generate_aes_key

from constants import AES_KEY


@pytest.mark.parametrize(
    "key",
    [
        AES_KEY,
        generate_aes_key(),
    ],
)
def test_encrypt_key(key):
    cipher, d, n = encrypt_key(key)
    assert isinstance(cipher, str)
    assert isinstance(d, int)
    assert isinstance(n, int)


@pytest.mark.parametrize(
    "path,expected",
    [
        (Path("__init__.py"), False),
        (Path("pyencrypt/__init__.py"), False),
        (Path("management/commands/user.py"), False),
        (Path("tests/test.pye"), False),
        (Path("tests/test_encrypt.py"), True),
    ],
)
def test_can_encrypt(path, expected):
    assert can_encrypt(path) == expected


class TestGenarateSoFile:
    def setup_method(self, method):
        if method.__name__ == "test_generate_so_file_default_path":
            shutil.rmtree(
                (Path(os.getcwd()) / "encrypted").as_posix(), ignore_errors=True
            )

    @pytest.mark.parametrize(
        "key",
        [
            AES_KEY,
            generate_aes_key(),
        ],
    )
    def test_generate_so_file(self, key, tmp_path):
        cipher_key, d, n = encrypt_key(key)
        assert generate_so_file(cipher_key, d, n, tmp_path)
        assert (tmp_path / "encrypted" / "loader.py").exists() is True
        assert (tmp_path / "encrypted" / "loader_origin.py").exists() is True
        if sys.platform.startswith("win"):
            assert (
                next((tmp_path / "encrypted").glob("loader.cp*-*.pyd"), None)
                is not None
            )
        else:
            assert (
                next((tmp_path / "encrypted").glob("loader.cpython-*-*.so"), None)
                is not None
            )

    @pytest.mark.parametrize(
        "key",
        [
            AES_KEY,
            generate_aes_key(),
        ],
    )
    def test_generate_so_file_default_path(self, key):
        cipher_key, d, n = encrypt_key(key)
        assert generate_so_file(cipher_key, d, n)
        assert (Path(os.getcwd()) / "encrypted" / "loader.py").exists() is True
        assert (Path(os.getcwd()) / "encrypted" / "loader_origin.py").exists() is True
        if sys.platform.startswith("win"):
            assert (
                next((Path(os.getcwd()) / "encrypted").glob("loader.cp*-*.pyd"), None)
                is not None
            )
        else:
            assert (
                next(
                    (Path(os.getcwd()) / "encrypted").glob("loader.cpython-*-*.so"),
                    None,
                )
                is not None
            )


@pytest.mark.parametrize(
    "path,key,exception",
    [
        (Path("tests/test.py"), AES_KEY, FileNotFoundError),
        (Path("tests/test.pye"), AES_KEY, Exception),  # TODO: 封装Exception
        (Path("tests/__init__.py"), AES_KEY, Exception),
    ],
)
def test_encrypt_file_path_exception(path, key, exception):
    with pytest.raises(exception) as excinfo:
        encrypt_file(path, key)
    assert excinfo.value.__class__ == exception


@pytest.fixture
def python_file_path(tmp_path):
    fn = tmp_path / "test.py"
    fn.touch()
    fn.write_text('print("hello world")')
    return fn


def test_encrypt_file_default(python_file_path):
    assert isinstance(encrypt_file(python_file_path, AES_KEY), bytes) is True
    assert python_file_path.exists() is True


def test_encrypt_file_delete_origin(python_file_path):
    encrypt_file(python_file_path, AES_KEY, delete_origin=True)
    assert python_file_path.exists() is False


def test_encrypt_file_new_path(python_file_path):
    new_path = python_file_path.parent / "test.pye"
    encrypt_file(python_file_path, AES_KEY, new_path=new_path)
    assert new_path.exists() is True
    assert python_file_path.exists() is True


def test_encrypt_file_new_path_exception(python_file_path):
    new_path = python_file_path.parent / "test.py"
    with pytest.raises(Exception) as excinfo:
        encrypt_file(python_file_path, AES_KEY, new_path=new_path)
    assert str(excinfo.value) == "Encrypted file path must be pye suffix."
