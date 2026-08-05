import os
from pathlib import Path

from pyencrypt.aes import aes_decrypt

MAGIC = b"PYE\x02"


def decrypt_key(cipher_key: str, d: int, n: int) -> str:
    plain_ls = list()
    for num in map(int, cipher_key.split("O")):
        plain_ls.append(pow(num, d, n))
    return "".join(map(chr, plain_ls))


def _decrypt_file(data: bytes, key: str) -> bytes:
    return aes_decrypt(data, key)


def decrypt_file(
    path: Path, key: str, delete_origin: bool = False, new_path: Path = None
) -> bytes:
    if path.suffix != ".pye":
        raise Exception(f"{path.name} can't be decrypted.")
    raw = path.read_bytes()
    if not raw.startswith(MAGIC):
        raise Exception(f"{path.name} has an invalid magic header.")
    data = _decrypt_file(raw[len(MAGIC) :], key)
    if new_path:
        if new_path.suffix != ".py":
            raise Exception("Origin file path must be py suffix.")
        new_path.touch(exist_ok=True)
        new_path.write_bytes(data)
    if delete_origin:
        os.remove(path)
    return data
