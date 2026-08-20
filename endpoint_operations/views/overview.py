import streamlit as st


def show(device):

    st.subheader("Endpoint Overview")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Hostname**")
        st.write(device["hostname"])

        st.write("**Device Type**")
        st.write(device["device_type"])

        st.write("**Operating System**")
        st.write(device["operating_system"])

        st.write("**OS Version**")
        st.write(device["os_version"])

    with col2:

        st.write("**Last Seen**")
        st.write(device["last_seen"])

        st.write("**Device Status**")
        st.write(device["device_status"])

        st.write("**Risk Score**")
        st.write(device["risk_score"])

        st.write("**Serial Number**")
        st.write(device["serial_number"])