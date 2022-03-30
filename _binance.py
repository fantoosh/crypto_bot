import requests

url = 'https://api-testnet.bscscan.com/api'

payload = {
    'module': 'account',
    'action': 'txlist',
    'address': '0xBF4a6C8dB939469fccA37a1EB76055bA8B7beaF8',
    'startblock': '0',
    'endblock': '99999999',
    'page': '1',
    'ofset': '10',
    'sort': 'asc',
    'apikey': 'E9Y68UVB3CFB1NEQY65B2ZUFWZ42R1H4XH'
}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

r = requests.get(url=url, params=payload, headers=headers)
print(r.url)

print(r.status_code)

print(r.json())

