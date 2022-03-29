from Crypto.Cipher import AES
import base64
import hashlib

iv = b'\0' * 16


def encrypt(text, key):
    aeskey = hashlib.sha256(key.encode('utf-8')).digest()
    aes = AES.new(aeskey, AES.MODE_CFB, iv)
    return base64.b64encode(aes.encrypt(text))


def decrypt(encrypted, key='zG2nSeEfSHfvTCHy5LCcqtBbQehKNLXn'):
    aeskey = hashlib.sha256(key.encode('utf-8')).digest()
    aes = AES.new(aeskey, AES.MODE_CBC, iv)
    return pkcs7unpadding(aes.decrypt(base64.b64decode(encrypted)))


def pkcs7unpadding(data):
    length = len(data)
    unpadding = ord(chr(data[length - 1]))
    return data[0:length - unpadding]


