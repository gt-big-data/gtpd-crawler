#!/usr/bin/env python

# This file is the main driver the crawls GTPD logs and stores things in the database.
import re
from datetime import datetime
from sys import argv

import requests
from bs4 import BeautifulSoup as Soup

import db

# This is the base URL where we grab data from.
# Note the wildcard page number at the end.
CRIMINAL_LOGS_URL = 'http://www.police.gatech.edu/crimeinfo/crimelogs/crimelog.php?offset=%d'
NON_CRIMINAL_LOGS_URL = 'http://www.police.gatech.edu/crimeinfo/crimelogs/noncrimelog.php?offset=%d'

# This selector returns the same thing in browsers and `html.parser`.
# For a more robust parser, deal with installing `lxml`.
ROWS_SELECTOR = 'form > table tr'

def clean(s):
    # Replace multiple whitespace characters with just a single space.
    s = re.sub('\W+', ' ', s)
    # Remove leading and trailing whitespace.
    s = s.strip()
    return s

def to_date(s):
    DATE_FORMAT = '%m %d %Y %H %M'
    # Convert whatever mess of a date string we are given into "mm dd yyyy [hh mm]".
    s = clean(s)
    parts = len(s.split(' '))
    if parts <= 1:
        # We've acquired an empty string. Pretend it doesn't exist.
        return None
    if parts == 3:
        # This record is missing a time component.
        # Can be a poorly formed start/end date or just a regular reported date.
        # Handle it by setting it to midnight of that day.
        s += ' 00 00'
    if parts > 5:
        # Something is very malformed, just take the first portion and hope it's a valid date.
        # e.g. "5/5/2016 @ 22:52   @ 23:00" => "5 5 2016 22 52 23 00" => "5 5 2016 22 52".
        s = ' '.join(s.split(' ')[:5])
    return datetime.strptime(s, DATE_FORMAT)

def parse_occurred_info(occurred_info):
    # `clean(...)` strips a lot of stuff out so this becomes the correct format.

    parts = occurred_info.split('-')
    start_date = to_date(parts[0])
    if len(parts) == 1:
        end_date = None
    else:
        end_date = to_date(parts[1])
    return start_date, end_date

CURRENT_YEAR = datetime.now().year

def is_valid(data):
    # Make sure key dates aren't None.
    if data['date_started'] is None or data['date_reported'] is None:
        return False
    # Make sure all of the dates are sane.
    date_started_year = data['date_started'].year
    date_reported_year = data['date_reported'].year
    if date_started_year < 2006 or date_started_year > CURRENT_YEAR:
        print('Invalid date started: %s' % data['date_started'])
        return False
    if date_reported_year < 2006 or date_reported_year > CURRENT_YEAR:
        print('Invalid date reported: %s' % data['date_reported'])
        return False

    # Make sure case_number makes sense
    if data['case_number'] is None or len(data['case_number']) == 0:
        print('Invalid case number: %s' % data['case_number'])
        return False

    # Several fields, notably date_ended, disposition, and location can be empty/null
    # and still be considered valid. Otherwise we'd have to remove too many records.

    # We've made it past all of the checks so consider the data valid.
    return True

def parse_record(row_1, row_2):
    """
    Convert two rows of HTML into a single object.

    Arguments:
    row_1 -- The first in a pair of HTML rows.
    row_2 -- The second in a pair of HTML rows.

    Return an object representing the single record from the two rows.
    """

    # The first row contains a bunch of cell.s
    # The second row is just one big cell.
    cells = row_1.find_all('td')
    date_started, date_ended = parse_occurred_info(cells[2].text)
    location, nature = row_2.text.split('Nature:')
    date_reported, _ = parse_occurred_info(cells[1].text)
    nature = nature
    location = location.split('Location:')[1]
    data = {
        'case_number': clean(cells[0].text),
        'date_reported': date_reported,
        'date_started': date_started,
        'date_ended': date_ended,
        'disposition': clean(cells[3].text),
        'status': clean(cells[4].text),
        'location': clean(location),
        'nature': clean(nature)
    }
    data['valid'] = is_valid(data)
    return data

def get_page(base_url, offset):
    """
    Download a page of logs with a given offset.

    Arguments:
    base_url -- A string refering to the URL for criminal or non-criminal logs.
    offset -- The value for the offset URL parameter in the URL.

    Return the HTML content of the page.
    """
    url = base_url % offset
    response = requests.get(url)
    return response.text

def scrape_page(html):
    """
    Convert an HTML page into a list of crime records.

    Arguments:
    html -- A string of the HTML of the page we are parsing.

    Return a list of crimes logged on that page.
    """
    # Note that criminal data is parsed exactly the same as non-criminal data.
    soup = Soup(html, 'html.parser')
    rows = soup.select(ROWS_SELECTOR)
    rows = rows[4:] # Skip the first four rows because those are headers.

    records = []
    # A single record exists in two rows of the table.
    for i in range(0, len(rows), 2):
        row_1 = rows[i]
        row_2 = rows[i + 1]
        data = parse_record(row_1, row_2)
        records.append(data)
    return records

def scrape_criminal_page(offset):
    """
    Scrape a page of criminal logs starting from `offset`.

    Updates the DB based on its findings.

    Arguments:
    offset -- The offset to jump into the logs.

    Return the number of records found (usually 100).
    """
    # Download the HTML content.
    html = get_page(CRIMINAL_LOGS_URL, offset)
    # Parse the HTML for individual police logs.
    records = scrape_page(html)
    # Save all of the records into the DB.
    new_records = 0
    for record in records:
        # Overwrite existing logs with the same case number.
        result = db.criminal_logs.update_one({'case_number': record['case_number']}, {'$set': record}, upsert=True)
        # Increment `new_records` if we inserted (but not if we updated).
        new_records += 1 - result.matched_count
    return new_records, len(records)

def scrape_non_criminal_page(offset):
    """
    Scrape a page of non-criminal logs starting from `offset`.

    Updates the DB based on its findings.

    Arguments:
    offset -- The offset to jump into the logs.

    Return the number of records found (usually 100).
    """
    # Download the HTML content.
    html = get_page(NON_CRIMINAL_LOGS_URL, offset)
    # Parse the HTML For individual police logs.
    records = scrape_page(html)
    # Save all of the records into the DB.
    new_records = 0
    for record in records:
        # Overwrite existing logs with the same case number.
        result = db.non_criminal_logs.update_one({'case_number': record['case_number']}, {'$set': record}, upsert=True)
        # Increment `new_records` if we inserted (but not if we updated).
        new_records += 1 - result.matched_count
    return new_records, len(records)

def print_usage():
    print(argv[0] + ' <criminal/non-criminal> [offset]')
    return -1

def fix(record):
    record['valid'] = is_valid(record)
    return record

def update():
    print('Updating non-criminal logs.')
    i = 0
    for record in db.non_criminal_logs.find():
        if i % 1000 == 0:
            print(i)
        record = fix(record)
        db.non_criminal_logs.update_one({'case_number': record['case_number']}, {'$set': record})
        i += 1

    i = 0
    for record in db.criminal_logs.find():
        if i % 1000 == 0:
            print(i)
        record = fix(record)
        db.criminal_logs.update_one({'case_number': record['case_number']}, {'$set': record})
        i += 1
    print('Updating criminal logs.')

def main():
    if len(argv) < 2:
        return print_usage()
    type = argv[1]
    if type == 'criminal':
        scrape_function = scrape_criminal_page
    elif type == 'non-criminal':
        scrape_function = scrape_non_criminal_page
    else:
        return print_usage()

    try:
        offset = int(argv[2])
    except Exception:
        offset = 0
    # Keep scraping pages until no new records are found.
    # When we hit the end of the list (or the beginning of the list we've already processed),
    # we will add 0 new records.
    new_records = -1
    while new_records != 0:
        # There's 100 records on every page. Don't question it.
        print('Scraping records from %d to %d' % (offset, offset + 100))
        new_records, total_records = scrape_function(offset)
        offset += total_records
    print('Stopping becuase there are no new records to crawl.')

# Run main() if we're directly running this file.
if __name__ == '__main__':
    # update()
    main()
