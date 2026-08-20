from services.auth_guard import require_login

require_login()

import streamlit as st
import pandas as pd

from endpoint_operations.policy_service import (
    load_all_policies,
    tune_policy,
    apply_policy,
    validate_policy_change,
    create_policy_timeline_event,
    create_policy_action
)

from endpoint_operations.remediation_service import (
    load_scripts,
    request_deployment,
    create_remediation_timeline_event,
    create_remediation_action
)

from services.permission_service import can


# ==================================================
# Page Configuration
# ==================================================

st.set_page_config(
    page_title="EESOP - Policy Management",
    page_icon="🛡️",
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
        "Please login to access Policy Management."
    )

    st.stop()


# ==================================================
# Header
# ==================================================

st.title(
    "🛡️ Enterprise Security Policy Management"
)

st.caption(
    "Centralized endpoint security policy management, "
    "compliance monitoring, policy tuning, deployment "
    "and remediation."
)

st.caption(
    f"👤 {st.session_state.get('display_name')} "
    f"| Role: {st.session_state.get('role')}"
)



# ==================================================
# Load Data
# ==================================================

policies = load_all_policies()

scripts = load_scripts()


if not policies:

    st.warning(
        "No endpoint security policies found."
    )

    st.stop()


# ==================================================
# Compliance Calculation
# ==================================================

def get_compliance_status(policy):

    current = str(
        policy["current_value"] or ""
    ).strip().lower()

    desired = str(
        policy["desired_value"] or ""
    ).strip().lower()

    status = str(
        policy["status"] or ""
    ).strip()

    deployment = str(
        policy["deployment_status"] or ""
    ).strip()

    if status == "Needs Review":

        return "Non-Compliant"

    if current == desired:

        return "Compliant"

    if deployment in [
        "Pending",
        "Not Deployed"
    ]:

        return "Non-Compliant"

    return "Non-Compliant"


# Convert sqlite3.Row into normal dictionaries
policies = [
    {
        **dict(policy),
        "compliance_status": get_compliance_status(
            policy
        )
    }

    for policy in policies
]


# ==================================================
# Summary
# ==================================================

total = len(policies)

compliant = len([
    p for p in policies
    if p["compliance_status"] == "Compliant"
])

non_compliant = len([
    p for p in policies
    if p["compliance_status"] == "Non-Compliant"
])

needs_review = len([
    p for p in policies
    if p["status"] == "Needs Review"
])

deployed = len([
    p for p in policies
    if p["deployment_status"] == "Applied"
])


compliance_percentage = (
    round(
        (compliant / total) * 100,
        1
    )
    if total
    else 0
)


# ==================================================
# Category Counts
# ==================================================

categories = [
    "CrowdStrike",
    "Defender",
    "Encryption",
    "Firewall",
    "Custom"
]

category_counts = {}

for category in categories:

    category_counts[category] = len([
        p for p in policies
        if p["policy_category"] == category
    ])


# ==================================================
# Policy Estate
# ==================================================

st.subheader("Policy Estate")

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.metric(
        "Total Policies",
        total
    )

with c2:
    st.metric(
        "Compliant",
        compliant
    )

with c3:
    st.metric(
        "Non-Compliant",
        non_compliant
    )

with c4:
    st.metric(
        "Needs Review",
        needs_review
    )

with c5:
    st.metric(
        "Deployed",
        deployed
    )

with c6:
    st.metric(
        "Compliance",
        f"{compliance_percentage}%"
    )


st.divider()


# ==================================================
# Security Tool Distribution
# ==================================================

st.subheader(
    "Security Policy Coverage"
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "CrowdStrike",
        category_counts["CrowdStrike"]
    )

with c2:
    st.metric(
        "Defender",
        category_counts["Defender"]
    )

with c3:
    st.metric(
        "Encryption",
        category_counts["Encryption"]
    )

with c4:
    st.metric(
        "Firewall",
        category_counts["Firewall"]
    )

with c5:
    st.metric(
        "Custom",
        category_counts["Custom"]
    )


st.divider()


# ==================================================
# Filters
# ==================================================

st.subheader(
    "🔎 Policy Search & Filters"
)

f1, f2, f3, f4, f5 = st.columns(5)


with f1:

    category_filter = st.selectbox(
        "Category",
        [
            "All",
            "CrowdStrike",
            "Defender",
            "Encryption",
            "Firewall",
            "Custom"
        ]
    )


with f2:

    compliance_filter = st.selectbox(
        "Compliance",
        [
            "All",
            "Compliant",
            "Non-Compliant"
        ]
    )


with f3:

    deployment_filter = st.selectbox(
        "Deployment",
        [
            "All",
            "Applied",
            "Pending",
            "Not Deployed"
        ]
    )


with f4:

    status_filter = st.selectbox(
        "Status",
        [
            "All",
            "Assigned",
            "Needs Review",
            "Validated",
            "Failed"
        ]
    )


with f5:

    risk_filter = st.selectbox(
        "Risk",
        [
            "All",
            "Low",
            "Medium",
            "High",
            "Critical"
        ]
    )


search = st.text_input(
    "Search Policies",
    placeholder=(
        "Hostname, policy name, tool, "
        "setting, type..."
    )
)


# ==================================================
# Apply Filters
# ==================================================

filtered = policies


if category_filter != "All":

    filtered = [
        p for p in filtered
        if p["policy_category"]
        == category_filter
    ]


if compliance_filter != "All":

    filtered = [
        p for p in filtered
        if p["compliance_status"]
        == compliance_filter
    ]


if deployment_filter != "All":

    filtered = [
        p for p in filtered
        if p["deployment_status"]
        == deployment_filter
    ]


if status_filter != "All":

    filtered = [
        p for p in filtered
        if p["status"]
        == status_filter
    ]


if risk_filter != "All":

    filtered = [
        p for p in filtered
        if p["risk_level"]
        == risk_filter
    ]


if search.strip():

    search_value = search.lower()

    filtered = [
        p for p in filtered

        if (
            search_value
            in str(
                p["hostname"]
            ).lower()

            or search_value
            in str(
                p["policy_name"]
            ).lower()

            or search_value
            in str(
                p["tool_name"]
            ).lower()

            or search_value
            in str(
                p["setting_name"]
            ).lower()

            or search_value
            in str(
                p["policy_type"]
            ).lower()
        )
    ]


st.write(
    f"Showing **{len(filtered)}** "
    f"of **{total}** policies"
)


st.divider()


# ==================================================
# Enterprise Policy Inventory
# ==================================================

st.subheader(
    "📋 Enterprise Policy Inventory"
)


if filtered:

    table_data = []

    for p in filtered:

        table_data.append(
            {
                "ID": p["policy_id"],
                "Endpoint": p["hostname"],
                "Category": p["policy_category"],
                "Policy": p["policy_name"],
                "Tool": p["tool_name"],
                "Current": p["current_value"],
                "Desired": p["desired_value"],
                "Compliance": p[
                    "compliance_status"
                ],
                "Status": p["status"],
                "Deployment": p[
                    "deployment_status"
                ],
                "Risk": p["risk_level"]
            }
        )

    df = pd.DataFrame(
        table_data
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=500
    )

else:

    st.info(
        "No policies match the selected filters."
    )


# ==================================================
# Policy Operations
# ==================================================

st.divider()

st.subheader(
    "⚙️ Policy Operations"
)


if not filtered:

    st.info(
        "No policy available for operations."
    )

else:

    policy_options = {
        (
            f"{p['policy_id']} | "
            f"{p['hostname']} | "
            f"{p['policy_name']}"
        ): p

        for p in filtered
    }

    selected_label = st.selectbox(
        "Select Policy",
        list(
            policy_options.keys()
        )
    )

    selected_policy = policy_options[
        selected_label
    ]


    # ==================================================
    # Selected Policy
    # ==================================================

    compliance_status = (
        selected_policy[
            "compliance_status"
        ]
    )


    if compliance_status == "Compliant":

        st.success(
            "🟢 Policy is Compliant"
        )

    else:

        st.warning(
            "⚠️ Policy is Non-Compliant"
        )


    st.markdown(
        f"### {selected_policy['policy_name']}"
    )

    st.caption(
        f"Endpoint: "
        f"{selected_policy['hostname']} "
        f"| Category: "
        f"{selected_policy['policy_category']} "
        f"| Tool: "
        f"{selected_policy['tool_name']}"
    )


    d1, d2, d3, d4 = st.columns(4)


    with d1:

        st.write("**Setting**")

        st.code(
            str(
                selected_policy[
                    "setting_name"
                ]
            )
        )


    with d2:

        st.write("**Current Value**")

        st.code(
            str(
                selected_policy[
                    "current_value"
                ]
            )
        )


    with d3:

        st.write("**Desired Value**")

        st.code(
            str(
                selected_policy[
                    "desired_value"
                ]
            )
        )


    with d4:

        st.write("**Risk Level**")

        st.write(
            selected_policy[
                "risk_level"
            ]
        )


    # ==================================================
    # Policy Tuning
    # ==================================================

    st.markdown(
        "### 🛠️ Policy Tuning"
    )


    if can("tune_policy"):

        new_value = st.text_input(
            "New Desired Value",
            value=str(
                selected_policy[
                    "desired_value"
                ]
            )
        )


        reason = st.text_area(
            "Change Reason",
            placeholder=(
                "Explain the security reason "
                "for this policy change..."
            )
        )


        if st.button(
            "🛠️ Submit Policy Change"
        ):

            if not new_value.strip():

                st.error(
                    "Desired value cannot be empty."
                )

            elif not reason.strip():

                st.error(
                    "Change reason is required."
                )

            else:

                tune_policy(
                    policy_id=(
                        selected_policy[
                            "policy_id"
                        ]
                    ),
                    desired_value=new_value,
                    change_reason=reason,
                    updated_by=(
                        st.session_state[
                            "display_name"
                        ]
                    )
                )


                create_policy_timeline_event(
                    device_id=(
                        selected_policy[
                            "device_id"
                        ]
                    ),
                    event_type="Policy Tuned",
                    description=(
                        f"Policy "
                        f"'{selected_policy['policy_name']}' "
                        f"changed to '{new_value}'. "
                        f"Reason: {reason}"
                    ),
                    severity=(
                        selected_policy[
                            "risk_level"
                        ]
                    ),
                    performed_by=(
                        st.session_state[
                            "display_name"
                        ]
                    )
                )


                create_policy_action(
                    device_id=(
                        selected_policy[
                            "device_id"
                        ]
                    ),
                    action_name=(
                        f"Tune Policy - "
                        f"{selected_policy['policy_name']}"
                    ),
                    action_category=(
                        "Policy Management"
                    ),
                    tool_name=(
                        selected_policy[
                            "tool_name"
                        ]
                    ),
                    result=(
                        "Policy change submitted"
                    ),
                    remarks=reason
                )


                st.success(
                    "Policy change submitted."
                )

                st.rerun()

    else:

        st.info(
            "🔒 Policy tuning requires "
            "Security Engineer, Security Lead "
            "or Administrator access."
        )


    # ==================================================
    # Policy Deployment
    # ==================================================

    st.markdown(
        "### 🚀 Policy Deployment"
    )


    if selected_policy["status"] == "Needs Review":

        if can("deploy_policy"):

            if st.button(
                "🚀 Deploy Selected Policy"
            ):

                success, message = (
                    apply_policy(
                        policy_id=(
                            selected_policy[
                                "policy_id"
                            ]
                        ),
                        updated_by=(
                            st.session_state[
                                "display_name"
                            ]
                        )
                    )
                )


                if success:

                    create_policy_timeline_event(
                        device_id=(
                            selected_policy[
                                "device_id"
                            ]
                        ),
                        event_type=(
                            "Policy Deployed"
                        ),
                        description=(
                            f"Policy "
                            f"'{selected_policy['policy_name']}' "
                            f"deployment completed."
                        ),
                        severity="Informational",
                        performed_by=(
                            st.session_state[
                                "display_name"
                            ]
                        )
                    )


                    create_policy_action(
                        device_id=(
                            selected_policy[
                                "device_id"
                            ]
                        ),
                        action_name=(
                            f"Deploy Policy - "
                            f"{selected_policy['policy_name']}"
                        ),
                        action_category=(
                            "Policy Deployment"
                        ),
                        tool_name=(
                            selected_policy[
                                "tool_name"
                            ]
                        ),
                        result=(
                            "Deployment completed"
                        ),
                        remarks=(
                            "Policy deployed through "
                            "EESOP Policy Management."
                        )
                    )


                    st.success(
                        "Policy deployment completed."
                    )

                    st.rerun()

                else:

                    st.error(
                        message
                    )

        else:

            st.info(
                "🔒 Policy deployment requires "
                "Security Engineer, Security Lead "
                "or Administrator access."
            )

    else:

        st.info(
            "Policy must be in "
            "'Needs Review' state before "
            "deployment."
        )


    # ==================================================
    # Policy Validation
    # ==================================================

    st.markdown(
        "### ✅ Policy Validation"
    )


    if (
        selected_policy[
            "deployment_status"
        ] == "Applied"

        and

        selected_policy[
            "status"
        ] != "Validated"
    ):

        if can("validate_policy"):

            if st.button(
                "✅ Validate Selected Policy"
            ):

                success, message = (
                    validate_policy_change(
                        policy_id=(
                            selected_policy[
                                "policy_id"
                            ]
                        ),
                        updated_by=(
                            st.session_state[
                                "display_name"
                            ]
                        )
                    )
                )


                if success:

                    create_policy_timeline_event(
                        device_id=(
                            selected_policy[
                                "device_id"
                            ]
                        ),
                        event_type=(
                            "Policy Validated"
                        ),
                        description=(
                            f"Policy "
                            f"'{selected_policy['policy_name']}' "
                            f"validated successfully."
                        ),
                        severity="Informational",
                        performed_by=(
                            st.session_state[
                                "display_name"
                            ]
                        )
                    )


                    st.success(
                        "Policy validation completed."
                    )

                    st.rerun()

                else:

                    st.error(
                        message
                    )

        else:

            st.info(
                "🔒 Policy validation requires "
                "Security Engineer, Security Lead "
                "or Administrator access."
            )


    elif (
        selected_policy["status"]
        == "Validated"
    ):

        st.success(
            "✅ Policy has already been validated."
        )

    else:

        st.info(
            "Deploy the policy before validation."
        )


    # ==================================================
    # Policy Remediation
    # ==================================================

    st.divider()

    st.markdown(
        "### 🔧 Policy Remediation"
    )


    if (
        selected_policy[
            "compliance_status"
        ]
        == "Non-Compliant"
    ):

        st.warning(
            "This policy is currently "
            "non-compliant."
        )


        # ----------------------------------------------
        # Recommended Script
        # ----------------------------------------------

        recommended_script = None

        category = (
            selected_policy[
                "policy_category"
            ]
        )


        for script in scripts:

            if (
                script[
                    "script_category"
                ]
                == category
            ):

                recommended_script = script

                break


        if recommended_script is None:

            for script in scripts:

                if category == "Defender":

                    if (
                        "Defender"
                        in script["script_name"]
                    ):

                        recommended_script = script
                        break

                elif category == "CrowdStrike":

                    if (
                        "CrowdStrike"
                        in script["script_name"]
                    ):

                        recommended_script = script
                        break

                elif category == "Encryption":

                    if (
                        script[
                            "script_category"
                        ]
                        == "Encryption"
                    ):

                        recommended_script = script
                        break

                elif category == "Firewall":

                    if (
                        script[
                            "script_category"
                        ]
                        == "Firewall"
                    ):

                        recommended_script = script
                        break


        if recommended_script:

            st.info(
                "Recommended remediation: "
                f"**{recommended_script['script_name']}**"
            )


            st.write(
                f"**Purpose:** "
                f"{recommended_script['purpose']}"
            )


            st.write(
                f"**Tool:** "
                f"{recommended_script['tool_name']}"
            )


            st.write(
                f"**Risk:** "
                f"{recommended_script['risk_level']}"
            )


            remediation_reason = st.text_area(
                "Remediation Reason",
                value=(
                    f"Remediation for non-compliant "
                    f"policy "
                    f"'{selected_policy['policy_name']}' "
                    f"on endpoint "
                    f"{selected_policy['hostname']}."
                ),
                key=(
                    f"policy_remediation_reason_"
                    f"{selected_policy['policy_id']}"
                )
            )


            if can(
                "create_remediation_request"
            ):

                if st.button(
                    "🚀 Create Remediation Request",
                    type="primary",
                    key=(
                        f"policy_remediate_"
                        f"{selected_policy['policy_id']}"
                    )
                ):

                    deployment_id = (
                        request_deployment(
                            script_id=(
                                recommended_script[
                                    "script_id"
                                ]
                            ),
                            device_id=(
                                selected_policy[
                                    "device_id"
                                ]
                            ),
                            requested_by=(
                                st.session_state[
                                    "display_name"
                                ]
                            ),
                            remarks=(
                                remediation_reason
                            )
                        )
                    )


                    create_remediation_timeline_event(
                        device_id=(
                            selected_policy[
                                "device_id"
                            ]
                        ),
                        event_type=(
                            "Policy Remediation Requested"
                        ),
                        description=(
                            f"Remediation requested "
                            f"for policy "
                            f"'{selected_policy['policy_name']}' "
                            f"using "
                            f"'{recommended_script['script_name']}'."
                        ),
                        severity=(
                            selected_policy[
                                "risk_level"
                            ]
                        ),
                        performed_by=(
                            st.session_state[
                                "display_name"
                            ]
                        )
                    )


                    create_remediation_action(
                        device_id=(
                            selected_policy[
                                "device_id"
                            ]
                        ),
                        action_name=(
                            f"Policy Remediation - "
                            f"{selected_policy['policy_name']}"
                        ),
                        tool_name=(
                            recommended_script[
                                "tool_name"
                            ]
                        ),
                        result=(
                            "Remediation request created"
                        ),
                        remarks=(
                            remediation_reason
                        ),
                        requested_by=(
                            st.session_state[
                                "display_name"
                            ]
                        )
                    )


                    st.success(
                        f"Remediation request "
                        f"#{deployment_id} created."
                    )


                    st.info(
                        "Open Remediation Center to "
                        "approve, execute and validate "
                        "the remediation."
                    )

                    st.rerun()

            else:

                st.info(
                    "🔒 You do not have permission "
                    "to create remediation requests."
                )


        else:

            st.warning(
                "No suitable remediation script "
                "was found for this policy."
            )


    else:

        st.success(
            "🟢 No remediation required. "
            "Policy is compliant."
        )