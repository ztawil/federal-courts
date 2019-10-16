# -*- coding: utf-8 -*-
import csv

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

with open('/Users/zeintawil/Downloads/indicators.csv') as f:
    reader = csv.DictReader(f)
    data = []
    for x in reader:
        # Remove null column
        x.pop('')
        # Make year an int
        x['Year'] = int(x['Year'])
        data.append(x)

locations = {row['Country Name'] for row in data}
indicators = {row['Indicator Name'] for row in data}
years = {row['Year'] for row in data}

app.layout = html.Div(children=[
    html.H1(children='Health Indicators'),

    # Create a div for the filters
    html.Div(id='filter-div', children=[
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in locations],
            value=['Arab World'],
            multi=True,
            ),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[{'label': indicator, 'value': indicator} for indicator in indicators],
            value=['Population density (people per sq. km of land area)'],
            multi=True,
            ),
        dcc.RangeSlider(
            id='year-slider',
            min=min(years),
            max=max(years),
            marks={str(year): str(year) for year in years},
            value=[min(years), max(years)],
            step=None,
            )
        ]
    ),

    # Create a div for the graphs
    html.Div(id='graph-div'),
    ]
)


@app.callback(
    Output(component_id='graph-div', component_property='children'),
    [
        Input(component_id='country-dropdown', component_property='value'),
        Input(component_id='indicator-dropdown', component_property='value'),
        Input(component_id='year-slider', component_property='value'),
    ]
)
def update_table(selected_countries, selected_indicators, selected_years):
    filtered_data = []
    for row in data:
        if selected_indicators and row['Indicator Name'] not in selected_indicators:
            continue
        if selected_countries and row['Country Name'] not in selected_countries:
            continue
        if selected_years and (int(row['Year']) >= selected_years[1] or int(row['Year']) <= selected_years[0]):
            continue
        filtered_data.append(row)
    return html.Table(
            # Header
            [html.Tr([html.Th(key) for key in data[0].keys()])] +
            # body
            [
                html.Tr([html.Td(v) for v in row.values()])
                for row in filtered_data
            ]
        )


if __name__ == '__main__':
    app.run_server(debug=True)
