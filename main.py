import requests



API_KEY = 'f49a23078cb82142021982d02376f4eb-509ddbe7730dee58b2f920caf378863e'
ACCOUNT_ID = '101-001-29078464-001'
OANDA_URL = 'https://api-fxpractice.oanda.com/v3'

SECURE_HEADER = {
    'Authorization': f'Bearer {API_KEY}'
}

session = requests.Session()
instrument = 'EUR_USD'
count = 10
granularity = 'H1'

url = f'{OANDA_URL}/instruments/{instrument}/candles'
params = dict(
    count=count,
    granularity=granularity,
    price = 'MBA'
)

response = session.get(url,params=params, headers=SECURE_HEADER)
print(response.json())