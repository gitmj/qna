"""OpenAI API connector."""

# Import from standard library
import os
import logging
import time

# Import from 3rd party libraries
import openai
import streamlit as st
from settings import *

# Assign credentials from environment variable or streamlit secrets dict
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]

# Suppress openai request/response logging
# Handle by manually changing the respective APIRequestor methods in the openai package
# Does not work hosted on Streamlit since all packages are re-installed by Poetry
# Alternatively (affects all messages from this logger):
logging.getLogger("openai").setLevel(logging.WARNING)


class Openai:
    """OpenAI Connector."""

    @staticmethod
    def moderate(prompt: str) -> bool:
        """Call OpenAI GPT Moderation with text prompt.
        Args:
            prompt: text prompt
        Return: boolean if flagged
        """
        try:
            response = openai.Moderation.create(prompt)
            return response["results"][0]["flagged"]

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            st.session_state.text_error = f"OpenAI API error: {e}"

    @staticmethod
    def complete(prompt: str, temperature: float = 0, max_tokens: int = 64) -> str:
        """Call OpenAI GPT Completion with text prompt.
        Args:
            prompt: text prompt
        Return: predicted response text
            "engine": "text-davinci-003",
            "engine": "text-ada-001",
            "engine": "text-ada-001",
        """
        kwargs = {
            "engine": "text-davinci-003",
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1,  # default
            "frequency_penalty": 0,  # default,
            "presence_penalty": 0,  # default
        }
        try:
            start_time = time.time()
            response = openai.Completion.create(**kwargs)
            end_time = time.time()
            logging.info(f"complete api latency:{end_time - start_time}")
            return (response["choices"][0]["text"], response["usage"]["total_tokens"])

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            st.session_state.text_error = f"OpenAI API error: {e}"


def generate_response(prompt: str) -> str:
    openai_obj = Openai()
    flagged = openai_obj.moderate(prompt)
    if flagged:
        st.session_state.text_error = "Input flagged as inappropriate."
        return None
    else:
        st.session_state.text_error = ""

    # limit response to 400 tokens
    response = openai_obj.complete(prompt, 0, MAX_OUTPUT_TOKENS)
    if response is None or len(response) == 0:
        st.session_state.text_error = "Empty response received from OpenAI API."
        return None

    return response[0]
