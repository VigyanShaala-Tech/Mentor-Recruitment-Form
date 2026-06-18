import streamlit as st


def show_thank_you_page():
    st.balloons()
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <h2>🎉 Thank You for Joining 'She for STEM' Movement!</h2>
            <p style="font-size: 18px;">
                We have received your mentor registration. Our team will review your application
                and reach out to you shortly.
            </p>
            <p style="font-size: 16px;">
                Excited to have you onboard!<br>
                – Team VigyanShaala
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
