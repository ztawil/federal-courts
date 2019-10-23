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

party_colors = [('Democratic', '#3440eb'), ('Republican', '#cc0808')]
delta_counts = [
    (
        year,
        {
            party: counts_dict[party] - sorted_aggregated_counts[i-1][1][party]
            for party, _ in party_colors
        },
    ) for i, (year, counts_dict) in enumerate(sorted_aggregated_counts[1:], 1)
]
delta_all_counts = [
    count for _, counts_dict in delta_counts for count in counts_dict.values()]

app.layout = html.Div(
    dcc.Graph(
        id='delta-bar-graph',
        figure={
            'data': [
                go.Bar(
                    name=party,
                    x=years[1:],
                    y=[counts_dict[party] for _, counts_dict in delta_counts],
                    marker_color=color,
                ) for party, color in party_colors
            ],
            'layout': go.Layout(
                xaxis={'title': 'Year', 'range': [min(years), max(years)]},
                yaxis={
                    'title': 'Change in Number of Judges',
                    'range': [min(delta_all_counts), max(delta_all_counts)]
                },
                legend={'x': 0, 'y': 1},
                title="Change in Number of Judgess by Appointing President's Party",
                barmode='relative',
            )
        }
    )
)

if __name__ == '__main__':
    app.run_server(debug=True)
