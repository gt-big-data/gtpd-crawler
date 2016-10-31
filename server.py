from flask import Flask, jsonify, send_file, send_from_directory

import db

app = Flask(__name__)

# Special route because "/" technically redirects to "index.html".
@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/api/total')
def total_logs():
    data = {
        'criminal_count': db.criminal_logs.count(),
        'non_criminal_count': db.non_criminal_logs.count()
    }
    return jsonify(data)

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
