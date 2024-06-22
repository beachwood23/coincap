import requests
import json
import os

API_ADDRESS = 'https://api.coingecko.com/api/v3/simple/price?'
API_REQUEST_HEADER = {'accept': 'application/json'}
# PORTFOLIO_FILE = "coincap_portfolio.json"
PORTFOLIO_FILE = "test_coincap_portfolio.json"

def read_portfolio():
    held_coins = {}
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            held_coins = json.load(f)

    return held_coins

def create_portfolio():
    # todo: interactive autocomplete for coin names
    # further todo: use sqlite db and cli for updating coin values, no config files necessary
    # further todo: using some charm.sh fun to jazz things up, or perhaps python-rich

    held_coins = {}
    print("""
    We see you don't have a portfolio created yet. Let's help you make one.
    Enter your coins in the full name like "bitcoin", "ethereum", "bitcoin-cash", etc.
    """)
    while True:
        coin = input("Enter a cryptocoin you want to track, or press Enter to finish): ").strip()
        if not coin:
            break
        value = int(input(f"Enter number of coins held for {coin}: ").strip())
        held_coins[coin] = value


    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(held_coins, f, indent=2)
        print(f"Data saved to {PORTFOLIO_FILE}.")

    return held_coins

def print_portfolio(held_coins):
    # todo: validate held_coins against possible coins in API
    # https://pro-api.coingecko.com/api/v3/coins/list returns json of all possible coins

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
    print("~~~~~ coin capitalization ~~~~~")
    for coin in held_coins_usd.keys():

        # round floating price to nearest cent
        usd_value = f'${held_coins_usd[coin]:,.2f}'.replace('$-', '-$')
        print(f"{coin}\n\t{usd_value}")

        total_coin_values += held_coins_usd[coin]

    print(f'Total coin value in USD: ${total_coin_values:,.2f}'.replace('$-', '-$'))

if __name__ == '__main__':

    held_coins = read_portfolio() # first try to get from stored param file
    if not held_coins:
        # we need to build json portfolio file
        held_coins = create_portfolio()

    print_portfolio(held_coins)
