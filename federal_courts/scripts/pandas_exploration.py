import pandas as pd

df = pd.read_json('./data/flat_judges.json')

start_date_mask = df.loc[:, 'start_date'].notnull()
clean_data = df.loc[start_date_mask, :]

def get_year_mask(df, year):
    start_mask = df['start_year'] <= year
    end_mask_none = df['end_year'].isnull()
    end_mask_year = df['end_year'].notnull() and df['end_year'] >= year
    end_mask = df.loc[:end_mask_none or end_mask_year]



def date_filter(row, year, step_size=2):
    return (df['start_date'].year <= year and (
        (df.get('end_date') and row.get('end_date').year >= year) or
        not row['end_date']))