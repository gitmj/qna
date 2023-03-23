# Import from standard library
import logging
import base64
import fitz
import os

from tempfile import NamedTemporaryFile


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


def show_pdf(file_path):
    with open(file_path,"rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800"' \
                  f' type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

    # components.iframe(f"data:application/pdf;base64,{base64_pdf}", height=800, scrolling=True)



def pdf_upload_callback():
    pdf_text = ""
    with pdfplumber.open(st.session_state["pdf_file"]) as pdf:
        pages = pdf.pages
        if len(pages) > MAX_PDF_PAGES:
            st.session_state.text_error = "PDF too long." + " Max supported page: " + str(MAX_PDF_PAGES)
            logging.info(f"File name: {st.session_state['pdf_file']} too big\n")
            st.error(st.session_state.text_error)
            return ""
        for p in pages:
            pdf_text = pdf_text + p.extract_text()
    logging.info("Number of words in file: " + str(len(pdf_text.split())))
    st.session_state["pdf_text"] = pdf_text

    # print(type(show_pdf(st.session_state["pdf_file"])))
    # show_pdf(st.session_state["pdf_file"])

    return


def show_ref(answer):
    if answer:
        source_text = answer.split('Source:')
    else:
        logging.info('Received empty answer')

    search_query = None
    # Take first 5 words to highlight
    if len(source_text) > 1:
        tokens = source_text[1].split()[:5]
        search_query = " ".join(tokens)
        # remove the first "
        if search_query[0] == '"':
            search_query = search_query[1:]
        logging.info(search_query)
    else:
        logging.info(f'Empty search query from {source_text}')

    if search_query:
        # Hack - write file in current directory because streamlit file uploader does not provide path yet
        with NamedTemporaryFile(dir='.', suffix='.pdf') as f:
            f.write(st.session_state['pdf_file'].getbuffer())
            pdf_in = fitz.open(f.name)
            for page in pdf_in:
                text_instances = [page.search_for(search_query)]
                for inst in text_instances:
                    page.add_highlight_annot(inst)
            pdf_out = f.name + 'output.pdf'
            pdf_in.save(pdf_out)
            show_pdf(pdf_out)
            # Cleanup tmp file
            os.remove(pdf_out)


# Render main page
with st.container():
    session_state.init()

    st.sidebar.button(label="Start Over",
                      type="primary",
                      on_click=user_input.start_over)

    source_file = st.file_uploader("Choose your .pdf file", type="pdf",
                                   on_change=pdf_upload_callback, key="pdf_file")

    # if source_file:
    #    show_pdf(source_file.name)

    user_input_text = user_input.get_text()

    if user_input_text:
        st.session_state.past.append(user_input_text)

        bot_answer = openai_wrapper.generate_response(prompt.qna_prompt() + '\n context:'
                                                      + st.session_state["pdf_text"]
                                                      + '\n user: ' + str(user_input_text))

        st.session_state.generated.append(bot_answer)

        # Show references
        show_ref(bot_answer)

    user_input.render_past_msg()

