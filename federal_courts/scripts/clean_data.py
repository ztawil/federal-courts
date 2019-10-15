import argparse
import copy
import csv
import json
import os
from collections import defaultdict
from datetime import datetime


DATE_FORMAT = '%Y-%m-%d'

MAX_DUP_COLS = 6

# Columns that come in clean
CLEAN_COLUMNS = [
    'nid', 'jid',
    'Last Name', 'First Name', 'Middle Name',
    'Birth Month', 'Birth Day', 'Birth Year',
    'Birth City', 'Birth State', 'Gender', 'Race or Ethnicity',
]

# Columns that come in as `<COL_NAME> (n)` for multiple appointments
APPT_COLUMNS_TO_FILL = [
    'Court Type', 'Court Name',
    'Appointing President', 'Party of Appointing President',
    'Reappointing President', 'Party of Reappointing President',
    'Recess Appointment Date', 'Nomination Date',
    'Senate Vote Type', 'Ayes/Nays', 'Confirmation Date',
    'Termination', 'Termination Date',
]


# Columns that come in as `<COL_NAME> (n)` for multiple degrees
EDU_COLUMNS_TO_FILL = ['School', 'Degree', 'Degree Year']


START_DATE_COLUMNS_TO_PARSE = ['Confirmation Date', 'Recess Appointment Date']
END_DATE_COLUMNS_TO_PARSE = ['Termination Date']


def _get_column_pattern(column_name, n):
    return f'{column_name} ({n})'


def get_important_values(row):
    """Subsets the row from the raw data with column used for the analysis.

    Parameters
    ----------
    row : dict
        Row from the judges.csv

    Returns
    -------
    dict
        Subset and cleaned row. Any columns related to possible multiple
        appointments will have values as dictionaries:
            1: value
            2: value
            for each appointment
    """
    # Start with a default dict
    new_row = defaultdict(dict)
    # This are the easy columns
    for col in CLEAN_COLUMNS:
        new_row[col] = row.get(col, '')
    # These are the columns that could have multiple values indicated like `Confirmation Date (1)`
    # `Termination Date (1)`
    for col in (EDU_COLUMNS_TO_FILL + APPT_COLUMNS_TO_FILL):
        # Structure so the new_row will have a new_row[col] = {n: value} for every n appointment
        col_dict = defaultdict(dict)
        for i in range(1, MAX_DUP_COLS):
            if row[_get_column_pattern(col, i)]:
                value = row[_get_column_pattern(col, i)]
                # if col in START_DATE_COLUMNS_TO_PARSE + END_DATE_COLUMNS_TO_PARSE:
                #     value = datetime.strptime(value, DATE_FORMAT)
                col_dict[i] = value
        new_row[col] = col_dict

    # Infer a generic start date based on the confirmation date or recess appointment date
    # See how many appointments they've had
    num_appts = max(len(new_row[col]) for col in START_DATE_COLUMNS_TO_PARSE)
    for i in range(1, num_appts + 1):
        # If a single appointment (`i`) has multiple start dates (rare) take the minimum
        # Need to convert to datetime for comparison, but want to store as string for json
        all_appointment_i_start_dates = [
            _strptime(new_row[col][i]) for col in START_DATE_COLUMNS_TO_PARSE if
            new_row.get(col, {}).get(i)]

        if all_appointment_i_start_dates:
            new_row['start_date'][i] = _strftime(min(all_appointment_i_start_dates))

        # If a single appointment (`i`) has multiple end dates (rare) take the max
        # Because active judges may not have an end date, need to first check if there are end dates
        # before taking a max
        potential_end_dates = [
            _strptime(new_row[col][i]) for col in END_DATE_COLUMNS_TO_PARSE
            if new_row.get(col, {}).get(i)]

        if potential_end_dates:
            new_row['end_date'][i] = _strftime(max(potential_end_dates))
        else:
            new_row['end_date'][i] = None

    return new_row


def _strptime(value):
    return datetime.strptime(value, DATE_FORMAT)


def _strftime(value):
    return value.strftime(DATE_FORMAT)


def main():
    args = _parse_args()
    file_name = args.file_name
    directory = args.directory

    clean_file_name, _ = os.path.splitext(file_name)
    out_nested_file_name = f'nested_{clean_file_name}.json'
    out_flat_file_name = f'flat_{clean_file_name}.json'

    with open(os.path.join(directory, file_name)) as f:
        reader = csv.DictReader(f)
        nested_rows = []
        flat_rows = []
        for row in reader:
            nested_row = get_important_values(row)
            nested_rows.append(nested_row)
            max_num_appointments = max(
                len(nested_row.get(col, [])) for col in APPT_COLUMNS_TO_FILL
            )
            for i in range(1, max_num_appointments + 1):
                flat_row = copy.deepcopy(nested_row)
                flat_row = dict(flat_row)
                for col in APPT_COLUMNS_TO_FILL + ['start_date', 'end_date']:
                    if nested_row.get(col, {}):
                        flat_row[col] = nested_row[col].get(i, '')
                    else:
                        flat_row[col] = None
                flat_rows.append(flat_row)

    json.dump(
        nested_rows,
        open(os.path.join(directory, out_nested_file_name), 'w')
    )

    json.dump(
        flat_rows,
        open(os.path.join(directory, out_flat_file_name), 'w')
    )


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
