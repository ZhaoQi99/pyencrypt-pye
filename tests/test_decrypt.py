from pathlib import Path

import pytest
from pyencrypt.decrypt import decrypt_key, decrypt_file
from pyencrypt.encrypt import encrypt_file, encrypt_key
from pyencrypt.generate import generate_aes_key

from constants import AES_KEY


@pytest.mark.parametrize(
    "key",
    [
        AES_KEY,
        generate_aes_key(),
    ],
)
def test_decrypt_key(key):
    cipher_key, d, n = encrypt_key(key)
    assert decrypt_key(cipher_key, d, n) == key.decode()


@pytest.fixture
def encrypted_python_file_path(tmp_path):
    path = tmp_path / "test.py"
    path.touch()
    path.write_text('print("hello world")')
    new_path = tmp_path / "test.pye"
    encrypt_file(path, AES_KEY, new_path=new_path)
    path.unlink()
    return new_path


@pytest.mark.parametrize(
    "path,key,exception",
    [
        (Path("tests/test.py"), AES_KEY, Exception),
        (Path("tests/__init__.pye"), AES_KEY, FileNotFoundError),
    ],
)
def test_decrypt_file_exception(path, key, exception):
    with pytest.raises(exception) as excinfo:
        decrypt_file(path, key)
    assert excinfo.value.__class__ == exception


def test_decrypt_file_default(encrypted_python_file_path):
    assert isinstance(decrypt_file(encrypted_python_file_path, AES_KEY), bytes) is True
    assert encrypted_python_file_path.exists() is True


def test_decrypt_file_delete_origin(encrypted_python_file_path):
    decrypt_file(encrypted_python_file_path, AES_KEY, delete_origin=True)
    assert encrypted_python_file_path.exists() is False


def test_decrypt_file_new_path(encrypted_python_file_path):
    new_path = encrypted_python_file_path.parent / "test.py"
    decrypt_file(encrypted_python_file_path, AES_KEY, new_path=new_path)
    assert new_path.exists() is True
    assert encrypted_python_file_path.exists() is True


def test_decrypt_file_new_path_exception(encrypted_python_file_path):
    new_path = encrypted_python_file_path.parent / "test.pye"
    with pytest.raises(Exception) as excinfo:
        decrypt_file(encrypted_python_file_path, AES_KEY, new_path=new_path)
    assert str(excinfo.value) == "Origin file path must be py suffix."
