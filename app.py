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

# Render main page
with st.container():
  # title = "Chatbot with important attribute extraction!!"
  # st.title(title)

  st.sidebar.button(label="Start Over",
    type="primary",
    on_click=start_over)   

  user_input = get_text()

  if user_input:
      st.session_state.past.append(user_input)
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
        source = "https://www.homedepot.com/s/"

        components.iframe(f"{source}{query}", height=2000, scrolling=True)

  if st.session_state['generated']:
      for i in range(len(st.session_state['generated'])-1, -1, -1):
        with st.sidebar:
          message(st.session_state["generated"][i], key=str(i))
          message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

