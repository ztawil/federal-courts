# -*- coding: utf-8 -*-
from collections import OrderedDict

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from sqlalchemy import sql

from database_utils import get_session
from models import Court
from tabs.counts_tab import update_line_graph
from tabs.wait_time_tab import update_wait_time_graph


with get_session() as session:
    court_type_name = OrderedDict(
        (x[0], x[1]) for x in
        session
        .query(Court.court_type, sql.func.array_agg(Court.court_name))
        .group_by(Court.court_type)
        .order_by(Court.court_type)
    )

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)

app.layout = html.Div(
    id='main', children=[
        html.H1(id='header', children='Welcome to the Court Explorer'),
        html.Div(
            id='filters',
            children=[
                html.Div(
                    dcc.Dropdown(
                        id='court-type-dd',
                        options=[{'label': ct, 'value': ct} for ct in court_type_name.keys()]
                    ),
                    style={'width': '33%', 'display': 'inline-block'}
                ),
                html.Div(
                    dcc.Dropdown(
                        id='court-name-dd',
                    ),
                    style={'width': '33%', 'display': 'inline-block'}
                ),
                html.Div(
                    dcc.Dropdown(
                        id='senate-party-dd',
                        options=[
                            {'label': 'Republican', 'value': 'Republican'},
                            {'label': 'Democratic', 'value': 'Democratic'},
                            ]
                    ),
                    style={'width': '33%', 'display': 'inline-block'}
                ),
            ]
        ),
        html.Div(
            id='graphs',
            children=[
                dcc.Tabs(id='main-tabs', style={'width': '49%'}, children=[
                    dcc.Tab(id='makeup-tab', label='Makeup', children=[
                        dcc.Tabs(id='makeup-subtabs', children=[
                            dcc.Tab(id='party-counts-tab', label='Party', children=[
                                dcc.Graph(
                                    id='party-counts-graph',
                                    config={'displayModeBar': False},
                                    style={'width': '100%'}
                                    ),
                                ]),
                            dcc.Tab(id='race-ethnicity-tab', label='Race / Ethnicity', children=[
                                dcc.Graph(
                                    id='race-ethnicity-graph',
                                    config={'displayModeBar': False},
                                    style={'width': '100%'}
                                    ),
                                ]),
                            ])
                        ]
                    ),
                    dcc.Tab(id='process-tab', label='Process', children=[
                        dcc.Tabs(id='process-subtabs', children=[
                            dcc.Tab(id='wait-time-tab', label='Time to Confirmation', children=[
                                dcc.Graph(id='wait-time-graph', config={'displayModeBar': False}),
                                ]),
                            dcc.Tab(id='unconfirmed-tab', label='Unconfirmed', children=[
                                dcc.Graph(id='unconfirme-graph', config={'displayModeBar': False}),
                                ])
                            ])
                        ]
                    ),
                ])
            ],
        ),
        ]
    )


@app.callback(
    Output('court-name-dd', 'options'),
    [Input('court-type-dd', 'value')]
)
def update_court_name(court_type_select):
    court_names = []

    if court_type_select:
        court_type_list = [court_type_select]
    else:
        court_type_list = court_type_name.keys()

    for court_type in court_type_list:
        court_names.extend(court_type_name[court_type])
    return [{'label': cn, 'value': cn} for cn in sorted(court_names)]


@app.callback(
    [Output('party-counts-graph', 'figure'), Output('wait-time-graph', 'figure')],
    [Input('court-type-dd', 'value'), Input('court-name-dd', 'value')]
)
def update_graphs(court_type_select, court_name_select):
    return (
        update_line_graph(session, court_type_select, court_name_select),
        update_wait_time_graph(session, court_type_select, court_name_select)
    )


if __name__ == '__main__':
    app.run_server(debug=True, port=8000, host='0.0.0.0')
