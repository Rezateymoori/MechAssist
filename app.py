from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "mechassist.db"
)


def get_db():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn



# صفحه اصلی
@app.route("/")
def index():

    conn = get_db()

    equipments = conn.execute("""
        SELECT 
        equipment.id,
        equipment.name,
        equipment.brand,
        equipment.description,
        categories.name_fa

        FROM equipment

        JOIN categories

        ON equipment.category_id = categories.id

    """).fetchall()


    conn.close()


    return render_template(
        "index.html",
        equipments=equipments
    )




# صفحه جزئیات تجهیز
@app.route("/equipment/<int:id>")
def equipment_detail(id):

    conn = get_db()



    equipment = conn.execute("""

        SELECT

        equipment.*,

        categories.name_fa


        FROM equipment


        JOIN categories

        ON equipment.category_id = categories.id


        WHERE equipment.id = ?

    """,
    (id,)
    ).fetchone()



    specifications = conn.execute("""

        SELECT
        parameter,
        value,
        unit

        FROM specifications

        WHERE equipment_id = ?

    """,
    (id,)
    ).fetchall()



    failures = conn.execute("""

        SELECT

        symptom,
        cause,
        solution

        FROM failures


        WHERE equipment_id = ?

    """,
    (id,)
    ).fetchall()



    alternatives = conn.execute("""

        SELECT

        alternative_name,
        brand


        FROM alternatives


        WHERE equipment_id = ?

    """,
    (id,)
    ).fetchall()



    conn.close()



    return render_template(

        "detail.html",

        equipment=equipment,

        specifications=specifications,

        failures=failures,

        alternatives=alternatives

    )


@app.route("/search")
def search():

    keyword = request.args.get(
        "q",
        ""
    )

    category = request.args.get(
        "category",
        ""
    )

    brand = request.args.get(
        "brand",
        ""
    )


    conn = get_db()



    query = """

    SELECT

    equipment.id,
    equipment.name,
    equipment.brand,
    equipment.description,
    categories.name_fa


    FROM equipment


    JOIN categories

    ON equipment.category_id =
       categories.id


    WHERE 1=1

    """


    params=[]



    if keyword:

        query += """

        AND
        (
        equipment.name LIKE ?
        OR equipment.description LIKE ?
        )

        """

        params.extend(
        [
        f"%{keyword}%",
        f"%{keyword}%"
        ]
        )



    if category:


        query += """

        AND categories.id=?

        """


        params.append(category)




    if brand:


        query += """

        AND equipment.brand LIKE ?

        """


        params.append(
            f"%{brand}%"
        )



    results = conn.execute(
        query,
        params
    ).fetchall()



    categories = conn.execute(

        """
        SELECT * FROM categories

        """

    ).fetchall()



    brands = conn.execute(

        """
        SELECT DISTINCT brand
        FROM equipment

        """

    ).fetchall()



    conn.close()



    return render_template(

        "search.html",

        results=results,

        categories=categories,

        brands=brands

    )

@app.route("/admin")
def admin():

    conn = get_db()

    equipments = conn.execute("""
    SELECT 
    equipment.id,
    equipment.name,
    equipment.brand,
    categories.name_fa

    FROM equipment

    JOIN categories

    ON equipment.category_id = categories.id

    ORDER BY equipment.id DESC

    """).fetchall()


    categories = conn.execute(
        "SELECT * FROM categories"
    ).fetchall()


    conn.close()


    return render_template(
        "admin.html",
        equipments=equipments,
        categories=categories
    )

@app.route("/admin/add", methods=["GET","POST"])
def add_equipment():


    conn=get_db()


    if request.method=="POST":


        name=request.form["name"]

        brand=request.form["brand"]

        category=request.form["category"]

        description=request.form["description"]



        conn.execute("""
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
        category,
        name,
        brand,
        description
        ))


        conn.commit()

        conn.close()


        return redirect("/admin")



    categories=conn.execute(
        "SELECT * FROM categories"
    ).fetchall()


    conn.close()


    return render_template(
        "add_equipment.html",
        categories=categories
    )



@app.route("/bearings")
def bearings():

    search = request.args.get("q", "").strip()

    conn = get_db()

    if search:

        bearings = conn.execute("""
            SELECT *
            FROM bearings
            WHERE
                name LIKE ?
                OR brand LIKE ?
                OR bearing_type LIKE ?
                OR series LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:

        bearings = conn.execute("""
            SELECT *
            FROM bearings
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "bearings.html",
        bearings=bearings,
        search=search
    )


@app.route("/bearing/<int:id>")
def bearing_detail(id):

    conn = get_db()

    bearing = conn.execute("""
        SELECT *
        FROM bearings
        WHERE id = ?
    """, (id,)).fetchone()

    conn.close()

    if bearing is None:
        return "برینگ مورد نظر پیدا نشد", 404

    return render_template(
        "bearing_detail.html",
        bearing=bearing
    )




@app.route("/bearing/calculator", methods=["GET", "POST"])
def bearing_calculator():

    result = None

    if request.method == "POST":

        C = float(request.form["C"])
        P = float(request.form["P"])
        rpm = float(request.form["rpm"])

        if P <= 0 or rpm <= 0:

            result = {
                "error": "مقادیر بار و RPM باید بزرگ‌تر از صفر باشند."
            }

        else:

            L10 = (C / P) ** 3

            hours = (
                L10 * 1000000
            ) / (60 * rpm)

            result = {
                "L10": round(L10, 2),
                "hours": round(hours, 2)
            }


    return render_template(
        "bearing_calculator.html",
        result=result
    )

@app.route("/knowledge/<equipment_type>")
def knowledge(equipment_type):

    # فقط اجازه استفاده از نام‌های مشخص را می‌دهیم
    allowed_types = {
        "bearing": "bearing_knowledge.json",
        "gearbox": "gearbox_knowledge.json",
        "coupling": "coupling_knowledge.json",
        "shaft": "shaft_knowledge.json",
        "belt": "belt_knowledge.json",
        "chain": "chain_knowledge.json",
        "pulley": "pulley_knowledge.json",
        "seal": "seal_knowledge.json",
        "lubrication": "lubrication_knowledge.json"
    }

    # بررسی وجود نوع تجهیز
    if equipment_type not in allowed_types:
        return "دانشنامه مورد نظر پیدا نشد", 404

    filename = allowed_types[equipment_type]

    filepath = os.path.join(
    BASE_DIR,
    "database",
    filename
)

    # بررسی وجود فایل
    if not os.path.exists(filepath):
        return f"فایل دانشنامه {filename} پیدا نشد", 404

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as f:

            knowledge_data = json.load(f)

    except json.JSONDecodeError:
        return f"فرمت فایل {filename} صحیح نیست", 500

    except Exception as e:
        return f"خطا در خواندن دانشنامه: {str(e)}", 500

    return render_template(
        "knowledge.html",
        knowledge=knowledge_data,
        equipment_type=equipment_type
    )

@app.route("/knowledge")
def knowledge_index():

    items = [
        {
            "name":"برینگ‌ها",
            "icon":"🔩",
            "url":"bearing"
        },
        {
            "name":"گیربکس‌ها",
            "icon":"⚙",
            "url":"gearbox"
        },
        {
            "name":"کوپلینگ‌ها",
            "icon":"🔗",
            "url":"coupling"
        },
        {
            "name":"شفت‌ها",
            "icon":"🔧",
            "url":"shaft"
        },
        {
            "name":"تسمه",
            "icon":"🛞",
            "url":"belt"
        },
        {
            "name":"روانکاری",
            "icon":"🛢",
            "url":"lubrication"
        },
        {
        "name":"زنجیر صنعتی",
        "icon":"⛓",
        "url":"chain"
    },

    {
        "name":"آب‌بندها",
        "icon":"⭕",
        "url":"seal"
    },
    {
        "name":"پولی",
        "icon":"🛞",
        "url":"pulley"
    },

    ]


    return render_template(
        "knowledge_index.html",
        items=items
    )

@app.route("/gearboxes")
def gearboxes():

    conn=get_db()

    data=conn.execute("""
    SELECT *
    FROM gearboxes
    ORDER BY id DESC
    """).fetchall()

    conn.close()


    return render_template(
        "gearboxes.html",
        gearboxes=data
    )

@app.route("/couplings")
def couplings():

    search = request.args.get("q", "").strip()

    conn = get_db()

    if search:

        data = conn.execute("""
            SELECT *
            FROM couplings

            WHERE
                name LIKE ?
                OR brand LIKE ?
                OR coupling_type LIKE ?
                OR series LIKE ?
                OR application LIKE ?

            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:

        data = conn.execute("""
            SELECT *
            FROM couplings
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "couplings.html",
        couplings=data,
        search=search
    )



@app.route("/standards")
def standards():

    conn = get_db()

    categories = conn.execute("""
        SELECT
            category,
            COUNT(*) AS count
        FROM standards
        GROUP BY category
        ORDER BY category
    """).fetchall()

    conn.close()

    return render_template(
        "standards_index.html",
        categories=categories
    )

@app.route("/standards/<category>")
def standard_table(category):

    search = request.args.get("q", "").strip()

    conn = get_db()

    if search:

        rows = conn.execute("""
            SELECT *
            FROM standards

            WHERE category = ?

            AND (
                code LIKE ?
                OR name LIKE ?
                OR standard LIKE ?
                OR size LIKE ?
                OR description LIKE ?
            )

            ORDER BY id
        """, (
            category,
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:

        rows = conn.execute("""
            SELECT *
            FROM standards
            WHERE category = ?
            ORDER BY id
        """, (category,)).fetchall()

    conn.close()

    titles = {
        "bearings": "🔩 ابعاد استاندارد برینگ‌ها",
        "threads": "🔩 رزوه‌های متریک",
        "bolts": "🔧 پیچ و مهره",
        "housings": "⚙️ یاتاقان‌ها",
        "torque": "🔄 گشتاور و تورک",
        "units": "📐 تبدیل واحدها",
        "keys": "🔗 خار و شفت",
        "tolerances": "🛠 تلرانس و انطباقات"
    }

    title = titles.get(
        category,
        "📊 جدول استاندارد"
    )

    return render_template(
        "standard_table.html",
        rows=rows,
        category=category,
        title=title,
        search=search
    )

if __name__=="__main__":

    app.run()
    

