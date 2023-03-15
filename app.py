# Import 3rd party libraries
import streamlit as st
import streamlit.components.v1 as components

# Import from standard library
import logging
import random
import re

# Import openai module 
import openai_wrapper

import streamlit as st
from streamlit_chat import message

import pdfplumber

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)

st.set_page_config(page_title="Chat bot with attribute extraction", page_icon="🤖", layout="wide")

max_context_size = 4096

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

# Two session state variables used so that UI could clear the input text box after enter.
def input_text_changed():
  st.session_state["input_text"] = st.session_state["input"]
  st.session_state["input"] = ""
  return

def get_text():
    input_text = st.sidebar.text_input(label="Search", placeholder="Enter text",
       key="input", on_change=input_text_changed)
    return st.session_state["input_text"]

def prompt_tunning():
  if len(st.session_state["past"]) == 0:
    return None

  # Date: Mar 10, Friday - First try to extract attributes
  # prompt = "Extract important attributes from following conversation: \n"
  # prompt = "Generate search query based on following series of user search session and and output in 'query: <generated query>' format\n"
  prompt = "Instructions: Generate search query based on following series of user search session. Don't output false content. Don't write 'Search query:' directly start the answer. \n"
  for i in range(len(st.session_state['past'])):
      prompt = prompt + st.session_state['past'][i] + ","

  num_prompt_words = len(prompt.split())
  if (num_prompt_words > max_context_size):
    print ("Error: prompt too big")
    err_str = f"Prompt too big to handle: {num_prompt_words}"
    st.session_state.text_error = err_str
    logging.info(err_str)
    st.error(err_str)
    return None

  return prompt

def prompt_tunning_for_qna():
  if len(st.session_state["past"]) == 0:
    return None

  prompt = ""
  prompt += 'search results:\n\n'
  prompt += st.session_state['pdf_text']

  prompt += "Instructions: Compose a reply to the query using the search results given."\
              "Cite each reference using [text]."\
              "Citation should be done at the end of each sentence. If the search results mention multiple subjects"\
              "with the same name, create separate answers for each. Only include information found in the results and"\
              "don't add any additional information. Make sure the answer is correct and don't output false content."\
              "If the text does not relate to the query, simply state 'Found Nothing'. Don't write 'Answer:'"\
              "Directly start the answer.\n"
    

  last_q_index = len(st.session_state['past'])
  prompt = prompt + st.session_state['past'][last_q_index - 1]

  num_prompt_words = len(prompt.split())
  if (num_prompt_words > max_context_size):
    print ("Error: prompt too big")
    err_str = f"Prompt too big to handle: {num_prompt_words}"
    st.session_state.text_error = err_str
    logging.info(err_str)
    st.error(err_str)
    return None

  return prompt

def generate_response(prompt: str):
  openai = openai_wrapper.Openai()
  flagged = openai.moderate(prompt)
  if flagged:
    st.session_state.text_error = "Input flagged as inappropriate."
    return None
  else:
    st.session_state.text_error = ""

  # limit reponse to 400 tokens
  response = openai.complete(prompt, 0, 400)
  if response == None or len(response) == 0:
    st.session_state.text_error = "Empty response received from OpenAI API."
    return None

  logging.info (f"Successfully extracted attributes")
  return response[0]
  
def start_over():
  for key in st.session_state.keys():
    del st.session_state[key]
  return

# streamlit_app.py

import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

max_pdf_pages = 5
def pdf_upload_callback():
  pdf_text = ""
  with pdfplumber.open(st.session_state["pdf_file"]) as pdf:
      pages = pdf.pages
      if (len(pages) > max_pdf_pages):
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
  # title = "Chatbot with important attribute extraction!!"
  # st.title(title)

  if check_password():
  # if True: 
    st.sidebar.button(label="Start Over",
      type="primary",
      on_click=start_over)   

    q_n_a = st.sidebar.radio("QnA mode?", ('Yes','No'), index = 1, horizontal=True)

    user_input = get_text()

    if q_n_a == "Yes":
      st.write ("developing")
      source_file = st.file_uploader("Choose your .pdf file", type="pdf",
        on_change=pdf_upload_callback, key="pdf_file")

    if user_input:
        st.session_state.past.append(user_input)

        if q_n_a == "Yes":
          prompt = prompt_tunning_for_qna()
        else:
          prompt = prompt_tunning()

        if prompt != None:
          print ("Here is what I am sending:")
          print (prompt)
          response = generate_response(prompt)

          print ("Here is what I got:")
          print (response)
          st.session_state.generated.append(response)

          # Output in a iframe
          # query = response.split(" ", 1)[1]
          query = response
          print(query)

          if q_n_a == "No":
            source = "https://www.homedepot.com/s/"

            components.iframe(f"{source}{query}", height=2000, scrolling=True)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
          with st.sidebar:
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

