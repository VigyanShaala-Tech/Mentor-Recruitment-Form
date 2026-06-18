import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import bindparam, create_engine, text

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.env"
load_dotenv(_CONFIG_PATH)
load_dotenv()


def _env(*keys, default=None):
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return default


def load_environment():
    load_dotenv(_CONFIG_PATH)
    load_dotenv()


@st.cache_resource
def get_db_connection():
    try:
        db_user = _env("DB_USER", "DB_USERNAME")
        db_password = _env("DB_PASSWORD")
        db_host = _env("DB_HOST", "DB_ENDPOINT")
        db_port = _env("DB_PORT")
        db_name = _env("DB_NAME")

        if not all([db_user, db_password, db_host, db_port, db_name]):
            raise ValueError("One or more required database environment variables are missing.")

        conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(
            conn_string,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True,
        )
        return engine
    except Exception as exc:
        st.error(f"Database connection error: {exc}")
        return None


@st.cache_data
def fetch_data(_engine, query, column_name=None, params=None):
    try:
        df = pd.read_sql(query, _engine, params=params)
        if column_name:
            return df[column_name].tolist()
        return df
    except Exception as exc:
        st.error(f"Error executing query: {exc}")
        return [] if column_name else pd.DataFrame()


@st.cache_data
def fetch_sub_fields_for_subject_areas(_engine, subject_areas):
    if not subject_areas:
        return pd.DataFrame()
    try:
        query = text("""
            SELECT DISTINCT ON ("sub_field") "sub_field", "id"
            FROM raw."subject_mapping"
            WHERE "subject_area" IN :areas
            ORDER BY "sub_field", "id"
        """).bindparams(bindparam("areas", expanding=True))
        return pd.read_sql(query, _engine, params={"areas": list(subject_areas)})
    except Exception as exc:
        st.error(f"Error executing query: {exc}")
        return pd.DataFrame()
