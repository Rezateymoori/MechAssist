import sqlite3

DATABASE = "mechassist.db"

conn = sqlite3.connect(DATABASE)

# =========================================================
# جدول اصلی جداول استاندارد
# =========================================================

conn.execute("""
CREATE TABLE IF NOT EXISTS standards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    code TEXT,
    name TEXT NOT NULL,
    standard TEXT,
    size TEXT,
    dimension_1 REAL,
    dimension_2 REAL,
    dimension_3 REAL,
    dimension_4 REAL,
    unit TEXT,
    material TEXT,
    property_class TEXT,
    value REAL,
    value_2 REAL,
    description TEXT
)
""")

# =========================================================
# حذف داده‌های قبلی برای جلوگیری از تکراری شدن
# =========================================================

conn.execute("DELETE FROM standards")


# =========================================================
# 1 - BEARINGS
# داده‌های سری 6200
# =========================================================

bearings_6200 = [
    ("6200", 10, 30, 9),
    ("6201", 12, 32, 10),
    ("6202", 15, 35, 11),
    ("6203", 17, 40, 12),
    ("6204", 20, 47, 14),
    ("6205", 25, 52, 15),
    ("6206", 30, 62, 16),
    ("6207", 35, 72, 17),
    ("6208", 40, 80, 18),
    ("6209", 45, 85, 19),
    ("6210", 50, 90, 20),
    ("6211", 55, 100, 21),
    ("6212", 60, 110, 22),
    ("6213", 65, 120, 23),
    ("6214", 70, 125, 24),
    ("6215", 75, 130, 25),
    ("6216", 80, 140, 26),
    ("6217", 85, 150, 28),
    ("6218", 90, 160, 30),
    ("6219", 95, 170, 32),
    ("6220", 100, 180, 34),
    ("6221", 105, 190, 36),
    ("6222", 110, 200, 38),
    ("6224", 120, 215, 40),
    ("6226", 130, 230, 40),
    ("6228", 140, 250, 42),
    ("6230", 150, 270, 45),
    ("6232", 160, 290, 48),
    ("6234", 170, 310, 52),
    ("6236", 180, 320, 52),
    ("6238", 190, 340, 55),
    ("6240", 200, 360, 58),
]

for code, d, D, B in bearings_6200:

    conn.execute("""
        INSERT INTO standards
        (
            category,
            code,
            name,
            standard,
            size,
            dimension_1,
            dimension_2,
            dimension_3,
            unit,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "bearings",
        code,
        f"برینگ {code}",
        "SKF / ISO",
        code,
        d,
        D,
        B,
        "mm",
        "بلبرینگ شیار عمیق سری 62"
    ))


# =========================================================
# 2 - METRIC THREADS
# =========================================================

threads = [
    ("M3", 3, 0.50),
    ("M4", 4, 0.70),
    ("M5", 5, 0.80),
    ("M6", 6, 1.00),
    ("M8", 8, 1.25),
    ("M10", 10, 1.50),
    ("M12", 12, 1.75),
    ("M14", 14, 2.00),
    ("M16", 16, 2.00),
    ("M18", 18, 2.50),
    ("M20", 20, 2.50),
    ("M22", 22, 2.50),
    ("M24", 24, 3.00),
    ("M27", 27, 3.00),
    ("M30", 30, 3.50),
    ("M33", 33, 3.50),
    ("M36", 36, 4.00),
    ("M39", 39, 4.00),
    ("M42", 42, 4.50),
    ("M45", 45, 4.50),
    ("M48", 48, 5.00),
    ("M52", 52, 5.00),
    ("M56", 56, 5.50),
    ("M60", 60, 5.50),
    ("M64", 64, 6.00),
    ("M68", 68, 6.00),
]

for code, diameter, pitch in threads:

    conn.execute("""
        INSERT INTO standards
        (
            category,
            code,
            name,
            standard,
            size,
            dimension_1,
            dimension_2,
            unit,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "threads",
        code,
        f"رزوه متریک {code}",
        "ISO 262:2023",
        code,
        diameter,
        pitch,
        "mm",
        "رزوه متریک عمومی"
    ))


# =========================================================
# 3 - BOLTS / NUTS
# =========================================================

bolt_sizes = [
    ("M3", 5.5),
    ("M4", 7),
    ("M5", 8),
    ("M6", 10),
    ("M8", 13),
    ("M10", 16),
    ("M12", 18),
    ("M14", 21),
    ("M16", 24),
    ("M18", 27),
    ("M20", 30),
    ("M22", 34),
    ("M24", 36),
    ("M27", 41),
    ("M30", 46),
    ("M33", 50),
    ("M36", 55),
    ("M39", 60),
]

for size, wrench in bolt_sizes:

    conn.execute("""
        INSERT INTO standards
        (
            category,
            code,
            name,
            standard,
            size,
            dimension_1,
            unit,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "bolts",
        size,
        f"پیچ و مهره {size}",
        "ISO metric",
        size,
        wrench,
        "mm",
        "اندازه اسمی و عرض آچار"
    ))


# =========================================================
# 4 - BEARING HOUSINGS
# =========================================================

housing_sizes = [
    ("UCP201", 12),
    ("UCP202", 15),
    ("UCP203", 17),
    ("UCP204", 20),
    ("UCP205", 25),
    ("UCP206", 30),
    ("UCP207", 35),
    ("UCP208", 40),
    ("UCP209", 45),
    ("UCP210", 50),
    ("UCP211", 55),
    ("UCP212", 60),
    ("UCP213", 65),
    ("UCP214", 70),
    ("UCP215", 75),
    ("UCP216", 80),
    ("UCP217", 85),
    ("UCP218", 90),
]

for code, bore in housing_sizes:

    conn.execute("""
        INSERT INTO standards
        (
            category,
            code,
            name,
            standard,
            size,
            dimension_1,
            unit,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "housings",
        code,
        f"یاتاقان پایه‌دار {code}",
        "UCP",
        code,
        bore,
        "mm",
        "یاتاقان واحد پایه‌دار"
    ))


# =========================================================
# 5 - TORQUE
# =========================================================

torque_rows = [
    ("M4", 0.7, 1.5),
    ("M5", 0.8, 3),
    ("M6", 1.0, 5),
    ("M8", 1.25, 12),
    ("M10", 1.5, 25),
    ("M12", 1.75, 45),
    ("M14", 2.0, 70),
    ("M16", 2.0, 110),
    ("M18", 2.5, 150),
    ("M20", 2.5, 220),
    ("M22", 2.5, 300),
    ("M24", 3.0, 380),
]

for size, pitch, torque in torque_rows:

    conn.execute("""
        INSERT INTO standards
        (
            category,
            code,
            name,
            standard,
            size,
            dimension_1,
            dimension_2,
            unit,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "torque",
        size,
        f"گشتاور مرجع {size}",
        "Engineering reference",
        size,
        pitch,
        torque,
        "N.m",
        "مقدار مرجع گشتاور؛ برای انتخاب نهایی باید کلاس و جنس اتصال بررسی شود."
    ))


# =========================================================
# 6 - UNITS
# =========================================================

units = [
    ("mm_to_m", "میلی‌متر به متر", 0.001),
    ("m_to_mm", "متر به میلی‌متر", 1000),
    ("inch_to_mm", "اینچ به میلی‌متر", 25.4),
    ("mm_to_inch", "میلی‌متر به اینچ", 1 / 25.4),
    ("kw_to_w", "کیلووات به وات", 1000),
    ("w_to_kw", "وات به کیلووات", 0.001),
    ("hp_to_kw", "اسب بخار به کیلووات", 0.7457),
    ("kw_to_hp", "کیلووات به اسب بخار", 1 / 0.7457),
    ("rpm_to_rads", "RPM به rad/s", 0.104719755),
]

for code, name, value in units:

    conn.execute("""
        INSERT INTO standards
        (
            category,
            code,
            name,
            value,
            description
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        "units",
        code,
        name,
        value,
        "ضریب تبدیل واحد"
    ))


# =========================================================
# 7 - KEYS
# =========================================================

keys = [
    (3, 3, 16),
    (4, 4, 20),
    (5, 5, 25),
    (6, 6, 28),
    (8, 7, 32),
    (10, 8, 36),
    (12, 8, 45),
    (14, 9, 50),
    (16, 10, 56),
    (18, 11, 63),
    (20, 12, 70),
    (22, 14, 80),
    (25, 14, 90),
    (28, 16, 100),
    (32, 18, 110),
    (36, 20, 125),
    (40, 22, 140),
    (45, 25, 160),
    (50, 28, 180),
]

for shaft, width, length in keys:

    conn.execute("""
        INSERT INTO standards
        (
            category,
            code,
            name,
            standard,
            size,
            dimension_1,
            dimension_2,
            dimension_3,
            unit,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "keys",
        f"KEY-{shaft}",
        f"خار شفت قطر {shaft} mm",
        "DIN / Engineering",
        f"{shaft} mm",
        width,
        width,
        length,
        "mm",
        "ابعاد نمونه خار موازی؛ برای طراحی نهایی استاندارد دقیق باید بررسی شود."
    ))


conn.commit()

count = conn.execute(
    "SELECT COUNT(*) FROM standards"
).fetchone()[0]

conn.close()

print(f"Standards imported successfully: {count} records")
