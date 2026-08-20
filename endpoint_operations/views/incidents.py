import streamlit as st

from endpoint_operations.incident_service import (
    load_incidents
)

from endpoint_operations.response_action_service import (
    get_response_actions,
    create_response_action,
    execute_response_action,
    get_incident_response_actions
)

from services.permission_service import can


def show(device):

    incidents = load_incidents(
        device["device_id"]
    )

    st.subheader(
        "🚨 Endpoint Incidents"
    )

    if not incidents:

        st.success(
            "No incidents found."
        )

        return


    # ==================================================
    # Incident List
    # ==================================================

    for incident in incidents:

        severity = incident["severity"]

        if severity == "Critical":

            icon = "⛔"

        elif severity == "High":

            icon = "🔴"

        elif severity == "Medium":

            icon = "🟠"

        elif severity == "Low":

            icon = "🟡"

        else:

            icon = "🟢"


        with st.expander(
            f"{icon} "
            f"{incident['incident_number']} | "
            f"{incident['title']}"
        ):


            # ==================================================
            # Incident Details
            # ==================================================

            col1, col2 = st.columns(2)


            with col1:

                st.write(
                    "**Severity**"
                )

                st.write(
                    incident["severity"]
                )


                st.write(
                    "**Status**"
                )

                st.write(
                    incident["status"]
                )


                st.write(
                    "**Detection Source**"
                )

                st.write(
                    incident["detection_source"]
                )


                st.write(
                    "**Assigned To**"
                )

                st.write(
                    incident["assigned_to"]
                )


            with col2:

                st.write(
                    "**SLA**"
                )

                st.write(
                    incident["sla_status"]
                )


                st.write(
                    "**Created**"
                )

                st.write(
                    incident["created_time"]
                )


                st.write(
                    "**Last Updated**"
                )

                st.write(
                    incident["updated_time"]
                )


            # ==================================================
            # Description
            # ==================================================

            st.markdown(
                "### Description"
            )

            st.write(
                incident["description"]
            )


            # ==================================================
            # Response Actions
            # ==================================================

            st.divider()

            st.markdown(
                "### 🛡️ Incident Response Actions"
            )


            st.caption(
                "Endpoint response actions are simulated "
                "for V1 and recorded in the security audit trail."
            )


            available_actions = (
                get_response_actions()
            )


            # ==================================================
            # Existing Actions
            # ==================================================

            existing_actions = (
                get_incident_response_actions(
                    incident["incident_id"]
                )
            )


            if existing_actions:

                st.markdown(
                    "#### 📋 Response Action History"
                )


                for action in existing_actions:

                    if action["status"] == "Completed":

                        action_icon = "✅"

                    elif action["status"] == "Pending":

                        action_icon = "🟡"

                    else:

                        action_icon = "⚪"


                    with st.expander(
                        f"{action_icon} "
                        f"{action['action_name']} "
                        f"| {action['status']}"
                    ):

                        action_col1, action_col2 = (
                            st.columns(2)
                        )


                        with action_col1:

                            st.write(
                                "**Action Type**"
                            )

                            st.write(
                                action["action_type"]
                            )


                            st.write(
                                "**Security Tool**"
                            )

                            st.write(
                                action["tool_name"]
                            )


                            st.write(
                                "**Requested By**"
                            )

                            st.write(
                                action["requested_by"]
                            )


                        with action_col2:

                            st.write(
                                "**Executed By**"
                            )

                            st.write(
                                action["executed_by"]
                                or "Not executed"
                            )


                            st.write(
                                "**Created**"
                            )

                            st.write(
                                action["created_at"]
                            )


                            st.write(
                                "**Executed**"
                            )

                            st.write(
                                action["executed_at"]
                                or "Not executed"
                            )


                        if action["result"]:

                            st.info(
                                f"Result: "
                                f"{action['result']}"
                            )


                        if action["remarks"]:

                            st.caption(
                                f"Remarks: "
                                f"{action['remarks']}"
                            )


            else:

                st.info(
                    "No response actions have been "
                    "recorded for this incident."
                )


            # ==================================================
            # Create Response Action
            # ==================================================

            st.markdown(
                "#### ⚙️ Create Response Action"
            )


            if can(
                "create_incident_remediation"
            ):

                action_options = {}

                for action in available_actions:

                    label = (
                        f"{action['action_name']} "
                        f"| "
                        f"{action['tool_name']} "
                        f"| "
                        f"{action['risk_level']} Risk"
                    )

                    action_options[
                        label
                    ] = action


                selected_action_label = (
                    st.selectbox(
                        "Select Response Action",
                        list(
                            action_options.keys()
                        ),
                        key=(
                            f"response_action_"
                            f"{incident['incident_id']}"
                        )
                    )
                )


                selected_action = (
                    action_options[
                        selected_action_label
                    ]
                )


                st.write(
                    f"**Action Type:** "
                    f"{selected_action['action_type']}"
                )


                st.write(
                    f"**Tool:** "
                    f"{selected_action['tool_name']}"
                )


                st.write(
                    f"**Risk:** "
                    f"{selected_action['risk_level']}"
                )


                remarks = st.text_area(
                    "Action Remarks",
                    placeholder=(
                        "Explain why this response "
                        "action is required..."
                    ),
                    key=(
                        f"response_remarks_"
                        f"{incident['incident_id']}"
                    )
                )


                if st.button(
                    "📨 Create Response Action",
                    key=(
                        f"create_response_"
                        f"{incident['incident_id']}"
                    )
                ):

                    action_id = (
                        create_response_action(
                            incident_id=(
                                incident[
                                    "incident_id"
                                ]
                            ),
                            device_id=(
                                device[
                                    "device_id"
                                ]
                            ),
                            action_type=(
                                selected_action[
                                    "action_type"
                                ]
                            ),
                            action_name=(
                                selected_action[
                                    "action_name"
                                ]
                            ),
                            tool_name=(
                                selected_action[
                                    "tool_name"
                                ]
                            ),
                            requested_by=(
                                st.session_state[
                                    "display_name"
                                ]
                            ),
                            remarks=remarks
                        )
                    )


                    st.success(
                        f"Response action "
                        f"#{action_id} created."
                    )


                    st.rerun()


            else:

                st.info(
                    "🔒 You do not have permission "
                    "to create incident response actions."
                )


            # ==================================================
            # Execute Pending Actions
            # ==================================================

            pending_actions = [

                action

                for action in existing_actions

                if action["status"] == "Pending"

            ]


            if pending_actions:

                st.markdown(
                    "#### ▶️ Execute Response Action"
                )


                for action in pending_actions:

                    if can(
                        "execute_remediation"
                    ):

                        if st.button(
                            f"▶️ Execute "
                            f"{action['action_name']}",
                            key=(
                                f"execute_response_"
                                f"{action['action_id']}"
                            )
                        ):

                            success, message = (
                                execute_response_action(
                                    action_id=(
                                        action[
                                            "action_id"
                                        ]
                                    ),
                                    executed_by=(
                                        st.session_state[
                                            "display_name"
                                        ]
                                    )
                                )
                            )


                            if success:

                                st.success(
                                    message
                                )

                                st.rerun()

                            else:

                                st.error(
                                    message
                                )

                    else:

                        st.info(
                            "🔒 Execution requires "
                            "Security Engineer, "
                            "Security Lead or "
                            "Administrator access."
                        )

                        break