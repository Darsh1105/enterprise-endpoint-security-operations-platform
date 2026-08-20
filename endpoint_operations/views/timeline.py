import streamlit as st

from endpoint_operations.timeline_service import load_timeline


def show(device):

    timeline = load_timeline(device["device_id"])

    st.subheader("📅 Endpoint Timeline")

    if not timeline:
        st.info("No timeline events found.")
        return

    for event in timeline:

        severity = event["severity"]

        if severity == "High":
            icon = "🔴"
        elif severity == "Medium":
            icon = "🟠"
        else:
            icon = "🟢"

        with st.expander(
            f"{icon} {event['event_time']} | {event['event_type']}"
        ):

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Category**")
                st.write(event["event_category"])

                st.write("**Source**")
                st.write(event["event_source"])

                st.write("**Severity**")
                st.write(event["severity"])

            with col2:
                st.write("**Performed By**")
                st.write(event["performed_by"])

                st.write("**Description**")
                st.write(event["description"])