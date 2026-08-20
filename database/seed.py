import sqlite3
from pathlib import Path

# Database Connection

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "eesop.db"
print(DATABASE_PATH)
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Regions

regions = [
    ("APAC",),
    ("Europe",),
    ("North America",),
    ("Australia & New Zealand",)
]

cursor.executemany(
    "INSERT OR IGNORE INTO regions(region_name) VALUES (?)",
    regions
)

# Countries

countries = [
    ("India", "IN", 1),
    ("Singapore", "SG", 1),
    ("Germany", "DE", 2),
    ("United Kingdom", "UK", 2),
    ("United States", "US", 3),
    ("Canada", "CA", 3),
    ("Australia", "AU", 4),
    ("New Zealand", "NZ", 4)
]

cursor.executemany("""
INSERT OR IGNORE INTO countries
(country_name, country_code, region_id)
VALUES (?, ?, ?)
""", countries)

# Departments

departments = [
    ("Security",),
    ("IT",),
    ("Finance",),
    ("HR",),
    ("Legal",),
    ("Operations",),
    ("Infrastructure",),
    ("Cloud",)
]

cursor.executemany(
    "INSERT OR IGNORE INTO departments(department_name) VALUES (?)",
    departments
)

conn.commit()
# Verify inserted data
cursor.execute("SELECT COUNT(*) FROM regions")
print("Regions:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM countries")
print("Countries:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM departments")
print("Departments:", cursor.fetchone()[0])

conn.close()

print("Master data inserted successfully.")