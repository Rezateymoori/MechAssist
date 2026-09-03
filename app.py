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


# ========================= FACILITIES MODULE =========================
FACILITY_CATEGORIES = {
    "pump": {"fa": "پمپ‌ها", "icon": "💧"},
    "fan": {"fa": "فن‌ها و هواکش‌ها", "icon": "🌀"},
    "compressor": {"fa": "کمپرسورها", "icon": "💨"},
    "chiller": {"fa": "چیلرها", "icon": "❄️"},
    "boiler": {"fa": "بویلرها", "icon": "🔥"},
    "hvac": {"fa": "تجهیزات HVAC", "icon": "🌬️"},
    "valve": {"fa": "شیرآلات", "icon": "🔧"},
    "heat_exchanger": {"fa": "مبدل‌های حرارتی", "icon": "♨️"},
    "tank": {"fa": "مخازن", "icon": "🛢️"},
    "pipe": {"fa": "لوله و اتصالات", "icon": "➰"},
    "fire_fighting": {"fa": "آتش‌نشانی", "icon": "🚒"},
    "water_treatment": {"fa": "تصفیه آب", "icon": "🚰"},
    "air_handling": {"fa": "هواسازها", "icon": "🌪️"},
    "cooling_tower": {"fa": "برج خنک‌کننده", "icon": "🏭"}
}

FACILITY_CALCS = [
    {"key":"pump_head","title":"هد پمپ","formula":"H = ΔP / (ρg)","description":"تبدیل اختلاف فشار به هد سیال."},
    {"key":"pump_power","title":"توان هیدرولیکی پمپ","formula":"P = ρgQH / η","description":"Q بر حسب m³/s، H بر حسب m و η به صورت اعشاری."},
    {"key":"pipe_velocity","title":"سرعت جریان در لوله","formula":"v = Q / A","description":"Q بر حسب m³/s و قطر داخلی لوله بر حسب m."},
    {"key":"pipe_diameter","title":"قطر لوله از روی دبی و سرعت","formula":"D = √(4Q / πv)","description":"قطر داخلی نظری لوله."},
    {"key":"pressure_drop","title":"افت فشار دارسی-ویسباخ","formula":"ΔP = f(L/D)(ρv²/2)","description":"برای افت اصطکاکی مستقیم؛ افت‌های موضعی جداگانه بررسی شوند."},
    {"key":"cooling_capacity","title":"ظرفیت سرمایش آب","formula":"Q̇ = ρ cp Q ΔT","description":"ظرفیت سرمایش بر اساس دبی حجمی آب و اختلاف دما."},
    {"key":"heating_capacity","title":"ظرفیت گرمایش آب","formula":"Q̇ = ρ cp Q ΔT","description":"ظرفیت گرمایش برای مدار آب گرم."},
    {"key":"tank_volume","title":"حجم مخزن استوانه‌ای","formula":"V = πD²H / 4","description":"D و H بر حسب متر؛ خروجی m³."},
    {"key":"airflow","title":"دبی هوا از سرعت و سطح","formula":"Q = vA","description":"Q بر حسب m³/s."},
    {"key":"fan_power","title":"توان هوادهی فن","formula":"P = QΔP / η","description":"Q بر حسب m³/s و ΔP بر حسب Pa."},
    {"key":"compressor_power","title":"توان تقریبی کمپرسور","formula":"P ≈ QΔP / η","description":"برای برآورد اولیه؛ طراحی کمپرسور نیازمند ترمودینامیک و دیتاشیت است."}
]

@app.route("/facilities")
def facilities():
    conn=get_db()
    counts=conn.execute("SELECT category, COUNT(*) count FROM facilities GROUP BY category").fetchall()
    conn.close()
    count_map={r["category"]:r["count"] for r in counts}
    cards=[]
    for key,meta in FACILITY_CATEGORIES.items():
        cards.append({"key":key,"fa":meta["fa"],"icon":meta["icon"],"count":count_map.get(key,0)})
    return render_template("facilities.html", categories=cards)

@app.route("/facilities/<category>")
def facility_category(category):
    if category not in FACILITY_CATEGORIES: return "دسته تأسیسات پیدا نشد",404
    q=request.args.get("q","").strip()
    conn=get_db()
    sql="SELECT * FROM facilities WHERE category=?"
    params=[category]
    if q:
        sql += " AND (name LIKE ? OR brand LIKE ? OR model LIKE ? OR description LIKE ? OR application LIKE ?)"
        params += [f"%{q}%"]*5
    sql += " ORDER BY id DESC"
    rows=conn.execute(sql,params).fetchall(); conn.close()
    return render_template("facility_list.html", rows=rows, category=FACILITY_CATEGORIES[category], category_key=category, search=q)

@app.route("/facility/<int:id>")
def facility_detail(id):
    conn=get_db()
    row=conn.execute("SELECT * FROM facilities WHERE id=?",(id,)).fetchone()
    if not row: conn.close(); return "تجهیز تأسیسات پیدا نشد",404
    specs=conn.execute("SELECT * FROM facility_specifications WHERE facility_id=?",(id,)).fetchall()
    failures=conn.execute("SELECT * FROM facility_failures WHERE facility_id=?",(id,)).fetchall()
    alternatives=conn.execute("SELECT * FROM facility_alternatives WHERE facility_id=?",(id,)).fetchall()
    conn.close()
    return render_template("facility_detail.html", facility=row, specs=specs, failures=failures, alternatives=alternatives, category=FACILITY_CATEGORIES.get(row["category"],{}))

@app.route("/facility-calculations", methods=["GET","POST"])
def facility_calculations():
    key=request.form.get("calc","") if request.method=="POST" else request.args.get("calc","")
    result=None; error=None
    try:
        if request.method=="POST":
            def f(name): return float(request.form.get(name,"0"))
            if key=="pump_head": result={"value": f("dp")/(f("rho")*f("g")),"unit":"m"}
            elif key=="pump_power": result={"value": f("rho")*f("g")*f("q")*f("h")/f("eta"),"unit":"W"}
            elif key=="pipe_velocity": result={"value": f("q")/(3.141592653589793*f("d")**2/4),"unit":"m/s"}
            elif key=="pipe_diameter": result={"value":(4*f("q")/(3.141592653589793*f("v")))**0.5,"unit":"m"}
            elif key=="pressure_drop": result={"value":f("friction")*(f("length")/f("diameter"))*(f("rho")*f("velocity")**2/2),"unit":"Pa"}
            elif key in ("cooling_capacity","heating_capacity"): result={"value":f("rho")*f("cp")*f("q")*f("dt"),"unit":"W"}
            elif key=="tank_volume": result={"value":3.141592653589793*f("d")**2*f("h")/4,"unit":"m³"}
            elif key=="airflow": result={"value":f("velocity")*f("area"),"unit":"m³/s"}
            elif key in ("fan_power","compressor_power"): result={"value":f("q")*f("pressure")/f("eta"),"unit":"W"}
            else: error="نوع محاسبه انتخاب نشده است."
            if result: result["value"]=round(result["value"],4)
    except (ValueError,ZeroDivisionError): error="مقادیر ورودی باید عددی و مخرج‌ها بزرگ‌تر از صفر باشند."
    return render_template("facility_calculations.html", calculations=FACILITY_CALCS, selected=key, result=result, error=error)

@app.route("/facility-knowledge")
def facility_knowledge():
    topics=[
      ("water-supply","آبرسانی","انتخاب پمپ، مخزن، قطر لوله و کنترل فشار در شبکه آبرسانی."),
      ("sewage","فاضلاب","شیب‌بندی، تهویه، انتخاب لوله و کنترل گرفتگی در شبکه فاضلاب."),
      ("heating","گرمایش","دیگ، پمپ، مبدل، کنترل دما و بالانس مدار گرمایش."),
      ("cooling","سرمایش","چیلر، برج خنک‌کننده، پمپ‌ها و مدار آب سرد."),
      ("hvac","تهویه مطبوع","بار سرمایش/گرمایش، هوای تازه، هواساز، کانال و کنترل کیفیت هوا."),
      ("compressed-air","هوای فشرده","کمپرسور، درایر، مخزن، افت فشار و کیفیت هوای فشرده."),
      ("steam","بخار","بویلر، تله بخار، مبدل و خطوط بخار و برگشت کندانس."),
      ("fire","آتش‌نشانی","پمپ آتش‌نشانی، اسپرینکلر، هیدرانت، مخزن و شبکه اطفا."),
      ("water-treatment","تصفیه آب","فیلتراسیون، سختی‌گیری، RO و کنترل کیفیت آب."),
    ]
    return render_template("facility_knowledge.html", topics=topics)

@app.route("/facility-knowledge/<topic>")
def facility_knowledge_topic(topic):
    data={
      "water-supply":("آبرسانی","محاسبه دبی همزمان، انتخاب قطر اقتصادی، افت فشار، هد استاتیک و کنترل فشار از مراحل اصلی طراحی شبکه است."),
      "sewage":("فاضلاب","در شبکه فاضلاب شیب، سرعت خودپاک‌کنندگی، تهویه و دسترسی برای تعمیرات اهمیت دارد."),
      "heating":("گرمایش","ظرفیت حرارتی از Q̇=ρcpQΔT به دست می‌آید؛ انتخاب دیگ و پمپ باید با بار واقعی و شرایط طراحی انجام شود."),
      "cooling":("سرمایش","ظرفیت سرمایش مدار آب سرد تابع دبی، گرمای ویژه و اختلاف دماست و باید با شرایط چیلر تطبیق داده شود."),
      "hvac":("تهویه مطبوع","بار حرارتی، هوای تازه، رطوبت، افت فشار کانال و انتخاب فن/هواساز در طراحی بررسی می‌شوند."),
      "compressed-air":("هوای فشرده","مصرف واقعی، فشار مورد نیاز، افت فشار، ذخیره‌سازی، درایر و کیفیت هوا باید همزمان بررسی شوند."),
      "steam":("بخار","فشار و دمای طراحی، تله‌های بخار، شیب خطوط، جداسازی کندانس و ایمنی دیگ از موارد کلیدی هستند."),
      "fire":("آتش‌نشانی","طراحی سامانه اطفا باید مطابق کدها و ضوابط محلی و توسط فرد صلاحیت‌دار انجام شود."),
      "water-treatment":("تصفیه آب","فرایند مناسب به کیفیت آب خام و هدف مصرف بستگی دارد؛ پایش پارامترهای آب برای بهره‌برداری ضروری است.")}
    if topic not in data: return "موضوع پیدا نشد",404
    return render_template("facility_knowledge_topic.html", title=data[topic][0], text=data[topic][1])

@app.route("/facility-standards")
def facility_standards():
    conn=get_db(); cats=conn.execute("SELECT category,COUNT(*) count FROM facility_standards GROUP BY category ORDER BY category").fetchall(); conn.close()
    return render_template("facility_standards.html", categories=cats)

@app.route("/facility-standards/<category>")
def facility_standard_table(category):
    q=request.args.get("q","").strip(); conn=get_db()
    sql="SELECT * FROM facility_standards WHERE category=?"; params=[category]
    if q:
        sql += " AND (code LIKE ? OR name LIKE ? OR standard LIKE ? OR size LIKE ? OR description LIKE ?)"; params += [f"%{q}%"]*5
    rows=conn.execute(sql,params).fetchall(); conn.close()
    return render_template("facility_standard_table.html", rows=rows, category=category, search=q)

if __name__=="__main__":

    app.run()
    

