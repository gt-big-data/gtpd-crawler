from pymongo import MongoClient as _MongoClient

# Nothing outside of this file should touch variables that start with _underscores.
# Note that all of the scripts expect the database to be at localhost
# (but aren't using this connection string).
_CONNECTION_STRING = 'localhost'

_client = _MongoClient(_CONNECTION_STRING)
_db = _client['gtpd_logs']

# The two collections with data are exposed publicly.
criminal_logs = _db['criminal_logs']
non_criminal_logs = _db['non_criminal_logs']
