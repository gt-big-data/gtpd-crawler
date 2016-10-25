# This file is the main driver the crawls GTPD logs and stores things in the database.
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup as Soup

import db

# This is the base URL where we grab data from.
# Note the wildcard page number at the end.
CRIMINAL_LOGS_URL = 'http://www.police.gatech.edu/crimeinfo/crimelogs/crimelog.php?offset=%d'

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
    if len(s.split(' ')) == 3:
        # This record is missing a time component.
        # Can be a poorly formed start/end date or just a regular reported date.
        # Handle it by setting it to midnight of that day.
        s += ' 00 00'
    return datetime.strptime(s, DATE_FORMAT)

def parse_occurred_info(occurred_info):
    # `clean(...)` strips a lot of stuff out so this becomes the correct format.

    parts = occurred_info.split('-')
    print(parts[0])
    start_date = to_date(parts[0])
    if len(parts) == 1:
        end_date = None
    else:
        end_date = to_date(parts[1])
    return start_date, end_date

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
    nature = nature
    location = location.split('Location:')[1]
    data = {
        'case_number': clean(cells[0].text),
        'date_reported': clean(cells[1].text),
        'date_started': date_started,
        'date_ended': date_ended,
        'disposition': clean(cells[3].text),
        'status': clean(cells[4].text),
        'location': clean(location),
        'nature': clean(nature)
    }
    return data

def get_page(base_url, offset):
    """
    Download a page of logs with a given offset.

    Arguments:
    base_url -- A string refering to the URL for criminal or non-criminal logs.
    offset -- The value for the offset URL parameter in the URL.

    Return the HTML content of the page.
    """
    # TODO: How do we detect an invalid offset?
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
    # Save all of the records in the DB.
    for record in records:
        db.criminal_logs.insert(record)
    return len(records)

def scrape_non_criminal_page(html):
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
    for record in records:
        # Overwrite existing logs with the same case number.
        db.non_criminal_logs.update({'case_number': record['case_number']}, record, {'upsert': True})
    return len(records)

def main():
    # TODO: Call scrape_[non]_criminal_page(offset) in a loop.
    # TODO: When should we terminate?
    # TODO: What if there's an error?
    records_found = scrape_criminal_page(0)
    print('Scraped %d records' % records_found)

# Run main() if we're directly running this file.
if __name__ == '__main__':
    main()
