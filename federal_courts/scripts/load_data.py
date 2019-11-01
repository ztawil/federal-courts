import argparse
import csv
import os
from collections import defaultdict
from datetime import datetime

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

    # A judge can have multiple appointments. There are a lot of columns associated with an apptmnet
    # and they are in the data as "<Column Description (N)>", go through and link all of these
    # together. There is no way of knowning how many (N) a judge may have and it's not sufficient to
    # just look for one column that has data, so loop through and look if _any_ of the appointment
    # pattern columns have data up to the MAX_DUP_COLS appointment.
    for i in range(1, MAX_DUP_COLS):
        appointment_dict = {}
        for col, slug_col in column_name_maps.appt_col_map.items():
            appt_row_val = row.get(_get_column_pattern(col, i))
            if appt_row_val:
                appointment_dict[slug_col] = clean_data(slug_col, appt_row_val)
        if len(appointment_dict) == 0:
            continue

        # In case there are multiple start dates due to bad data, assume the earliest
        appointment_dict['start_date'] = min(
            appointment_dict[date_col]
            for date_col in column_name_maps.START_DATE_COLUMNS_TO_PARSE
            if appointment_dict.get(date_col))

        appointment_dict['start_year'] = datetime.strptime(
            appointment_dict['start_date'], DATE_FORMAT).year

        # Multiple columns indicate a judgeship ending, take the min of them if duplicates.
        potential_end_dates = [
            appointment_dict[date_col]
            for date_col in column_name_maps.END_DATE_COLUMNS_TO_PARSE
            if appointment_dict.get(date_col)]

        # Empty list means still in job
        if not potential_end_dates:
            appointment_dict['end_date'] = None
        else:
            appointment_dict['end_date'] = min(potential_end_dates)

        if appointment_dict['end_date']:
            appointment_dict['end_year'] = datetime.strptime(
                appointment_dict['end_date'], DATE_FORMAT).year
        else:
            appointment_dict['end_year'] = None

        judge_row.appointments.append(Appointment(**appointment_dict))

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

    recreate_db()
    with get_session() as session:
        with open(os.path.join(directory, file_name)) as f:
            for row in csv.DictReader(f, quoting=csv.QUOTE_NONNUMERIC):
                session.add(get_models(row))

        conn = session.connection()
        conn.execute(
            """
            INSERT INTO year_party(year, party) (
                SELECT year, party
                FROM (SELECT generate_series(1900, 2020, 2) AS year) as year_sq
                JOIN (SELECT party FROM (VALUES
                    ('Democratic'),
                    ('Republican')) AS party_table (party)) as party_sq_party
                ON 1 = 1)
            """
        )


if __name__ == "__main__":
    main()
