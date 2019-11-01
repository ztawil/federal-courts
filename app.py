# -*- coding: utf-8 -*-
import math
from collections import defaultdict

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from sqlalchemy import sql

from database_utils import get_session
from models.models import Appointment, YearParty


start_year, end_year = 1900, 2020
party_colors = {'Democratic': '#3440eb', 'Republican': '#cc0808'}

with get_session() as session:
    court_types = [
        x[0] for x in
        session
        .query(sql.func.distinct(Appointment.court_type))
        .filter(Appointment.court_type.notin_([
            'U.S. Circuit Court (1801-1802)',
            'U.S. Circuit Court (1869-1911)',
            'U.S. Circuit Court (other)']))
        .order_by(Appointment.court_type)
    ]

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
                    options=[{'label': ct, 'value': ct} for ct in court_types]
                )
            ]
        ),
        html.Div(
            id='graphs', children=[
                dcc.Graph(id='line-graph')
                ]
            )
        ]
    )


@app.callback(
    Output('line-graph', 'figure'),
    [Input('court-type-dd', 'value')]
)
def update_line_graph(court_type_select):

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

    fig.update_layout(
        xaxis={
            'title': 'Year',
            'range': [start_year, end_year + 2],
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
        },
        yaxis={'title': 'Number of Judges', 'range': [ymin * 1.5, math.ceil(ymax * 1.2)]},
        yaxis2={
            'title': '\u0394 Number of Judges',
            'range': [ymin * 1.5, ymax],
            'tickvals': [],
            'tickmode': 'array',
        },

        barmode='relative',
        hovermode='x',
        spikedistance=-1,
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
