import sqlite3
import json


DB="mechassist.db"


conn=sqlite3.connect(DB)

cursor=conn.cursor()


with open(
    "equipment_data.json",
    encoding="utf-8"
) as file:

    data=json.load(file)



for item in data:


    cursor.execute("""
    INSERT INTO equipment
    (
    category_id,
    name,
    brand,
    description
    )

    VALUES(?,?,?,?)

    """,
    (
    item["category_id"],
    item["name"],
    item["brand"],
    item["description"]
    ))


    equipment_id=cursor.lastrowid



    for spec in item["specifications"]:


        cursor.execute("""
        INSERT INTO specifications
        (
        equipment_id,
        parameter,
        value,
        unit
        )

        VALUES(?,?,?,?)

        """,
        (
        equipment_id,
        spec["parameter"],
        spec["value"],
        spec["unit"]
        ))



    for failure in item["failures"]:


        cursor.execute("""
        INSERT INTO failures
        (
        equipment_id,
        symptom,
        cause,
        solution
        )

        VALUES(?,?,?,?)

        """,
        (
        equipment_id,
        failure["symptom"],
        failure["cause"],
        failure["solution"]
        ))



conn.commit()

conn.close()


print(
"1000+ equipment imported successfully"
)
