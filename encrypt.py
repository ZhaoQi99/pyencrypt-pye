from Crypto.PublicKey import RSA
from cryptography.fernet import Fernet
import os
from generate import generate_aes_key, generate_rsa_number
from pathlib import Path
from ntt import ntt
from decrypt import decrypt_key

NOT_ALLOWED_ENCRYPT_FILES = ['wsgi.py', 'manage.py']


def _encrypt_file(path: Path, key: bytes, delete_origin: bool) -> None:
    file_data = path.read_bytes()
    encrypted_data = Fernet(key).encrypt(file_data)
    new_path = path.parent / f'{path.stem}.pye'
    new_path.write_bytes(encrypted_data)
    if delete_origin:
        os.remove(path)


def can_encrypt(path: Path) -> bool:
    if path.name in NOT_ALLOWED_ENCRYPT_FILES:
        return False
    if 'management/commands/' in path.as_posix():
        return False
    return True


def encrypt_key(key: bytes) -> str:
    ascii_ls = [ord(x) for x in key.decode()]
    numbers = generate_rsa_number(2048)
    e, n = numbers['e'], numbers['n']
    cipher_ls = list()
    # ntt后再用RSA加密
    for num in ntt(ascii_ls):
        cipher_ls.append(pow(num, e, n))
    return 'O'.join(map(str, cipher_ls)), numbers['d'], numbers['n']


def encrypt(dirname: str, delete_origin: bool):
    p = Path(dirname)
    key = generate_aes_key()
    if p.is_file():
        if can_encrypt(p):
            _encrypt_file(p, key, delete_origin)
    else:
        files = filter(lambda x: x.name != '__init__.py', p.glob('**/*.py'))
        for path in files:
            if can_encrypt(path):
                _encrypt_file(path, key, delete_origin)

    cipher_key, d, n = encrypt_key(key) # 需要放进导入器中


if __name__ == '__main__':
    # encrypt('encrypt.py',False)
    key = generate_aes_key()
    cipher_key, d, n = encrypt_key(key)
    assert decrypt_key(cipher_key, n, d) == key.decode()
