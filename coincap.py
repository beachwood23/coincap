import requests
import json
import os
import readline
import logging

API_ADDRESS = 'https://api.coingecko.com/api/v3/simple/price?'
API_REQUEST_HEADER = {'accept': 'application/json'}
# PORTFOLIO_FILE = "coincap_portfolio.json"
PORTFOLIO_FILE = "test_coincap_portfolio.json"

LOG_FILENAME = './coincap.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    )

class AutoCompleter:
    def __init__(self, options):
        self.options = sorted(options)
        self.matches = []

    def complete(self, text, state):
        # When state is 0, it means it's a new completion session, so we need to compute the matches
        if state == 0:
            if text:  # If there's already some text, match it
                self.matches = [s for s in self.options if s.startswith(text)]
            else:  # If no text, list all options
                self.matches = self.options[:]
        # Return the state-th match
        try:
            return self.matches[state]
        except IndexError:
            return None


def read_portfolio():
    """Attempts to read from the PORTFOLIO_FILE. Returns values if it exists."""
    held_coins = {}
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            held_coins = json.load(f)

    return held_coins

def create_portfolio():
    """Creates portfolio file. Assumes we have already checked if it exists."""
    # todo: interactive autocomplete for coin names
    # Can borrow some type of functionality from https://github.com/darrenburns/textual-autocomplete
    # This takes an array of DropDownItems, like strings, that then autocompletes.
    # further todo: using some charm.sh fun to jazz things up, or perhaps python-rich
    # further todo: use sqlite db and cli for updating coin values, no config files necessary

    held_coins = {}
    print("""
    We see you don't have a portfolio created yet. Let's help you make one.
    Enter your coins in the full name like "bitcoin", "ethereum", "bitcoin-cash", etc.
    Use TAB to autocomplete coin names.
    """)

    completer = AutoCompleter(['bitcoin', 'ethereum', 'litecoin'])
    readline.set_completer(completer.complete)
    # Ensure we are in the correct mode for completion
    # readline.parse_and_bind('tab: complete') # works for linux and windows
    readline.parse_and_bind('bind ^I rl_complete') # works for Mac
    # readline.parse_and_bind('set editing-mode emacs')

    while True:
        try:
            coin = input("Enter a cryptocoin you want to track, or press Enter to finish): ").strip()
            if not coin:
                break
            value = int(input(f"Enter number of coins held for {coin}: ").strip())
            held_coins[coin] = value
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(held_coins, f, indent=2)
        print(f"Data saved to {PORTFOLIO_FILE}.")

    return held_coins

def print_portfolio(held_coins):
    """Prints the value of the held_coins"""
    # todo: validate held_coins against possible coins in API
    # https://pro-api.coingecko.com/api/v3/coins/list returns json of all possible coins
    # could combine comparing this list with autocomplete in coin entry?

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
