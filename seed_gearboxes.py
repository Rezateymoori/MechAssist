import sqlite3
import json


conn = sqlite3.connect("mechassist.db")

with open(
    "database/gearboxes_data.json",
    encoding="utf-8"
) as f:

    data=json.load(f)



for g in data:

    conn.execute("""

    INSERT INTO gearboxes

    (
    name,
    brand,
    gearbox_type,
    series,
    ratio,
    power,
    input_speed,
    output_speed,
    torque,
    application,
    lubrication,
    description
    )

    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)

    """,

    (
    g["name"],
    g["brand"],
    g["gearbox_type"],
    g["series"],
    g["ratio"],
    g["power"],
    g["input_speed"],
    g["output_speed"],
    g["torque"],
    g["application"],
    g["lubrication"],
    g["description"]
    ))




conn.commit()
conn.close()


print("Gearboxes imported")
