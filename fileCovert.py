import pandas as pd
import json

def json_to_csv_pandas(json_file, csv_file):
    """
    Converts a JSON file (or list of JSON objects) to a CSV file using pandas.
    Handles moderately nested JSON by flattening it automatically.
    """
    # Read the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert JSON data to a pandas DataFrame
    # json_normalize helps flatten nested data
    if isinstance(data, list):
        df = pd.json_normalize(data)
    else:
        # If the root is a dictionary and contains a key with a list of records
        # you might need to specify the record path, e.g., data["issues"]
        # The following line treats the single dictionary as a single row
        df = pd.json_normalize([data]) 

    # Write the DataFrame to a CSV file, without the pandas index
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"Successfully converted {json_file} to {csv_file}")

# Example usage:
# Assuming you have a file named 'data.json' in the same directory
json_to_csv_pandas('data.json', 'output.csv')
