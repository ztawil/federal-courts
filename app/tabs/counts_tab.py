# -*- coding: utf-8 -*-
from collections import defaultdict

import plotly.graph_objs as go
from sqlalchemy import sql

from constants import party_colors
from models import Appointment, YearParty


def update_line_graph(session, court_type_select, court_name_select):
    party_counts_dict, years = get_line_graph_data(session, court_type_select, court_name_select)

    fig = go.Figure()

    for party, counts_dict in party_counts_dict.items():
        color = party_colors.get(party)
        fig.add_trace(
            go.Scatter(
                x=years,
                y=counts_dict['n_judges'],
                marker={'opacity': 1, 'color': color},
                text=party,
                name=party,
                # mode='markers',
                error_y=dict(
                    type='data',
                    thickness=0.5,
                    symmetric=False,
                    array=counts_dict['n_appointed'],
                    arrayminus=counts_dict['n_terminated'])
                ),
        )

    fig.update_layout(
        xaxis={
            'range': [min(years) - 2, max(years) + 2],
            'showticklabels': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
        },
        yaxis={'title': 'Number of Judges'},
        hovermode='x',
        spikedistance=-1,
    )
    return fig


def get_line_graph_data(session, court_type_select, court_name_select):
    start_query = (
        get_start_count_query(session, court_type_select, court_name_select)
        .subquery('start_query')
    )
    end_query = (
        get_end_count_query(session, court_type_select, court_name_select).subquery('end_query')
    )
    count_query = (
        get_judge_count_query(session, court_type_select, court_name_select)
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


def get_judge_count_query(session, court_type_select=None, court_name_select=None):
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


def get_start_count_query(session, court_type_select=None, court_name_select=None):
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


def get_end_count_query(session, court_type_select=None, court_name_select=None):
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
