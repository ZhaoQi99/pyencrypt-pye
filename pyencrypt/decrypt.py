from pathlib import Path
from pyencrypt.aes import aes_decrypt
from pyencrypt.ntt import intt


def decrypt_key(cipher_key: str, n: int, d: int) -> str:
    plain_ls = list()
    for num in map(int, cipher_key.split('O')):
        plain_ls.append(pow(num, d, n))
    # 去掉intt后末尾多余的0
    return ''.join(map(chr, filter(lambda x: x != 0, intt(plain_ls))))



def _decrypt_file(data:bytes, key:str) -> bytes:
    return aes_decrypt(data,key)


def decrypt_file(path: Path, key: str, new_path: Path = None) -> bytes:
    if path.suffix != '.pye':
        raise Exception(f"{path.name} can't be decrypted.")
    data =  _decrypt_file(path.read_bytes(),key)
    if new_path:
        if new_path.suffix != '.py':
            raise Exception("Origin file path must be py suffix.")
        new_path.touch(exist_ok=True)
        new_path.write_bytes(data)
    return data