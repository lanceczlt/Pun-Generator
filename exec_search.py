from flask import Flask, jsonify
import subprocess

app = Flask(__name__)


@app.route('/results')
def run_script():
    output = subprocess.check_output(['python', './src/query/query_rhymes.py', './my_db.sqlite', 'friar', '--mode', 'word'])
    return jsonify({'output': output.decode('utf-8')})
