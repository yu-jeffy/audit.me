import json
import os

# Folder where the contract results are stored
results_dir = '52resultsrepeatability'
# The output file
output_file_path = 'summary_results.jsonl'

summary_results = []

# Get a sorted list of filenames
file_list = sorted(os.listdir(results_dir))

# Go through each file in the sorted list
for filename in file_list:
    if filename.endswith(".jsonl"):
        filepath = os.path.join(results_dir, filename)
        yes_count, no_count = 0, 0
        
        # Open and process each file
        with open(filepath, 'r') as file:
            for line in file:
                entry = json.loads(line)
                result = entry["result"]["output_text"]
                if result == "YES":
                    yes_count += 1
                elif result == "NO":
                    no_count += 1
        
        # Total responses for the success rate calculation.
        total_responses = yes_count + no_count  # This should be 40, but we calculate it just to be safe

        # Ensure we don't divide by zero when calculating the success rate.
        success_rate = yes_count / total_responses if total_responses > 0 else 0.0
        
        # Extract contract_id and address from the filename
        contract_id_str, address = filename.split(' - ')
        contract_id = int(contract_id_str)
        address = address.rstrip('.jsonl')  # Remove extension from the address
        
        # Extract attacktype from any entry (assuming all entries in a file have the same attacktype)
        attacktype = entry["attacktype"] if "attacktype" in entry else "Unknown"

        # Append the summary for each contract to the list
        summary_results.append({
            "contract_id": contract_id,
            "address": address,
            "attacktype": attacktype,
            "yescount": yes_count,
            "nocount": no_count,
            "successrate": success_rate
        })

# Write the summary to the output file
with open(output_file_path, 'a') as output_file:
    for summary in summary_results:
        output_file.write(json.dumps(summary) + '\n')

print(f"Processed {len(summary_results)} contracts. Summary written to {output_file_path}")