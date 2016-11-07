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

@app.route('/api/by_year')
def logs_by_year():
    pipeline = [{
        '$match': {
            'date_started': {
                '$ne': None
            }
        }
    },
    {
        '$project': {
            'year': {'$year': '$date_started'}
        }
    }, {
        '$group': {
            '_id': '$year',
            'count': {'$sum': 1}
        }
    }, {
        '$project': {
            '_id': False,
            'year': '$_id',
            'count': '$count'
        }
    }, {
        '$sort': {
            'count': 1
        }
    }]
    data = {
        'criminal_by_year': list(db.criminal_logs.aggregate(pipeline)),
        'non_criminal_by_year': list(db.non_criminal_logs.aggregate(pipeline))
    }
    return jsonify(data)

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
