import os
import re
import csv

# Define parameters to test
parameter_values = [
    {"param1": value1, "param2": value2}  # Replace with actual parameters
    for value1 in range(10) for value2 in range(5)
]

# Path to the CLI program and the algorithm file
cli_command = "prosperity3bt"
algorithm_path = "algorithm_round_3.py"

results = []

for params in parameter_values:
    # Construct the CLI command with parameters
    command = f"{cli_command} {algorithm_path}"  # Adjust according to your CLI
    output = os.popen(command).read()  # Run the command and capture output
    
    # Print the raw output for debugging
    print("Command Output:\n", output)
    
    # Extract the 'Total profit' value using regex
    match = re.search(r"Total profit:\s*([\d,-]+)", output)
    if match:
        total_profit = int(match.group(1).replace(",", ""))
        params["total_profit"] = total_profit
        results.append(params)

# Sort results by profit and store the best one
best_result = max(results, key=lambda x: x["total_profit"])

# Save results to a CSV file
with open("backtest_results.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["param1", "param2", "total_profit"])
    writer.writeheader()
    writer.writerows(results)

print("Best Parameters:", best_result)
