# gtpd-crawler

A crawler for GTPD crime logs.

## Installation

You need:

* Python (2 or 3)
* MongoDB

### Python Packages

You also need the following Python packages:

    pip install requests pymongo bs4

## Run the crawler

In a separate terminal window, run `mongod` to start MongoDB on your local computer.

Then run:

    python crawler.py
