from services.auth_guard import require_login

require_login()
import streamlit as st

from endpoint_operations.endpoint360 import show

st.set_page_config(
    page_title="Endpoint 360",
    page_icon="🖥️",
    layout="wide"
)

show()