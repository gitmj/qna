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

if "text_error" not in st.session_state:
  st.session_state.text_error = ""

def query(payload):
  response = "static"
  return "static"

def get_text():
    input_text = st.text_input(label="Input", placeholder="Enter text", key="input")
    return input_text

def prompt_tunning():
  if len(st.session_state["past"]) == 0:
    return None

  prompt = "Extract important attributes from following conversation: \n"
  for i in range(len(st.session_state['past'])):
      prompt = prompt + "[user]" + st.session_state['past'][i] + "\n"

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
  if (len(response) == 0):
    st.session_state.text_error = "Empty response received from OpenAI API."
    return None

  logging.info (f"Successfully extracted attributes")
  return response[0]
  
# Render main page
with st.container():
  title = "Chatbot with important attribute extraction!!"
  st.title(title)

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

  if st.session_state['generated']:
      for i in range(len(st.session_state['generated'])-1, -1, -1):
          message(st.session_state["generated"][i], key=str(i))
          message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

