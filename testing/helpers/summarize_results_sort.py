import json

# The path to the JSONL file to sort
input_file_path = 'p2_results_analysis.jsonl'
# The path to the new sorted JSONL file
sorted_file_path = 'p2_sorted_summary_results.jsonl'

# Read in all entries from the JSONL file
entries = []
with open(input_file_path, 'r') as input_file:
    for line in input_file:
        entry = json.loads(line)
        # Check to ensure 'id' can be cast to an integer
        try:
            entry['id'] = int(entry['id'])
            entries.append(entry)
        except ValueError:
            print(f"Warning: ID '{entry['id']}' is not a valid integer and will be excluded from sorting.")

# Sort the entries by contract_id numerically
sorted_entries = sorted(entries, key=lambda x: x['id'])

# Write them back to a new file
with open(sorted_file_path, 'w') as output_file:
    for entry in sorted_entries:
        # Convert the `id` back to a string if necessary
        entry['id'] = str(entry['id'])
        output_file.write(json.dumps(entry) + '\n')

print(f"Sorted file written to {sorted_file_path}")