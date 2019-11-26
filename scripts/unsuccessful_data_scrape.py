import re
from csv import DictWriter
from datetime import datetime

from bs4 import BeautifulSoup

# Has a robot detection so had to save the HTML manually, not through a GET
# https://www.fjc.gov/node/7511
with open('./data/unsuccessful_nominations.html') as f:
    html_code = f.read()
soup = BeautifulSoup(html_code, 'lxml')

DATE_FORMAT = '%B %d, %Y'

# First row, one column president
# Second row is the headers, Congress, Nominee, Court, Nomination Date, Outcome
scrapped_data = []
for table in soup.find_all('table'):
    president = table.find('tr').text
    for row in table.find_all('tr')[2:]:
        columns = row.find_all('td')
        # congress column is blank for the rows after the first time mentioned
        # look for a value, otherwise use the previous.
        if columns[0].text.strip('\xa0'):
            congress, yearspan = columns[0].text.strip('\xa0').split()  # 1st (1789-1791)
            split_yearspan = yearspan.split('-')
            congress_start_year = split_yearspan[0][1:]
            congress_end_year = split_yearspan[1][:-1]
            congress_end_year = None if congress_end_year == 'present' else congress_end_year
        raw_nomination_date = columns[3].text
        if re.findall(r'.*(\(recess appointment\))', raw_nomination_date):
            recess_appointment = True
        else:
            recess_appointment = False
        str_nomination_date = raw_nomination_date.strip(' (recess appointment)')
        try:
            nomination_date = datetime.strptime(str_nomination_date, DATE_FORMAT)
        except ValueError:
            nomination_date = datetime.strptime(str_nomination_date, '%B, %d, %Y')
        scrapped_data.append(
            {
                'president': president,
                'congress': congress,
                'congress_start_year': congress_start_year,
                'congress_end_year': congress_end_year,
                'nominee': columns[1].text,
                'court_name': columns[2].text,
                'nomination_date': nomination_date,
                'recess_appointment': recess_appointment,
                'outcome': columns[4].text,
            }
        )

with open('./data/unsuccessful_nominations.csv', 'w') as f:
    writer = DictWriter(f, fieldnames=scrapped_data[0].keys())
    writer.writeheader()
    writer.writerows(scrapped_data)
