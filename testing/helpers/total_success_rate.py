import json

# Initializing counters for successful attempts and total attempts
total_successful_attempts = 0
total_attempts = 0
total_no = 0

# Opening the .jsonl file to read the lines
with open('../phase1_results/summary_results_sorted.jsonl', 'r') as file:
    for line in file:
        entry = json.loads(line)  # Convert the JSON line to a Python dictionary
        total_successful_attempts += entry['yescount']
        total_no += entry['nocount']
        total_attempts += (entry['yescount'] + entry['nocount'])
        

# Calculating the overall success rate
overall_success_rate = total_successful_attempts / total_attempts if total_attempts != 0 else 0

# Printing the result
print(f'The total number of successful attempts is: {total_successful_attempts}')
print(f'The total number of unsuccessful attempts is: {total_no}')
print(f'The overall success rate is: {overall_success_rate:.4f}')