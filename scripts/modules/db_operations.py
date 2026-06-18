import streamlit as st

from modules.db_connection import fetch_data

DEFAULT_LANGUAGES = [
    "English",
    "Hindi",
    "Marathi",
    "Malayalam",
    "Kannada",
    "Telgu",
    "Assamese",
    "Bengali",
    "Gujarati",
    "Manipuri",
    "Tamil",
    "Odia",
    "Punjabi",
    "Urdu",
    "Maithili",
    "Konkani",
    "Kashmiri",
    "Others",
]

DEFAULT_JOIN_OPTIONS = [
    (
        "Inspirational female role model for young women in STEM| You will\n"
        " share your personal & professional journey in STEM|\n"
        " Virtual engagement| 1.5 hours 1-2 times a year"
    ),
    (
        "Mentor|Help fellows advance their STEM skills through innovative & frugal\n"
        "hands-on projects|Virtual engagement|\n"
        " 3 hours per week for 12-14 weeks once a year"
    ),
    (
        "Tech Capstone Project/Research Project Developers| Design challenging hands on "
        "projects for fellows to elicit critical thinking| Virtual engagement |"
        "atleast 2-3 hours per week/1 month"
    ),
]

DEFAULT_STEM_EXPERIENCE_OPTIONS = [
    "2-3 years",
    "4-6 years",
    "7-10 years",
    " More than 10 years",
]

DEFAULT_SCHEDULE_CALL_OPTIONS = ["Yes", "No", "Maybe"]

TRAINING_SESSION_OPTIONS = ["Yes", "No"]
HOURS_PER_WEEK_OPTIONS = ["1-2", "2-3", "3-4", "4-5", ">5"]
TIME_SLOT_OPTIONS = [
    "9 am - 12:00 noon IST",
    "12 noon - 3 pm IST",
    "3 pm - 6 pm IST",
    "6 pm - 9 pm IST",
    "9 pm - 12:00 am midnight IST",
]
DESIGN_PROJECT_OPTIONS = ["Yes", "No"]

MENTOR_SCHEMA = "old"
MENTOR_TABLE = "mentor_recruitment"


@st.cache_data
def fetch_degree_data(_engine):
    degree_data = fetch_data(
        _engine,
        """
        SELECT DISTINCT ON ("display_name")
            "display_name", "course_id", course_duration
        FROM raw."course_mapping"
        WHERE course_duration != 1
        ORDER BY "display_name"
        """,
    )
    if degree_data.empty:
        return [], {}, degree_data

    degrees = degree_data["display_name"].tolist()
    degree_dict = dict(zip(degree_data["display_name"], degree_data["course_id"]))
    return degrees, degree_dict, degree_data


@st.cache_data
def fetch_country_data(_engine):
    country_data = fetch_data(
        _engine,
        """
        SELECT DISTINCT ON ("country")
            "country", "location_id"
        FROM raw."location_mapping"
        ORDER BY "country"
        """,
    )
    if country_data.empty:
        return [], {}, country_data

    countries = country_data["country"].tolist()
    country_dict = dict(zip(country_data["country"], country_data["location_id"]))
    return countries, country_dict, country_data


@st.cache_data
def fetch_subject_data(_engine):
    subject_data = fetch_data(
        _engine,
        """
        SELECT DISTINCT ON ("sub_field")
            "sub_field", "id"
        FROM raw."subject_mapping"
        ORDER BY "sub_field", "id"
        """,
    )
    if subject_data.empty:
        return [], {}

    subjects = subject_data["sub_field"].tolist()
    subject_dict = dict(zip(subject_data["sub_field"], subject_data["id"]))
    return subjects, subject_dict


def fetch_language_options():
    """Languages are fixed options (no language_mapping table in DB)."""
    return DEFAULT_LANGUAGES


def fetch_join_movement_options():
    """Join options are fixed choices (no mentor_join_mapping table in DB)."""
    return DEFAULT_JOIN_OPTIONS


def insert_mentor_record(engine, record):
    import pandas as pd

    df = pd.DataFrame([record])
    df = df.map(lambda value: ", ".join(value) if isinstance(value, list) else value)
    df.to_sql(
        MENTOR_TABLE,
        con=engine,
        schema=MENTOR_SCHEMA,
        if_exists="append",
        index=False,
    )

