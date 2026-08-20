import streamlit as st

from endpoint_operations.policy_service import (
    load_policies,
    tune_policy,
    apply_policy,
    validate_policy_change,
    create_policy_timeline_event,
    create_policy_action
)


# ==================================================
# Policy Helpers
# ==================================================

def get_category_icon(category):

    icons = {
        "CrowdStrike": "🦅",
        "Defender": "🛡️",
        "Encryption": "🔐",
        "Firewall": "🧱",
        "Custom": "⚙️"
    }

    return icons.get(
        category,
        "📋"
    )


def get_status_icon(status):

    if status == "Validated":
        return "✅"

    if status == "Assigned":
        return "🟢"

    if status == "Needs Review":
        return "🟠"

    if status == "Failed":
        return "🔴"

    return "⚪"


def get_deployment_icon(status):

    if status == "Applied":
        return "🟢"

    if status == "Pending":
        return "🟡"

    if status == "Failed":
        return "🔴"

    return "⚪"


# ==================================================
# Policy Management Workspace
# ==================================================

def show(device):

    policies = load_policies(
        device["device_id"]
    )

    st.subheader(
        "🛡️ Security Policy Management"
    )

    st.caption(
        "Endpoint security policy review, tuning, "
        "controlled deployment and validation."
    )

    if not policies:

        st.info(
            "No security policies assigned "
            "to this endpoint."
        )

        return

    # ==================================================
    # Summary
    # ==================================================

    total = len(policies)

    needs_review = len(
        [
            p for p in policies
            if p["status"] == "Needs Review"
        ]
    )

    applied = len(
        [
            p for p in policies
            if p["deployment_status"] == "Applied"
        ]
    )

    pending = len(
        [
            p for p in policies
            if p["deployment_status"] == "Pending"
        ]
    )

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.metric(
            "Total Policies",
            total
        )

    with s2:
        st.metric(
            "Needs Review",
            needs_review
        )

    with s3:
        st.metric(
            "Applied",
            applied
        )

    with s4:
        st.metric(
            "Pending",
            pending
        )

    st.divider()

    # ==================================================
    # Filters
    # ==================================================

    categories = sorted(
        set(
            policy["policy_category"]
            for policy in policies
        )
    )

    filter1, filter2 = st.columns(2)

    with filter1:

        selected_category = st.selectbox(
            "Policy Category",
            ["All"] + categories
        )

    with filter2:

        deployment_options = [
            "All",
            "Applied",
            "Pending",
            "Not Deployed"
        ]

        selected_deployment = st.selectbox(
            "Deployment Status",
            deployment_options
        )

    filtered_policies = policies

    if selected_category != "All":

        filtered_policies = [
            policy
            for policy in filtered_policies
            if policy["policy_category"]
            == selected_category
        ]

    if selected_deployment != "All":

        filtered_policies = [
            policy
            for policy in filtered_policies
            if policy["deployment_status"]
            == selected_deployment
        ]

    st.write(
        f"Showing **{len(filtered_policies)}** policies"
    )

    st.divider()

    # ==================================================
    # Policy Cards
    # ==================================================

    for policy in filtered_policies:

        category_icon = get_category_icon(
            policy["policy_category"]
        )

        status_icon = get_status_icon(
            policy["status"]
        )

        deployment_icon = get_deployment_icon(
            policy["deployment_status"]
        )

        with st.expander(
            f"{category_icon} "
            f"{policy['policy_name']} "
            f"| {status_icon} "
            f"{policy['status']} "
            f"| {deployment_icon} "
            f"{policy['deployment_status']}"
        ):

            # ==================================================
            # Header
            # ==================================================

            st.markdown(
                f"### {category_icon} "
                f"{policy['policy_name']}"
            )

            st.caption(
                f"{policy['policy_category']} "
                f"• "
                f"{policy['policy_type']} "
                f"• "
                f"{policy['tool_name']}"
            )

            # ==================================================
            # Policy Information
            # ==================================================

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.write("**Tool**")

                st.write(
                    policy["tool_name"]
                )

            with c2:

                st.write("**Risk**")

                st.write(
                    policy["risk_level"]
                )

            with c3:

                st.write("**Policy Status**")

                st.write(
                    f"{status_icon} "
                    f"{policy['status']}"
                )

            with c4:

                st.write("**Deployment**")

                st.write(
                    f"{deployment_icon} "
                    f"{policy['deployment_status']}"
                )

            # ==================================================
            # Configuration
            # ==================================================

            st.divider()

            st.markdown(
                "### ⚙️ Configuration"
            )

            config1, config2 = st.columns(2)

            with config1:

                st.write(
                    "**Setting**"
                )

                st.code(
                    str(
                        policy["setting_name"]
                    )
                )

                st.write(
                    "**Current Value**"
                )

                st.code(
                    str(
                        policy["current_value"]
                    )
                )

            with config2:

                st.write(
                    "**Desired Value**"
                )

                st.code(
                    str(
                        policy["desired_value"]
                    )
                )

                st.write(
                    "**Last Updated**"
                )

                st.write(
                    policy["last_updated"]
                )

            # ==================================================
            # Change Information
            # ==================================================

            st.divider()

            st.markdown(
                "### 📝 Change Information"
            )

            st.write(
                f"**Updated By:** "
                f"{policy['updated_by']}"
            )

            st.write(
                f"**Change Reason:** "
                f"{policy['change_reason']}"
            )

            # ==================================================
            # Tune Policy
            # ==================================================

            st.divider()

            st.markdown(
                "### 🛠️ Policy Tuning"
            )

            new_value = st.text_input(
                "Desired Configuration",
                value=str(
                    policy["desired_value"]
                ),
                key=f"value_{policy['policy_id']}"
            )

            reason = st.text_area(
                "Change Reason",
                placeholder=(
                    "Explain why this policy "
                    "configuration should change..."
                ),
                key=f"reason_{policy['policy_id']}"
            )

            tune_button = st.button(
                "🛠️ Submit Policy Change",
                key=f"tune_{policy['policy_id']}"
            )

            if tune_button:

                if not new_value.strip():

                    st.error(
                        "Desired configuration "
                        "cannot be empty."
                    )

                elif not reason.strip():

                    st.error(
                        "Please provide a change reason."
                    )

                else:

                    tune_policy(
                        policy_id=policy["policy_id"],
                        desired_value=new_value,
                        change_reason=reason,
                        updated_by="Security Engineer"
                    )

                    create_policy_timeline_event(
                        device_id=device["device_id"],
                        event_type="Policy Tuned",
                        description=(
                            f"{policy['policy_name']} "
                            f"tuned from "
                            f"'{policy['current_value']}' "
                            f"to '{new_value}'. "
                            f"Reason: {reason}"
                        ),
                        severity=policy["risk_level"],
                        performed_by="Security Engineer"
                    )

                    create_policy_action(
                        device_id=device["device_id"],
                        action_name=(
                            f"Tune Policy - "
                            f"{policy['policy_name']}"
                        ),
                        action_category="Policy Management",
                        tool_name=policy["tool_name"],
                        result="Policy change submitted",
                        remarks=reason
                    )

                    st.success(
                        "Policy change submitted "
                        "for deployment."
                    )

                    st.rerun()

            # ==================================================
            # Deployment
            # ==================================================

            st.markdown(
                "### 🚀 Policy Deployment"
            )

            if policy["status"] == "Needs Review":

                if st.button(
                    "🚀 Deploy Policy",
                    key=f"deploy_{policy['policy_id']}"
                ):

                    success, message = apply_policy(
                        policy_id=policy["policy_id"],
                        updated_by="Security Engineer"
                    )

                    if success:

                        create_policy_timeline_event(
                            device_id=device["device_id"],
                            event_type="Policy Deployed",
                            description=(
                                f"{policy['policy_name']} "
                                f"deployment simulated successfully. "
                                f"Configuration applied: "
                                f"'{policy['desired_value']}'"
                            ),
                            severity="Informational",
                            performed_by="Security Engineer"
                        )

                        create_policy_action(
                            device_id=device["device_id"],
                            action_name=(
                                f"Deploy Policy - "
                                f"{policy['policy_name']}"
                            ),
                            action_category="Policy Deployment",
                            tool_name=policy["tool_name"],
                            result="Deployment simulated successfully",
                            remarks=(
                                f"Configuration applied: "
                                f"{policy['desired_value']}"
                            )
                        )

                        st.success(
                            "Policy deployment completed."
                        )

                        st.rerun()

                    else:

                        st.error(message)

            else:

                st.info(
                    "Policy must be tuned before "
                    "deployment is available."
                )

            # ==================================================
            # Validation
            # ==================================================

            st.markdown(
                "### ✅ Policy Validation"
            )

            if (
                policy["deployment_status"]
                == "Applied"
                and policy["status"]
                != "Validated"
            ):

                if st.button(
                    "✅ Validate Policy",
                    key=f"validate_{policy['policy_id']}"
                ):

                    success, message = (
                        validate_policy_change(
                            policy_id=policy["policy_id"],
                            updated_by="Security Engineer"
                        )
                    )

                    if success:

                        create_policy_timeline_event(
                            device_id=device["device_id"],
                            event_type="Policy Validated",
                            description=(
                                f"{policy['policy_name']} "
                                f"validated successfully on "
                                f"{device['hostname']}."
                            ),
                            severity="Informational",
                            performed_by="Security Engineer"
                        )

                        create_policy_action(
                            device_id=device["device_id"],
                            action_name=(
                                f"Validate Policy - "
                                f"{policy['policy_name']}"
                            ),
                            action_category="Policy Validation",
                            tool_name=policy["tool_name"],
                            result="Validation successful",
                            remarks=(
                                "Policy configuration "
                                "verified after deployment."
                            )
                        )

                        st.success(
                            "Policy validation completed."
                        )

                        st.rerun()

                    else:

                        st.error(message)

            elif policy["status"] == "Validated":

                st.success(
                    "✅ Policy has been validated."
                )

            else:

                st.info(
                    "Deploy the policy before validation."
                )