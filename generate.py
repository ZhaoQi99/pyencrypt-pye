from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA

def generate_aes_key():
    return Fernet.generate_key()

def generate_rsa_number(bits:int):
    r = RSA.generate(bits)
    return {
        'p':r.p,
        'q':r.q,
        'n': r.n,
        'e': r.e,
        'd':r.d
    }

if __name__ == '__main__':
    print(generate_aes_key())
    print(generate_rsa_number(2048))