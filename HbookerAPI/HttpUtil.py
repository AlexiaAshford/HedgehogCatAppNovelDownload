import json
from Crypto.Cipher import AES
import base64
import hashlib
import requests

headers = {'User-Agent': 'Android'}


def decrypt(encrypted: str) -> bytes:
    aes_key = hashlib.sha256('zG2nSeEfSHfvTCHy5LCcqtBbQehKNLXn'.encode('utf-8')).digest()
    data = AES.new(aes_key, AES.MODE_CBC, b'\0' * 16).decrypt(base64.b64decode(encrypted))
    return data[0:len(data) - ord(chr(data[len(data) - 1]))]


def get(url, params=None, max_retry=10, **kwargs):
    for retry in range(max_retry):
        try:
            return json.loads(decrypt(requests.get(url, params=params, headers=headers, **kwargs).text))
        except requests.exceptions.RequestException:
            print("Max retries exceeded with url:", url)


def post(url, data=None, max_retry=10, **kwargs):
    for retry in range(max_retry):
        try:
            return json.loads(decrypt(requests.post(url, data, headers=headers, **kwargs).text))
        except requests.exceptions.RequestException:
            print(" Max retries exceeded with url:", url)
