# gtpd-crawler

A crawler for GTPD crime logs.

## Installation

You need:

* Python (2 or 3)
* MongoDB

### Python Packages

You also need a few Python packages:

    pip install -r requirements.txt

## Run the crawler

In a separate terminal window, run `mongod` to start MongoDB on your local computer.

Then run:

    ./scripts/run.sh or scripts\run.bat

# Importing and Exporting Data

Data can be imported to your local MongoDB by running:

    ./scripts/import_mongo.sh or scripts\import_mongo.bat

Data can be saved to the repository with:

    ./scripts/export_mongo.sh or scripts\export_mongo.bat
