import argparse
import os
from collections import defaultdict

import rapidjson as json


DATE_FORMAT = '%Y-%m-%d'


def partition_data(rows, court_type=''):
    partitioned_data = defaultdict(dict)
    for year in range(1920, 2020, 2):
        for row in rows:
            # some blanks from bad data
            if not row['start_date']:
                continue
            if date_filter(row):
                party = row['Party of Appointing President']
                if partitioned_data[year].get(party):
                    partitioned_data[year][party] += 1
                else:
                    partitioned_data[year][party] = 1
    return partitioned_data


def date_filter(row, year, step_size=2):
    return (row['start_date'].year <= year and (
        (row.get('end_date') and row.get('end_date').year >= year) or
        not row['end_date']))


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--directory', '-d', type=str, dest='directory', required=True,
        help="Directory to use")

    parser.add_argument(
        '--file_name', '-f', type=str, dest='file_name', required=True,
        help="File name to use")

    return parser.parse_args()


def main():
    args = _parse_args()

    file_name = args.file_name
    directory = args.directory
    out_file_name = f'paritioned_{file_name}.json'

    with open(os.path.join(directory, file_name)) as f:
        in_rows = json.load(f, datetime_mode=json.DM_ISO8601)
        partitioned_data = partition_data(in_rows)
    with open(os.path.join(directory, out_file_name), 'w') as f:
        json.dump(partitioned_data, f, datetime_mode=json.DM_ISO8601)


if __name__ == "__main__":
    main()
