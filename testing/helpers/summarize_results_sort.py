import json

# The path to the JSONL file to sort
input_file_path = 'summary_results.jsonl'
# The path to the new sorted JSONL file
sorted_file_path = 'sorted_summary_results.jsonl'

# Read in all entries from the JSONL file
with open(input_file_path, 'r') as input_file:
    entries = [json.loads(line) for line in input_file]

# Sort the entries by contract_id
sorted_entries = sorted(entries, key=lambda x: x['contract_id'])

# Write them back to a new file
with open(sorted_file_path, 'w') as output_file:
    for entry in sorted_entries:
        output_file.write(json.dumps(entry) + '\n')

print(f"Sorted file written to {sorted_file_path}")