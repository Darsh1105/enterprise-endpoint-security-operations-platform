import random

from database.connection import get_connection


conn = get_connection()
cursor = conn.cursor()


manufacturers = [
    "Dell",
    "HP",
    "Lenovo"
]

models = [
    "Latitude 7440",
    "EliteBook 840",
    "ThinkPad T14"
]

users = [
    "John Smith",
    "Alice Johnson",
    "David Brown",
    "Sarah Wilson",
    "Michael Lee",
    "Emily Davis",
    "Daniel White",
    "Sophia Taylor",
    "James Anderson",
    "Olivia Martin"
]