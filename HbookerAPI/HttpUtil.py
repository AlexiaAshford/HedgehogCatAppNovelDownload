import json
from Crypto.Cipher import AES
import base64
import hashlib
from rich import print
import requests


def decrypt(encrypted: str, key: str = 'zG2nSeEfSHfvTCHy5LCcqtBbQehKNLXn') -> bytes:
    data = AES.new(hashlib.sha256(key.encode('utf-8')).digest(), AES.MODE_CBC, b'\0' * 16). \
        decrypt(base64.b64decode(encrypted))
    return data[0:len(data) - ord(chr(data[len(data) - 1]))]


def get(url, headers: dict, params=None, max_retry=10, **kwargs):
    for retry in range(max_retry):
        try:
            with requests.Session() as session:
                result = session.get(url, params=params, headers=headers, **kwargs)
                return json.loads(decrypt(str(result.text)))
        except requests.exceptions.RequestException:
            if retry > 3:
                print("Max retries exceeded with url:", url)


def post(url, headers: dict, params=None, max_retry=10, **kwargs):
    for retry in range(max_retry):
        try:
            with requests.Session() as session:
                result = session.post(url, data=params, headers=headers, **kwargs)
                return json.loads(decrypt(result.text))
        except requests.exceptions.RequestException:
            if retry > 3:
                print(" Max retries exceeded with url:", url)
