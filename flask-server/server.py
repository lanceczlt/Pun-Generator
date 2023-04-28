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


@app.route('/query', methods=['GET', 'POST'])
def query():
    # if request.method == 'GET':
    #     return "<h1>success<h1>"
    if request.method == 'POST':
        data = json.loads(request.data)
        word = data["input"]

        output = subprocess.check_output(
            ['python', '../src/query/query_rhymes.py', '../db.sqlite', word, '--mode', 'word'])
        return jsonify({'output': output.decode('utf-8')})

        # @app.route('/test')
        # def run_script():
        #     output = subprocess.check_output(
        #         ['python', './src/query/query_rhymes.py', './db.sqlite', 'rye', '--mode', 'word'])
        #     return jsonify({'output': output.decode('utf-8')})


if __name__ == "__main__":
    app.run(debug=True)
