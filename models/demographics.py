from sqlalchemy import Column, Date, Integer, String, Table
from sqlalchemy.orm import relationship

from base import Base


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


def Appointment(Base):
    __tablename__ = 'appointment'


Court Type (1)
Court Name (1)
Appointment Title (1)
Appointing President (1)
Party of Appointing President (1)
Reappointing President (1)
Party of Reappointing President (1)
ABA Rating (1)
Seat ID (1)
Statute Authorizing New Seat (1)
Recess Appointment Date (1)
Nomination Date (1)
Committee Referral Date (1)
Hearing Date (1)
Judiciary Committee Action (1)
Committee Action Date (1)
Senate Vote Type (1)
Ayes/Nays (1)
Confirmation Date (1)
Commission Date (1)
Service as Chief Judge, Begin (1)
Service as Chief Judge, End (1)
2nd Service as Chief Judge, Begin (1)
2nd Service as Chief Judge, End (1)
Senior Status Date (1)
Termination (1)
Termination Date (1)




School (1)
Degree (1)
Degree Year (1)
School (2)
Degree (2)
Degree Year (2)
School (3)
Degree (3)
Degree Year (3)
School (4)
Degree (4)
Degree Year (4)
School (5)
Degree (5)
Degree Year (5)
Professional Career
Other Nominations/Recess Appointments