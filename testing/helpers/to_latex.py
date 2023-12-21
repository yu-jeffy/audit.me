import json

# Assuming your JSONL data is in a file called 'data.jsonl'
data_file = 'p2_sorted_summary_results.jsonl'

with open(data_file, 'r') as file:
    # Read JSONL lines one by one
    for line in file:
        entry = json.loads(line)  # Convert JSON line to a dictionary
        id = entry['id']
        address = entry['address'][:6] + "..." + entry['address'][-4:]
        description = entry['description']
        success_rate = entry['percent_success_rate']

        # Print formatted LaTeX table row
        print(f"{id} & {address} & {description} & {success_rate} \\\\")