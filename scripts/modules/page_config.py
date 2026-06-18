import streamlit as st


def setup_mentor_page():
    st.set_page_config(
        page_title="She for STEM — Mentor Registration",
        page_icon="👩‍🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    image_path = (
        "https://raw.githubusercontent.com/VigyanShaala-Tech/"
        "Mentor-Recruitment-Form/main/image/VS-logo.png"
    )
    st.markdown(
        f'<div style="text-align:center"><img src="{image_path}" width="150"></div>',
        unsafe_allow_html=True,
    )


def render_page_header():
    st.markdown(
        "<div style='text-align: center;margin-bottom: 30px;'>"
        "<span style='font-size: 34px; font-weight: bold;'>Join 'She for STEM' Movement</span><br>"
        "<span style='font-size: 22px;font-weight: bold;'>"
        "Sign up to shape the future of next generation in STEM"
        "</span>"
        "</div>",
        unsafe_allow_html=True,
    )
