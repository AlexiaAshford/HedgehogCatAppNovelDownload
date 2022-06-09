import json
from Crypto.Cipher import AES
import base64
import hashlib
import httpx
from rich import print
import requests


def decrypt(encrypted: str, key: str = 'zG2nSeEfSHfvTCHy5LCcqtBbQehKNLXn') -> bytes:
    data = AES.new(hashlib.sha256(key.encode('utf-8')).digest(),
                   AES.MODE_CBC, b'\0' * 16).decrypt(base64.b64decode(encrypted))
    return data[0:len(data) - ord(chr(data[len(data) - 1]))]


# print(json.loads(decrypt(
#     "jjUGSk4ZaZ+d7XumG0q4SBPkBcBZlfthbdJiItHXYemgfpQCzs1IIiDcKHmrJWsHObhMX/TNvRKOA15CFPjHffcQVcOeL+qsgRoShZertkopC3z3V0ugHz3+M02+mKd4gOAJcI7y2L9WLvDeR3jSXqBCBYY0Ax0gK4TCGfxRCMMPWrudegexZot0Gm800Pg8piroGjlw5hA7NVNceleehHopBY9pGyGCRSXw6twhIgCOmxXMWKvafeKu8Uk/b14MAcjbKiB3tyHvC4g99VbVcfiZiu5T2s1Magakb/cVTBgdINO2aCti0+7/iOtIdEqHQv1/VNkm9t4BthYwwF94qmMqyKWNwMECbnYxi7bes851C0UQERV3yTmukDLwupIDt/6KmYRM+o/+Bz9dpnxw7UPBlmJffvCZMITysPS1tAKGr1QHuap1xcTR5iWr9oQ5t5VBzsR/LDqO1Vi1RQ4eQXFEbuNDiUEdomWXWza3MUvxhv2r0Rflx2DyhRsJyYF/bj2o/El1PdytueYm+bvckasR4wbXElMW55hr61EPtxpyccmfhzwA7NDv782L0WLPnUvZDPzANXuG4BRncDdODUr71DkgUmtVE/aJNtJie7vuwoo4XeeXv/LU9P3SMSJ75rHsEaMA8GGwzL/7e6n6AO2A4LiGF+aO15/Z5w2apfffekc+NkvflK4x/qnGHt1UWWzCY43GOy92Pe3Q2pG/qNhTNO8q8ykHJcH0MjC0NgF9+FSE4a48tR3gY3fyifhowhpTxNE0qTJCwq/rHvqUzyDWZfThsas2WPbejuDqCBW4o82skUYtN82XX+p4Cuf8C8IUR7iaSlRIReQQzwofHsCWLkmnUbMdzWm+kri+2n8LMEdwLZ770wrmrd6cRwH0y6Y0ymVKnT5xi9E0qWtu1+A907JtVflIhnJeyYnBlwyTjz8dLFWM7P6zObDF2SRozzWC9C0CMU/M1RdHfLohEZW7MeeAXZN4DWD3+hMZ1zqq+dt+2EvN54KuMfD9BZ7Etp+gK56pKPN5IrCWiPiAZle4z3JfCsoDIr6BX1a9WjwG4QJJDRBUYDLZN5wg7jpl8jESX9gQIWhAqNcyKsdKHKl8bjl1nuUn5X7x0ca4P1ykYgjR40wmfd0YVPpRIyZl25AXqEo4fTMlaWTRVd/LKQ==")))


def get(url, headers: dict, params=None, max_retry=10, **kwargs):
    for retry in range(max_retry):
        try:

            ret = requests.get(url, params=params, headers=headers, **kwargs)
            return json.loads(decrypt(ret.text))
        except requests.exceptions.RequestException:
            if retry > 3:
                print("Max retries exceeded with url:", url)


def post(url, headers: dict, params=None, max_retry=10, **kwargs):
    for retry in range(max_retry):
        try:
            res = requests.post(url, params=params, headers=headers, **kwargs)
            return json.loads(decrypt(res.text))
        except requests.exceptions.RequestException:
            if retry > 3:
                print(" Max retries exceeded with url:", url)
