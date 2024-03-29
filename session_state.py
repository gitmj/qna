import streamlit as st


def init():
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'input_text' not in st.session_state:
        st.session_state['input_text'] = []

    if 'pdf_text' not in st.session_state:
        st.session_state['pdf_text'] = ''

    if "text_error" not in st.session_state:
        st.session_state.text_error = ""
