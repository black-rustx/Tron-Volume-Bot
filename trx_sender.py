from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionError
from decimal import Decimal
import trontxsize  # Import module to calculate transaction size
import requests
from tronpy.providers import HTTPProvider

# Create a connection to the Tron network
# You can use HTTPProvider with an API key if needed
# tron = Tron(HTTPProvider(api_key="your-api-key"))

tron = Tron(network="nile")  # Connect to the Nile test network

# Destination address for transferring TRX
recipient_address = input('Please enter your recipient address: ')

# Request the wallet file name
wallet_file = input("Enter the wallet file name (e.g., wallets1.txt): ")

# Function to read wallets from a file
def read_wallets(file_path):
    wallets = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Each wallet entry spans 3 lines in the file
        for i in range(0, len(lines), 3):
            address = lines[i].strip().replace('Address: ', '')
            private_key = lines[i+1].strip().replace('Private Key: ', '')
            wallets.append({
                'address': address,
                'private_key': private_key
            })
    return wallets

# Function to fetch the bandwidth price (cost per bandwidth point) from the Tron network
def get_bandwidth_price():
    url = "https://api.trongrid.io/wallet/getchainparameters"  # API endpoint to get chain parameters
    response = requests.get(url)
    data = response.json()
    # Extract bandwidth price in TRX (adjusting for unit conversion)
    bandwidth_price = Decimal(data['chainParameter'][3]['value']) / Decimal(1_000_000)
    return bandwidth_price

# Function to calculate transaction fees
def calculate_transaction_fee(transaction):
    bandwidth_price = get_bandwidth_price()
    # Calculate transaction size in bandwidth points
    tx_size = trontxsize.get_tx_size({"raw_data": transaction._raw_data, "signature": transaction._signature})
    bandwidth_points = Decimal(tx_size) * bandwidth_price
    return bandwidth_points

# Function to send TRX from a wallet to the recipient address
def send_trx_from_wallet(wallet, recipient_address):
    private_key = PrivateKey(bytes.fromhex(wallet["private_key"]))  # Convert private key from hex
    sender_address = wallet["address"]

    try:
        # Fetch the balance of the sender's wallet
        balance = Decimal(tron.get_account_balance(sender_address))
        print(f"Current balance of {sender_address}: {balance} TRX")

        available_balance = balance
        estimated_fees = []

        if balance > 0:
            # Step 1: Build a transaction for fee estimation
            txn = tron.trx.transfer(
                sender_address,
                recipient_address,
                int(balance)  # Use entire balance for estimation
            ).memo("Fee estimation").build()

            # Calculate estimated transaction fee
            estimated_fee = calculate_transaction_fee(txn) * 10
            estimated_fees.append(estimated_fee)
            print(f"Estimated fee for transaction to {wallet['address']}: {estimated_fee} TRX")

            # Total estimated fees
            total_estimated_fee = sum(estimated_fees)
            print(f"Total estimated fees: {total_estimated_fee} TRX")

            # Step 2: Check if balance is sufficient for fees
            if available_balance <= total_estimated_fee:
                print("Not enough balance to cover all transaction fees.")
                return

            # Deduct fees to calculate the final amount available for sending
            available_balance -= total_estimated_fee

            # Build the transaction to send remaining balance to the recipient
            txn = (
                tron.trx.transfer(
                    sender_address,
                    recipient_address,
                    int((available_balance) * 1_000_000)  # Convert TRX to SUN (smallest unit)
                )
                .memo("TRX distribution")  # Add a transaction memo
                .build()
                .sign(private_key)  # Sign the transaction with the sender's private key
            )

            # Broadcast the transaction to the network and wait for confirmation
            txn_result = txn.broadcast().wait()
            print(f"Transaction result: {txn_result}")

            # Check if the transaction result includes a txid
            if 'txid' in txn_result:
                print(f"Sent {balance} TRX from {sender_address} to {recipient_address}: {txn_result['txid']}")
            else:
                print(f"Transaction did not include 'txid'. Full result: {txn_result}")

        else:
            print(f"Insufficient balance in wallet {sender_address}.")

    except TransactionError as e:
        # Handle transaction-related errors
        print(f"Transaction error while transferring from {sender_address} to {recipient_address}: {e}")
    except Exception as e:
        # Handle other exceptions
        print(f"Error occurred while transferring from {sender_address} to {recipient_address}: {e}")

# Read wallets from the specified file
wallets = read_wallets(wallet_file)

# Process each wallet and send TRX
for wallet in wallets:
    send_trx_from_wallet(wallet, recipient_address)
