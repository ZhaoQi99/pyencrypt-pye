from aes import aes_decrypt
from ntt import intt


def decrypt_key(cipher_key: str, n: str, d: str) -> str:
    n = int(n)
    d = int(d)
    plain_ls = list()
    for num in map(int, cipher_key.split('O')):
        plain_ls.append(pow(num, d, n))
    # 去掉intt后末尾多余的0
    return ''.join(map(chr, filter(lambda x: x != 0, intt(plain_ls))))


def decrypt_file(data:bytes,key:str):
    return aes_decrypt(data,key)
