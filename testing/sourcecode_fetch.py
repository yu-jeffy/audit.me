import requests
import json
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')

# Etherscan API endpoint
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# Function to get source code from Etherscan
def get_source_code(contract_address):
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
    if response.status_code == 200 and response.json()['status'] == '1':
        source_code = response.json()['result'][0]['SourceCode']
        return source_code
    else:
        print(f"Failed to fetch the source code for address: {contract_address}")
        return None

# Read the JSONL file, fetch the source code, and write to a new JSONL file
with open('52samplefull.jsonl', 'r') as jsonl_input, open('52samplesourcecode.jsonl', 'a') as jsonl_output:
    for line in jsonl_input:
        # Load the JSON object from the line
        data = json.loads(line)
        # Fetch the source code using the contract address
        contract_address = data['address']
        source_code = get_source_code(contract_address)
        if source_code:
            # Add the source code to the JSON object
            data['sourcecode'] = source_code
        else:
            # If source code not found, add an empty string or None
            data['sourcecode'] = ""
        # Write the updated JSON object to the output file
        jsonl_output.write(json.dumps(data) + '\n')
        # Wait for 1 second before making the next API call
        time.sleep(1)

print("Completed fetching source codes in 52samplesourcecode.jsonl")