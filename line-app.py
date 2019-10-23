# -*- coding: utf-8 -*-
import json
from collections import defaultdict

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = json.load(open('./data/partitioned_appeals_counts.json'))

aggregated_counts = defaultdict(lambda: defaultdict(int))
for year, vals in data.items():
    for counts_dict in vals.values():
        for party, count in counts_dict.items():
            if party in ('Democratic', 'Republican'):
                aggregated_counts[year][party] += count

sorted_aggregated_counts = sorted(aggregated_counts.items(), key=lambda x: x[0])
years = [x[0] for x in sorted_aggregated_counts]

all_counts = [
    count for _, counts_dict in sorted_aggregated_counts for count in counts_dict.values()]

party_colors = [('Democratic', '#3440eb'), ('Republican', '#cc0808')]

line_data = [
    go.Scatter(
        x=years, y=[counts_dict[party] for _, counts_dict in sorted_aggregated_counts],
        marker={'size': 10, 'opacity': 1, 'color': color}, text=party, name=party, hoverinfo='y',
    ) for party, color in party_colors
]

app.layout = html.Div(
    dcc.Graph(
        id='line-graph',
        figure={
            'data': line_data,
            'layout': go.Layout(
                xaxis={'title': 'Year', 'range': [min(years), max(years)]},
                yaxis={
                    'title': 'Number of Appeals Judges',
                    'range': [min(all_counts), max(all_counts)]},
                legend={'x': 0, 'y': 1},
                title="Number of Appeals Judges by Appointing President's Party"
            )
        }
    )
)

if __name__ == '__main__':
    app.run_server(debug=True)
