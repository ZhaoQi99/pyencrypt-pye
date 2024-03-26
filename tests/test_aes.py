from pyencrypt.aes import AESModeOfOperationECB, aes_encrypt, aes_decrypt
import pytest

from constants import AES_KEY

PLAIN_1 = b"hello world"
CIPHER_1 = b"\xc5\xa1\xf8\xed\xf7\xa0\x03\xd8\xffu\x01\xac\x93\xcd+\xe1"
PLAIN_PADDING_1 = PLAIN_1 + b"\x05" * 5

PLAIN_2 = "你好 世界!".encode()
CIPHER_2 = b"\t\xb6R0B\x1fgz\x06x\x9d\xaf\xb4\xe7_\x9f"
PLAIN_PADDING_2 = PLAIN_2 + b"\x02" * 2

PLAIN_3 = b"abcdefghijklmnop"
CIPHER_3 = (
    b"r\x14\xa7\x92\xd6\x1f\x0c\xf4\x10g\x99\t/\xf0z\xfc"
    + b"&\x80\xdb\x94\xd1\xf7\x9f\xe0Qo\x05\x98\x7f\xe6j\x8c"
)


class TestAES:
    @pytest.mark.parametrize(
        "key, plain, cipher",
        [
            (AES_KEY, PLAIN_1, CIPHER_1),
            (AES_KEY, PLAIN_2, CIPHER_2),
            (AES_KEY, PLAIN_3, CIPHER_3),
        ],
    )
    def test_aes_encrypt(self, plain, cipher, key):
        assert aes_encrypt(plain, key) == cipher

    @pytest.mark.parametrize(
        "key, plain, cipher",
        [
            (AES_KEY, PLAIN_1, CIPHER_1),
            (AES_KEY, PLAIN_2, CIPHER_2),
            (AES_KEY, PLAIN_3, CIPHER_3),
        ],
    )
    def test_aes_decrypt(self, plain, cipher, key):
        assert aes_decrypt(cipher, key) == plain


class TestAESModeOfOperationECB:
    def setup_class(self):
        self.cipher = AESModeOfOperationECB(AES_KEY)

    @pytest.mark.parametrize("length", [17, 18, 19, 20])
    def test_encrypt_exception(self, length):
        with pytest.raises(ValueError) as excinfo:
            self.cipher.encrypt(b"a" * length)
        assert str(excinfo.value) == "plain block must be 16 bytes"

    @pytest.mark.parametrize("length", [17, 18, 19, 20])
    def test_decrypt_exception(self, length):
        with pytest.raises(ValueError) as excinfo:
            self.cipher.decrypt(b"a" * length)
        assert str(excinfo.value) == "cipher block must be 16 bytes"

    @pytest.mark.parametrize(
        "plain, cipher",
        [
            (PLAIN_PADDING_1, CIPHER_1),
            (PLAIN_PADDING_2, CIPHER_2),
        ],
    )
    def test_encrypt(self, plain, cipher):
        assert self.cipher.encrypt(plain) == cipher

    @pytest.mark.parametrize(
        "plain, cipher",
        [
            (PLAIN_PADDING_1, CIPHER_1),
            (PLAIN_PADDING_2, CIPHER_2),
        ],
    )
    def test_decrypt(self, plain, cipher):
        assert self.cipher.decrypt(cipher) == plain
