import streamlit as st
import pandas as pd

from database.connection import get_connection

from services.auth_guard import require_login
from services.permission_service import can

from endpoint_operations.response_action_service import (
    get_response_actions,
    create_response_action,
    execute_response_action,
    get_incident_response_actions
)

from endpoint_operations.remediation_service import (
    load_scripts,
    load_deployments,
    request_deployment,
    approve_script_deployment,
    run_script_deployment,
    validate_script_deployment
)

# ==================================================
# Authentication
# ==================================================

require_login()


# ==================================================
# Page Configuration
# ==================================================

st.title("🚨 Incident Management")

st.caption(
    "Central Security Operations Center incident queue"
)


# ==================================================
# Permission
# ==================================================

if not can("view_incidents"):

    st.error(
        "⛔ You do not have permission to view incidents."
    )

    st.stop()


# ==================================================
# Load Incidents
# ==================================================

def get_incidents():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                i.incident_id,
                i.incident_number,
                i.device_id,
                d.hostname,
                i.title,
                i.severity,
                i.status,
                i.detection_source,
                i.assigned_to,
                i.sla_status,
                i.created_time,
                i.updated_time,
                i.description

            FROM endpoint_incidents i

            LEFT JOIN devices d
                ON d.device_id = i.device_id

            ORDER BY
                CASE i.severity
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    ELSE 5
                END,
                i.created_time DESC
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


# ==================================================
# Incident Details
# ==================================================

def get_incident(incident_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                i.incident_id,
                i.incident_number,
                i.device_id,
                d.hostname,
                d.operating_system,
                d.risk_score,
                i.title,
                i.severity,
                i.status,
                i.detection_source,
                i.assigned_to,
                i.sla_status,
                i.created_time,
                i.updated_time,
                i.description

            FROM endpoint_incidents i

            LEFT JOIN devices d
                ON d.device_id = i.device_id

            WHERE i.incident_id = ?
            """,
            (incident_id,)
        )

        return cursor.fetchone()

    finally:

        conn.close()


# ==================================================
# Load Data
# ==================================================

incidents = get_incidents()


# ==================================================
# Convert To DataFrame
# ==================================================

columns = [
    "incident_id",
    "incident_number",
    "device_id",
    "hostname",
    "title",
    "severity",
    "status",
    "detection_source",
    "assigned_to",
    "sla_status",
    "created_time",
    "updated_time",
    "description"
]


incident_df = pd.DataFrame(
    incidents,
    columns=columns
)


# ==================================================
# KPI SECTION
# ==================================================

if incident_df.empty:

    total_open = 0
    critical_open = 0
    high_open = 0
    sla_breach = 0

else:

    # ------------------------------------------
    # Operational/open incidents
    # ------------------------------------------

    open_mask = (
        incident_df["status"]
        .fillna("")
        .str.lower()
        .isin([
            "open",
            "in progress",
            "monitoring"
        ])
    )

    total_open = len(
        incident_df[open_mask]
    )


    # ------------------------------------------
    # Critical OPEN incidents
    # ------------------------------------------

    critical_open = len(
        incident_df[
            open_mask
            &
            (
                incident_df["severity"]
                .fillna("")
                .str.lower()
                == "critical"
            )
        ]
    )


    # ------------------------------------------
    # High OPEN incidents
    # ------------------------------------------

    high_open = len(
        incident_df[
            open_mask
            &
            (
                incident_df["severity"]
                .fillna("")
                .str.lower()
                == "high"
            )
        ]
    )


    # ------------------------------------------
    # SLA breaches
    # ------------------------------------------

    sla_breach = len(
        incident_df[
            incident_df["sla_status"]
            .fillna("")
            .str.lower()
            .isin([
                "breached",
                "breach",
                "overdue"
            ])
        ]
    )


kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.metric(
        "📂 Active Incidents",
        total_open
    )


with kpi2:

    st.metric(
        "🔴 Critical Active",
        critical_open
    )


with kpi3:

    st.metric(
        "🟠 High Active",
        high_open
    )


with kpi4:

    st.metric(
        "⏱️ SLA Breach",
        sla_breach
    )


st.divider()


# ==================================================
# FILTERS
# ==================================================

st.subheader("🔎 Incident Queue Filters")


filter1, filter2, filter3, filter4 = st.columns(4)


with filter1:

    severity_options = ["All"]

    if not incident_df.empty:

        severity_options += sorted(
            incident_df["severity"]
            .dropna()
            .unique()
            .tolist()
        )

    severity_filter = st.selectbox(
        "Severity",
        severity_options
    )


with filter2:

    status_options = ["All"]

    if not incident_df.empty:

        status_options += sorted(
            incident_df["status"]
            .dropna()
            .unique()
            .tolist()
        )

    status_filter = st.selectbox(
        "Status",
        status_options
    )


with filter3:

    source_options = ["All"]

    if not incident_df.empty:

        source_options += sorted(
            incident_df["detection_source"]
            .dropna()
            .unique()
            .tolist()
        )

    source_filter = st.selectbox(
        "Detection Source",
        source_options
    )


with filter4:

    search_filter = st.text_input(
        "Search",
        placeholder=(
            "Incident, hostname or title..."
        )
    )


# ==================================================
# APPLY FILTERS
# ==================================================

filtered_df = incident_df.copy()


if severity_filter != "All":

    filtered_df = filtered_df[
        filtered_df["severity"]
        == severity_filter
    ]


if status_filter != "All":

    filtered_df = filtered_df[
        filtered_df["status"]
        == status_filter
    ]


if source_filter != "All":

    filtered_df = filtered_df[
        filtered_df["detection_source"]
        == source_filter
    ]


if search_filter:

    search_value = search_filter.lower()

    filtered_df = filtered_df[
        filtered_df[
            [
                "incident_number",
                "hostname",
                "title"
            ]
        ]
        .fillna("")
        .astype(str)
        .apply(
            lambda row:
            row.str.lower()
            .str.contains(
                search_value,
                regex=False
            )
            .any(),
            axis=1
        )
    ]


# ==================================================
# INCIDENT QUEUE
# ==================================================

st.subheader("🚨 SOC Incident Queue")


if filtered_df.empty:

    st.info(
        "No incidents match the selected filters."
    )

else:

    display_df = filtered_df[
        [
            "incident_number",
            "hostname",
            "title",
            "severity",
            "status",
            "detection_source",
            "assigned_to",
            "sla_status",
            "created_time"
        ]
    ].copy()


    display_df.columns = [
        "Incident ID",
        "Endpoint",
        "Incident",
        "Severity",
        "Status",
        "Detection Source",
        "Assigned To",
        "SLA",
        "Created"
    ]


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# INCIDENT SELECTION
# ==================================================

st.divider()

st.subheader("🔍 Investigate Incident")


if filtered_df.empty:

    st.info(
        "Select filters that return an incident."
    )

    st.stop()


incident_options = (
    filtered_df[
        "incident_id"
    ]
    .tolist()
)


incident_labels = {

    row["incident_id"]:
        f"{row['incident_number']} | "
        f"{row['severity']} | "
        f"{row['hostname']} | "
        f"{row['title']}"

    for _, row in filtered_df.iterrows()
}


selected_incident_id = st.selectbox(
    "Select Incident",
    incident_options,
    format_func=lambda x:
        incident_labels.get(
            x,
            str(x)
        )
)


# ==================================================
# DETAILS
# ==================================================

incident = get_incident(
    selected_incident_id
)


if incident is None:

    st.error(
        "Incident could not be loaded."
    )

    st.stop()


(
    incident_id,
    incident_number,
    device_id,
    hostname,
    operating_system,
    risk_score,
    title,
    severity,
    status,
    detection_source,
    assigned_to,
    sla_status,
    created_time,
    updated_time,
    description
) = incident


# ==================================================
# Incident Header
# ==================================================

st.markdown(
    f"### 🚨 {incident_number}"
)

st.write(
    f"**{title}**"
)


detail1, detail2, detail3, detail4 = st.columns(4)


with detail1:

    st.metric(
        "Severity",
        severity or "Unknown"
    )


with detail2:

    st.metric(
        "Status",
        status or "Unknown"
    )


with detail3:

    st.metric(
        "SLA",
        sla_status or "Unknown"
    )


with detail4:

    st.metric(
        "Risk Score",
        risk_score if risk_score is not None
        else "N/A"
    )


# ==================================================
# Incident Information
# ==================================================

info1, info2 = st.columns(2)


with info1:

    st.markdown("#### 🖥️ Endpoint")

    st.write(
        f"**Hostname:** {hostname or 'Unknown'}"
    )

    st.write(
        f"**Device ID:** {device_id}"
    )

    st.write(
        f"**Operating System:** "
        f"{operating_system or 'Unknown'}"
    )


with info2:

    st.markdown("#### 🛡️ Detection")

    st.write(
        f"**Source:** "
        f"{detection_source or 'Unknown'}"
    )

    st.write(
        f"**Assigned To:** "
        f"{assigned_to or 'Unassigned'}"
    )

    st.write(
        f"**Created:** "
        f"{created_time or 'Unknown'}"
    )

    st.write(
        f"**Updated:** "
        f"{updated_time or 'Unknown'}"
    )


# ==================================================
# Description
# ==================================================

st.markdown("#### 📝 Description")

if description:

    st.info(description)

else:

    st.info(
        "No incident description available."
    )

# ==================================================
# Investigation Timeline
# ==================================================

st.divider()

st.subheader(
    "🔍 Investigation Timeline"
)


conn = get_connection()
cursor = conn.cursor()

try:

    cursor.execute(
        """
        SELECT
            event_time,
            event_type,
            event_category,
            event_source,
            severity,
            description,
            performed_by

        FROM endpoint_timeline

        WHERE device_id = ?

        ORDER BY event_time DESC

        LIMIT 50
        """,
        (device_id,)
    )

    timeline_events = cursor.fetchall()

finally:

    conn.close()


if timeline_events:

    timeline_df = pd.DataFrame(
        timeline_events,
        columns=[
            "Event Time",
            "Event Type",
            "Category",
            "Source",
            "Severity",
            "Description",
            "Performed By"
        ]
    )


    timeline_df["Event Time"] = (
        pd.to_datetime(
            timeline_df["Event Time"],
            errors="coerce"
        )
        .dt.strftime(
            "%d-%b-%Y %H:%M"
        )
    )


    st.dataframe(
        timeline_df,
        use_container_width=True,
        hide_index=True,
        column_config={

            "Event Time":
                st.column_config.TextColumn(
                    "Time",
                    width="medium"
                ),

            "Event Type":
                st.column_config.TextColumn(
                    "Event",
                    width="medium"
                ),

            "Category":
                st.column_config.TextColumn(
                    "Category",
                    width="medium"
                ),

            "Source":
                st.column_config.TextColumn(
                    "Source",
                    width="medium"
                ),

            "Severity":
                st.column_config.TextColumn(
                    "Severity",
                    width="small"
                ),

            "Description":
                st.column_config.TextColumn(
                    "Description",
                    width="large"
                ),

            "Performed By":
                st.column_config.TextColumn(
                    "Performed By",
                    width="medium"
                )
        }
    )

else:

    st.info(
        "No security timeline events found "
        "for this endpoint."
    )
# ==================================================
# Response Actions
# ==================================================

st.divider()

st.subheader("⚡ Response Actions")


# ==================================================
# Existing Actions
# ==================================================

response_actions = get_incident_response_actions(
    incident_id
)


if response_actions:

    action_df = pd.DataFrame(
        response_actions,
        columns=[
            "Action ID",
            "Incident ID",
            "Device ID",
            "Action Type",
            "Action",
            "Tool",
            "Status",
            "Requested By",
            "Executed By",
            "Result",
            "Remarks",
            "Created",
            "Executed"
        ]
    )

    st.dataframe(
        action_df[
            [
                "Action ID",
                "Action Type",
                "Action",
                "Tool",
                "Status",
                "Requested By",
                "Executed By",
                "Created",
                "Executed"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No response actions recorded for this incident."
    )


# ==================================================
# Request New Response Action
# ==================================================

if can("create_incident_remediation"):

    st.markdown("### ➕ Request Response Action")

    available_actions = get_response_actions()

    action_labels = [
        (
            f"{action['action_name']} "
            f"| {action['tool_name']} "
            f"| Risk: {action['risk_level']}"
        )
        for action in available_actions
    ]

    selected_label = st.selectbox(
        "Response Action",
        action_labels,
        key=f"response_action_{incident_id}"
    )

    selected_action = available_actions[
        action_labels.index(selected_label)
    ]

    remarks = st.text_area(
        "Remarks",
        placeholder=(
            "Explain why this response action "
            "is required..."
        ),
        key=f"response_remarks_{incident_id}"
    )

    if st.button(
        "📨 Request Response Action",
        use_container_width=True,
        key=f"request_action_{incident_id}"
    ):

        requested_by = st.session_state.get(
            "username",
            st.session_state.get(
                "display_name",
                "Unknown"
            )
        )

        try:

            action_id = create_response_action(
                incident_id=incident_id,
                device_id=device_id,
                action_type=selected_action[
                    "action_type"
                ],
                action_name=selected_action[
                    "action_name"
                ],
                tool_name=selected_action[
                    "tool_name"
                ],
                requested_by=requested_by,
                remarks=remarks
            )

            st.success(
                f"Response action requested successfully. "
                f"Action ID: {action_id}"
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Unable to create response action: {error}"
            )


# ==================================================
# Execute Pending Actions
# ==================================================

if response_actions:

    pending_actions = [
        action
        for action in response_actions
        if action["status"] == "Pending"
    ]

    if pending_actions:

        st.markdown(
            "### ▶️ Pending Response Actions"
        )

        if can("execute_remediation"):

            pending_labels = {
                action["action_id"]:
                    (
                        f"#{action['action_id']} | "
                        f"{action['action_name']} | "
                        f"{action['tool_name']}"
                    )
                for action in pending_actions
            }

            selected_action_id = st.selectbox(
                "Select pending action",
                list(pending_labels.keys()),
                format_func=lambda action_id:
                    pending_labels[action_id],
                key=f"pending_action_{incident_id}"
            )

            if st.button(
                "▶️ Execute Response Action",
                type="primary",
                use_container_width=True,
                key=f"execute_action_{incident_id}"
            ):

                executed_by = st.session_state.get(
                    "username",
                    st.session_state.get(
                        "display_name",
                        "Unknown"
                    )
                )

                success, message = (
                    execute_response_action(
                        selected_action_id,
                        executed_by
                    )
                )

                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)

        else:

            st.warning(
                "Your role does not have permission "
                "to execute response actions."
            )
# ==================================================
# Remediation Workflow
# ==================================================

st.divider()

st.subheader("🛠️ Remediation Workflow")

st.caption(
    f"Remediation operations for endpoint: "
    f"{hostname or 'Unknown'}"
)


# ==================================================
# Load deployments for this endpoint
# ==================================================

all_deployments = load_deployments()

device_deployments = [
    deployment
    for deployment in all_deployments
    if deployment[5] == device_id
]


if device_deployments:

    deployment_df = pd.DataFrame(
        device_deployments,
        columns=[
            "Deployment ID",
            "Script ID",
            "Script Name",
            "Script Category",
            "Tool",
            "Device ID",
            "Hostname",
            "Requested By",
            "Requested Time",
            "Approval Status",
            "Deployment Status",
            "Execution Status",
            "Execution Result",
            "Validation Status",
            "Completed Time",
            "Remarks"
        ]
    )

    st.markdown("### 📋 Existing Remediation Deployments")

    st.dataframe(
        deployment_df[
            [
                "Deployment ID",
                "Script Name",
                "Tool",
                "Requested By",
                "Approval Status",
                "Deployment Status",
                "Execution Status",
                "Validation Status",
                "Requested Time"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No remediation deployments exist for this endpoint."
    )


# ==================================================
# Request Remediation
# ==================================================

if can("create_remediation_request"):

    st.markdown("### ➕ Request Remediation")

    scripts = load_scripts()

    if scripts:

        script_labels = [
            (
                f"{script['script_name']} | "
                f"{script['tool_name']} | "
                f"Risk: {script['risk_level']}"
            )
            for script in scripts
        ]

        selected_script_label = st.selectbox(
            "Remediation Script",
            script_labels,
            key=f"remediation_script_{incident_id}"
        )

        selected_script = scripts[
            script_labels.index(
                selected_script_label
            )
        ]

        remediation_remarks = st.text_area(
            "Remediation Remarks",
            placeholder=(
                "Explain why remediation is required..."
            ),
            key=f"remediation_remarks_{incident_id}"
        )

        if st.button(
            "📨 Request Remediation",
            use_container_width=True,
            key=f"request_remediation_{incident_id}"
        ):

            requested_by = st.session_state.get(
                "username",
                st.session_state.get(
                    "display_name",
                    "Unknown"
                )
            )

            try:

                deployment_id = request_deployment(
                    script_id=selected_script[
                        "script_id"
                    ],
                    device_id=device_id,
                    requested_by=requested_by,
                    remarks=remediation_remarks
                )

                st.success(
                    f"Remediation request created. "
                    f"Deployment ID: {deployment_id}"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to create remediation request: "
                    f"{error}"
                )

    else:

        st.info(
            "No active remediation scripts are available."
        )


# ==================================================
# Remediation Approval
# ==================================================

pending_approvals = [
    deployment
    for deployment in device_deployments
    if deployment[9] == "Pending"
]


if pending_approvals and can("approve_remediation"):

    st.markdown("### 👤 Lead Approval")

    approval_options = {
        deployment[0]:
            (
                f"#{deployment[0]} | "
                f"{deployment[2]} | "
                f"{deployment[4]} | "
                f"Requested by: {deployment[7]}"
            )
        for deployment in pending_approvals
    }

    selected_approval_id = st.selectbox(
        "Pending Remediation",
        list(approval_options.keys()),
        format_func=lambda deployment_id:
            approval_options[deployment_id],
        key=f"approval_{incident_id}"
    )

    if st.button(
        "✅ Approve Remediation",
        type="primary",
        use_container_width=True,
        key=f"approve_remediation_{incident_id}"
    ):

        approved_by = st.session_state.get(
            "display_name",
            st.session_state.get(
                "username",
                "Security Lead"
            )
        )

        try:

            approve_script_deployment(
                selected_approval_id,
                approved_by
            )

            st.success(
                f"Deployment #{selected_approval_id} "
                "approved successfully."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Unable to approve remediation: {error}"
            )


# ==================================================
# Remediation Execution
# ==================================================

approved_deployments = [
    deployment
    for deployment in device_deployments
    if deployment[9] == "Approved"
    and deployment[11] == "Not Executed"
]


if approved_deployments and can("execute_remediation"):

    st.markdown("### 👨‍💻 Execute Remediation")

    execution_options = {
        deployment[0]:
            (
                f"#{deployment[0]} | "
                f"{deployment[2]} | "
                f"{deployment[4]}"
            )
        for deployment in approved_deployments
    }

    selected_execution_id = st.selectbox(
        "Approved Remediation",
        list(execution_options.keys()),
        format_func=lambda deployment_id:
            execution_options[deployment_id],
        key=f"execution_{incident_id}"
    )

    if st.button(
        "▶️ Execute Remediation",
        type="primary",
        use_container_width=True,
        key=f"execute_remediation_{incident_id}"
    ):

        try:

            run_script_deployment(
                selected_execution_id
            )

            st.success(
                f"Deployment #{selected_execution_id} "
                "executed successfully."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Unable to execute remediation: {error}"
            )


# ==================================================
# Remediation Validation
# ==================================================

validation_deployments = [
    deployment
    for deployment in device_deployments
    if deployment[11] == "Completed"
    and deployment[13] == "Pending"
]


if validation_deployments and can("validate_remediation"):

    st.markdown("### ✅ Validate Remediation")

    validation_options = {
        deployment[0]:
            (
                f"#{deployment[0]} | "
                f"{deployment[2]} | "
                f"Execution: Completed"
            )
        for deployment in validation_deployments
    }

    selected_validation_id = st.selectbox(
        "Completed Remediation",
        list(validation_options.keys()),
        format_func=lambda deployment_id:
            validation_options[deployment_id],
        key=f"validation_{incident_id}"
    )

    if st.button(
        "✅ Validate Remediation",
        type="primary",
        use_container_width=True,
        key=f"validate_remediation_{incident_id}"
    ):

        try:

            validate_script_deployment(
                selected_validation_id
            )

            st.success(
                f"Deployment #{selected_validation_id} "
                "validated successfully."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Unable to validate remediation: {error}"
            )
# ==================================================
# Investigation Notice
# ==================================================

if can("investigate_incidents"):

    st.success(
        "✅ You have permission to investigate "
        "this incident."
    )

else:

    st.warning(
        "You have view-only access to this incident."
    )