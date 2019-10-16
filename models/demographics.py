from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import generic_repr

from models.base import Base


@generic_repr
class Demographic(Base):
    __tablename__ = 'demographic'

    nid = Column(Integer, primary_key=True)
    jid = Column(Integer)
    last_name = Column(String)
    first_name = Column(String)
    middle_name = Column(String)
    suffix = Column(String)
    birth_month = Column(Integer)
    birth_day = Column(Integer)
    birth_year = Column(Integer)
    birth_city = Column(String)
    birth_state = Column(String)
    death_month = Column(Integer)
    death_day = Column(Integer)
    death_year = Column(Integer)
    death_city = Column(String)
    death_state = Column(String)
    gender = Column(String)
    race_or_ethnicity = Column(String)

    appointments = relationship('Appointment', back_populates='demographic', uselist=True)
    education = relationship('Education', back_populates='demographic', uselist=True)


@generic_repr
class Appointment(Base):
    __tablename__ = 'appointment'

    id = Column(Integer, primary_key=True)
    nid = Column(Integer, ForeignKey('demographic.nid'))
    court_type = Column(String)
    court_name = Column(String)
    appointment_title = Column(String)
    appointing_president = Column(String)
    party_of_appointing_president = Column(String)
    reappointing_president = Column(String)
    party_of_reappointing_president = Column(String)
    aba_rating = Column(String)
    seat_id = Column(String)
    statute_authorizing_new_seat = Column(String)
    recess_appointment_date = Column(Date)
    nomination_date = Column(Date)
    committee_referral_date = Column(Date)
    hearing_date = Column(Date)
    judiciary_committee_action = Column(String)
    committee_action_date = Column(Date)
    senate_vote_type = Column(String)
    ayes_nays = Column(String)
    confirmation_date = Column(Date)
    commission_date = Column(Date)
    service_as_chief_judge_begin = Column(Date)
    service_as_chief_judge_end = Column(Date)
    second_service_as_chief_judge_begin = Column(Date)
    second_service_as_chief_judge_end = Column(Date)
    senior_status_date = Column(Date)
    termination = Column(String)
    termination_date = Column(Date)

    demographic = relationship('Demographic', back_populates='appointments', uselist=False)


@generic_repr
class Education(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True)
    nid = Column(Integer, ForeignKey('demographic.nid'))
    school = Column(String)
    degree = Column(String)
    degree_year = Column(Integer)

    demographic = relationship('Demographic', back_populates='education', uselist=False)
