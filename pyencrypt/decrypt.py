from pyencrypt.aes import aes_decrypt
from pyencrypt.ntt import intt


def decrypt_key(cipher_key: str, n: int, d: int) -> str:
    plain_ls = list()
    for num in map(int, cipher_key.split('O')):
        plain_ls.append(pow(num, d, n))
    # 去掉intt后末尾多余的0
    return ''.join(map(chr, filter(lambda x: x != 0, intt(plain_ls))))


def decrypt_file(data:bytes,key:str) -> bytes:
    return aes_decrypt(data,key)
