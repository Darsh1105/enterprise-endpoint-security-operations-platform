import time
import streamlit as st

from services.auth_service import get_session_user
from services.auth_ui import (
    get_cookie_controller,
    show_login
)


COOKIE_NAME = "eesop_session"

COOKIE_WAIT_SECONDS = 1.0


def restore_session(cookies):

    # Give the browser cookie component time to
    # return cookies after a fresh Streamlit execution.
    time.sleep(COOKIE_WAIT_SECONDS)

    token = cookies.get(
        COOKIE_NAME
    )

    if not token:
        return False

    user = get_session_user(token)

    if user is None:

        cookies.remove(COOKIE_NAME)

        return False

    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user["user_id"]
    st.session_state["username"] = user["username"]
    st.session_state["display_name"] = user["display_name"]
    st.session_state["role"] = user["role"]

    return True


def require_login():

    if st.session_state.get(
        "authenticated",
        False
    ):
        return True

    cookies = get_cookie_controller()

    if restore_session(cookies):
        return True

    show_login(cookies)

    st.stop()