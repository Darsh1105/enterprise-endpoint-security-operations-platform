import streamlit as st

from endpoint_operations.action_service import load_actions


def show(device):

    actions = load_actions(device["device_id"])

    st.subheader("🔧 Endpoint Operations")

    if not actions:
        st.info("No operations available.")
        return

    for action in actions:

        status = action["status"]

        if status == "Completed":
            icon = "✅"
        elif status == "Running":
            icon = "🟡"
        elif status == "Failed":
            icon = "❌"
        else:
            icon = "⚪"

        with st.expander(
            f"{icon} {action['action_name']}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.write("**Category**")
                st.write(action["action_category"])

                st.write("**Requested By**")
                st.write(action["requested_by"])

                st.write("**Tool**")
                st.write(action["tool_name"])

                st.write("**Status**")
                st.write(action["status"])

            with col2:

                st.write("**Requested Time**")
                st.write(action["requested_time"])

                st.write("**Completed Time**")
                st.write(action["completed_time"])

                st.write("**Result**")
                st.write(action["result"])

            st.markdown("### Remarks")

            st.write(action["remarks"])