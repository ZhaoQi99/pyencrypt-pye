from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA

def generate_aes_key():
    return Fernet.generate_key()

def generate_rsa_key():
    r = RSA.generate(2048)
    return r.publickey().exportKey("PEM"),r.exportKey("PEM")

if __name__ == '__main__':
    print(generate_aes_key())
    print(generate_rsa_key())