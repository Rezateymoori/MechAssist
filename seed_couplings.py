import sqlite3
import json


DATABASE = "mechassist.db"

JSON_FILE = "database/couplings_data.json"


conn = sqlite3.connect(DATABASE)


with open(
    JSON_FILE,
    encoding="utf-8"
) as f:

    data = json.load(f)


inserted = 0

skipped = 0


for c in data:

    exists = conn.execute("""

        SELECT id

        FROM couplings

        WHERE

            name = ?

            AND brand = ?

            AND series = ?

    """, (

        c["name"],

        c["brand"],

        c["series"]

    )).fetchone()


    if exists:

        skipped += 1

        continue


    conn.execute("""

        INSERT INTO couplings

        (

            name,

            brand,

            coupling_type,

            series,

            bore,

            max_rpm,

            nominal_torque,

            max_torque,

            material,

            application,

            lubrication,

            description

        )

        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)

    """, (

        c["name"],

        c["brand"],

        c["coupling_type"],

        c["series"],

        c["bore"],

        c["max_rpm"],

        c["nominal_torque"],

        c["max_torque"],

        c["material"],

        c["application"],

        c["lubrication"],

        c["description"]

    ))


    inserted += 1


conn.commit()


total = conn.execute("""

    SELECT COUNT(*)

    FROM couplings

""").fetchone()[0]


conn.close()


print()

print("=" * 50)

print("✅ بانک کوپلینگ به‌روزرسانی شد")

print(f"📥 رکورد جدید: {inserted}")

print(f"⏭ تکراری: {skipped}")

print(f"📊 مجموع رکوردها: {total}")

print("=" * 50)
