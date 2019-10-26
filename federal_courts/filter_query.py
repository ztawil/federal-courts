from sqlalchemy import sql

from database_utils import get_session
from models.models import Appointment, Education, Judge


filter_conditions = [
    Appointment.party_of_appointing_president.in_(['Republican', 'Democratic']),
    Appointment.court_type == 'U.S. Court of Appeals'
]


start_query = (
    session
    .query(
        Appointment.party_of_appointing_president.label('party'),
        Appointment.start_year.label('year'),
        sql.func.sum(1).label('num_started'))
    .filter(sql.and_(*filter_conditions))
    .group_by(Appointment.party_of_appointing_president, Appointment.start_year)
    .subquery('start_query')
)


d_end_query = (
    session
    .query(
        Appointment.party_of_appointing_president.label('party'),
        Appointment.end_year.label('year'),
        sql.func.sum(1).label('num_ended')
    )
    .filter(sql.and_(*filter_conditions, Appointment.party_of_appointing_president == 'Democratic'))
    .group_by(Appointment.party_of_appointing_president, Appointment.end_year)
    .subquery('d_end_query')
)

r_end_query = (
    session
    .query(
        Appointment.party_of_appointing_president.label('party'),
        Appointment.end_year.label('year'),
        sql.func.sum(1).label('num_ended')
    )
    .filter(sql.and_(*filter_conditions, Appointment.party_of_appointing_president == 'Republican'))
    .group_by(Appointment.party_of_appointing_president, Appointment.end_year)
    .subquery('r_end_query')
)


joined_query = (
    session
    .query(
        start_query.c.year,
        sql.case(
            [(start_query.c.party == 'Republican', start_query.c.num_started)], else_=0
            ).label('num_r_started'),
        sql.case(
            [(start_query.c.party == 'Democratic', start_query.c.num_started)], else_=0
            ).label('num_d_started'),
        r_end_query.c.num_ended.label('num_r_ended'),
        d_end_query.c.num_ended.label('num_d_ended'),
        sql.case([(
            start_query.c.party == 'Republican',
            start_query.c.num_started - r_end_query.c.num_ended)], else_=0-r_end_query.c.num_ended
            ).label('net_r'),
        sql.case([(
            start_query.c.party == 'Democratic',
            start_query.c.num_started - r_end_query.c.num_ended)], else_=0-r_end_query.c.num_ended
            ).label('net_d')
    )
    .join(
        r_end_query,
        sql.and_(
            start_query.c.year == r_end_query.c.year,
        )
    )
    .join(
        d_end_query,
        sql.and_(
            start_query.c.year == d_end_query.c.year,
        )
    )
    .order_by(start_query.c.year.asc())
)

