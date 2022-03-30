import requests


def fetch(*, base_url, params, headers):
    """
    fetch information from the blockchain API
    """
    response = requests.get(url=base_url, params=params, headers=headers)
    return response.json()
