import csv
import json

# Read the CSV file and build a mapping of last 4 characters to full contract addresses
# Convert both keys and values to lowercase for case-insensitive matching
address_mapping = {}
with open('defi_sok_sc_causes.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        # Extract the last 4 characters of the contract address and convert to lowercase
        last_four_chars = row['contract'][-4:].lower()
        # Map the last four characters to the full contract address
        address_mapping[last_four_chars] = row['contract']

# Read the JSONL file, update the addresses, and write to a new JSONL file
with open('52sampleraw.jsonl', 'r') as jsonl_input, open('52samplefull.jsonl', 'a') as jsonl_output:
    for line in jsonl_input:
        # Load the JSON object from the line
        data = json.loads(line)
        # Fetch the full address using the last 4 characters from the address_mapping
        # Convert the address to lowercase for case-insensitive matching
        last_four_chars = data['address'][-4:].lower()
        full_address = address_mapping.get(last_four_chars, None)
        if full_address:
            # Update the address with the full address
            data['address'] = full_address
        else:
            # If address not found, you can choose to skip, raise an error, or keep the original
            print(f"Warning: Address ending with '{last_four_chars}' not found in CSV.")
            # For this example, we'll keep the original address
        # Write the updated JSON object to the output file
        jsonl_output.write(json.dumps(data) + '\n')

print("Completed updating addresses in 52samplefull.jsonl")