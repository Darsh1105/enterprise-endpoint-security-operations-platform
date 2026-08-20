from pathlib import Path

# ==========================
# Project Information
# ==========================

APP_NAME = "EESOP"
APP_VERSION = "1.0.0"

COMPANY_NAME = "Darshayu Global Solutions"

# ==========================
# Base Directory
# ==========================

BASE_DIR = Path(__file__).resolve().parent

# ==========================
# Database
# ==========================

DATABASE_PATH = BASE_DIR / "database" / "eesop.db"

# ==========================
# Data Directories
# ==========================

DATA_DIR = BASE_DIR / "data"

TELEMETRY_DIR = DATA_DIR / "telemetry"

REPORT_DIR = DATA_DIR / "reports"