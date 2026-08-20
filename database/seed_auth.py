import hashlib
import secrets

from database.connection import get_connection


# ==================================================
# Demo Account Passwords
# ==================================================
#
# These are used ONLY during initial account creation.
# They are never stored in the database.
#
# Change these after your first successful login
# when we build the user-management screen.
# ==================================================

USERS = [

    {
        "username": "analyst",
        "password": "Analyst@123",
        "display_name": "Security Analyst",
        "role": "Security Analyst"
    },

    {
        "username": "engineer",
        "password": "Engineer@123",
        "display_name": "Security Engineer",
        "role": "Security Engineer"
    },

    {
        "username": "lead",
        "password": "Lead@123",
        "display_name": "Security Lead",
        "role": "Security Lead"
    },

    {
        "username": "admin",
        "password": "Admin@123",
        "display_name": "EESOP Administrator",
        "role": "Administrator"
    }
]


# ==================================================
# RBAC Permissions
# ==================================================

ROLE_PERMISSIONS = {

    "Security Analyst": [

        "view_endpoints",
        "view_threats",
        "view_incidents",
        "create_incident_remediation",
        "create_remediation_request",
        "view_policies",
        "view_timeline"

    ],

    "Security Engineer": [

        "view_endpoints",
        "view_threats",
        "view_incidents",
        "create_incident_remediation",
        "create_remediation_request",
        "tune_policy",
        "deploy_policy",
        "validate_policy",
        "execute_remediation",
        "validate_remediation",
        "view_policies",
        "view_timeline"

    ],

    "Security Lead": [

        "view_endpoints",
        "view_threats",
        "view_incidents",
        "create_incident_remediation",
        "create_remediation_request",
        "tune_policy",
        "deploy_policy",
        "validate_policy",
        "approve_remediation",
        "execute_remediation",
        "validate_remediation",
        "view_policies",
        "view_timeline",
        "manage_incidents"

    ],

    "Administrator": [

        "view_endpoints",
        "view_threats",
        "view_incidents",
        "create_incident_remediation",
        "create_remediation_request",
        "tune_policy",
        "deploy_policy",
        "validate_policy",
        "approve_remediation",
        "execute_remediation",
        "validate_remediation",
        "view_policies",
        "view_timeline",
        "manage_incidents",
        "manage_users",
        "manage_platform"

    ]
}


# ==================================================
# Password Hashing
# ==================================================

def hash_password(password, salt=None):

    if salt is None:

        salt = secrets.token_bytes(32)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310000
    )

    return (
        password_hash.hex(),
        salt.hex()
    )


# ==================================================
# Seed Authentication
# ==================================================

def seed_auth():

    conn = get_connection()
    cursor = conn.cursor()

    created_users = 0
    existing_users = 0

    # ==================================================
    # Create Users
    # ==================================================

    for user in USERS:

        cursor.execute(
            """
            SELECT user_id
            FROM platform_users
            WHERE username = ?
            """,
            (user["username"],)
        )

        existing = cursor.fetchone()

        if existing:

            existing_users += 1

            continue

        password_hash, password_salt = (
            hash_password(
                user["password"]
            )
        )

        cursor.execute(
            """
            INSERT INTO platform_users (

                username,
                password_hash,
                password_salt,
                display_name,
                role,
                is_active

            )

            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                user["username"],
                password_hash,
                password_salt,
                user["display_name"],
                user["role"]
            )
        )

        created_users += 1


    # ==================================================
    # Create Permissions
    # ==================================================

    created_permissions = 0

    for role, permissions in (
        ROLE_PERMISSIONS.items()
    ):

        for permission in permissions:

            cursor.execute(
                """
                INSERT OR IGNORE INTO role_permissions (

                    role,
                    permission

                )

                VALUES (?, ?)
                """,
                (
                    role,
                    permission
                )
            )

            if cursor.rowcount > 0:

                created_permissions += 1


    conn.commit()
    conn.close()

    print(
        f"{created_users} users created."
    )

    print(
        f"{existing_users} users already existed."
    )

    print(
        f"{created_permissions} permissions created."
    )


if __name__ == "__main__":
    seed_auth()