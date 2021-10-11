from Crypto.PublicKey import RSA
from cryptography.fernet import Fernet
import os
from generate import generate_aes_key
from pathlib import Path


NOT_ALLOWED_ENCRYPT_FILES = ['wsgi.py', 'manage.py']


def _encrypt_file(path: Path, key: bytes, delete_origin: bool):
    file_data = path.read_bytes()
    encrypted_data = Fernet(key).encrypt(file_data)
    new_path = path.parent / f'{path.stem}.pye'
    new_path.write_bytes(encrypted_data)
    if delete_origin:
        os.remove(path)


def can_encrypt(path: Path):
    if path.name in NOT_ALLOWED_ENCRYPT_FILES:
        return False
    if 'management/commands/' in path.as_posix():
        return False
    return True


def encrypt(dirname: str, delete_origin: bool):
    p = Path(dirname)
    key = generate_aes_key()
    if p.is_file():
        if can_encrypt(p):
            _encrypt_file(p,key,delete_origin)
    else:
        files = filter(lambda x: x.name != '__init__.py',p.glob('**/*.py'))
        for path in files:
            if can_encrypt(path):
                _encrypt_file(path, key, delete_origin)


if __name__ == '__main__':
    encrypt('encrypt.py',False)