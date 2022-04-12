import os
import re
import subprocess
from pathlib import Path

from pyencrypt.aes import aes_encrypt
from pyencrypt.generate import generate_rsa_number
from pyencrypt.ntt import ntt

NOT_ALLOWED_ENCRYPT_FILES = [
    '__init__.py',
]

REMOVE_SELF_IMPORT = re.compile(r'^from pyencrypt\.[\s\S]*?$', re.MULTILINE)


def _encrypt_file(
    data: bytes,
    key: bytes,
) -> bytes:
    return aes_encrypt(data, key)


def can_encrypt(path: Path) -> bool:
    if path.name in NOT_ALLOWED_ENCRYPT_FILES:
        return False
    if 'management/commands/' in path.as_posix():
        return False
    if path.suffix != '.py':
        return False
    return True


def encrypt_key(key: bytes) -> str:
    ascii_ls = [ord(x) for x in key.decode()]
    numbers = generate_rsa_number(2048)
    e, n = numbers['e'], numbers['n']
    # fill length to be a power of 2
    length = len(ascii_ls)
    if length & (length - 1) != 0:
        length = 1 << length.bit_length()
        ascii_ls = ascii_ls + [0] * (length - len(ascii_ls))
    cipher_ls = list()
    # ntt后再用RSA加密
    for num in ntt(ascii_ls):
        cipher_ls.append(pow(num, e, n))
    return 'O'.join(map(str, cipher_ls)), numbers['d'], numbers['n']


def generate_so_file(cipher_key: str, d: int, n: int, base_dir: Path = None, license: bool = False) -> Path:
    private_key = f'{n}O{d}'
    path = Path(os.path.abspath(__file__)).parent

    decrypt_source_ls = list()
    need_import_files = ['ntt.py', 'aes.py', 'decrypt.py', 'license.py']
    for file in need_import_files:
        file_path = path / file
        decrypt_source_ls.append(REMOVE_SELF_IMPORT.sub('', file_path.read_text()))

    loader_source_path = path / 'loader.py'
    loader_source = REMOVE_SELF_IMPORT.sub('', loader_source_path.read_text()).replace(
        "__private_key = ''", f"__private_key = '{private_key}'", 1
    ).replace("__cipher_key = ''", f"__cipher_key = '{cipher_key}'", 1).replace(
        'license = None', f'license = {license}', 1
    )

    if base_dir is None:
        base_dir = Path(os.getcwd())

    temp_dir = base_dir / 'encrypted'
    temp_dir.mkdir(exist_ok=True)
    loader_file_path = temp_dir / 'loader.py'
    loader_file_path.touch(exist_ok=True)

    decrypt_source = '\n'.join(decrypt_source_ls)
    loader_file_path.write_text(f"{decrypt_source}\n{loader_source}")

    # Origin file
    loader_origin_file_path = temp_dir / 'loader_origin.py'
    loader_origin_file_path.touch(exist_ok=True)
    loader_origin_file_path.write_text(f"{decrypt_source}\n{loader_source}")

    args = [
        'pyminifier',
        '--obfuscate-classes',
        '--obfuscate-import-methods',
        '--replacement-length',
        '20',
        '-o',
        loader_file_path.as_posix(),
        loader_file_path.as_posix(),
    ]
    ret = subprocess.run(args, shell=False, encoding='utf-8')
    if ret.returncode == 0:
        pass

    from setuptools import setup
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
    setup(
        ext_modules=cythonize(loader_file_path.as_posix(), language_level="3"),
        script_args=['build_ext', '--build-lib', temp_dir.as_posix()],
        cmdclass={'build_ext': build_ext},
    )
    return list(temp_dir.glob('loader.cpython-*-*.so'))[0].absolute()


def encrypt_file(path: Path, key: str, delete_origin: bool = False, new_path: Path = None):
    if not can_encrypt(path):
        raise Exception(f"{path.name} can't be encrypted.")
    encrypted_data = _encrypt_file(path.read_bytes(), key)
    if new_path:
        if new_path.suffix != '.pye':
            raise Exception("Encrypted file path must be pye suffix.")
        new_path.touch(exist_ok=True)
        new_path.write_bytes(encrypted_data)
    if delete_origin:
        os.remove(path)
    return encrypted_data
