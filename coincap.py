import requests
import json
import os

API_ADDRESS = 'https://api.coingecko.com/api/v3/simple/price?'
API_REQUEST_HEADER = {'accept': 'application/json'}
PORTFOLIO_FILE = "coincap_portfolio.json"

def f2usd( value ):
    return f'${value:,.2f}'.replace('$-', '-$')

# further todo: ask questions to set up config file, no direct user set up for config file
# further todo: use sqlite db and cli for updating coin values, no config files necessary
# Using JSON here, to minimize the libraries used. Already using JSON to parse the API request.
if os.path.exists(PORTFOLIO_FILE):
    with open(PORTFOLIO_FILE, "r") as f:
        held_coins = json.load(f)
# held_coins = {
#     'bitcoin': 0.1,
#     'ethereum': 0.1,
#     'bitcoin-cash': 0.1,
#     'dogecoin': 1,
#     }

held_coins_usd = {}

# format of API call as of Feb 29, 2024:
# GET 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cethereum&vs_currencies=usd'
coin_ids = ','.join(held_coins.keys())

# make single request for all coin prices
resp = requests.get(API_ADDRESS + 'ids=' + coin_ids + '&vs_currencies=usd', headers=API_REQUEST_HEADER)

if (resp.status_code == 200):
    resp_json = json.loads(resp.text)
else:
    print(resp.text)

for coin, currency_price in resp_json.items():
    # we assume there is only one currency price in the response
    if len(currency_price) == 1:
        currency, price = next(iter(currency_price.items()))
        held_coins_usd[coin] = price * held_coins[coin]
    else:
        print("Multiple currency pairs found")

total_coin_values = 0
for coin in held_coins_usd.keys():

    # round floating price to nearest cent
    usd_value = f'${held_coins_usd[coin]:,.2f}'.replace('$-', '-$')
    print(f"{coin}\n\t{usd_value}")

    total_coin_values += held_coins_usd[coin]

print(f'Total coin value in USD: ${total_coin_values:,.2f}'.replace('$-', '-$'))

