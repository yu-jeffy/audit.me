import requests
from web3 import Web3
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

# Initialize web3 with Infura
web3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_API_KEY}'))

# Etherscan API endpoint
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# Smart contract address (replace with actual contract address)
contract_address = "0x...Contract Address..."

# Forming the API request
params = {
    'module': 'contract',
    'action': 'getsourcecode',
    'address': contract_address,
    'apikey': ETHERSCAN_API_KEY
}

# Sending the request
response = requests.get(ETHERSCAN_API_URL, params=params)

# Parsing the response
if response.status_code == 200:
    source_code = response.json()['result'][0]['SourceCode']
    # Do something with the source code
    print(source_code)
else:
    print("Failed to fetch the source code")