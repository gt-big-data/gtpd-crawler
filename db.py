from pymongo import MongoClient as _MongoClient, TEXT as _TEXT

# Nothing outside of this file should touch variables that start with _underscores.
# Note that all of the scripts expect the database to be at localhost
# (but aren't using this connection string).
_CONNECTION_STRING = 'localhost'

_client = _MongoClient(_CONNECTION_STRING)
_db = _client['gtpd_logs']

# The two collections with data are exposed publicly.
criminal_logs = _db['criminal_logs']
non_criminal_logs = _db['non_criminal_logs']

# Add some indexes to make a bunch of operations way faster.
criminal_logs.create_index('case_number')
non_criminal_logs.create_index('case_number')

criminal_logs.create_index([('nature', _TEXT)])
non_criminal_logs.create_index([('nature', _TEXT)])
