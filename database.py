import sqlite3
import hashlib
import datetime

DB_PATH = "data/organ_donation.db"

# -------------------- UTILITIES --------------------
def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------- INIT --------------------
def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT,
        city TEXT,
        state TEXT,
        country TEXT,
        blood_group TEXT,
        verified INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        license TEXT,
        address TEXT,
        lat REAL,
        lon REAL,
        capacity INTEGER,
        verified INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS sos_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        patient_age INTEGER,
        blood_group TEXT,
        organ TEXT,
        urgency INTEGER,
        location TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor TEXT,
        action TEXT,
        timestamp TEXT
    )
    """)

    # Seed admin
    c.execute("SELECT * FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute("""
        INSERT INTO users (role, name, email, password, verified)
        VALUES ('admin','Admin','admin@jeevsetu.org',?,1)
        """, (hash_password("admin123"),))

    db.commit()
    db.close()
