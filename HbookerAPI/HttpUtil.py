import requests

headers = {'User-Agent': 'Android'}


def get(url, params=None, max_retry=10, **kwargs):
    for retry in range(max_retry):
        try:
            return str(requests.get(url, params=params, headers=headers, **kwargs).text)
        except requests.exceptions.RequestException as error:
            print("Max retries exceeded with url:", url)


def post(url, data=None, max_retry=10, **kwargs):
    for retry in range(max_retry):
        try:
            return str(requests.post(url, data, headers=headers, **kwargs).text)
        except requests.exceptions.RequestException as error:
            print(" Max retries exceeded with url:", url)
