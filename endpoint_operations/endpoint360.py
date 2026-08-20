import streamlit as st

from endpoint_operations.endpoint_service import (
    load_devices,
    search_endpoint
)

from endpoint_operations.views import (
    overview,
    security,
    incidents,
    threats,
    engineering,
    policy,
    timeline,
    operations
)


def show():

    st.title(
        "🖥️ Endpoint 360 Workspace"
    )

    # -----------------------------
    # Load all devices
    # -----------------------------

    devices = load_devices()

    if not devices:

        st.warning(
            "No devices found."
        )

        return

    # -----------------------------
    # Device Selection
    # -----------------------------

    hostnames = [
        device["hostname"]
        for device in devices
    ]

    selected_hostname = st.selectbox(
        "Select Endpoint",
        hostnames
    )

    # -----------------------------
    # Load selected device
    # -----------------------------

    device = search_endpoint(
        selected_hostname
    )

    if device is None:

        st.error(
            "Endpoint not found."
        )

        return

    st.success(
        f"Loaded Endpoint : "
        f"{device['hostname']}"
    )

    # -----------------------------
    # Tabs
    # -----------------------------

    tabs = st.tabs([
        "Overview",
        "Security",
        "Incidents",
        "Threats",
        "Engineering",
        "Policy Management",
        "Timeline",
        "Operations"
    ])

    with tabs[0]:

        overview.show(
            device
        )

    with tabs[1]:

        security.show(
            device
        )

    with tabs[2]:

        incidents.show(
            device
        )

    with tabs[3]:

        threats.show(
            device
        )

    with tabs[4]:

        engineering.show(
            device
        )

    with tabs[5]:

        policy.show(
            device
        )

    with tabs[6]:

        timeline.show(
            device
        )

    with tabs[7]:

        operations.show(
            device
        )