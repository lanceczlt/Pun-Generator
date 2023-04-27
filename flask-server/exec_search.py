from flask import Flask, jsonify
import subprocess

app = Flask(__name__)


@app.route('/')
def run_script():
    output = subprocess.check_output(['python', './src/query/query_rhymes.py', './db.sqlite', 'rye', '--mode', 'word'])
    return jsonify({'output': output.decode('utf-8')})


if __name__ == "__main__":
    app.run(debug=True)