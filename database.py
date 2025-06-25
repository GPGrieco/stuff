import sqlite3

DB_FILE = "safety_app.db"

CREATE_TABLES_SQL = [
    # Hazards
    """
    CREATE TABLE IF NOT EXISTS Hazards (
        id INTEGER PRIMARY KEY,
        latitude REAL,
        longitude REAL,
        description TEXT,
        severity TEXT,
        status TEXT,
        date_reported TEXT
    )
    """,
    # Mitigation Notes
    """
    CREATE TABLE IF NOT EXISTS MitigationNotes (
        note_id INTEGER PRIMARY KEY,
        hazard_id INTEGER,
        note_text TEXT,
        photo_path TEXT,
        author TEXT,
        date TEXT
    )
    """,
    # Patrol Shifts
    """
    CREATE TABLE IF NOT EXISTS Shifts (
        shift_id INTEGER PRIMARY KEY,
        date TEXT,
        time_slot TEXT,
        crew TEXT
    )
    """,
    # Incidents
    """
    CREATE TABLE IF NOT EXISTS Incidents (
        incident_id INTEGER PRIMARY KEY,
        shift_id INTEGER,
        category TEXT,
        description TEXT,
        photo_path TEXT,
        latitude REAL,
        longitude REAL,
        timestamp TEXT
    )
    """,
    # Inventory Items
    """
    CREATE TABLE IF NOT EXISTS Items (
        item_id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        location TEXT,
        quantity INTEGER,
        unit TEXT,
        threshold INTEGER,
        supplier TEXT,
        supplier_contact TEXT,
        supplier_sku TEXT,
        unit_cost REAL
    )
    """,
    # Transactions (Check-in/Check-out)
    """
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INTEGER PRIMARY KEY,
        item_id INTEGER,
        person TEXT,
        out_date TEXT,
        expected_return_date TEXT,
        actual_return_date TEXT,
        out_notes TEXT,
        return_notes TEXT,
        out_photo TEXT,
        return_photo TEXT,
        status TEXT
    )
    """
]


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for sql in CREATE_TABLES_SQL:
        cursor.execute(sql)
    conn.commit()
    conn.close()
