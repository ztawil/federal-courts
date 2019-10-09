import argparse
from collections import defaultdict

import rapidjson as json


DATE_FORMAT = '%Y-%m-%d'


def partition_data(rows):
    partitioned_data = defaultdict(dict)
    for year in range(1920, 2020, 2):
        for row in rows:
            if row['start_date'].year >= year and (
                    row['end_date'].year <= year or not row['end_date']):
                party = row['Party of Appointing President']
                if partitioned_data[year].get(party):
                    partitioned_data[year][party] += 1
                else:
                    partitioned_data[year][party] = 0
    return partitioned_data


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
