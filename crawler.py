# This file is the main driver the crawls GTPD logs and stores things in the database.
import requests
from bs4 import BeautifulSoup as Soup

import db

# This is the base URL where we grab data from.
# Note the wildcard page number at the end.
CRIMINAL_LOGS_URL = 'http://www.police.gatech.edu/crimeinfo/crimelogs/crimelog.php?offset=%d'

# This selector returns the same thing in browsers and `html.parser`.
# For a more robust parser, deal with installing `lxml`.
ROWS_SELECTOR = 'form > table tr'

def parse_record(row_1, row_2):
    """Convert two rows of HTML into a single object.

    Arguments:
    row_1 -- The first in a pair of HTML rows.
    row_2 -- The second in a pair of HTML rows.

    Return an object representing the single record from the two rows."""
    # TODO: Do something!
    pass

def get_page(base_url, offset):
    """Download a page of logs with a given offset.

    Arguments:
    base_url -- A string refering to the URL for criminal or non-criminal logs.
    offset -- The value for the offset URL parameter in the URL.

    Return the HTML content of the page.
    """
    url = base_url % offset
    response = requests.get(url)
    return response.text

def scrape_page(html):
    """Convert an HTML page into a list of crime records.

    Arguments:
    html -- A string of the HTML of the page we are parsing.

    Return a list of crimes logged on that page."""
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
    """Scrape a page of criminal logs starting from `offset`.

    Updates the DB based on its findings.

    Arguments:
    offset -- The offset to jump into the logs.

    Return the number of records found.
    """
    html = get_page(CRIMINAL_LOGS_URL, offset)
    records = scrape_page(html)
    for record in records:
        db.criminal_logs.insert(record)
    return len(records)

def scrape_non_criminal_page(html):
    html = get_page(NON_CRIMINAL_LOGS_URL, offset)
    records = scrape_page(html)
    for record in records:
        db.non_criminal_logs.insert(record)
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
