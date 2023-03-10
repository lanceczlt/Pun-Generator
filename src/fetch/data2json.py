import os
import csv
import json

# define the output json format
output_template = {
    "type": "file_name",
    "phrase(s?)": [],
    "source": {}
}

# list of all csv and txt files in the current directory
data_dir = './data/'
csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
txt_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]

for file_name in csv_files:
    with open(os.path.join(data_dir, file_name)) as f:
        csv_reader = csv.reader(f)
        first_column = [row[0] for row in csv_reader]
        
        # fill in the output dictionary with the extracted data
        output = output_template.copy()
        output["type"] = os.path.splitext(file_name)[0]
        output["phrase(s?)"] = first_column
        
        print(json.dumps(output))

for file_name in txt_files:
    with open(os.path.join(data_dir, file_name)) as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        
        # fill in the output dictionary with the extracted data
        output = output_template.copy()
        output["type"] = os.path.splitext(file_name)[0]
        output["phrase(s?)"] = lines
        
        print(json.dumps(output))