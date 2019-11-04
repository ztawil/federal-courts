import requests
from csv import DictWriter

from bs4 import BeautifulSoup


# character for '-'
WIKI_DASH = chr(8211)


def main():
    html_code = requests.get(
        'https://en.wikipedia.org/wiki/Party_divisions_of_United_States_Congresses').text
    soup = BeautifulSoup(html_code, 'lxml')
    table = soup.find('table', {'class': 'wikitable'})

    all_rows = table.find_all('tr')
    for i, row in enumerate(all_rows):
        if row.find_all('td') and row.find_all('td')[1].text.strip().split(WIKI_DASH)[0] == '1901':
            break
    start_idx = i

    all_rows = table.find_all('tr')
    for i, row in enumerate(all_rows[start_idx:]):
        if row.find_all('td') and row.find_all('td')[1].text.strip().split(WIKI_DASH)[0] == '2019':
            break
    end_idx = i + 1

    data = []
    party_colors = {
        '#FFB6B6': 'Republican',
        '#B0CEFF': 'Democratic',
    }

    for row in all_rows[start_idx: start_idx + end_idx]:
        columns = row.find_all('td')

        if len(columns) == 13:
            col = columns[12]
            president = clean_col(col)
            party_president = party_colors[get_color(col)]

        time_span = clean_col(columns[1])
        start_year, end_year = [int(x) for x in time_span.split(WIKI_DASH)]

        row_dict = {
            'title': clean_col(columns[0]),
            'time_span': time_span,
            'start_year': start_year,
            'end_year': end_year,
            'total_senators': mk_int(clean_col(columns[2])),
            'senate_democrats': mk_int(clean_col(columns[3])),
            'senate_republicans': mk_int(clean_col(columns[4])),
            'total_house': mk_int(clean_col(columns[7])),
            'house_democrats': mk_int(clean_col(columns[8])),
            'house_republicans': mk_int(clean_col(columns[9])),
            'president': president,
            'party_of_president': party_president,
        }

        senate_independents = mk_int(clean_col(columns[5]))
        row_dict['senate_independents'] = senate_independents
        house_independents = mk_int(clean_col(columns[10]))
        row_dict['house_independents'] = house_independents

        row_dict = hand_fill(row_dict)

        # re-assign after hand filling
        senate_independents = row_dict['senate_independents']

        senate_independents_color = get_color(columns[5])
        if senate_independents_color:
            if party_colors[senate_independents_color] == 'Democratic':
                row_dict['senate_dem_caucus'] = row_dict['senate_democrats'] + senate_independents
                row_dict['senate_rep_caucus'] = row_dict['senate_republicans']
            elif party_colors[senate_independents_color] == 'Republican':
                row_dict['senate_dem_caucus'] = row_dict['senate_democrats']
                row_dict['senate_rep_caucus'] = row_dict['senate_republicans'] + senate_independents
        else:
            row_dict['senate_dem_caucus'] = row_dict['senate_democrats']
            row_dict['senate_rep_caucus'] = row_dict['senate_republicans']

        if row_dict['senate_rep_caucus'] > row_dict['senate_dem_caucus']:
            row_dict['senate_majority_party'] = 'Republican'
        elif row_dict['senate_rep_caucus'] < row_dict['senate_dem_caucus']:
            row_dict['senate_majority_party'] = 'Democratic'
        elif row_dict['senate_rep_caucus'] == row_dict['senate_dem_caucus']:
            row_dict['senate_majority_party'] = row_dict['party_of_president']

        if row_dict['party_of_president'] == 'Republican':
            row_dict['president_party_senate_majority'] = \
                row_dict['senate_rep_caucus'] - row_dict['senate_dem_caucus']
        else:
            row_dict['president_party_senate_majority'] = \
                row_dict['senate_dem_caucus'] - row_dict['senate_rep_caucus']

        row_dict['president_party_senate_majority_perc'] = \
            row_dict['president_party_senate_majority'] / row_dict['total_senators']

        data.append(row_dict)

    with open('./data/congress_data.csv', 'w') as f:
        writer = DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    return data


def clean_col(col):
    return ''.join(col.text.strip()).split('[')[0]


def mk_int(v):
    if v.isdigit():
        return int(v)
    else:
        return 0


def get_color(col):
    if col.attrs.get('style'):
        return col.attrs['style'].split(':')[1]
    else:
        return None


def hand_fill(row_dict):
    """Updates the data from wikipedia when there is a split in the number of senators in the term.
    Chosen values are based on reading the citations and choosing the most appropriate (i.e. value)
    that is most representative of the Congression term.
    """

    data_map = {
        '115th': {
             'senate_democrats': 47,
             'senate_republicans': 51,
        },
        '111th': {
             'senate_democrats': 57,
             'senate_republicans': 41,
        },
        '107th': {
             'senate_republicans': 49,
             'senate_independents': 1,
        },
    }
    if row_dict['title'] in data_map:
        row_title = row_dict['title']
        data_dict = [data_dict for title, data_dict in data_map.items() if title == row_title][0]
        row_dict.update(data_dict)
    return row_dict


if __name__ == "__main__":
    data = main()
