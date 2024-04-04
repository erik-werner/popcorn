import streamlit as st
import numpy as np

from utils import add_user, setup_connection, add_event

from time import time, sleep

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

def check_username():
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.form_submit_button("Log in", on_click=username_entered)

    def username_entered():
        add_user(st.session_state.username)
        st.session_state["user_id"] = st.session_state.username
        st.session_state["username_correct"] = True

    # Return True if the username + password is validated.
    if st.session_state.get("username_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

if not check_username():
    st.stop()

global clear
def rate_popcorn_widget():
    """Widget for rating popcorn"""
    col1, col2 = st.columns(2)
    clear = False
    
    def gen_popcorn_ids():
        possible_popcorn_ids = np.arange(10)
        popcorn_id_1 = np.random.choice(possible_popcorn_ids)
        popcorn_id_2 = np.random.choice(list(set(possible_popcorn_ids) - {popcorn_id_1}))

        if "popcorn_id_1_gen" not in st.session_state:
            st.session_state["popcorn_id_1_gen"] = popcorn_id_1
        if "popcorn_id_2_gen" not in st.session_state:
            st.session_state["popcorn_id_2_gen"] = popcorn_id_2

    st.button("Generera förslag", on_click=gen_popcorn_ids, key="gen_popcorn_ids")

    with col1:
        popcorn_id_1 = st.text_input("Popcorn 1", key="popcorn_id_1", value=st.session_state.get("popcorn_id_1_gen", ""))
    
    with col2:
        popcorn_id_2 = st.text_input("Popcorn 2", key="popcorn_id_2", value=st.session_state.get("popcorn_id_2_gen", ""))
    
    score = st.slider("Poäng", -2.0, 2.0, 0.0, key="score")

    timestamp = int(time())

    if st.button("Add Score", key="add_score"):
        add_event(st.session_state.user_id, popcorn_id_1, popcorn_id_2, score, timestamp)

        success = st.success("Score added!")
        sleep(3) # Wait for 3 seconds
        success.empty() # Clear the alert

        clear = True

        if clear:
            if "popcorn_id_1_gen" in st.session_state:
                del st.session_state["popcorn_id_1_gen"]
            if "popcorn_id_2_gen" in st.session_state:
                del st.session_state["popcorn_id_2_gen"]
            if "popcorn_id_1" in st.session_state:
                del st.session_state["popcorn_id_1"]
            if "popcorn_id_2" in st.session_state:
                del st.session_state["popcorn_id_2"]
            if "score" in st.session_state:
                del st.session_state["score"]
            
        return rate_popcorn_widget()
        
# Main Streamlit app starts here
st.write("Rejta din popcorn! 🍿🍿🍿")
rate_popcorn_widget()