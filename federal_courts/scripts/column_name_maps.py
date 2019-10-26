DEMOGRAPHIC_COLUMNS = [
    'nid',
    'jid',
    'Last Name',
    'First Name',
    'Middle Name',
    'Suffix',
    'Birth Month',
    'Birth Day',
    'Birth Year',
    'Birth City',
    'Birth State',
    'Death Month',
    'Death Day',
    'Death Year',
    'Death City',
    'Death State',
    'Gender',
    'Race or Ethnicity'
 ]

# demographic_col_map = {col: _slugify(col) for col in DEMOGRAPHIC_COLUMNS}

demographic_col_map = {
    "nid": "nid",
    "jid": "jid",
    "Last Name": "last_name",
    "First Name": "first_name",
    "Middle Name": "middle_name",
    "Suffix": "suffix",
    "Birth Month": "birth_month",
    "Birth Day": "birth_day",
    "Birth Year": "birth_year",
    "Birth City": "birth_city",
    "Birth State": "birth_state",
    "Death Month": "death_month",
    "Death Day": "death_day",
    "Death Year": "death_year",
    "Death City": "death_city",
    "Death State": "death_state",
    "Gender": "gender",
    "Race or Ethnicity": "race_or_ethnicity"
}

# Columns that come in as `<COL_NAME> (n)` for multiple appointments
APPT_COLUMNS_TO_FILL = [
    'Court Type',
    'Court Name',
    'Appointment Title',
    'Appointing President',
    'Party of Appointing President',
    'Reappointing President',
    'Party of Reappointing President',
    'ABA Rating',
    'Seat ID',
    'Statute Authorizing New Seat',
    'Recess Appointment Date',
    'Nomination Date',
    'Committee Referral Date',
    'Hearing Date',
    'Judiciary Committee Action',
    'Committee Action Date',
    'Senate Vote Type',
    'Ayes/Nays',
    'Confirmation Date',
    'Commission Date',
    'Service as Chief Judge, Begin',
    'Service as Chief Judge, End',
    '2nd Service as Chief Judge, Begin',
    '2nd Service as Chief Judge, End',
    'Senior Status Date',
    'Termination',
    'Termination Date'
]

# appt_col_map = {col: _slugify(col) for col in APPT_COLUMNS_TO_FILL}

appt_col_map = {
  "Court Type": "court_type",
  "Court Name": "court_name",
  "Appointment Title": "appointment_title",
  "Appointing President": "appointing_president",
  "Party of Appointing President": "party_of_appointing_president",
  "Reappointing President": "reappointing_president",
  "Party of Reappointing President": "party_of_reappointing_president",
  "ABA Rating": "aba_rating",
  "Seat ID": "seat_id",
  "Statute Authorizing New Seat": "statute_authorizing_new_seat",
  "Recess Appointment Date": "recess_appointment_date",
  "Nomination Date": "nomination_date",
  "Committee Referral Date": "committee_referral_date",
  "Hearing Date": "hearing_date",
  "Judiciary Committee Action": "judiciary_committee_action",
  "Committee Action Date": "committee_action_date",
  "Senate Vote Type": "senate_vote_type",
  "Ayes/Nays": "ayes_nays",
  "Confirmation Date": "confirmation_date",
  "Commission Date": "commission_date",
  "Service as Chief Judge, Begin": "service_as_chief_judge_begin",
  "Service as Chief Judge, End": "service_as_chief_judge_end",
  "2nd Service as Chief Judge, Begin": "second_service_as_chief_judge_begin",
  "2nd Service as Chief Judge, End": "second_service_as_chief_judge_end",
  "Senior Status Date": "senior_status_date",
  "Termination": "termination",
  "Termination Date": "termination_date"
}


# Columns that come in as `<COL_NAME> (n)` for multiple degrees
EDU_COLUMNS_TO_FILL = ['School', 'Degree', 'Degree Year']


edu_col_map = {
    'School': 'school',
    'Degree': 'degree',
    'Degree Year': 'degree_year',
}


START_DATE_COLUMNS_TO_PARSE = ['confirmation_date', 'recess_appointment_date', 'commission_date']
