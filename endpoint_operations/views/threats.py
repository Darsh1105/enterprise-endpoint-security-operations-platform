import streamlit as st

from endpoint_operations.threat_service import load_threats

from endpoint_operations.threat_investigation_service import (
    load_related_incidents,
    load_related_timeline,
    load_endpoint_risk,
    create_response_action
)


# ==================================================
# Helper Functions
# ==================================================

def get_severity_icon(severity):

    if severity == "Critical":
        return "⛔"

    if severity == "High":
        return "🔴"

    if severity == "Medium":
        return "🟠"

    if severity == "Low":
        return "🟡"

    return "🟢"


# ==================================================
# Threat Investigation Workspace
# ==================================================

def show(device):

    threats = load_threats(device["device_id"])

    st.subheader("👾 Threat Investigation")

    if not threats:

        st.success(
            "No threats detected on this endpoint."
        )

        return

    st.caption(
        "Security analyst workspace for investigating "
        "endpoint detections, telemetry and response."
    )

    # ==================================================
    # Threat List
    # ==================================================

    for threat in threats:

        severity = threat["severity"]

        icon = get_severity_icon(severity)

        with st.expander(
            f"{icon} {threat['threat_name']}  |  "
            f"{severity}  |  {threat['status']}",
            expanded=False
        ):

            # ==================================================
            # Threat Header
            # ==================================================

            st.markdown(
                f"## {icon} {threat['threat_name']}"
            )

            st.caption(
                f"Detection Source: "
                f"{threat['detection_source']}"
            )

            # ==================================================
            # Threat Information
            # ==================================================

            left, right = st.columns(2)

            with left:

                st.markdown("### Detection")

                st.write(
                    f"**Severity:** {threat['severity']}"
                )

                st.write(
                    f"**Status:** {threat['status']}"
                )

                st.write(
                    f"**Detection Source:** "
                    f"{threat['detection_source']}"
                )

                st.write(
                    f"**Detected Time:** "
                    f"{threat['detected_time']}"
                )

            with right:

                st.markdown("### Threat Intelligence")

                st.write(
                    f"**MITRE ATT&CK:** "
                    f"{threat['mitre_technique']}"
                )

                st.write(
                    f"**IOC:** "
                    f"{threat['ioc']}"
                )

            # ==================================================
            # Endpoint Risk
            # ==================================================

            st.divider()

            endpoint = load_endpoint_risk(
                device["device_id"]
            )

            if endpoint:

                st.markdown("### 🖥️ Endpoint Risk Context")

                e1, e2, e3, e4 = st.columns(4)

                with e1:

                    st.metric(
                        "Endpoint",
                        endpoint["hostname"]
                    )

                with e2:

                    st.metric(
                        "Risk Score",
                        endpoint["risk_score"]
                    )

                with e3:

                    st.metric(
                        "OS",
                        endpoint["operating_system"]
                    )

                with e4:

                    st.metric(
                        "Status",
                        endpoint["device_status"]
                    )

            # ==================================================
            # Description
            # ==================================================

            st.divider()

            st.markdown("### 🔎 Detection Analysis")

            st.write(
                threat["description"]
            )

            # ==================================================
            # MITRE ATT&CK
            # ==================================================

            st.markdown("### 🎯 MITRE ATT&CK")

            if threat["mitre_technique"]:

                st.info(
                    f"Observed Technique: "
                    f"{threat['mitre_technique']}"
                )

            else:

                st.info(
                    "No MITRE ATT&CK technique mapped."
                )

            # ==================================================
            # Related Incidents
            # ==================================================

            st.divider()

            st.markdown(
                "### 🚨 Related Incidents"
            )

            incidents = load_related_incidents(
                device["device_id"],
                threat["threat_name"]
            )

            if incidents:

                for incident in incidents:

                    st.write(
                        f"**{incident['incident_number']}** — "
                        f"{incident['title']}  |  "
                        f"{incident['severity']}  |  "
                        f"{incident['status']}"
                    )

                    st.caption(
                        f"Source: {incident['detection_source']} "
                        f"| SLA: {incident['sla_status']}"
                    )

            else:

                st.success(
                    "No related incident currently linked."
                )

            # ==================================================
            # Related Timeline
            # ==================================================

            st.markdown(
                "### 🕒 Related Endpoint Telemetry"
            )

            events = load_related_timeline(
                device["device_id"],
                threat["threat_name"]
            )

            if events:

                timeline_data = []

                for event in events:

                    timeline_data.append(
                        {
                            "Time": event["event_time"],
                            "Event": event["event_type"],
                            "Category": event["event_category"],
                            "Source": event["event_source"],
                            "Severity": event["severity"],
                            "Description": event["description"]
                        }
                    )

                st.dataframe(
                    timeline_data,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No related telemetry found."
                )

            # ==================================================
            # Recommended Action
            # ==================================================

            st.divider()

            st.markdown(
                "### 🧠 Recommended Response"
            )

            st.info(
                threat["recommended_action"]
            )

            # ==================================================
            # Response Actions
            # ==================================================

            st.markdown(
                "### ⚡ Response Actions"
            )

            st.caption(
                "Actions are simulated and recorded in the "
                "EESOP endpoint action history."
            )

            action1, action2, action3 = st.columns(3)

            with action1:

                if st.button(
                    "🔍 Collect Logs",
                    key=f"logs_{threat['threat_id']}"
                ):

                    action_id = create_response_action(
                        device_id=device["device_id"],
                        action_name="Collect Endpoint Logs",
                        action_category="Investigation",
                        tool_name=threat["detection_source"]
                    )

                    st.success(
                        f"Action #{action_id} queued."
                    )

            with action2:

                if st.button(
                    "🛡 Run Defender Scan",
                    key=f"scan_{threat['threat_id']}"
                ):

                    action_id = create_response_action(
                        device_id=device["device_id"],
                        action_name="Run Microsoft Defender Scan",
                        action_category="Threat Response",
                        tool_name="Microsoft Defender"
                    )

                    st.success(
                        f"Action #{action_id} queued."
                    )

            with action3:

                if st.button(
                    "🚫 Isolate Endpoint",
                    key=f"isolate_{threat['threat_id']}"
                ):

                    action_id = create_response_action(
                        device_id=device["device_id"],
                        action_name="Isolate Endpoint",
                        action_category="Containment",
                        tool_name=threat["detection_source"]
                    )

                    st.warning(
                        f"Simulation action #{action_id} queued."
                    )