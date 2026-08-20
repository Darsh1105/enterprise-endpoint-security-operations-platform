import hashlib
import os

from services.auth_service import (
    ROLE_PERMISSIONS,
    has_permission,
    verify_password,
)


# ============================================================
# RBAC TESTS
# ============================================================

def test_security_analyst_permissions():

    role = "Security Analyst"

    assert has_permission(role, "view_policies")
    assert has_permission(role, "view_incidents")
    assert has_permission(role, "investigate_incidents")
    assert has_permission(role, "create_remediation_request")

    assert not has_permission(role, "tune_policy")
    assert not has_permission(role, "deploy_policy")
    assert not has_permission(role, "validate_policy")
    assert not has_permission(role, "approve_remediation")
    assert not has_permission(role, "execute_remediation")
    assert not has_permission(role, "validate_remediation")


def test_security_engineer_permissions():

    role = "Security Engineer"

    assert has_permission(role, "view_policies")
    assert has_permission(role, "tune_policy")
    assert has_permission(role, "deploy_policy")
    assert has_permission(role, "validate_policy")
    assert has_permission(role, "execute_remediation")
    assert has_permission(role, "validate_remediation")

    # Engineer should not have Lead approval permission.
    assert not has_permission(
        role,
        "approve_remediation"
    )


def test_security_lead_permissions():

    role = "Security Lead"

    assert has_permission(role, "tune_policy")
    assert has_permission(role, "deploy_policy")
    assert has_permission(role, "validate_policy")
    assert has_permission(role, "execute_remediation")
    assert has_permission(role, "validate_remediation")
    assert has_permission(role, "approve_remediation")


def test_administrator_permissions():

    role = "Administrator"

    assert has_permission(role, "view_policies")
    assert has_permission(role, "investigate_incidents")
    assert has_permission(role, "tune_policy")
    assert has_permission(role, "deploy_policy")
    assert has_permission(role, "validate_policy")
    assert has_permission(role, "execute_remediation")
    assert has_permission(role, "validate_remediation")
    assert has_permission(role, "approve_remediation")
    assert has_permission(role, "manage_users")
    assert has_permission(role, "manage_roles")
    assert has_permission(role, "system_configuration")


def test_unknown_role_has_no_permissions():

    assert not has_permission(
        "Unknown Role",
        "view_policies"
    )

    assert not has_permission(
        "Unknown Role",
        "manage_users"
    )


def test_unknown_permission_is_denied():

    for role in ROLE_PERMISSIONS:

        assert not has_permission(
            role,
            "this_permission_does_not_exist"
        )


# ============================================================
# PASSWORD TESTS
# ============================================================

def test_password_verification():

    password = "TestPassword123!"

    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310000
    ).hex()

    salt_hex = salt.hex()

    assert verify_password(
        password,
        password_hash,
        salt_hex
    )


def test_wrong_password_is_rejected():

    password = "CorrectPassword123!"
    wrong_password = "WrongPassword123!"

    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310000
    ).hex()

    salt_hex = salt.hex()

    assert not verify_password(
        wrong_password,
        password_hash,
        salt_hex
    )


def test_invalid_password_salt_is_rejected():

    assert not verify_password(
        "TestPassword123!",
        "invalid_hash",
        "invalid_salt"
    )