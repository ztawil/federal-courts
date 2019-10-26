# -*- coding: utf-8 -*-
import json
from collections import defaultdict

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots


data = json.load(open('./data/partitioned_appeals_counts.json'))
"""
{
    year: {
        <Appeals Court Name>: {
            'Republican': <count>,
            'Democratic': <count>,
        }
    },
    year: ...
}
"""
cumulative_counts = []
delta_counts = []
last_year_counts = {'Democratic': 0, 'Republican': 0}
for i, (year, vals) in enumerate(sorted(data.items(), key=lambda x: x[0])):
    aggregated_counts = defaultdict(int)
    for counts_dict in vals.values():
        for party, count in counts_dict.items():
            if party in ('Democratic', 'Republican'):
                aggregated_counts[party] += count

    delta_counts_dict = defaultdict(int)
    for party in ('Democratic', 'Republican'):
        delta_counts_dict[party] = aggregated_counts[party] - last_year_counts[party]
        last_year_counts[party] = aggregated_counts[party]
    cumulative_counts.append((year, aggregated_counts))
    if i == 0:
        # Zero out the first data point
        delta_counts_dict = {'Democratic': 0, 'Republican': 0}
    delta_counts.append((year, delta_counts_dict))


years = [x[0] for x in cumulative_counts]

party_colors = [('Democratic', '#3440eb'), ('Republican', '#cc0808')]

all_counts = [
    count for _, counts_dict in cumulative_counts for count in counts_dict.values()]

delta_all_counts = [
    count for _, counts_dict in delta_counts for count in counts_dict.values()]

min_years = str(int(min(years)) - 2)
max_years = str(int(max(years)) + 2)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig = make_subplots(specs=[[{"secondary_y": True}]])

for party, color in party_colors:
    fig.add_trace(
        go.Scatter(
            x=years,
            y=[counts_dict[party] for _, counts_dict in cumulative_counts],
            marker={'size': 10, 'opacity': 1, 'color': color},
            text=party, name=party, hoverinfo='y'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            name=party,
            x=years[1:],
            y=[counts_dict[party] for _, counts_dict in delta_counts][1:],
            marker_color=color, hoverinfo='y', showlegend=False,
            ), secondary_y=True,
    )

ymin = int(min(delta_all_counts) * 1.5)
ymax = int(max(all_counts) * 1.1)
fig.update_layout(
    xaxis={
        'title': 'Year',
        'range': [min_years, max_years],
        'spikemode': 'across',
        'spikesnap': 'cursor',
        'spikecolor': 'black',
        'spikethickness': 1,
    },
    yaxis={'title': 'Number of Appeals Judges', 'range': [ymin, ymax]},
    yaxis2={
        'title': '\u0394 Number of Appeals Judges',
        'range': [ymin, ymax],
        'tickvals': [],
        'tickmode': 'array',
    },
    barmode='relative',
    hovermode='x',
    spikedistance=-1,
)

app.layout = html.Div(
    id='graphs', children=[dcc.Graph(id='da-graphs', figure=fig)]
)

if __name__ == '__main__':
    app.run_server(debug=True)
