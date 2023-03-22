import streamlit as st
from streamlit_chat import message


# Clear the input text box. Value is stored in st.session_state["input_text"]
def input_text_changed():
    st.session_state["input_text"] = st.session_state["input"]
    st.session_state["input"] = ""
    return


def get_text():
    st.sidebar.text_input(label="Search", placeholder="Enter text",
                          key="input", on_change=input_text_changed)
    return st.session_state["input_text"]


def start_over():
    for key in st.session_state.keys():
        del st.session_state[key]
    return


def render_past_msg():
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            with st.sidebar:
                message(st.session_state["generated"][i], key=str(i))
                message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')