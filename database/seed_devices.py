import random

from database.connection import get_connection


TOTAL_DEVICES = 25


MANUFACTURERS = {
    "Dell": [
        "Latitude 7440",
        "Latitude 5450",
        "Precision 3591"
    ],
    "HP": [
        "EliteBook 840",
        "EliteBook 650",
        "ZBook Firefly"
    ],
    "Lenovo": [
        "ThinkPad T14",
        "ThinkPad X1 Carbon",
        "ThinkCentre M90"
    ],
    "Microsoft": [
        "Surface Laptop 6"
    ]
}


DEVICE_TYPES = [
    "Laptop",
    "Desktop"
]


OS_VERSIONS = [
    "23H2",
    "24H2"
]


PROFILES = [
    "Healthy",
    "Healthy",
    "Healthy",
    "Healthy",
    "Healthy",
    "Healthy",
    "Warning",
    "Warning",
    "Critical",
    "Healthy"
]


def get_risk(profile):

    if profile == "Healthy":
        return random.randint(5, 25)

    if profile == "Warning":
        return random.randint(26, 70)

    return random.randint(71, 100)


def seed_devices():

    conn = get_connection()

    cursor = conn.cursor()

    for i in range(1, TOTAL_DEVICES + 1):

        manufacturer = random.choice(list(MANUFACTURERS.keys()))

        model = random.choice(MANUFACTURERS[manufacturer])

        profile = random.choice(PROFILES)

        cursor.execute("""
        INSERT INTO devices(

            hostname,
            serial_number,
            asset_tag,
            device_type,
            manufacturer,
            model,
            operating_system,
            os_version,
            assigned_user_id,
            office_id,
            device_status,
            purchase_date,
            warranty_expiry,
            last_seen,
            risk_score,
            is_active

        )

        VALUES(

            ?,?,?,?,?,?,
            'Windows 11',
            ?,
            NULL,
            NULL,
            'Online',
            '2025-01-15',
            '2028-01-15',
            datetime('now'),
            ?,
            1

        )

        """,

        (

            f"DGS-LAP-{i:03}",

            f"SN{100000+i}",

            f"AST{5000+i}",

            random.choice(DEVICE_TYPES),

            manufacturer,

            model,

            random.choice(OS_VERSIONS),

            get_risk(profile)

        ))

    conn.commit()

    conn.close()

    print(f"{TOTAL_DEVICES} devices inserted successfully.")


if __name__ == "__main__":
    seed_devices()