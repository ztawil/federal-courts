# -*- coding: utf-8 -*-
import math
from collections import defaultdict, OrderedDict

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from sqlalchemy import sql

from database_utils import get_session
from models.models import Appointment, Court, YearParty


start_year, end_year = 1900, 2020
party_colors = {'Democratic': '#3440eb', 'Republican': '#cc0808'}

with get_session() as session:
    court_type_name = OrderedDict(
        (x[0], x[1]) for x in
        session
        .query(Court.court_type, sql.func.array_agg(Court.court_name))
        .group_by(Court.court_type)
        .order_by(Court.court_type)
    )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    id='main', children=[
        html.H1(id='header', children='Welcome to the Court Explorer'),
        html.Div(
            id='filters',
            children=[
                dcc.Dropdown(
                    id='court-type-dd',
                    options=[{'label': ct, 'value': ct} for ct in court_type_name.keys()]
                ),
                dcc.Dropdown(
                    id='court-name-dd',
                )
            ]
        ),
        html.Div(
            id='graphs', children=[
                dcc.Graph(id='wait-graph'),
                dcc.Graph(id='line-graph'),
                ]
            )
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
    [Output('line-graph', 'figure'), Output('wait-graph', 'figure')],
    [Input('court-type-dd', 'value'), Input('court-name-dd', 'value')]
)
def update_graphs(court_type_select, court_name_select):
    line_fig = update_line_graph(court_type_select, court_name_select)
    wait_fig = update_wait_graph(court_type_select, court_name_select)
    return line_fig, wait_fig


def update_wait_graph(court_type_select, court_name_select):
    join_conditions = [
        # Join condition for if the judge was serving that year
        sql.and_(
            sql.func.date_part('year', Appointment.nomination_date) >= YearParty.year,
            sql.func.date_part('year', Appointment.nomination_date) < YearParty.year + 2,
        )
    ]

    if court_type_select:
        join_conditions.append(Appointment.court_type.in_([court_type_select]))

    if court_name_select:
        join_conditions.append(Appointment.court_name.in_([court_name_select]))

    wait_time_query = (
        session
        .query(
            YearParty.year,
            sql.func.array_agg(Appointment.days_to_confirm).label('days_to_confirm')
        )
        .outerjoin(
            Appointment, sql.and_(*join_conditions)
        )
        .filter(Appointment.days_to_confirm.isnot(None))
        .group_by(YearParty.year)
        .order_by(YearParty.year.asc())
    )

    fig = go.Figure()
    for year, wait_times in wait_time_query.all():
        fig.add_trace(go.Box(y=wait_times, x=[year for _ in wait_times], name=year, marker_color='indianred'))
    return fig


def update_line_graph(court_type_select, court_name_select):

    join_conditions = [
        # Join condition for if the judge was serving that year
        sql.and_(
            Appointment.start_year <= YearParty.year,
            sql.or_(
                Appointment.end_year > YearParty.year, Appointment.end_year.is_(None)
            )
        ),
        # Join condition for party
        YearParty.party == Appointment.party_of_appointing_president,
    ]

    if court_type_select:
        join_conditions.append(Appointment.court_type.in_([court_type_select]))

    if court_name_select:
        join_conditions.append(Appointment.court_name.in_([court_name_select]))

    with get_session() as session:
        counts_query = (
            session
            .query(
                YearParty.year,
                YearParty.party,
                sql.func.count(Appointment.start_year).label('count')
            )
            .outerjoin(
                Appointment, sql.and_(*join_conditions)
            )
            .group_by(YearParty.year, YearParty.party)
            .order_by(YearParty.year.asc())
        )

        y_cum_values = defaultdict(list)
        y_delta_values = defaultdict(list)
        # Make a set because of dups
        years = set()
        ymin = 0
        ymax = 0
        for row in counts_query:
            years.add(row.year)
            this_year_cum = row.count
            y_delta = 0
            party = row.party
            if len(y_delta_values[party]) > 0:
                y_delta = this_year_cum - y_cum_values[party][-1]  # last year value
            ymax = max(ymax, this_year_cum)
            ymin = min(ymin, y_delta)
            y_delta_values[party].append(y_delta)
            y_cum_values[party].append(this_year_cum)

    # sort
    years = sorted(years)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for party, y_cum_values in y_cum_values.items():
        color = party_colors.get(party)
        fig.add_trace(
            go.Scatter(
                x=years,
                y=y_cum_values,
                marker={'size': 10, 'opacity': 1, 'color': color},
                text=party, name=party, hoverinfo='y'),
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(
                name=party,
                x=years[1:],
                y=y_delta_values[party][1:],
                marker_color=color, showlegend=False,
                # hoverinfo='y',
                ), secondary_y=True,
        )

    y_range = [math.floor(ymin * 1.5), math.ceil(ymax * 1.2)]
    fig.update_layout(
        xaxis={
            'title': 'Year',
            'range': [start_year, end_year + 2],
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
        },
        yaxis={'title': 'Number of Judges', 'range': y_range},
        yaxis2={
            'title': '\u0394 Number of Judges',
            'range': y_range,
            'tickvals': [],  # don't want to show ticks
            'tickmode': 'array',
        },

        barmode='relative',
        hovermode='x',
        spikedistance=-1,
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
