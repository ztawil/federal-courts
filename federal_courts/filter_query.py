from sqlalchemy import sql

from database_utils import get_session
from models.models import Appointment, Education, Judge


filter_conditions = [
    Appointment.party_of_appointing_president.in_(['Republican', 'Democratic']),
    Appointment.court_type == 'U.S. Court of Appeals'
]

year_series_sq = sql.select([sql.func.generate_series(1920, 2020, 2).label('year')]).alias('ysq')

session = get_session()
counts_query = (
    session
    .query(
        year_series_sq.c.year,
        Appointment.party_of_appointing_president.label('party'),
        sql.func.sum(1).label('count')
    )
    .join(
        year_series_sq,
        sql.and_(
            (Appointment.start_year <= year_series_sq.c.year),
            sql.or_(Appointment.end_year > year_series_sq.c.year, Appointment.end_year.is_(None))
        )
    )
    .filter(*filter_conditions)
    .group_by(year_series_sq.c.year, Appointment.party_of_appointing_president)
    .order_by(year_series_sq.c.year.desc())
)