import argparse
import json
import logging
import os
import readline
from typing import Dict, List

import requests

API_ADDRESS = 'https://api.coingecko.com/api/v3/'
API_REQUEST_HEADER = {'accept': 'application/json'}
PORTFOLIO_FILE = 'coincap_portfolio.json'

LOG_FILENAME = './coincap.log'
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)


def set_args() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(
        description='A simple tracker of your cryptocurrency portfolio.'
    )

    arg_parser.add_argument(
        '--clean',
        help='Sets up a clean portfolio file. Removes your existing portfolio file.',
        required=False,
        action='store_true',
    )
    # todo: add 'force' flag, and confirmation option
    # arg_parser.add_argument(
    #     '-f',
    #     '--force',
    #     help='Skips the confirmation prompt before cleaning portfolio file.',
    #     required=False)

    return arg_parser


class AutoCompleter:
    def __init__(self, options):
        self.options = sorted(options)
        self.matches = []

    def complete(self, text, state) -> str:
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


def populate_possible_coins() -> List[str]:
    """Attempts to populate a json map of all possible coins that can be tracked."""
    possible_coins = []

    # Source: https://docs.coingecko.com/v3.0.1/reference/coins-markets
    resp = requests.get(
        API_ADDRESS + 'coins/markets?vs_currency=usd&order=market_cap_desc',
        headers=API_REQUEST_HEADER,
    )

    if resp.status_code == 200:
        resp_json = json.loads(resp.text)
    else:
        print(resp.text)

    for coin in resp_json:
        possible_coins.append(coin['id'])

    return possible_coins


def remove_portfolio():
    """Deletes the existing portfolio at PORTFOLIO_FILE"""
    if os.path.exists(PORTFOLIO_FILE):
        print(f'Cleaning the existing portfolio file at {PORTFOLIO_FILE}...')
        os.remove(PORTFOLIO_FILE)


def read_portfolio() -> Dict[str, float]:
    """Attempts to read from the PORTFOLIO_FILE. Returns values if it exists."""
    held_coins = {}
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            held_coins = json.load(f)

    return held_coins


def create_portfolio() -> Dict[str, float]:
    """Creates portfolio file. Assumes we have already checked if it exists."""
    # todo: interactive autocomplete for coin names
    # Can borrow some type of functionality from https://github.com/darrenburns/textual-autocomplete
    # This takes an array of DropDownItems, like strings, that then autocompletes.
    # further todo: using some charm.sh fun to jazz things up, or perhaps python-rich
    # further todo: use sqlite db and cli for updating coin values, no config files necessary

    held_coins = {}
    print("""
    We see you don't have a portfolio created yet. Let's help you make one 🤠

    Enter your coins in the full name like "bitcoin", "ethereum", "bitcoin-cash", etc.
    If the coin is in the top 100 by market cap, use TAB to autocomplete coin names.

    Other coins can be tracked, if they have a price on https://www.coingecko.com.
    """)

    ## todo: Fill up these coins with the full list of possible working coins
    possible_coins = populate_possible_coins()
    completer = AutoCompleter(possible_coins)
    readline.set_completer(completer.complete)

    ## todo: enter the correct mode for completion based on OS
    # Ensure we are in the correct mode for completion
    # readline.parse_and_bind('tab: complete') # works for linux and windows
    readline.parse_and_bind('bind ^I rl_complete')  # works for Mac

    # todo: fix bug in autocomplete for hyphenated coins like 'bitcoin-cash'
    while True:
        try:
            coin = input(
                'Enter a cryptocoin you want to track, or press Enter to finish): '
            ).strip()
            if not coin:
                break
            value = float(input(f'Enter number of coins held for {coin}: ').strip())
            held_coins[coin] = value
        except (EOFError, KeyboardInterrupt):
            print('\nExiting.')
            break

    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(held_coins, f, indent=2)
        print(f'Data saved to {PORTFOLIO_FILE}.')

    return held_coins


def print_portfolio(held_coins):
    """Prints the value of the held_coins."""
    # todo: validate held_coins against possible coins in API
    # https://pro-api.coingecko.com/api/v3/coins/list returns json of all possible coins
    # could combine comparing this list with autocomplete in coin entry?

    held_coins_usd = {}

    # format of API call as of Feb 29, 2024:
    # GET 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cethereum&vs_currencies=usd'
    coin_ids = ','.join(held_coins.keys())

    # make single request for all coin prices
    resp = requests.get(
        API_ADDRESS + 'simple/price?' + 'ids=' + coin_ids + '&vs_currencies=usd',
        headers=API_REQUEST_HEADER,
    )

    if resp.status_code == 200:
        resp_json = json.loads(resp.text)
    else:
        print(resp.text)

    for coin, currency_price in resp_json.items():
        # we assume there is only one currency price in the response
        currency, price = [(x, y) for x, y in currency_price.items()][0]
        held_coins_usd[coin] = price * held_coins[coin]

        # if len(currency_price) == 1:
        #     currency, price = next(iter(currency_price.items()))
        #     held_coins_usd[coin] = price * held_coins[coin]
        # else:
        #     print("Multiple currency pairs found")

    total_coin_values = 0
    print('~~~~~ coin capitalization ~~~~~')
    for coin in held_coins_usd.keys():
        # round floating price to nearest cent
        usd_value = f'${held_coins_usd[coin]:,.2f}'.replace('$-', '-$')
        print(f'{coin}\n\t{usd_value}')

        total_coin_values += held_coins_usd[coin]

    print(f'Total coin value in USD: ${total_coin_values:,.2f}'.replace('$-', '-$'))


def main():
    # Sets user arguments, then calls the class method to parse.
    args = set_args().parse_args()

    if args.clean:
        remove_portfolio()

    held_coins = read_portfolio()  # first try to get from stored param file

    if not held_coins:
        # we need to build json portfolio file
        held_coins = create_portfolio()
    elif args.clean:
        remove_portfolio()
        held_coins = create_portfolio()

    print_portfolio(held_coins)


if __name__ == '__main__':
    main()
