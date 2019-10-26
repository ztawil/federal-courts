import argparse
import csv
import os
from collections import defaultdict

import column_name_maps
from database_utils import get_session, recreate_db
from models.models import Appointment, Education, Judge


DATE_FORMAT = '%Y-%m-%d'

MAX_DUP_COLS = 6


def get_models(row):
    """
    """
    judge_row = Judge(**{
        slug_col: clean_data(slug_col, row[col])
        for col, slug_col in column_name_maps.demographic_col_map.items()
    })

    appointment_dict = defaultdict(dict)
    for i in range(1, MAX_DUP_COLS):
        for col, slug_col in column_name_maps.appt_col_map.items():
            appt_row_val = row.get(_get_column_pattern(col, i))
            if appt_row_val:
                appointment_dict[i][slug_col] = clean_data(slug_col, appt_row_val)
        if len(appointment_dict[i]) == 0:
            appointment_dict.pop(i)
            continue
        judge_row.appointments.append(Appointment(**appointment_dict[i]))

    education_dict = defaultdict(dict)
    for i in range(1, MAX_DUP_COLS):
        for col, slug_col in column_name_maps.edu_col_map.items():
            edu_row_val = row.get(_get_column_pattern(col, i))
            if edu_row_val:
                education_dict[i][slug_col] = clean_data(slug_col, edu_row_val)
        if len(education_dict[i]) == 0:
            education_dict.pop(i)
            continue
        judge_row.educations.append(Education(**education_dict[i]))

    return judge_row


def clean_data(column_name, value):
    cleaning_functions = {
        'birth_year': _clean_year,
        'degree_year': _clean_year
    }
    if not value:
        return

    stripped_value = value.strip()
    if not stripped_value:
        return None

    if column_name not in cleaning_functions:
        # Converts empty strings to Null
        return stripped_value

    return cleaning_functions[column_name](stripped_value)


def _get_column_pattern(column_name, n):
    return f'{column_name} ({n})'


def _clean_year(value):
    if isinstance(value, int):
        return value
    # Some were 'ca. YYYY'
    return int(value[-4:]) or None


def main():
    args = _parse_args()
    file_name = args.file_name
    directory = args.directory

    recreate_db()
    with get_session() as session:
        with open(os.path.join(directory, file_name)) as f:
            for row in csv.DictReader(f, quoting=csv.QUOTE_NONNUMERIC):
                session.add(get_models(row))


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--directory', '-d', type=str, dest='directory', required=True,
        help="Directory to use")

    parser.add_argument(
        '--file_name', '-f', type=str, dest='file_name', required=True,
        help="File name to use")

    return parser.parse_args()


if __name__ == "__main__":
    main()
