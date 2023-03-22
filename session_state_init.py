import streamlit as st


def session_state_init():
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'input_text' not in st.session_state:
        st.session_state['input_text'] = []

    if 'pdf_file' not in st.session_state:
        st.session_state['pdf_file'] = ''

    if 'pdf_text' not in st.session_state:
        st.session_state['pdf_text'] = ''

    if "text_error" not in st.session_state:
        st.session_state.text_error = ""
