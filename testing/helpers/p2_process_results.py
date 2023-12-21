import json
import os

def process_jsonl_files(directory, output_file):
    results = []

    # Ensure the directory exists
    if not os.path.exists(directory):
        print(f"The directory '{directory}' does not exist.")
        return

    # Iterate over all JSONL files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.jsonl'):
            yes_count = 0
            no_count = 0
            file_id, address = filename.split('-', 1)
            attacktype = ""
            address = address.replace('.jsonl', '')  # Remove the file extension to get the contract address

            # Open and read each JSONL file
            with open(os.path.join(directory, filename), 'r') as file:
                for line in file:
                    try:
                        record = json.loads(line)
                        attacktype = record.get('description', '')
                        # Count the YES and NO results
                        if record.get('result', {}).get('output_text', '') == "YES":
                            yes_count += 1
                        elif record.get('result', {}).get('output_text', '') == "NO":
                            no_count += 1
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {filename}")
            
            # Calculate the percent success
            total_counts = yes_count + no_count
            percent_success = (yes_count / total_counts) * 100 if total_counts > 0 else 0

            # Record the results for the output JSONL
            result_data = {
                "id": file_id,
                "address": address,
                "description": attacktype,
                "YES_count": yes_count,
                "NO_count": no_count,
                "percent_success_rate": percent_success
            }
            results.append(result_data)
    
    # Write the accumulated results to the output JSONL file
    with open(output_file, 'w') as f_out:
        for result in results:
            f_out.write(json.dumps(result) + '\n')

    print(f"Results analysis has been written to {output_file}.")

# Directory containing the JSONL files
directory_path = 'phase2_results'
# Output file path
output_file = 'p2_results_analysis.jsonl'

process_jsonl_files(directory_path, output_file)