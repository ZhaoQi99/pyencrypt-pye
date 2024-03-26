import base64
import os

from Crypto.PublicKey import RSA


def generate_aes_key(size: int = 32) -> bytes:
    return base64.b64encode(os.urandom(size))


def generate_rsa_number(bits: int) -> dict:
    r = RSA.generate(bits)
    return {"p": r.p, "q": r.q, "n": r.n, "e": r.e, "d": r.d}
