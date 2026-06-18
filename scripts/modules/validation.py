import os
import re
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import text

from modules.country_codes import (
    build_calling_code_options,
    calling_label_for_country,
)
from modules.db_connection import get_db_connection
from modules.db_operations import MENTOR_SCHEMA, MENTOR_TABLE

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.env"
load_dotenv(_CONFIG_PATH)


def _is_duplicate_email_check_enabled():
    value = os.getenv("CHECK_DUPLICATE_EMAIL", "false").strip().lower()
    return value in ("true", "1", "yes", "on")


def render_form_field(label, required=True):
    if required:
        st.markdown(f"**{label}** <span style='color:red'>*</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"**{label}**", unsafe_allow_html=True)


def selectbox_index(options, value):
    return options.index(value) if value in options else None


def radio_index(options, value):
    idx = selectbox_index(options, value)
    return idx if idx is not None else 0


def multiselect_from_state(state_key, options, *, placeholder="", widget_key=None, max_selections=None):
    if not options:
        return []
    kwargs = {
        "label": "",
        "options": options,
        "default": st.session_state.get(state_key, []),
        "placeholder": placeholder,
        "label_visibility": "collapsed",
        "key": widget_key or f"{state_key}_multiselect",
    }
    if max_selections is not None:
        kwargs["max_selections"] = max_selections
    return st.multiselect(**kwargs)


LANGUAGE_OTHER_OPTION = "Others"


def finalize_communication_languages(selected, other_text=""):
    languages = [lang for lang in selected if lang != LANGUAGE_OTHER_OPTION]
    if LANGUAGE_OTHER_OPTION in selected and other_text:
        for part in other_text.split(","):
            part = part.strip()
            if part:
                languages.append(part)
    return languages


def render_communication_languages_field(language_options):
    st.markdown(
        "**What communication languages are you comfortable in?** "
        "<span style='color:red'>*</span><br>"
        "<span style='font-size: 0.8rem; color: #6b7280; font-weight: normal;'>"
        "If your language isn't listed, select <strong>Others</strong> and enter the name manually."
        "</span>",
        unsafe_allow_html=True,
    )
    selected = multiselect_from_state(
        "languages",
        language_options,
        placeholder="Select one or more languages",
        widget_key="languages_multiselect",
    )
    other_text = ""
    if LANGUAGE_OTHER_OPTION in selected:
        render_form_field("Please specify other language(s)", required=True)
        other_text = st.text_input(
            "",
            value=st.session_state.get("languages_other", ""),
            placeholder="Enter language(s) not listed above",
            label_visibility="collapsed",
            key="languages_other_input",
        ).strip()
    return selected, other_text


def get_email_suggestion(email):
    common_domains = {"g": "gmail.com", "y": "yahoo.com", "o": "outlook.com"}
    try:
        user, domain = email.split("@")
        first_char = domain[0].lower()
        if first_char in common_domains and domain != common_domains[first_char]:
            return f"{user}@{common_domains[first_char]}"
    except ValueError:
        pass
    return None


def validate_email(email):
    email = (email or "").strip()
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, email):
        return False, "Invalid email format"

    common_typos = {
        "gamil.com": "gmail.com",
        "gnail.com": "gmail.com",
        "gmial.com": "gmail.com",
        "yaho.com": "yahoo.com",
        "outlok.com": "outlook.com",
    }

    try:
        user, domain = email.split("@")
    except ValueError:
        return False, "Invalid email format"

    if domain.lower() in common_typos:
        suggestion = f"{user}@{common_typos[domain.lower()]}"
        return False, f"Did you mean {suggestion}?"

    if not _is_duplicate_email_check_enabled():
        return True, ""

    try:
        engine = get_db_connection()
        if not engine:
            return False, "Could not connect to the database"

        with engine.connect() as conn:
            query = text(
                f"SELECT email FROM {MENTOR_SCHEMA}.{MENTOR_TABLE} "
                f"WHERE LOWER(email) = LOWER(:email)"
            )
            row = conn.execute(query, {"email": email}).fetchone()
            if row:
                return False, "This email is already registered. Please use a different email or contact support."
    except Exception as exc:
        return False, f"Database error while checking email: {exc}"

    return True, ""


def validate_phone(phone):
    """Validate a 10-digit Indian mobile number (local part only)."""
    if not phone:
        return False, "Phone number is required"

    if any(char.isalpha() for char in phone):
        return False, "Phone number should not contain letters"

    phone = re.sub(r"[^0-9]", "", phone)

    if not phone.isdigit():
        return False, "Phone number should contain only digits"

    if len(phone) != 10:
        return False, f"Phone number must be exactly 10 digits (you entered {len(phone)} digits)"

    if not phone.startswith(("6", "7", "8", "9")):
        return False, "Phone number should start with 6, 7, 8, or 9"

    return True, "Valid phone number"


def combine_whatsapp_number(country_code, local_number):
    local_digits = re.sub(r"[^0-9]", "", local_number or "")
    if not country_code or not local_digits:
        return ""
    return f"{country_code}{local_digits}"


def validate_whatsapp_parts(country_code, local_number):
    local_digits = re.sub(r"[^0-9]", "", local_number or "")
    if not country_code:
        return False, "Please select a country code"
    if not local_digits:
        return False, "Please enter your phone number"

    if country_code == "91":
        return validate_phone(local_digits)

    if country_code == "1" and len(local_digits) != 10:
        return False, "US/Canada numbers must be 10 digits"

    if len(local_digits) < 6 or len(local_digits) > 12:
        return False, "Please enter a valid phone number (6–12 digits)"

    return True, "Valid phone number"


def render_whatsapp_field(residence_country=None, db_countries=None):
    render_form_field("WhatsApp Number")

    options = build_calling_code_options(db_countries)
    labels = [label for label, _, _ in options]
    label_to_code = {label: code for label, code, _ in options}

    saved_label = st.session_state.get("whatsapp_calling_label")
    residence_label = calling_label_for_country(residence_country, options)
    default_label = (
        saved_label
        if saved_label in labels
        else residence_label
        if residence_label in labels
        else "+91 India"
    )

    code_col, number_col = st.columns([1, 2])
    with code_col:
        country_label = st.selectbox(
            "Country code",
            labels,
            index=selectbox_index(labels, default_label) or 0,
            label_visibility="collapsed",
        )
    with number_col:
        local_number = st.text_input(
            "Phone number",
            value=st.session_state.get("whatsapp_number", ""),
            placeholder="9876543210",
            label_visibility="collapsed",
        )

    country_code = label_to_code.get(country_label, "")
    full_number = combine_whatsapp_number(country_code, local_number)
    return country_code, local_number, full_number, country_label


def validate_word_count(text, min_words=0, max_words=None):
    words = [word for word in (text or "").split() if word.strip()]
    count = len(words)
    if count < min_words:
        return False, f"Please enter at least {min_words} words (you entered {count} words)"
    if max_words is not None and count > max_words:
        return False, f"Maximum {max_words} words allowed (you entered {count} words)"
    return True, "Valid word count"


def validate_whatsapp_number(phone):
    if not phone:
        return False, "WhatsApp number is required"

    if any(char.isalpha() for char in phone):
        return False, "Phone number should not contain letters"

    digits = re.sub(r"[^0-9]", "", phone)
    if not digits.isdigit():
        return False, "Phone number should contain only digits (no '+' sign)"

    if len(digits) < 10 or len(digits) > 15:
        return False, "Enter a valid number with country code (10–15 digits, without '+')"

    return True, "Valid phone number"
