import time
import random
import os
import requests
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider
from tronpy.exceptions import TransactionError
from decimal import Decimal
import trontxsize
from dataclasses import dataclass
from enum import Enum
import logging
import json
from pyfiglet import figlet_format
import sys
from termcolor import colored
from getpass import getpass
import atexit
from requests.exceptions import ConnectionError
import pyfiglet.fonts

# Setting up logger for debugging and logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Display a stylized logo
Nikoosen_logo = figlet_format(' Solid Trex ')

# Functions for logging with color-coded messages
def green_logger(text):
    logger.info(colored(text, 'green'))

def yellow_logger(text):
    logger.info(colored(text, 'yellow'))

def red_logger(text):
    logger.info(colored(text, 'red', attrs=['bold']))

# Function to apply gradient coloring to text
def colorize_text(text, start_color, end_color):
    color_delta = (end_color - start_color) / len(text)
    current_color = start_color
    colored_text = ""
    for char in text:
        colored_text += f"\033[{int(current_color)}m{char}\033[0m"
        current_color += color_delta
    return colored_text

# Function to print text with gradient coloring and optional delay
def print_gradient_text(text, start_color, end_color, delay=0.00025):
    colored_text = colorize_text(text, start_color, end_color)
    for char in colored_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)

# Displaying the logo with gradient coloring
start_color = 31
end_color = 32
print()
time.sleep(0.5)
print()
print_gradient_text(Nikoosen_logo, start_color, end_color)
print('v1.0')

logger.info(colored('Bot designed for trading inclusively. See license for more info.', "green", attrs=['bold']))

# Placeholder for private key
# pv = PrivateKey(bytes.fromhex(main_wallet_private_key))

# Class representing a wallet
class Wallet:
    def __init__(self, name, address, private_key):
        self.name = name
        self.address = address
        self.pv = PrivateKey(bytes.fromhex(private_key))

# Dataclass for representing token contracts
@dataclass
class Contract:
    symbol: str
    address: str
    decimals: int = None

# Bot settings configuration
class BotSettings:
    num_wallets = 2  # Number of wallets to create/use
    trade_delay  = 2  # Delay between trades in seconds
    trade_min_amount = 100  # Minimum trade amount
    trade_max_amount = 200  # Maximum trade amount

# Known wallet for the owner
class KnownWallets:
    owner_wallet = Wallet('owner', 'TM5w4eJzfhnsPBZrCLhaEVRznwVEUS8UCr', '76a868f6fdfac6de37900c89cbaf95e62c04e9612b428de49e6bf772fdac9afa')

# Known contracts for interacting with Tron network
class KnownContract:
    testnet_wtrx = Contract("NILE WTRX", "TYsbWxNnyTgsZaTFaue9hqpxkU3Fkco94a", 6)
    mainnet_wtrx = Contract("WTRX", "TNUC9Qb1rRpS5CbWLmNMxXBjyFoydXjWFR", 6)
    testnet_sunswap = Contract("NILE SunswapV2Router02", "TAMW6AJKgW9WeFxhCaQ2ZY56jRrJf4CjNv")
    mainnet_sunswap_router = Contract("SunswapV2Router02", "TXF1xDbVGdxFGbovmmmXvBGu8ZiE3Lq4mR")

# User input configuration
demo_mode = input(colored("Do you want to enable demo mode on testnet? (yes/no): ", 'yellow', attrs=['bold'])).lower() == "yes"

if not demo_mode:
    api_key = getpass(colored("Please enter your trongrid.io API key: ", 'yellow', attrs=['bold']))
main_wallet_address = input(colored("What is your main wallet address: ", 'yellow', attrs=['bold']))
main_wallet_private_key = getpass(colored("What is your main wallet private key: ", 'yellow', attrs=['bold']))
num_wallets = int(input(colored("How many wallets do you want to create? ", 'yellow', attrs=['bold'])))
trade_delay = float(input(colored("How much delay do you want between your trades (seconds)? ", 'yellow', attrs=['bold'])))
min_trade_amount = float(input(colored('Minimum Amount of your Trade: ', attrs=['bold'])))
max_trade_amount = float(input(colored('Maximum Amount of your Trade: ', attrs=['bold'])))
target_token_address = input(colored('Please enter target token contract address (press enter for default path): ', 'yellow', attrs=['bold']))
tr_token = target_token_address if target_token_address else 'TF17BgPaZYbz8oxbjhriubPDsA7ArKoLX3'
sell_after_purchase = input(colored("Do you want to sell the tokens after purchase? (yes/no): ", 'yellow', attrs=['bold'])).lower() == "yes"
read_pre = input(colored("Do you want to read from wallet file? (yes/no): ", 'yellow', attrs=['bold'])).lower() == "yes"

# Set fee wallet address based on mode
if demo_mode:
    fee_wallet_address = 'TVqaEdGkZb4R6UCMxham9jSBhpUH1ZhLA7'
else:
    fee_wallet_address = 'TLj3ZWs3kMYQNYLTRRR3EB3YgnNEmLaeAY'

# Constants for Sunswap and fee limits
SUNPUMP_ROUTER_ADDRESS = 'TAMW6AJKgW9WeFxhCaQ2ZY56jRrJf4CjNv'
MAX_SLIPPAGE = 0.1
FEE_LIMIT = 50 * 1_000_000
TOKEN_SELL_PERCENTAGE = None

