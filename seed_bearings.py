import sqlite3
import json


conn = sqlite3.connect(
"mechassist.db"
)

cursor = conn.cursor()



with open(
"database/bearings_data.json",
encoding="utf-8"
) as f:

    bearings=json.load(f)



for b in bearings:


    cursor.execute("""

    INSERT INTO bearings

    (

    name,
    brand,
    bearing_type,
    series,
    bore,
    outer_diameter,
    width,
    dynamic_load,
    static_load,
    max_rpm,
    clearance,
    seal,
    lubrication,
    applications,
    failures,
    equivalent

    )

    VALUES
    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

    """,

    (

    b["name"],
    b["brand"],
    b["bearing_type"],
    b["series"],
    b["bore"],
    b["outer_diameter"],
    b["width"],
    b["dynamic_load"],
    b["static_load"],
    b["max_rpm"],
    b["clearance"],
    b["seal"],
    b["lubrication"],
    b["applications"],
    b["failures"],
    b["equivalent"]

    ))



conn.commit()

conn.close()


print("Bearings imported")
