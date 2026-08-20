import streamlit as st

from endpoint_operations.security_service import load_security_status


def show(device):

    security = load_security_status(device["device_id"])

    if security is None:
        st.warning("No security information available.")
        return

    st.subheader("🛡 Endpoint Security Status")

    st.divider()

    # ----------------------------------------
    # Security Health Cards
    # ----------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        st.success("Microsoft Defender")
        st.write(f"Status : **{security['defender_status']}**")
        st.write(f"Real-Time Protection : **{security['realtime_protection']}**")
        st.write(f"Tamper Protection : **{security['tamper_protection']}**")

    with c2:
        st.success("CrowdStrike Falcon")
        st.write(f"Status : **{security['crowdstrike_status']}**")
        st.write(f"Sensor Version : **{security['crowdstrike_sensor_version']}**")
        st.write(f"Policy : **{security['crowdstrike_policy']}**")

    with c3:
        st.success("BitLocker")
        st.write(f"Status : **{security['bitlocker_status']}**")
        st.write(f"Encryption : **{security['encryption_method']}**")
        st.write(f"Recovery Key : **{security['recovery_key_available']}**")

    st.divider()

    c4, c5, c6 = st.columns(3)

    with c4:
        st.success("Firewall")
        st.write(f"Status : **{security['firewall_status']}**")
        st.write(f"Profile : **{security['firewall_profile']}**")

    with c5:
        st.success("TPM")
        st.write(f"Status : **{security['tpm_status']}**")
        st.write(f"Version : **{security['tpm_version']}**")

    with c6:
        st.success("Compliance")
        st.write(f"Status : **{security['compliance_status']}**")
        st.write(f"Secure Boot : **{security['secure_boot']}**")

    st.divider()

    st.markdown("### Version Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Defender Engine Version**")
        st.write(security["defender_engine_version"])

        st.write("**Platform Version**")
        st.write(security["defender_platform_version"])

        st.write("**Signature Version**")
        st.write(security["defender_signature_version"])

    with col2:
        st.write("**Last Defender Scan**")
        st.write(security["defender_last_scan"])

        st.write("**Last CrowdStrike Check-in**")
        st.write(security["crowdstrike_last_checkin"])

        st.write("**Last Security Sync**")
        st.write(security["last_sync"])