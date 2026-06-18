import os
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

from modules.about_us import show_about_us
from modules.db_connection import get_db_connection
from modules.db_operations import (
    DEFAULT_SCHEDULE_CALL_OPTIONS,
    DEFAULT_STEM_EXPERIENCE_OPTIONS,
    DESIGN_PROJECT_OPTIONS,
    HOURS_PER_WEEK_OPTIONS,
    TIME_SLOT_OPTIONS,
    TRAINING_SESSION_OPTIONS,
    fetch_country_data,
    fetch_degree_data,
    fetch_join_movement_options,
    fetch_language_options,
    fetch_subject_data,
    insert_mentor_record,
)
from modules.page_config import render_page_header, setup_mentor_page
from modules.s3_upload import build_s3_file_url, upload_to_s3
from modules.thankyou import show_thank_you_page
from modules.validation import (
    LANGUAGE_OTHER_OPTION,
    finalize_communication_languages,
    get_email_suggestion,
    multiselect_from_state,
    render_communication_languages_field,
    render_form_field,
    render_whatsapp_field,
    selectbox_index,
    validate_email,
    validate_whatsapp_parts,
    validate_word_count,
    radio_index,
)

load_dotenv("config.env")
load_dotenv()


def _init_session_state():
    defaults = {
        "page": 1,
        "name": "",
        "email": "",
        "whatsapp": "",
        "whatsapp_country_code": "91",
        "whatsapp_number": "",
        "whatsapp_calling_label": "",
        "linkedin": "",
        "institute": "",
        "job_title": "",
        "degree": "",
        "degree_id": None,
        "country": "",
        "country_location_id": None,
        "city": "",
        "languages": [],
        "languages_other": "",
        "training_session": "",
        "selected_subjects": [],
        "selected_subject_ids": [],
        "stem_keywords": "",
        "work_explanation": "",
        "hours_per_week": "",
        "preferred_time_slots": [],
        "mentee_skills": "",
        "design_project": "",
        "project_design": "",
        "join_option": "",
        "stem_experience": "",
        "schedule_call": "",
        "comments": "",
        "resume_url": "",
        "bio_url": "Not uploaded",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _save_page1_state(
    name, email, whatsapp, whatsapp_country_code, whatsapp_number, whatsapp_calling_label,
    linkedin, institute, job_title, degree, degree_dict, country, country_dict, city,
    languages, languages_other,
):
    st.session_state.name = name
    st.session_state.email = email
    st.session_state.whatsapp = whatsapp
    st.session_state.whatsapp_country_code = whatsapp_country_code
    st.session_state.whatsapp_number = whatsapp_number
    st.session_state.whatsapp_calling_label = whatsapp_calling_label
    st.session_state.linkedin = linkedin
    st.session_state.institute = institute
    st.session_state.job_title = job_title
    st.session_state.degree = degree
    st.session_state.degree_id = degree_dict.get(degree) if degree else None
    st.session_state.country = country
    st.session_state.country_location_id = country_dict.get(country) if country else None
    st.session_state.city = city
    st.session_state.languages = languages
    st.session_state.languages_other = languages_other


def _save_page2_state(
    training_session, selected_subjects, subject_dict, stem_keywords, work_explanation,
    hours_per_week, preferred_time_slots, mentee_skills, design_project, project_design,
):
    st.session_state.training_session = training_session
    st.session_state.selected_subjects = selected_subjects
    st.session_state.selected_subject_ids = [
        subject_dict[subject] for subject in selected_subjects if subject in subject_dict
    ]
    st.session_state.stem_keywords = stem_keywords
    st.session_state.work_explanation = work_explanation
    st.session_state.hours_per_week = hours_per_week
    st.session_state.preferred_time_slots = preferred_time_slots
    st.session_state.mentee_skills = mentee_skills
    st.session_state.design_project = design_project
    st.session_state.project_design = project_design


def _save_page3_state(join_option, stem_experience, schedule_call, comments):
    st.session_state.join_option = join_option
    st.session_state.stem_experience = stem_experience
    st.session_state.schedule_call = schedule_call
    st.session_state.comments = comments


def _upload_resume(uploaded_file, bucket_name):
    folder_name = "cv_resume"
    s3_file_name = f"{folder_name}/{uploaded_file.name}"
    if upload_to_s3(uploaded_file, bucket_name, s3_file_name):
        return build_s3_file_url(bucket_name, folder_name, uploaded_file.name)
    return None


def _upload_bio(uploaded_file, bucket_name):
    folder_name = "Bio and a professional headshot"
    s3_file_name = f"{folder_name}/{uploaded_file.name}"
    if upload_to_s3(uploaded_file, bucket_name, s3_file_name):
        return build_s3_file_url(bucket_name, folder_name, uploaded_file.name)
    return "Not uploaded"


def _build_mentor_record(primary_key, resume_url, bio_url):
    return {
        "id": primary_key,
        "full_name": st.session_state.name,
        "email": st.session_state.email,
        "whatsapp_number": st.session_state.whatsapp,
        "linkedin_url": st.session_state.linkedin,
        "organization_name": st.session_state.institute,
        "job_title": st.session_state.job_title,
        "highest_degree": st.session_state.degree,
        "residence_country": st.session_state.country,
        "residence_city": st.session_state.city,
        "communication_languages": finalize_communication_languages(
            st.session_state.languages,
            st.session_state.get("languages_other", ""),
        ),
        "training_session_available": st.session_state.training_session,
        "subject_area_specializations": st.session_state.selected_subjects,
        "stem_keywords": st.session_state.stem_keywords,
        "work_explanation": st.session_state.work_explanation,
        "weekly_commitment_hours": st.session_state.hours_per_week,
        "preferred_time_slots_ist": st.session_state.preferred_time_slots,
        "skills_offered": st.session_state.mentee_skills,
        "willing_to_design_project": st.session_state.design_project,
        "project_design_approach": st.session_state.project_design,
        "engagement_preference": st.session_state.join_option,
        "stem_experience_years": st.session_state.stem_experience,
        "intro_call_preference": st.session_state.schedule_call,
        "resume_file_url": resume_url,
        "bio_headshot_file_url": bio_url,
        "comments": st.session_state.comments,
        "submitted_at": datetime.now(timezone.utc),
    }


def main():
    _init_session_state()

    if st.session_state.page == "thank_you":
        show_thank_you_page()
        return

    render_page_header()

    engine = get_db_connection()
    if engine is None:
        st.stop()

    if st.session_state.page == 1:
        st.markdown("### Registration")

        render_form_field("Enter your full name")
        name = st.text_input(
            "",
            value=st.session_state.name,
            placeholder="Enter your full name",
            label_visibility="collapsed",
        )

        render_form_field("Enter your email address (Work/Personal)")
        email = st.text_input(
            "",
            value=st.session_state.email,
            placeholder="Enter your email address",
            label_visibility="collapsed",
        )
        if "@" in email:
            suggestion = get_email_suggestion(email)
            if suggestion and st.button(f"Did you mean {suggestion}?"):
                st.session_state.email = suggestion
                st.rerun()

        render_form_field("Enter your LinkedIn profile link here", required=False)
        linkedin = st.text_input(
            "",
            value=st.session_state.linkedin,
            placeholder="https://linkedin.com/in/your-profile",
            label_visibility="collapsed",
        )

        render_form_field("Enter your current Institute/University/Organization")
        institute = st.text_input(
            "",
            value=st.session_state.institute,
            placeholder="Enter your organization",
            label_visibility="collapsed",
        )

        render_form_field("Current Job title/Designation", required=False)
        job_title = st.text_input(
            "",
            value=st.session_state.job_title,
            placeholder="Enter your job title",
            label_visibility="collapsed",
        )

        degrees, degree_dict, _ = fetch_degree_data(engine)
        render_form_field("Highest degree obtained")
        degree = st.selectbox(
            "",
            degrees,
            index=selectbox_index(degrees, st.session_state.degree),
            placeholder="Select your highest degree",
            label_visibility="collapsed",
        ) if degrees else None

        countries, country_dict, _ = fetch_country_data(engine)
        render_form_field("Country you currently reside in")
        country = st.selectbox(
            "",
            countries,
            index=selectbox_index(countries, st.session_state.country),
            placeholder="Select your country",
            label_visibility="collapsed",
        ) if countries else None

        whatsapp_country_code, whatsapp_number, whatsapp, whatsapp_calling_label = (
            render_whatsapp_field(residence_country=country, db_countries=countries)
        )

        render_form_field("Your current city")
        city = st.text_input(
            "",
            value=st.session_state.city,
            placeholder="Enter your city",
            label_visibility="collapsed",
        )

        languages_selected, languages_other = render_communication_languages_field(
            fetch_language_options()
        )

        if st.button("Next", key="p1_next"):
            if not all([name, email, whatsapp_number, institute, degree, country, city, languages_selected]):
                st.error("Please fill in all required fields marked with *.")
            elif LANGUAGE_OTHER_OPTION in languages_selected and not languages_other:
                st.error("Please specify other language(s).")
            else:
                is_valid_email, email_message = validate_email(email)
                if not is_valid_email:
                    st.error(email_message)
                else:
                    is_valid_phone, phone_message = validate_whatsapp_parts(
                        whatsapp_country_code, whatsapp_number
                    )
                    if not is_valid_phone:
                        st.error(phone_message)
                    else:
                        _save_page1_state(
                            name, email, whatsapp, whatsapp_country_code, whatsapp_number,
                            whatsapp_calling_label, linkedin, institute, job_title, degree,
                            degree_dict, country, country_dict, city,
                            languages_selected, languages_other,
                        )
                        st.session_state.page = 2
                        st.rerun()

        st.markdown("---")
        show_about_us()

    elif st.session_state.page == 2:
        col1, _ = st.columns([1, 4])
        with col1:
            page2_back_clicked = st.button("← Back", key="p2_back")

        st.write(f"Email: {st.session_state.email}")

        render_form_field(
            "Would you be available to participate in a two-hour training session "
            "at the start of the program?"
        )
        training_session = st.radio(
            "",
            TRAINING_SESSION_OPTIONS,
            index=radio_index(TRAINING_SESSION_OPTIONS, st.session_state.training_session),
            label_visibility="collapsed",
            key="p2_training_session",
        )

        subjects, subject_dict = fetch_subject_data(engine)
        render_form_field(
            "Subject Area & Specialization (In case of no specialization, choose your favourite subject area)"
        )
        selected_subjects = multiselect_from_state(
            "selected_subjects",
            subjects,
            max_selections=8,
            placeholder="Search and select up to 8 subject areas",
            widget_key="p2_selected_subjects",
        )

        render_form_field("Give us three keywords that associated with your current STEM work")
        stem_keywords = st.text_input(
            "",
            value=st.session_state.stem_keywords,
            placeholder="e.g. robotics, sustainability, machine learning",
            label_visibility="collapsed",
        )

        render_form_field(
            "How would you explain your current work to a broad undergraduate STEM community? "
            "(Max 50 words)"
        )
        work_explanation = st.text_area(
            "",
            value=st.session_state.work_explanation,
            placeholder="Briefly describe your work in simple terms",
            label_visibility="collapsed",
            height=100,
        )

        render_form_field(
            "How many hours per week are you willing to commit for this mentoring program?"
        )
        hours_per_week = st.radio(
            "",
            HOURS_PER_WEEK_OPTIONS,
            index=radio_index(HOURS_PER_WEEK_OPTIONS, st.session_state.hours_per_week),
            label_visibility="collapsed",
            key="p2_hours_per_week",
        )

        render_form_field(
            "For conducting mentoring sessions, please indicate your preferred time slots (IST)"
        )
        preferred_time_slots = multiselect_from_state(
            "preferred_time_slots",
            TIME_SLOT_OPTIONS,
            placeholder="Select one or more time slots",
            widget_key="p2_preferred_time_slots",
        )

        render_form_field("What 4 technical skills/soft skills can you share with the mentees?")
        mentee_skills = st.text_area(
            "",
            value=st.session_state.mentee_skills,
            placeholder="List four skills, e.g. Python, communication, project planning, mentoring",
            label_visibility="collapsed",
            height=100,
        )

        render_form_field(
            "Would you like to design a hands-on scientific project for this mentoring program?"
        )
        design_project = st.radio(
            "",
            DESIGN_PROJECT_OPTIONS,
            index=radio_index(DESIGN_PROJECT_OPTIONS, st.session_state.design_project),
            label_visibility="collapsed",
            key="p2_design_project",
        )

        project_design = ""
        if design_project == "Yes":
            render_form_field(
                "If yes, how would you design a home-lab based and/or computational "
                "hands-on scientific project for mentoring She for STEM (Kalpana) fellows?",
                required=True,
            )
            project_design = st.text_area(
                "",
                value=st.session_state.project_design,
                placeholder="Describe your project idea",
                label_visibility="collapsed",
                height=120,
            )

        st.markdown(" ", unsafe_allow_html=True)

        if page2_back_clicked:
            _save_page2_state(
                training_session, selected_subjects, subject_dict, stem_keywords,
                work_explanation, hours_per_week, preferred_time_slots, mentee_skills,
                design_project, project_design,
            )
            st.session_state.page = 1
            st.rerun()

        if st.button("Next", key="p2_next"):
            errors = []
            if not training_session:
                errors.append("Please answer the training session question.")
            if not selected_subjects:
                errors.append("Please select at least one subject area.")
            if not stem_keywords:
                errors.append("Please provide three keywords for your STEM work.")
            if not work_explanation:
                errors.append("Please explain your current work.")
            else:
                is_valid, message = validate_word_count(work_explanation, max_words=50)
                if not is_valid:
                    errors.append(message)
            if not hours_per_week:
                errors.append("Please select hours per week.")
            if not preferred_time_slots:
                errors.append("Please select at least one preferred time slot.")
            if not mentee_skills:
                errors.append("Please list four skills you can share with mentees.")
            if not design_project:
                errors.append("Please answer the hands-on project design question.")
            elif design_project == "Yes" and not project_design:
                errors.append("Please describe your hands-on project design.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                _save_page2_state(
                    training_session, selected_subjects, subject_dict, stem_keywords,
                    work_explanation, hours_per_week, preferred_time_slots, mentee_skills,
                    design_project, project_design,
                )
                st.session_state.page = 3
                st.rerun()

    elif st.session_state.page == 3:
        col1, _ = st.columns([1, 4])
        with col1:
            page3_back_clicked = st.button("← Back", key="p3_back")

        st.write(f"Email: {st.session_state.email}")

        join_options = fetch_join_movement_options()
        render_form_field("How would you like to join VigyanShaala's #SheforSTEM movement?")
        join_option = st.selectbox(
            "",
            join_options,
            index=selectbox_index(join_options, st.session_state.join_option),
            placeholder="Select how you would like to contribute",
            label_visibility="collapsed",
            key="p3_join_option",
        ) if join_options else None

        render_form_field("How many years have you worked as a STEM professional?")
        stem_experience = st.radio(
            "",
            DEFAULT_STEM_EXPERIENCE_OPTIONS,
            index=radio_index(
                DEFAULT_STEM_EXPERIENCE_OPTIONS,
                st.session_state.stem_experience,
            ),
            label_visibility="collapsed",
            key="p3_stem_experience",
        )

        render_form_field(
            "Would you like to schedule a 10-15 minute call with us "
            "for understanding the structure/content of your talk?"
        )
        schedule_call = st.radio(
            "",
            DEFAULT_SCHEDULE_CALL_OPTIONS,
            index=radio_index(
                DEFAULT_SCHEDULE_CALL_OPTIONS,
                st.session_state.schedule_call,
            ),
            label_visibility="collapsed",
            key="p3_schedule_call",
        )

        render_form_field("Upload your Curriculum Vitae/Resume")
        resume_file = st.file_uploader(
            "",
            accept_multiple_files=False,
            type=["pdf", "txt"],
            label_visibility="collapsed",
            key="p3_resume",
        )

        render_form_field("Please upload your bio and a professional headshot", required=False)
        bio_file = st.file_uploader(
            "",
            accept_multiple_files=False,
            type=["pdf", "txt", "png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="p3_bio",
        )

        render_form_field(
            "If you have any comments, suggestions you want us to think about, please let us know",
            required=False,
        )
        comments = st.text_area(
            "",
            value=st.session_state.comments,
            placeholder="Optional comments or suggestions",
            label_visibility="collapsed",
            height=100,
        )

        st.markdown(" ", unsafe_allow_html=True)

        if page3_back_clicked:
            _save_page3_state(join_option, stem_experience, schedule_call, comments)
            st.session_state.page = 2
            st.rerun()

        if st.button("Submit", type="primary", key="p3_submit"):
            if not all([join_option, stem_experience, schedule_call, resume_file]):
                st.error("Please fill in all required fields and upload your resume.")
            else:
                bucket_name = os.getenv("BUCKET_NAME")
                if not bucket_name:
                    st.error("File upload is not configured. Please contact support.")
                    st.stop()

                resume_url = _upload_resume(resume_file, bucket_name)
                if not resume_url:
                    st.error("Failed to upload resume. Please try again.")
                    st.stop()

                bio_url = "Not uploaded"
                if bio_file is not None:
                    bio_url = _upload_bio(bio_file, bucket_name)

                _save_page3_state(join_option, stem_experience, schedule_call, comments)
                primary_key = f"{st.session_state.whatsapp}_{st.session_state.name}"
                record = _build_mentor_record(primary_key, resume_url, bio_url)

                try:
                    insert_mentor_record(engine, record)
                    st.session_state.page = "thank_you"
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to save your registration: {exc}")


setup_mentor_page()
main()
