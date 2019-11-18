from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import generic_repr

from models.base import Base


@generic_repr
class Judge(Base):
    __tablename__ = 'judge'

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

    appointments = relationship('Appointment', back_populates='judge', uselist=True)
    educations = relationship('Education', back_populates='judge', uselist=True)


@generic_repr
class Appointment(Base):
    __tablename__ = 'appointment'

    id = Column(Integer, primary_key=True)
    nid = Column(Integer, ForeignKey('judge.nid'), index=True)
    court_type = Column(String, index=True)
    court_name = Column(String, index=True)
    appointment_title = Column(String)
    appointing_president = Column(String)
    party_of_appointing_president = Column(String, index=True)
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
    service_as_chief_judge_begin = Column(Integer)
    service_as_chief_judge_end = Column(Integer)
    second_service_as_chief_judge_begin = Column(Integer)
    second_service_as_chief_judge_end = Column(Integer)
    senior_status_date = Column(Date)
    termination = Column(String)
    termination_date = Column(Date)
    start_date = Column(Date, index=True)
    start_year = Column(Integer, index=True)
    end_date = Column(Date, index=True)
    end_year = Column(Integer, index=True)
    days_to_confirm = Column(Integer, index=True)

    judge = relationship('Judge', back_populates='appointments', uselist=False)


@generic_repr
class Education(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True)
    nid = Column(Integer, ForeignKey('judge.nid'), index=True)
    school = Column(String)
    degree = Column(String)
    degree_year = Column(Integer)

    judge = relationship('Judge', back_populates='educations', uselist=False)


@generic_repr
class YearParty(Base):
    __tablename__ = 'year_party'

    year = Column(Integer, primary_key=True)
    party = Column(String, primary_key=True)


@generic_repr
class Court(Base):
    __tablename__ = 'court'

    court_type = Column(String, primary_key=True)
    court_name = Column(String, primary_key=True)


@generic_repr
class Congress(Base):
    __tablename__ = 'congress'

    title = Column(String, primary_key=True, nullable=False)
    time_span = Column(String, nullable=False)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)
    total_senators = Column(Integer, nullable=False)
    senate_democrats = Column(Integer, nullable=False)
    senate_republicans = Column(Integer, nullable=False)
    total_house = Column(Integer, nullable=False)
    house_democrats = Column(Integer, nullable=False)
    house_republicans = Column(Integer, nullable=False)
    president = Column(String, nullable=False)
    party_of_president = Column(String, nullable=False)
    senate_independents = Column(Integer, nullable=False)
    house_independents = Column(Integer, nullable=False)
    senate_dem_caucus = Column(Integer, nullable=False)
    senate_rep_caucus = Column(Integer, nullable=False)
    senate_majority_party = Column(String, nullable=False)
    president_party_senate_majority = Column(Integer, nullable=False)
    president_party_senate_majority_perc = Column(Float, nullable=False)

@generic_repr
class UnsuccessfulNomination(Base):
    __tablename__ = 'unsuccessful_nomination'

    president = Column(String, nullable=False, primary_key=True)
    congress = Column(String, nullable=False, primary_key=True)
    nominee = Column(String, nullable=False, primary_key=True)
    court_name = Column(String, nullable=False, primary_key=True)
    nomination_date = Column(String, nullable=False, primary_key=True)
    outcome = Column(String, nullable=False, primary_key=True)