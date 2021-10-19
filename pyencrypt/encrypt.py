import os
import subprocess
from pathlib import Path
from typing import List

from pyencrypt.aes import aes_encrypt
from pyencrypt.decrypt import decrypt_key
from pyencrypt.generate import generate_aes_key, generate_rsa_number
from pyencrypt.ntt import ntt

NOT_ALLOWED_ENCRYPT_FILES = ['wsgi.py', 'manage.py','__init__.py']


def _encrypt_file(path: Path, key: bytes, delete_origin: bool) -> None:
    file_data = path.read_bytes()
    encrypted_data = aes_encrypt(file_data,key)
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


def generate_so_file(cipher_key: str, private_key: str):
    path = Path(os.path.abspath(__file__)).parent

    decrypt_source_ls = list()
    need_import_files = ['ntt.py','aes.py','decrypt.py']
    for file in need_import_files:
        file_path = path / file
        decrypt_source_ls.append(file_path.read_text().replace(
            'from pyencrypt.ntt import intt', '').replace('from pyencrypt.aes import aes_decrypt',''))

    loader_source_path = path / 'loader.py'
    loader_source = loader_source_path.read_text().replace(
        "PRIVATE_KEY = ''", f"PRIVATE_KEY = '{private_key}'",
        1).replace("CIPHER_KEY = ''", f"CIPHER_KEY = '{cipher_key}'",
                   1).replace("from pyencrypt.decrypt import *", '')

    temp_dir = Path(os.getcwd()) / 'encrypted'
    temp_dir.mkdir(exist_ok=True)
    loader_file_path = temp_dir / 'loader.py'
    loader_file_path.touch(exist_ok=True)

    decrypt_source = '\n'.join(decrypt_source_ls)
    loader_file_path.write_text(f"{decrypt_source}\n{loader_source}")

    # Origin file
    loader_origin_file_path = temp_dir / 'loader_origin.py'
    loader_origin_file_path.touch(exist_ok=True)
    loader_origin_file_path.write_text(f"{decrypt_source}\n{loader_source}")

    setup_file_path = Path(os.path.abspath(__file__)).parent / 'setup.py'
    args = [
        'pyminifier', '--obfuscate-classes' ,'--obfuscate-import-methods', '--replacement-length', '20', '-o',
        loader_file_path.as_posix(),
        loader_file_path.as_posix()
    ]
    ret = subprocess.run(args, shell=False, encoding='utf-8')
    if ret.returncode == 0:
        pass

    args = ['python', setup_file_path.as_posix(), 'build_ext','--build-lib', temp_dir.as_posix()]
    ret = subprocess.run(args, shell=False, stderr=subprocess.PIPE,encoding='utf-8')
    if ret.returncode == 0:
        pass



def encrypt(files: List[Path], delete_origin: bool, key: str = None):
    for p in files:
        if can_encrypt(p):
            _encrypt_file(p, key, delete_origin)

    cipher_key, d, n = encrypt_key(key.encode())  # 需要放进导入器中
    private_key = f'{n}O{d}'
    generate_so_file(cipher_key, private_key)


if __name__ == '__main__':
    key = generate_aes_key()
    encrypt(Path('flag.py'), False,key.decode())
    cipher_key, d, n = encrypt_key(key)
    assert decrypt_key(cipher_key, n, d) == key.decode()
