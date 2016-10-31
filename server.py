from flask import Flask, jsonify, send_file, send_from_directory
app = Flask(__name__)

import db

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route("/api/total")
def total_logs():
    data = {
        'criminal_count': db.criminal_logs.count(),
        'non_criminal_count': db.non_criminal_logs.count()
    }
    return jsonify(data)

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True)
