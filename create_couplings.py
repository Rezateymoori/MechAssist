import sqlite3

conn = sqlite3.connect("mechassist.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS couplings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    brand TEXT,

    coupling_type TEXT,

    series TEXT,

    bore TEXT,

    max_rpm REAL,

    nominal_torque REAL,

    max_torque REAL,

    material TEXT,

    application TEXT,

    lubrication TEXT,

    description TEXT

)
""")

conn.commit()
conn.close()

print("✅ جدول couplings ساخته شد")
