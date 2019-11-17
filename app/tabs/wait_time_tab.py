# -*- coding: utf-8 -*-
import plotly.graph_objs as go
from sqlalchemy import sql

from constants import party_colors
from models import Appointment, Congress


def update_wait_time_graph(session, court_type_select, court_name_select):
    wait_time_query = get_wait_time_query(session, court_type_select, court_name_select)

    fig = go.Figure()

    for president, party, years, wait_times in wait_time_query.all():
        fig.add_trace(
            go.Box(
                y=wait_times,
                x=years,
                name=president,
                # hoverinfo='name',
                marker_color=party_colors.get(party),
            )
        )

    fig.update_layout(
        xaxis={'showticklabels': True},
        yaxis={'title': 'Wait Times (days)'},
    )
    return fig


def get_wait_time_query(session, court_type_select, court_name_select):
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
            Congress.president,
            Congress.party_of_president.label('party'),
            sql.func.array_agg(Congress.start_year).label('start_years'),
            sql.func.array_agg(Appointment.days_to_confirm).label('days_to_confirm')
        )
        .join(
            Appointment, sql.and_(*join_conditions)
        )
        .filter(Appointment.days_to_confirm.isnot(None))
        .group_by(Congress.president, Congress.party_of_president)
        .order_by(sql.func.min(Congress.start_year))
    )
    return wait_time_query
