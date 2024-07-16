# ref: https://discuss.streamlit.io/t/how-to-get-click-action-in-a-text/39441/8
import streamlit as st

if st.button("Click me", type="primary", key="testBtn"):
    st.write("Clicked")

# st.button("Another button!")

st.markdown(
    """
    <style>
    button[kind="primary"] {
        background: none!important;
        border: none;
        padding: 0!important;
        color: black !important;
        text-decoration: none;
        cursor: pointer;
        border: none !important;
    }
    button[kind="primary"]:hover {
        text-decoration: none;
        color: black !important;
    }
    button[kind="primary"]:focus {
        outline: none !important;
        box-shadow: none !important;
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)