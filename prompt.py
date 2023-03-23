import logging

import streamlit as st

from settings import *


def attr_prompt() -> str:
    return "Instructions: Extract important attributes and entities from list of user queries. \n" \
           "Don't add additional information or false content. \n" \
           "Use following as an examples of the task. \n" \
           "For Examples: \n" \
           "Query: security locks \n" \
           "Output: Item: security locks \n" \
           "Query: I want a yellow Ferrari that can go over 100 MPH and 20 MPG \n" \
           "Output: Item: Car, Color: Yellow, Make:Ferrari, Maximum speed: 200 MPH, Fuel Efficiency: 20 MPG \n" \
           "Query: MIG welders that are portable, weighs less than 75 lbs and can support at least 200A \n" \
           "Output: Item: MIG welder, Weight: less than 75 lbs, Type: portable, Current: 200A \n"


def qna_prompt() -> str:
    return "Instructions: Compose a reply to the query using the context given. \n" \
           "Only include information found in the context and don't add any additional information. \n" \
           "Make sure answer is correct and don't output false content. \n" \
           "If the question does not relate to the given context, simply state 'Didn't find anything in the page' \n" \
           "Always include a 'Source' section in your answer which is the reference text from context used to answer" \
           "the question. \n"


def check_prompt_size(prompt):
    num_prompt_words = len(prompt.split())
    if num_prompt_words > MAX_CONTEXT_SIZE:
        logging.error("Error: prompt too big")
        err_str = f"Prompt too big to handle: {num_prompt_words}"
        st.session_state.text_error = err_str
        logging.error(err_str)
        st.error(err_str)
        return False
    return True
