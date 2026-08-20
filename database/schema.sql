-- REGIONS

CREATE TABLE IF NOT EXISTS regions (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE
);

-- COUNTRIES

CREATE TABLE IF NOT EXISTS countries (
    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_name TEXT NOT NULL,
    country_code TEXT NOT NULL UNIQUE,
    region_id INTEGER,
    FOREIGN KEY(region_id) REFERENCES regions(region_id)
);

-- OFFICES

CREATE TABLE IF NOT EXISTS offices (
    office_id INTEGER PRIMARY KEY AUTOINCREMENT,
    office_name TEXT NOT NULL,
    city TEXT,
    country_id INTEGER,
    FOREIGN KEY(country_id) REFERENCES countries(country_id)
);

-- DEPARTMENTS

CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL UNIQUE
);

-- USERS

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    department_id INTEGER,
    office_id INTEGER,
    job_title TEXT,
    manager_id INTEGER,
    account_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(department_id) REFERENCES departments(department_id),
    FOREIGN KEY(office_id) REFERENCES offices(office_id),
    FOREIGN KEY(manager_id) REFERENCES users(user_id)
);

-- ANALYSTS


CREATE TABLE IF NOT EXISTS analysts (
    analyst_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    analyst_level TEXT,
    specialization TEXT,
    team TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- DEVICES


CREATE TABLE IF NOT EXISTS devices (

    device_id INTEGER PRIMARY KEY AUTOINCREMENT,

    hostname TEXT NOT NULL UNIQUE,

    serial_number TEXT UNIQUE,

    asset_tag TEXT,

    device_type TEXT,

    manufacturer TEXT,

    model TEXT,

    operating_system TEXT,

    os_version TEXT,

    assigned_user_id INTEGER,

    office_id INTEGER,

    device_status TEXT,

    purchase_date DATE,

    warranty_expiry DATE,

    last_seen TIMESTAMP,

    risk_score INTEGER DEFAULT 0,

    is_active INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(assigned_user_id) REFERENCES users(user_id),

    FOREIGN KEY(office_id) REFERENCES offices(office_id)

);



-- ENDPOINT SECURITY STATUS

CREATE TABLE IF NOT EXISTS endpoint_security_status (

    security_status_id INTEGER PRIMARY KEY AUTOINCREMENT,

    device_id INTEGER NOT NULL,

    defender_status TEXT,

    defender_engine_version TEXT,

    defender_platform_version TEXT,

    defender_signature_version TEXT,

    defender_last_scan TIMESTAMP,

    realtime_protection TEXT,

    tamper_protection TEXT,

    crowdstrike_status TEXT,

    crowdstrike_sensor_version TEXT,

    crowdstrike_policy TEXT,

    crowdstrike_last_checkin TIMESTAMP,

    bitlocker_status TEXT,

    encryption_method TEXT,

    recovery_key_available TEXT,

    firewall_status TEXT,

    firewall_profile TEXT,

    tpm_status TEXT,

    tpm_version TEXT,

    secure_boot TEXT,

    compliance_status TEXT,

    last_sync TIMESTAMP,

    FOREIGN KEY(device_id)
        REFERENCES devices(device_id)
);


-- ENDPOINT TIMELINE


CREATE TABLE IF NOT EXISTS endpoint_timeline (

    timeline_id INTEGER PRIMARY KEY AUTOINCREMENT,

    device_id INTEGER NOT NULL,

    event_time TIMESTAMP NOT NULL,

    event_type TEXT NOT NULL,

    event_category TEXT,

    event_source TEXT,

    severity TEXT,

    description TEXT,

    performed_by TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(device_id)
        REFERENCES devices(device_id)

);


-- ENDPOINT INCIDENTS


CREATE TABLE IF NOT EXISTS endpoint_incidents (

    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,

    device_id INTEGER NOT NULL,

    incident_number TEXT UNIQUE,

    title TEXT,

    severity TEXT,

    status TEXT,

    detection_source TEXT,

    assigned_to TEXT,

    sla_status TEXT,

    created_time TIMESTAMP,

    updated_time TIMESTAMP,

    description TEXT,

    FOREIGN KEY(device_id)
        REFERENCES devices(device_id)

);

-- ENDPOINT THREATS

CREATE TABLE IF NOT EXISTS endpoint_threats (

    threat_id INTEGER PRIMARY KEY AUTOINCREMENT,

    device_id INTEGER NOT NULL,

    threat_name TEXT NOT NULL,

    severity TEXT,

    status TEXT,

    detection_source TEXT,

    mitre_technique TEXT,

    ioc TEXT,

    detected_time TIMESTAMP,

    description TEXT,

    recommended_action TEXT,

    FOREIGN KEY(device_id)
        REFERENCES devices(device_id)

);


-- ENDPOINT ENGINEERING


CREATE TABLE IF NOT EXISTS endpoint_engineering (

    engineering_id INTEGER PRIMARY KEY AUTOINCREMENT,

    device_id INTEGER NOT NULL,

    activity_name TEXT NOT NULL,

    activity_type TEXT,

    status TEXT,

    tool_name TEXT,

    engineer TEXT,

    started_time TIMESTAMP,

    completed_time TIMESTAMP,

    result TEXT,

    notes TEXT,

    FOREIGN KEY(device_id)
        REFERENCES devices(device_id)

);


-- ENDPOINT ACTIONS


CREATE TABLE IF NOT EXISTS endpoint_actions (

    action_id INTEGER PRIMARY KEY AUTOINCREMENT,

    device_id INTEGER NOT NULL,

    action_name TEXT NOT NULL,

    action_category TEXT,

    requested_by TEXT,

    requested_time TIMESTAMP,

    tool_name TEXT,

    status TEXT,

    completed_time TIMESTAMP,

    result TEXT,

    remarks TEXT,

    FOREIGN KEY(device_id)
        REFERENCES devices(device_id)

);