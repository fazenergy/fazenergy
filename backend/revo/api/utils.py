import requests


def make_revo_request(method, url, token=None, data=None):
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    response = requests.request(method, url, headers=headers, json=data)
    return response
