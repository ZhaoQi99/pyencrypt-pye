from random import randint
from pyencrypt.generate import generate_aes_key, generate_rsa_number
import pytest


def test_generate_aes_key_default():
    assert isinstance(generate_aes_key(), bytes)


@pytest.mark.parametrize("size", [32, 64, 1024, 4096])
def test_generate_aes_key(size):
    assert isinstance(generate_aes_key(size), bytes)


@pytest.mark.parametrize("bits", [1024, 1025, 2045, 2048, 4096])
def test_generate_rsa_number(bits):
    numbers = generate_rsa_number(bits)
    assert len(numbers) == 5
    p, q, n, e, d = numbers["p"], numbers["q"], numbers["n"], numbers["e"], numbers["d"]
    assert p * q == n
    assert e * d % (p - 1) == 1
    assert e * d % (q - 1) == 1
    plain = randint(0, n)
    assert pow(pow(plain, e, n), d, n) == plain


@pytest.mark.parametrize("bits", [-1, 123])
def test_generate_rsa_number_exception(bits):
    with pytest.raises(ValueError) as excinfo:
        generate_rsa_number(bits)
    assert str(excinfo.value) == "RSA modulus length must be >= 1024"
