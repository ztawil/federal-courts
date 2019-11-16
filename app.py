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
from models import Appointment, Congress, Court, YearParty


start_year, end_year = 1901, 2021
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
            id='graphs-holder', children=[
                dcc.Graph(id='graphs'),
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
    Output('graphs', 'figure'),
    [Input('court-type-dd', 'value'), Input('court-name-dd', 'value')]
)
def update_graphs(court_type_select, court_name_select):
    party_counts_dict, years = get_line_graph_data(court_type_select, court_name_select)

    wait_time_query = get_wait_time_query(court_type_select, court_name_select)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.05,
        specs=[[{}], [{"secondary_y": True}]])

    for year, president, party, wait_times in wait_time_query.all():
        fig.add_trace(
            go.Box(
                y=wait_times,
                x=[year for _ in wait_times],
                name=president,
                # hoverinfo='name',
                marker_color=party_colors.get(party),
                showlegend=False,
            ),
            row=1, col=1)

    for party, counts_dict in party_counts_dict.items():
        color = party_colors.get(party)
        fig.add_trace(
            go.Scatter(
                x=years,
                y=counts_dict['n_judges'],
                marker={'opacity': 1, 'color': color},
                text=party,
                name=party,
                mode='markers',
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=counts_dict['n_appointed'],
                    arrayminus=counts_dict['n_terminated'])
                ),
            row=2, col=1,
        )

    # y_range = [math.floor(ymin * 1.5), math.ceil(ymax * 1.2)]
    fig.update_layout(
        width=1600, height=800,
        xaxis1={
            'showticklabels': True,
        },
        xaxis2={
            # 'range': [min(years) - 1, max(years) + 1],
            'showticklabels': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
            'rangeslider': {'visible': True},
        },
        yaxis1={'title': 'Wait Times (days)'},
        yaxis2={'title': 'Number of Judges', 'range': [-100, 500]},
        hovermode='x',
        spikedistance=-1,
    )
    return fig


def get_wait_time_query(court_type_select, court_name_select):
    join_conditions = [
        # Join condition for if the judge was serving that year
        sql.and_(
            sql.func.date_part('year', Appointment.nomination_date) >= Congress.start_year,
            sql.func.date_part('year', Appointment.nomination_date) < Congress.end_year,
        )
    ]

    if court_type_select:
        join_conditions.append(Appointment.court_type.in_([court_type_select]))

    if court_name_select:
        join_conditions.append(Appointment.court_name.in_([court_name_select]))

    wait_time_query = (
        session
        .query(
            Congress.start_year,
            Congress.president,
            Congress.party_of_president.label('party'),
            sql.func.array_agg(Appointment.days_to_confirm).label('days_to_confirm')
        )
        .join(
            Appointment, sql.and_(*join_conditions)
        )
        .filter(Appointment.days_to_confirm.isnot(None))
        .group_by(Congress.start_year, Congress.president, Congress.party_of_president)
        .order_by(Congress.start_year)
    )
    return wait_time_query


def get_line_graph_data(court_type_select, court_name_select):
    start_query = (
        get_start_count_query(court_type_select, court_name_select)
        .subquery('start_query')
    )
    end_query = get_end_count_query(court_type_select, court_name_select).subquery('end_query')
    count_query = (
        get_judge_count_query(court_type_select, court_name_select)
        .subquery('count_query')
    )

    full_query = (
        session
        .query(
            count_query.c.year,
            count_query.c.party,
            count_query.c.count.label('n_judges'),
            start_query.c.count.label('n_appointed'),
            end_query.c.count.label('n_terminated'),
        )
        .join(
            start_query,
            sql.and_(
                start_query.c.year == count_query.c.year,
                start_query.c.party == count_query.c.party,
            )
        )
        .join(
            end_query,
            sql.and_(
                end_query.c.year == count_query.c.year,
                end_query.c.party == count_query.c.party,
            )
        )
        .order_by(count_query.c.year)
    )

    party_counts_dict = defaultdict(lambda: defaultdict(list))
    years = set()  # set because of dups
    for row in full_query:
        years.add(row.year)
        party_counts_dict[row.party]['n_judges'].append(row.n_judges) 
        party_counts_dict[row.party]['n_appointed'].append(row.n_appointed) 
        party_counts_dict[row.party]['n_terminated'].append(row.n_terminated) 
    return party_counts_dict, sorted(years)


def get_judge_count_query(court_type_select=None, court_name_select=None):
    join_conditions = [
        # Join condition for if the judge was serving that year
        sql.and_(
            Appointment.start_year < YearParty.year + 2,
            sql.or_(
                Appointment.end_year >= YearParty.year, Appointment.end_year.is_(None)
            )
        ),
        # Join condition for party
        YearParty.party == Appointment.party_of_appointing_president,
    ]

    if court_type_select:
        join_conditions.append(Appointment.court_type.in_([court_type_select]))

    if court_name_select:
        join_conditions.append(Appointment.court_name.in_([court_name_select]))

    return (
        session
        .query(
            YearParty.year,
            YearParty.party,
            sql.func.count(Appointment.start_year).label('count'),
        )
        .outerjoin(
            Appointment,
            sql.and_(*join_conditions)
        )
        .group_by(YearParty.year, YearParty.party)
        .order_by(YearParty.year)
    )


def get_start_count_query(court_type_select=None, court_name_select=None):
    join_conditions = [
        # Need to have started / left in that congress or after
        Appointment.start_year >= YearParty.year,
        # Need to have started /  before the start of the next congress
        Appointment.start_year < YearParty.year + 2,
        # Join condition for party
        YearParty.party == Appointment.party_of_appointing_president,
    ]

    if court_type_select:
        join_conditions.append(Appointment.court_type.in_([court_type_select]))

    if court_name_select:
        join_conditions.append(Appointment.court_name.in_([court_name_select]))

    return (
        session
        .query(
            YearParty.year,
            YearParty.party,
            sql.func.count(Appointment.start_year).label('count'),
        )
        .outerjoin(
            Appointment,
            sql.and_(*join_conditions)
        )
        .group_by(YearParty.year, YearParty.party)
        .order_by(YearParty.year)
    )


def get_end_count_query(court_type_select=None, court_name_select=None):
    join_conditions = [
        # Need to have started / left in that congress or after
        Appointment.end_year >= YearParty.year - 2,
        # Need to have started /  before the start of the next congress
        Appointment.end_year < YearParty.year,
        # Join condition for party
        YearParty.party == Appointment.party_of_appointing_president,
    ]

    if court_type_select:
        join_conditions.append(Appointment.court_type.in_([court_type_select]))

    if court_name_select:
        join_conditions.append(Appointment.court_name.in_([court_name_select]))

    return (
        session
        .query(
            YearParty.year,
            YearParty.party,
            sql.func.count(Appointment.start_year).label('count'),
        )
        .outerjoin(
            Appointment,
            sql.and_(*join_conditions)
        )
        .group_by(YearParty.year, YearParty.party)
        .order_by(YearParty.year)
    )

if __name__ == '__main__':
    app.run_server(debug=True)
