import streamlit as st
import pandas as pd
from datetime import datetime

from endpoint_operations.endpoint360 import show as endpoint360

from services.dashboard_service import (
    get_total_devices,
    get_defender_coverage,
    get_crowdstrike_coverage,
    get_bitlocker_compliance,
    get_high_risk_devices,
    get_open_incidents,
    get_average_risk_score,
    get_sla_compliance,
    get_recent_incidents,
    get_recent_timeline,
    get_defender_chart,
    get_bitlocker_chart,
    get_risk_distribution
)

from services.auth_guard import restore_session
from services.auth_ui import (
    get_cookie_controller,
    show_login,
    logout
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="EESOP",
    page_icon="🛡️",
    layout="wide"
)


# ==================================================
# LOGIN PAGE
# ==================================================

def login_page():

    # ----------------------------------------------
    # If logout explicitly occurred, do not try
    # to restore the old browser cookie.
    # ----------------------------------------------

    force_login = st.session_state.get(
        "force_login",
        False
    )

    # ----------------------------------------------
    # Already authenticated
    # ----------------------------------------------

    if st.session_state.get(
        "authenticated",
        False
    ):

        return


    # ----------------------------------------------
    # Create ONE cookie controller for this run
    # ----------------------------------------------

    cookies = get_cookie_controller()


    # ----------------------------------------------
    # Try persistent session restoration
    # ----------------------------------------------

    if not force_login:

        if restore_session(cookies):

            st.rerun()


    # ----------------------------------------------
    # Show login
    # ----------------------------------------------

    show_login(cookies)

    st.stop()


# ==================================================
# DASHBOARD PAGE
# ==================================================

def dashboard_page():

    # ----------------------------------------------
    # Header
    # ----------------------------------------------

    col1, col2 = st.columns([6, 2])

    with col1:

        st.title(
            "🛡️ Enterprise Endpoint Security "
            "Operations Platform"
        )

        st.write(
            "### Darshayu Global Solutions"
        )


    with col2:

        st.write("### Version")

        st.write("v1.0")

        st.write(
            datetime.now().strftime(
                "%d-%b-%Y"
            )
        )


    st.divider()


    # ==================================================
    # USER SESSION
    # ==================================================

    user_col1, user_col2 = st.columns(
        [6, 1]
    )

    with user_col1:

        st.info(
            f"👤 Logged in as: "
            f"**{st.session_state['display_name']}** "
            f"| Role: "
            f"**{st.session_state['role']}**"
        )


    with user_col2:

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            logout()


    # ==================================================
    # ENDPOINT SEARCH
    # ==================================================

    search_col1, search_col2 = st.columns(
        [5, 1]
    )


    with search_col1:

        hostname = st.text_input(
            "🔍 Search Endpoint",
            placeholder="Enter Hostname..."
        )


    with search_col2:

        st.write("")
        st.write("")

        open_endpoint = st.button(
            "Open Endpoint",
            use_container_width=True
        )


    # ==================================================
    # OPEN ENDPOINT
    # ==================================================

    if open_endpoint and hostname:

        st.divider()

        endpoint360()


    # ==================================================
    # LIVE KPI SECTION
    # ==================================================

    st.divider()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)


    with kpi1:

        st.metric(
            "🖥️ Total Endpoints",
            get_total_devices(),
            "Live"
        )


    with kpi2:

        st.metric(
            "🛡️ Defender Coverage",
            f"{get_defender_coverage()}%"
        )


    with kpi3:

        st.metric(
            "🛡️ CrowdStrike Coverage",
            f"{get_crowdstrike_coverage()}%"
        )


    with kpi4:

        st.metric(
            "🔒 BitLocker Compliance",
            f"{get_bitlocker_compliance()}%"
        )


    kpi5, kpi6, kpi7, kpi8 = st.columns(4)


    with kpi5:

        st.metric(
            "⚠️ High Risk Endpoints",
            get_high_risk_devices()
        )


    with kpi6:

        st.metric(
            "🚨 Open Incidents",
            get_open_incidents()
        )


    with kpi7:

        st.metric(
            "⏱️ SLA Compliance",
            f"{get_sla_compliance()}%"
        )


    with kpi8:

        st.metric(
            "📊 Average Risk Score",
            get_average_risk_score()
        )


    # ==================================================
    # CRITICAL INCIDENT QUEUE
    # ==================================================

    st.divider()

    st.subheader(
        "🚨 Critical Incident Queue"
    )

    incidents = get_recent_incidents()


    if incidents:

        incident_df = pd.DataFrame(
            incidents,
            columns=[
                "Incident ID",
                "Endpoint",
                "Incident Title",
                "Severity",
                "Status",
                "Detection Source"
            ]
        )


        st.dataframe(
            incident_df,
            use_container_width=True,
            hide_index=True,
            column_config={

                "Incident ID":
                    st.column_config.TextColumn(
                        "Incident ID",
                        width="small"
                    ),

                "Endpoint":
                    st.column_config.TextColumn(
                        "Endpoint",
                        width="medium"
                    ),

                "Incident Title":
                    st.column_config.TextColumn(
                        "Incident Title",
                        width="large"
                    ),

                "Severity":
                    st.column_config.TextColumn(
                        "Severity",
                        width="small"
                    ),

                "Status":
                    st.column_config.TextColumn(
                        "Status",
                        width="small"
                    ),

                "Detection Source":
                    st.column_config.TextColumn(
                        "Detection Source",
                        width="medium"
                    )
            }
        )


    else:

        st.success(
            "No active incidents found."
        )


    # ==================================================
    # COMPLIANCE DASHBOARD
    # ==================================================

    st.divider()

    st.subheader(
        "📈 Compliance Dashboard"
    )


    chart1, chart2, chart3 = st.columns(3)


    # --------------------------------------------------
    # Defender
    # --------------------------------------------------

    with chart1:

        st.markdown(
            "### 🛡️ Defender Health"
        )


        defender_data = pd.DataFrame(
            get_defender_chart(),
            columns=[
                "Status",
                "Count"
            ]
        )


        if not defender_data.empty:

            st.bar_chart(
                defender_data.set_index(
                    "Status"
                ),
                height=260
            )


        else:

            st.info(
                "No Defender data available."
            )


    # --------------------------------------------------
    # BitLocker
    # --------------------------------------------------

    with chart2:

        st.markdown(
            "### 🔒 BitLocker"
        )


        bitlocker_data = pd.DataFrame(
            get_bitlocker_chart(),
            columns=[
                "Status",
                "Count"
            ]
        )


        if not bitlocker_data.empty:

            st.bar_chart(
                bitlocker_data.set_index(
                    "Status"
                ),
                height=260
            )


        else:

            st.info(
                "No BitLocker data available."
            )


    # --------------------------------------------------
    # Risk
    # --------------------------------------------------

    with chart3:

        st.markdown(
            "### ⚠️ Risk Distribution"
        )


        risk_data = pd.DataFrame(
            get_risk_distribution(),
            columns=[
                "Risk Level",
                "Count"
            ]
        )


        if not risk_data.empty:

            st.bar_chart(
                risk_data.set_index(
                    "Risk Level"
                ),
                height=260
            )


        else:

            st.info(
                "No risk data available."
            )


    # ==================================================
    # RECENT SECURITY ACTIVITIES
    # ==================================================

    st.divider()

    st.subheader(
        "📋 Recent Security Activities"
    )

    activities = get_recent_timeline()


    if activities:

        activity_df = pd.DataFrame(
            activities,
            columns=[
                "Endpoint",
                "Event Time",
                "Security Activity",
                "Severity"
            ]
        )


        activity_df["Event Time"] = (
            pd.to_datetime(
                activity_df["Event Time"]
            ).dt.strftime(
                "%d-%b-%Y %H:%M"
            )
        )


        st.dataframe(
            activity_df,
            use_container_width=True,
            hide_index=True,
            column_config={

                "Endpoint":
                    st.column_config.TextColumn(
                        "Endpoint",
                        width="medium"
                    ),

                "Event Time":
                    st.column_config.TextColumn(
                        "Time",
                        width="medium"
                    ),

                "Security Activity":
                    st.column_config.TextColumn(
                        "Security Activity",
                        width="large"
                    ),

                "Severity":
                    st.column_config.TextColumn(
                        "Severity",
                        width="small"
                    )
            }
        )


    else:

        st.info(
            "No recent endpoint activities found."
        )


    # ==================================================
    # FOOTER
    # ==================================================

    st.divider()

    st.caption(
        "EESOP v1.0 | Enterprise Endpoint Security "
        "Operations Platform"
    )


# ==================================================
# NAVIGATION DEFINITIONS
# ==================================================

login = st.Page(
    login_page,
    title="Secure Login",
    icon="🔐",
    url_path="login",
    default=True
)


dashboard = st.Page(
    dashboard_page,
    title="Dashboard",
    icon="🏠",
    url_path="dashboard"
)


endpoint_page = st.Page(
    "pages/1_Endpoint_360.py",
    title="Endpoint 360",
    icon="🖥️",
    url_path="endpoint-360"
)


policy_page = st.Page(
    "pages/2_Policy_Management.py",
    title="Policy Management",
    icon="📋",
    url_path="policy-management"
)


remediation_page = st.Page(
    "pages/3_Remediation_Center.py",
    title="Remediation Center",
    icon="🛠️",
    url_path="remediation-center"
)

incident_page = st.Page(
    "pages/4_Incident_Management.py",
    title="Incident Management",
    icon="🚨",
    url_path="incident-management"
)

# ==================================================
# DYNAMIC NAVIGATION
# ==================================================

if st.session_state.get(
    "authenticated",
    False
):

    pg = st.navigation(
        {
            "EESOP": [
                dashboard,
                incident_page,
                endpoint_page,
                policy_page,
                remediation_page
            ]
        },
        position="sidebar",
        expanded=True
    )


else:

    pg = st.navigation(
        [
            login
        ],
        position="sidebar"
    )


# ==================================================
# RUN SELECTED PAGE
# ==================================================

pg.run()