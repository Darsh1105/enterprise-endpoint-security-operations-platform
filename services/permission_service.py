import streamlit as st

from services.auth_service import has_permission


def can(permission):

    role = st.session_state.get("role")

    if not role:
        return False

    return has_permission(
        role,
        permission
    )


def require_permission(permission):

    if not can(permission):

        st.error(
            "⛔ You do not have permission "
            "to perform this action."
        )

        return False

    return True