from csv import DictWriter

from bs4 import BeautifulSoup

# Has a robot detection so had to save the HTML manually, not through a GET
# https://www.fjc.gov/node/7511
with open('./data/unsuccessful_nominations.html') as f:
    html_code = f.read()
soup = BeautifulSoup(html_code, 'lxml')

# First row, one column president
# Second row is the headers, Congress, Nominee, Court, Nomination Date, Outcome
scrapped_data = []
for table in soup.find_all('table'):
    president = table.find('tr').text
    for row in table.find_all('tr')[2:]:
        columns = row.find_all('td')
        # congress column is blank for the rows after the first time mentioned
        # look for a value, otherwise use the previous.
        congress = columns[0].text.strip('\xa0') or congress
        scrapped_data.append(
            {
                'president': president,
                'congress': congress,
                'nominee': columns[1].text,
                'court_name': columns[2].text,
                'nomination_date': columns[3].text,
                'outcome': columns[4].text,
            }
        )

with open('./data/unsuccesful_nominations.csv', 'w') as f:
    writer = DictWriter(f, fieldnames=scrapped_data[0].keys())
    writer.writeheader()
    writer.writerows(scrapped_data)