import streamlit as st
import time

from streamlit_cookies_controller import CookieController

from services.auth_service import (
    authenticate_user,
    create_session,
    revoke_session
)


COOKIE_NAME = "eesop_session"


# ==================================================
# Cookie Controller
# ==================================================

def get_cookie_controller():

    return CookieController(
        key="eesop_cookie_controller"
    )


# ==================================================
# Login
# ==================================================

def show_login(cookies):

    st.title("🛡️ EESOP")

    st.subheader(
        "Enterprise Endpoint Security "
        "Operations Platform"
    )

    st.divider()

    st.markdown(
        "### 🔐 Secure Login"
    )

    username = st.text_input(
        "Username",
        key="login_username"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button(
        "🔐 Sign In",
        use_container_width=True
    ):

        if not username or not password:

            st.error(
                "Please enter username and password."
            )

            return

        # ------------------------------------------
        # Authenticate user
        # ------------------------------------------

        user = authenticate_user(
            username,
            password
        )

        if user is None:

            st.error(
                "Invalid username or password."
            )

            return

        # ------------------------------------------
        # Create server-side session
        # ------------------------------------------

        token = create_session(
            user["user_id"]
        )

        # ------------------------------------------
        # Store browser cookie
        # ------------------------------------------

        cookies.set(
            COOKIE_NAME,
            token
        )

        # ------------------------------------------
        # Store authenticated state
        # ------------------------------------------

        st.session_state["authenticated"] = True
        st.session_state["user_id"] = user["user_id"]
        st.session_state["username"] = user["username"]
        st.session_state["display_name"] = user["display_name"]
        st.session_state["role"] = user["role"]

        # ------------------------------------------
        # Give browser component time to process
        # ------------------------------------------

        time.sleep(1)

        st.rerun()


# ==================================================
# Logout
# ==================================================

# ==================================================
# Logout
# ==================================================

def logout():

    cookies = get_cookie_controller()

    # ------------------------------------------
    # Get current browser session token
    # ------------------------------------------

    token = cookies.get(
        COOKIE_NAME
    )

    # ------------------------------------------
    # Revoke server-side session
    # ------------------------------------------

    if token:

        revoke_session(
            token
        )

    # ------------------------------------------
    # Remove browser cookie
    #
    # CookieController can sometimes already have
    # removed the cookie internally because of its
    # asynchronous browser update.
    # ------------------------------------------

    try:

        cookies.remove(
            COOKIE_NAME
        )

    except KeyError:

        # Cookie is already absent.
        # Logout can safely continue.
        pass

    # ------------------------------------------
    # Clear Streamlit authentication state
    # ------------------------------------------

    for key in [
        "authenticated",
        "user_id",
        "username",
        "display_name",
        "role"
    ]:

        st.session_state.pop(
            key,
            None
        )

    # ------------------------------------------
    # Allow cookie component to process removal
    # ------------------------------------------

    import time

    time.sleep(1)

    st.rerun()