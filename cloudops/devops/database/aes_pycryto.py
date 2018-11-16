from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

"""
Author: qingyw
Date: 2018/03/22
@note: Prpcrypt Class
functions: decrypt、encrypt
:return:
"""


class Prpcrypt():
    def __init__(self):
        self.key = b'aukeyopsaukeyops'
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        ciphertext = cryptor.encrypt(text.encode(encoding='utf8'))
        return b2a_hex(ciphertext).decode()

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text.encode(encoding='utf8')))
        return plain_text.decode().rstrip('\0')
