from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import json

app = Flask(__name__)
CORS(app)

# class Data:
#     def update_params(params: object) -> object:
# output = "success"


@app.route('/')
def home():
    return "<h1>Hello World<h1>"


@app.route('/query', methods=['POST'])
def query():
    if request.method == 'POST':
        data = json.loads(request.data)
        word = data["input"]
        filters = data["filters"]

        filter_list = []
        for filter_name, isSelected in filters.items():
            if isSelected:
                filter_list.append(filter_name)

        filter_str = json.dumps(filter_list)

        try:
            output = subprocess.check_output(
                ['python', '../src/query/query_rhymes.py', '../src/my_db.sqlite', word, '--filters', filter_str, '--mode', 'word'])
        except subprocess.CalledProcessError as e:
            output = e.output

        return jsonify({'output': output.decode('utf-8')})


if __name__ == "__main__":
    app.run(debug=True)
