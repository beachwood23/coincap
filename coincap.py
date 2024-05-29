import requests
import json


def f2usd( value ):
    return f'${value:,.2f}'.replace('$-', '-$')


held_coins = {
    'bitcoin': 0.1,
    'ethereum': 0.1,
    'bitcoin-cash': 0.1,
    'dogecoin': 1,
    }

CONFIG_FILE = "coincap_config.json"

held_coins_usd = {}

api_address = 'https://api.coingecko.com/api/v3/simple/price?'
request_header = {'accept': 'application/json'}


# we want to make a single API call here, instead of one for each coin
# format of API call as of Feb 29, 2024:
# GET 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cethereum&vs_currencies=usd'
coin_ids = ','.join(held_coins.keys())

# make single request for all coin prices
resp = requests.get(api_address + 'ids=' + coin_ids + '&vs_currencies=usd', headers=request_header)

if (resp.status_code == 200):
    resp_json = json.loads(resp.text)
    # print(resp_json)
    # held_coins_usd[coin] = float(resp_json['ticker']['price']) * held_coins[coin]
    # print(coin + ': ' + f2usd(float(resp_json['ticker']['price'])) + ' -> ' + f2usd(held_coins_usd[coin]))
else:
    print(resp.text)

for coin, currency_price in resp_json.items():
    # we assume there is only one currency price in the response
    if len(currency_price) == 1:
        currency, price = next(iter(currency_price.items()))
        held_coins_usd[coin] = price * held_coins[coin]
    else:
        print("Multiple currency pairs found")

# old loop
# for coin in held_coins.keys():
#     # api_format = api_address + coin
#     resp = requests.get(api_address + 'ids=' + coin_ids + '&vs_currencies=usd', headers=request_header)
#     print(resp)
#     if (resp.status_code == 200):
#         resp_json = json.loads(resp.text)
#         print(resp_json)
#         # held_coins_usd[coin] = float(resp_json['ticker']['price']) * held_coins[coin]
#         # print(coin + ': ' + f2usd(float(resp_json['ticker']['price'])) + ' -> ' + f2usd(held_coins_usd[coin]))
#     else:
#         print(resp.text)


total_coin_values = 0
for coin in held_coins_usd.keys():

    # round floating price to nearest cent
    usd_value = f'${held_coins_usd[coin]:,.2f}'.replace('$-', '-$')
    print(f"{coin}\n\t{usd_value}")

    total_coin_values += held_coins_usd[coin]

print(f'Total coin value in USD: ${total_coin_values:,.2f}'.replace('$-', '-$'))

