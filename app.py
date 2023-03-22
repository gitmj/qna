# Import from standard library
import logging

# Import 3rd party libraries
import streamlit as st
import pdfplumber
import streamlit.components.v1 as components
from streamlit_chat import message

# local imports
import openai_wrapper
import prompt
import session_state
from settings import *
import user_input


# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)
st.set_page_config(page_title="AMA (Ask me anything) bot about this product", page_icon="🤖", layout="wide")


def pdf_upload_callback():
    pdf_text = ""
    with pdfplumber.open(st.session_state["pdf_file"]) as pdf:
        pages = pdf.pages
        if len(pages) > MAX_PDF_PAGES:
            st.session_state.text_error = "PDF too long." + " Max supported page: " + str(max_pdf_pages)
            logging.info(f"File name: {st.session_state['pdf_file']} too big\n")
            st.error(st.session_state.text_error)
            return ""
        for p in pages:
            pdf_text = pdf_text + p.extract_text()
    logging.info("Number of words in resume: " + str(len(pdf_text.split())))
    st.session_state["pdf_text"] = pdf_text
    return


# Render main page
with st.container():
    session_state.init()

    st.sidebar.button(label="Start Over",
                      type="primary",
                      on_click=user_input.start_over)

    source_file = st.file_uploader("Choose your .pdf file", type="pdf",
                                   on_change=pdf_upload_callback, key="pdf_file")
    user_input_text = user_input.get_text()

    if user_input_text:
        st.session_state.past.append(user_input_text)

        bot_answer = openai_wrapper.generate_response(prompt.qna_prompt() + '\n context:'
                                                      + st.session_state["pdf_text"]
                                                      + '\n user: ' + str(user_input_text))
        st.session_state.generated.append(bot_answer)

    user_input.render_past_msg()

