import streamlit as st

from endpoint_operations.engineering_service import load_engineering


def show(device):

    activities = load_engineering(device["device_id"])

    st.subheader("⚙️ Endpoint Engineering")

    if not activities:
        st.info("No engineering activities found.")
        return

    for activity in activities:

        status = activity["status"]

        if status == "Completed":
            icon = "✅"
        elif status == "Running":
            icon = "🟡"
        elif status == "Failed":
            icon = "❌"
        else:
            icon = "⚪"

        with st.expander(f"{icon} {activity['activity_name']}"):

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Activity Type**")
                st.write(activity["activity_type"])

                st.write("**Tool**")
                st.write(activity["tool_name"])

                st.write("**Engineer**")
                st.write(activity["engineer"])

                st.write("**Result**")
                st.write(activity["result"])

            with col2:
                st.write("**Status**")
                st.write(activity["status"])

                st.write("**Started**")
                st.write(activity["started_time"])

                st.write("**Completed**")
                st.write(activity["completed_time"])

            st.markdown("### Notes")
            st.write(activity["notes"])