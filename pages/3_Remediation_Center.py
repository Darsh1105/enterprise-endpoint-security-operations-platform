from services.auth_guard import require_login

require_login()
import streamlit as st

from endpoint_operations.endpoint_service import (
    load_devices
)

from endpoint_operations.remediation_service import (
    load_scripts,
    load_deployments,
    request_deployment,
    approve_script_deployment,
    run_script_deployment,
    validate_script_deployment,
    create_remediation_timeline_event,
    create_remediation_action
)

from services.permission_service import can


# ==================================================
# Page Configuration
# ==================================================

st.set_page_config(
    page_title="EESOP - Remediation Center",
    page_icon="🔧",
    layout="wide"
)


# ==================================================
# Authentication
# ==================================================

if not st.session_state.get(
    "authenticated",
    False
):

    st.error(
        "Please login to access Remediation Center."
    )

    st.stop()


# ==================================================
# Header
# ==================================================

st.title(
    "🔧 Endpoint Remediation Center"
)

st.caption(
    "Security remediation, script deployment, "
    "approval, execution and validation."
)

st.caption(
    f"👤 {st.session_state.get('display_name')} "
    f"| Role: {st.session_state.get('role')}"
)


# ==================================================
# Load Data
# ==================================================

scripts = load_scripts()

deployments = load_deployments()

devices = load_devices()


if not scripts:

    st.warning(
        "No remediation scripts found."
    )

    st.stop()


if not devices:

    st.warning(
        "No endpoints found."
    )

    st.stop()


# ==================================================
# Summary
# ==================================================

total_scripts = len(scripts)

total_deployments = len(deployments)

pending_approval = len([
    d for d in deployments
    if d["approval_status"] == "Pending"
])

completed = len([
    d for d in deployments
    if d["execution_status"] == "Completed"
])

validated = len([
    d for d in deployments
    if d["validation_status"] == "Validated"
])


st.subheader(
    "Remediation Operations"
)


c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Scripts",
        total_scripts
    )

with c2:
    st.metric(
        "Deployments",
        total_deployments
    )

with c3:
    st.metric(
        "Pending Approval",
        pending_approval
    )

with c4:
    st.metric(
        "Executed",
        completed
    )

with c5:
    st.metric(
        "Validated",
        validated
    )


st.divider()


# ==================================================
# Create Deployment Request
# ==================================================

st.subheader(
    "🚀 Create Remediation Request"
)


if can("create_remediation_request"):

    left, right = st.columns(2)


    # ==================================================
    # Script Selection
    # ==================================================

    with left:

        script_options = {
            (
                f"{script['script_name']} | "
                f"{script['script_category']} | "
                f"{script['risk_level']} Risk"
            ): script

            for script in scripts
        }


        selected_script_label = st.selectbox(
            "Select Security Script",
            list(
                script_options.keys()
            )
        )


        selected_script = script_options[
            selected_script_label
        ]


        st.markdown(
            f"**Purpose:** "
            f"{selected_script['purpose']}"
        )


        st.write(
            f"**Tool:** "
            f"{selected_script['tool_name']}"
        )


        st.write(
            f"**Type:** "
            f"{selected_script['script_type']}"
        )


        st.write(
            f"**Version:** "
            f"{selected_script['version']}"
        )


        st.write(
            f"**Risk:** "
            f"{selected_script['risk_level']}"
        )


    # ==================================================
    # Endpoint Selection
    # ==================================================

    with right:

        device_options = {
            device["hostname"]: device
            for device in devices
        }


        selected_hostname = st.selectbox(
            "Target Endpoint",
            list(
                device_options.keys()
            )
        )


        selected_device = device_options[
            selected_hostname
        ]


        st.write(
            f"**Operating System:** "
            f"{selected_device['operating_system']}"
        )


        st.write(
            f"**Risk Score:** "
            f"{selected_device['risk_score']}"
        )


        st.write(
            f"**Device Status:** "
            f"{selected_device['device_status']}"
        )


        remarks = st.text_area(
            "Deployment Request Remarks",
            placeholder=(
                "Describe why this remediation "
                "is required..."
            )
        )


    # ==================================================
    # Pre-check
    # ==================================================

    st.divider()

    st.subheader(
        "🔍 Pre-check"
    )


    precheck_col1, precheck_col2 = st.columns(2)


    with precheck_col1:

        if st.button(
            "🔍 Run Pre-check"
        ):

            st.success(
                "Pre-check completed successfully."
            )

            st.write(
                "✓ Endpoint reachable"
            )

            st.write(
                "✓ Security agent detected"
            )

            st.write(
                "✓ Target operating system supported"
            )

            st.write(
                "✓ Script version approved"
            )


    with precheck_col2:

        st.info(
            "V1 pre-check is simulated. "
            "Actual endpoint connectivity can be "
            "integrated in a future version."
        )


    # ==================================================
    # Request Deployment
    # ==================================================

    st.divider()


    if st.button(
        "📨 Request Script Deployment",
        type="primary"
    ):

        deployment_id = request_deployment(
            script_id=(
                selected_script["script_id"]
            ),
            device_id=(
                selected_device["device_id"]
            ),
            requested_by=(
                st.session_state[
                    "display_name"
                ]
            ),
            remarks=remarks
        )


        create_remediation_timeline_event(
            device_id=(
                selected_device["device_id"]
            ),
            event_type=(
                "Remediation Requested"
            ),
            description=(
                f"Remediation script "
                f"'{selected_script['script_name']}' "
                f"requested for "
                f"{selected_device['hostname']}."
            ),
            severity=(
                selected_script["risk_level"]
            ),
            performed_by=(
                st.session_state[
                    "display_name"
                ]
            )
        )


        create_remediation_action(
            device_id=(
                selected_device["device_id"]
            ),
            action_name=(
                f"Request Remediation - "
                f"{selected_script['script_name']}"
            ),
            tool_name=(
                selected_script["tool_name"]
            ),
            result=(
                "Deployment request created"
            ),
            remarks=remarks,
            requested_by=(
                st.session_state[
                    "display_name"
                ]
            )
        )


        st.success(
            f"Deployment request "
            f"#{deployment_id} created."
        )


        st.rerun()


else:

    st.info(
        "🔒 Creating remediation requests "
        "requires the appropriate role."
    )


# ==================================================
# Deployment Queue
# ==================================================

st.divider()

st.subheader(
    "📋 Remediation Deployment Queue"
)


deployments = load_deployments()


if not deployments:

    st.info(
        "No remediation deployment requests."
    )


else:

    for deployment in deployments:

        status_icon = "🟢"


        if (
            deployment["approval_status"]
            == "Pending"
        ):

            status_icon = "🟡"


        if (
            deployment["validation_status"]
            == "Validated"
        ):

            status_icon = "✅"


        with st.expander(
            f"{status_icon} "
            f"#{deployment['deployment_id']} | "
            f"{deployment['script_name']} | "
            f"{deployment['hostname']}"
        ):

            # ==========================================
            # Details
            # ==========================================

            d1, d2, d3 = st.columns(3)


            with d1:

                st.write(
                    "**Script**"
                )

                st.write(
                    deployment["script_name"]
                )

                st.write(
                    "**Category**"
                )

                st.write(
                    deployment["script_category"]
                )


            with d2:

                st.write(
                    "**Endpoint**"
                )

                st.write(
                    deployment["hostname"]
                )

                st.write(
                    "**Tool**"
                )

                st.write(
                    deployment["tool_name"]
                )


            with d3:

                st.write(
                    "**Requested By**"
                )

                st.write(
                    deployment["requested_by"]
                )

                st.write(
                    "**Requested Time**"
                )

                st.write(
                    deployment["requested_time"]
                )


            st.divider()


            # ==========================================
            # Lifecycle
            # ==========================================

            st.markdown(
                "### 🔄 Deployment Lifecycle"
            )


            st.write(
                f"Approval: "
                f"**{deployment['approval_status']}**"
            )


            st.write(
                f"Deployment: "
                f"**{deployment['deployment_status']}**"
            )


            st.write(
                f"Execution: "
                f"**{deployment['execution_status']}**"
            )


            st.write(
                f"Validation: "
                f"**{deployment['validation_status']}**"
            )


            # ==========================================
            # Approval
            # ==========================================

            if (
                deployment["approval_status"]
                == "Pending"
            ):

                if can("approve_remediation"):

                    if st.button(
                        "👤 Approve Deployment",
                        key=(
                            f"approve_"
                            f"{deployment['deployment_id']}"
                        )
                    ):

                        approve_script_deployment(
                            deployment[
                                "deployment_id"
                            ],
                            approved_by=(
                                st.session_state[
                                    "display_name"
                                ]
                            )
                        )


                        create_remediation_timeline_event(
                            device_id=(
                                deployment[
                                    "device_id"
                                ]
                            ),
                            event_type=(
                                "Remediation Approved"
                            ),
                            description=(
                                f"Deployment "
                                f"#{deployment['deployment_id']} "
                                f"approved for "
                                f"{deployment['script_name']}."
                            ),
                            severity="Informational",
                            performed_by=(
                                st.session_state[
                                    "display_name"
                                ]
                            )
                        )


                        st.success(
                            "Deployment approved."
                        )

                        st.rerun()

                else:

                    st.info(
                        "🔒 Approval requires "
                        "Security Lead or Administrator "
                        "access."
                    )


            # ==========================================
            # Execution
            # ==========================================

            elif (
                deployment[
                    "approval_status"
                ]
                == "Approved"

                and

                deployment[
                    "execution_status"
                ]
                == "Not Executed"
            ):

                if can(
                    "execute_remediation"
                ):

                    if st.button(
                        "▶️ Execute Remediation",
                        key=(
                            f"execute_"
                            f"{deployment['deployment_id']}"
                        )
                    ):

                        run_script_deployment(
                            deployment[
                                "deployment_id"
                            ]
                        )


                        create_remediation_timeline_event(
                            device_id=(
                                deployment[
                                    "device_id"
                                ]
                            ),
                            event_type=(
                                "Remediation Executed"
                            ),
                            description=(
                                f"Remediation script "
                                f"'{deployment['script_name']}' "
                                f"executed successfully on "
                                f"{deployment['hostname']}."
                            ),
                            severity="Informational",
                            performed_by=(
                                st.session_state[
                                    "display_name"
                                ]
                            )
                        )


                        create_remediation_action(
                            device_id=(
                                deployment[
                                    "device_id"
                                ]
                            ),
                            action_name=(
                                f"Execute - "
                                f"{deployment['script_name']}"
                            ),
                            tool_name=(
                                deployment[
                                    "tool_name"
                                ]
                            ),
                            result=(
                                "Execution completed successfully"
                            ),
                            remarks=(
                                "V1 simulated script execution."
                            ),
                            requested_by=(
                                st.session_state[
                                    "display_name"
                                ]
                            )
                        )


                        st.success(
                            "Remediation execution completed."
                        )

                        st.rerun()

                else:

                    st.info(
                        "🔒 Remediation execution "
                        "requires Security Engineer, "
                        "Security Lead or Administrator "
                        "access."
                    )


            # ==========================================
            # Validation
            # ==========================================

            elif (
                deployment[
                    "execution_status"
                ]
                == "Completed"

                and

                deployment[
                    "validation_status"
                ]
                != "Validated"
            ):

                if can(
                    "validate_remediation"
                ):

                    if st.button(
                        "✅ Validate Remediation",
                        key=(
                            f"validate_"
                            f"{deployment['deployment_id']}"
                        )
                    ):

                        validate_script_deployment(
                            deployment[
                                "deployment_id"
                            ]
                        )


                        create_remediation_timeline_event(
                            device_id=(
                                deployment[
                                    "device_id"
                                ]
                            ),
                            event_type=(
                                "Remediation Validated"
                            ),
                            description=(
                                f"Remediation "
                                f"'{deployment['script_name']}' "
                                f"validated successfully on "
                                f"{deployment['hostname']}."
                            ),
                            severity="Informational",
                            performed_by=(
                                st.session_state[
                                    "display_name"
                                ]
                            )
                        )


                        create_remediation_action(
                            device_id=(
                                deployment[
                                    "device_id"
                                ]
                            ),
                            action_name=(
                                f"Validate - "
                                f"{deployment['script_name']}"
                            ),
                            tool_name=(
                                deployment[
                                    "tool_name"
                                ]
                            ),
                            result=(
                                "Remediation validated successfully"
                            ),
                            remarks=(
                                "Post-remediation validation "
                                "completed."
                            ),
                            requested_by=(
                                st.session_state[
                                    "display_name"
                                ]
                            )
                        )


                        st.success(
                            "Remediation validated."
                        )

                        st.rerun()

                else:

                    st.info(
                        "🔒 Remediation validation "
                        "requires Security Engineer, "
                        "Security Lead or Administrator "
                        "access."
                    )


            # ==========================================
            # Completed
            # ==========================================

            elif (
                deployment[
                    "validation_status"
                ]
                == "Validated"
            ):

                st.success(
                    "✅ Remediation successfully "
                    "completed and validated."
                )


            # ==========================================
            # Remarks
            # ==========================================

            if deployment["remarks"]:

                st.caption(
                    f"Remarks: "
                    f"{deployment['remarks']}"
                )


            if deployment[
                "execution_result"
            ]:

                st.info(
                    f"Execution Result: "
                    f"{deployment['execution_result']}"
                )