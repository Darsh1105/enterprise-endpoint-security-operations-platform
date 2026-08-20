import hashlib
import secrets
from datetime import datetime, timedelta

from database.connection import get_connection


# ==================================================
# Session Configuration
# ==================================================

SESSION_DURATION_HOURS = 12


# ==================================================
# RBAC Permission Matrix
# ==================================================

ROLE_PERMISSIONS = {

    "Security Analyst": {

        "view_policies",
        "create_incident_remediation",
        "create_remediation_request",
        "view_incidents",
        "investigate_incidents",
        "view_timeline"

    },

    "Security Engineer": {

        "view_policies",
        "create_incident_remediation",
        "create_remediation_request",
        "execute_remediation",
        "validate_remediation",
        "tune_policy",
        "deploy_policy",
        "validate_policy",
        "view_incidents",
        "investigate_incidents",
        "view_timeline"

    },

    "Security Lead": {

        "view_policies",
        "create_incident_remediation",
        "create_remediation_request",
        "execute_remediation",
        "validate_remediation",
        "approve_remediation",
        "tune_policy",
        "deploy_policy",
        "validate_policy",
        "view_incidents",
        "investigate_incidents",
        "view_timeline"

    },

    "Administrator": {

        "view_policies",
        "create_incident_remediation",
        "create_remediation_request",
        "execute_remediation",
        "validate_remediation",
        "approve_remediation",
        "tune_policy",
        "deploy_policy",
        "validate_policy",
        "view_incidents",
        "investigate_incidents",
        "view_timeline",
        "manage_users",
        "manage_roles",
        "system_configuration"

    }
}


# ==================================================
# Permission Check
# ==================================================

def has_permission(role, permission):

    permissions = ROLE_PERMISSIONS.get(
        role,
        set()
    )

    return permission in permissions


# ==================================================
# Password Verification
# ==================================================

def verify_password(
    password,
    password_hash,
    password_salt
):

    try:

        salt = bytes.fromhex(
            password_salt
        )

    except (
        ValueError,
        TypeError
    ):

        return False


    derived_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310000
    ).hex()


    return secrets.compare_digest(
        derived_hash,
        password_hash
    )


# ==================================================
# Authenticate User
# ==================================================

def authenticate_user(
    username,
    password
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                user_id,
                username,
                password_hash,
                password_salt,
                display_name,
                role,
                is_active

            FROM platform_users

            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

    finally:

        conn.close()


    if user is None:

        return None


    if not user["is_active"]:

        return None


    if not verify_password(
        password,
        user["password_hash"],
        user["password_salt"]
    ):

        return None


    return user


# ==================================================
# Create Persistent Session
# ==================================================

def create_session(user_id):

    # Generate secure random token

    token = secrets.token_urlsafe(
        48
    )


    # Never store the raw token

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


    expires_at = (
        datetime.utcnow()
        + timedelta(
            hours=SESSION_DURATION_HOURS
        )
    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    conn = get_connection()
    cursor = conn.cursor()


    try:

        # IMPORTANT:
        #
        # We intentionally DO NOT invalidate
        # previous sessions here.
        #
        # This prevents a refresh/login cycle
        # from accidentally invalidating the
        # browser session that is currently being
        # restored.

        cursor.execute(
            """
            INSERT INTO auth_sessions (
                user_id,
                token_hash,
                expires_at,
                is_active
            )

            VALUES (?, ?, ?, 1)
            """,
            (
                user_id,
                token_hash,
                expires_at
            )
        )


        conn.commit()


    except Exception:

        conn.rollback()

        raise


    finally:

        conn.close()


    return token


# ==================================================
# Get Session User
# ==================================================

def get_session_user(token):

    if not token:

        return None


    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            SELECT

                u.user_id,
                u.username,
                u.display_name,
                u.role,
                u.is_active,

                s.session_id,
                s.expires_at

            FROM auth_sessions s

            JOIN platform_users u
                ON u.user_id = s.user_id

            WHERE s.token_hash = ?
            AND s.is_active = 1
            """,
            (token_hash,)
        )


        session = cursor.fetchone()


        if session is None:

            return None


        if not session["is_active"]:

            return None


        # ------------------------------------------
        # Check expiration
        # ------------------------------------------

        try:

            expires_at = datetime.strptime(
                session["expires_at"],
                "%Y-%m-%d %H:%M:%S"
            )

        except (
            ValueError,
            TypeError
        ):

            return None


        if datetime.utcnow() >= expires_at:

            cursor.execute(
                """
                UPDATE auth_sessions

                SET is_active = 0

                WHERE session_id = ?
                """,
                (
                    session["session_id"],
                )
            )

            conn.commit()

            return None


        # ------------------------------------------
        # Update activity
        # ------------------------------------------

        cursor.execute(
            """
            UPDATE auth_sessions

            SET last_seen_at = CURRENT_TIMESTAMP

            WHERE session_id = ?
            """,
            (
                session["session_id"],
            )
        )

        conn.commit()


        return session


    finally:

        conn.close()


# ==================================================
# Revoke Session
# ==================================================

def revoke_session(token):

    if not token:

        return


    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            UPDATE auth_sessions

            SET is_active = 0

            WHERE token_hash = ?
            """,
            (
                token_hash,
            )
        )

        conn.commit()


    finally:

        conn.close()


# ==================================================
# Cleanup Expired Sessions
# ==================================================

def cleanup_expired_sessions():

    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            UPDATE auth_sessions

            SET is_active = 0

            WHERE expires_at <= CURRENT_TIMESTAMP
            """
        )

        conn.commit()


    finally:

        conn.close()