from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
import os
import math

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



FACILITIES_SEED = os.path.join(BASE_DIR, "database", "facilities_seed.json")


def init_facilities_db():
    """Create and seed the facilities module without disturbing existing tables."""
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS facility_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name_fa TEXT NOT NULL,
        icon TEXT DEFAULT '🏢',
        description TEXT
    );
    CREATE TABLE IF NOT EXISTS facilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        brand TEXT,
        model TEXT,
        description TEXT,
        application TEXT,
        status TEXT,
        FOREIGN KEY(category_id) REFERENCES facility_categories(id)
    );
    CREATE TABLE IF NOT EXISTS facility_specifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_id INTEGER NOT NULL,
        parameter TEXT,
        value TEXT,
        unit TEXT,
        FOREIGN KEY(facility_id) REFERENCES facilities(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS facility_failures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_id INTEGER NOT NULL,
        symptom TEXT,
        cause TEXT,
        solution TEXT,
        FOREIGN KEY(facility_id) REFERENCES facilities(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS facility_alternatives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_id INTEGER NOT NULL,
        alternative_name TEXT,
        brand TEXT,
        FOREIGN KEY(facility_id) REFERENCES facilities(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS facility_standards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        scope TEXT
    );
    CREATE TABLE IF NOT EXISTS facility_calculators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        formula TEXT,
        description TEXT
    );
    CREATE TABLE IF NOT EXISTS facility_systems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name_fa TEXT NOT NULL,
        description TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_facilities_category ON facilities(category_id);
    CREATE INDEX IF NOT EXISTS idx_facility_specs_facility ON facility_specifications(facility_id);
    CREATE INDEX IF NOT EXISTS idx_facility_failures_facility ON facility_failures(facility_id);
    """)
    count = conn.execute("SELECT COUNT(*) FROM facilities").fetchone()[0]
    if count == 0 and os.path.exists(FACILITIES_SEED):
        with open(FACILITIES_SEED, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for slug, name_fa, desc, _families in data['categories']:
            icon = {'pump':'💧','fan':'🌀','compressor':'💨','chiller':'❄️','boiler':'🔥','hvac':'🌬️','valve':'🔧','heat_exchanger':'♨️','tank':'🛢️','pipe':'➰','fire_fighting':'🚒','water_treatment':'🚰','cooling_tower':'🏭'}.get(slug,'🏢')
            conn.execute("INSERT OR IGNORE INTO facility_categories(slug,name_fa,icon,description) VALUES(?,?,?,?)", (slug,name_fa,icon,desc))
        conn.commit()
        cat_ids={r['slug']:r['id'] for r in conn.execute('SELECT id,slug FROM facility_categories').fetchall()}
        for x in data['equipment']:
            cur=conn.execute("INSERT INTO facilities(category_id,name,brand,model,description,application,status) VALUES(?,?,?,?,?,?,?)", (cat_ids[x['category']],x['name'],x['brand'],x['model'],x['description'],x['application'],x['status']))
            fid=cur.lastrowid
            for q in [z for z in data['specifications'] if z['equipment_id']==x['id']]:
                conn.execute("INSERT INTO facility_specifications(facility_id,parameter,value,unit) VALUES(?,?,?,?)",(fid,q['parameter'],q['value'],q['unit']))
            for q in [z for z in data['failures'] if z['equipment_id']==x['id']]:
                conn.execute("INSERT INTO facility_failures(facility_id,symptom,cause,solution) VALUES(?,?,?,?)",(fid,q['symptom'],q['cause'],q['solution']))
            for q in [z for z in data['alternatives'] if z['equipment_id']==x['id']]:
                conn.execute("INSERT INTO facility_alternatives(facility_id,alternative_name,brand) VALUES(?,?,?)",(fid,q['alternative_name'],q['brand']))
        for code,name,description in data['standards']:
            conn.execute("INSERT INTO facility_standards(code,name,description,scope) VALUES(?,?,?,?)",(code,name,description,'تأسیسات مکانیکی، HVAC، لوله‌کشی، آتش‌نشانی یا تجهیزات مرتبط'))
        for slug,title,formula,description in data['calculators']:
            conn.execute("INSERT INTO facility_calculators(slug,title,formula,description) VALUES(?,?,?,?)",(slug,title,formula,description))
        for slug,name_fa,description in data.get('systems',[]):
            conn.execute("INSERT INTO facility_systems(slug,name_fa,description) VALUES(?,?,?)",(slug,name_fa,description))
        conn.commit()
    conn.close()


init_facilities_db()


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
        "SELECT DISTINCT brand FROM equipment WHERE brand IS NOT NULL AND brand <> ''"
    ).fetchall()

    facility_results = []
    if keyword:
        facility_results = conn.execute("""
            SELECT f.id, f.name, f.brand, f.model, f.description, c.name_fa, c.slug, c.icon
            FROM facilities f
            JOIN facility_categories c ON f.category_id=c.id
            WHERE f.name LIKE ? OR f.brand LIKE ? OR f.model LIKE ?
               OR f.description LIKE ? OR c.name_fa LIKE ?
            ORDER BY f.id DESC
        """, tuple([f"%{keyword}%"] * 5)).fetchall()

    conn.close()

    return render_template(
        "search.html",
        results=results,
        facility_results=facility_results,
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

@app.route("/mechanical-calculator/<component>", methods=["GET", "POST"])
def mechanical_calculator(component):
    configs = {
        "belt": {"title":"محاسبه‌گر تسمه", "fields":[{"name":"D","label":"قطر پولی (m)"},{"name":"rpm","label":"دور پولی (rpm)"}], "mode":"speed"},
        "pulley": {"title":"محاسبه‌گر پولی", "fields":[{"name":"n1","label":"دور پولی محرک (rpm)"},{"name":"D1","label":"قطر پولی محرک (m)"},{"name":"D2","label":"قطر پولی متحرک (m)"}], "mode":"pulley"},
        "chain": {"title":"محاسبه‌گر زنجیر", "fields":[{"name":"p","label":"گام زنجیر (mm)"},{"name":"z","label":"تعداد دندانه چرخ زنجیر"},{"name":"rpm","label":"دور (rpm)"}], "mode":"chain"},
        "seal": {"title":"محاسبه‌گر آب‌بند", "fields":[{"name":"d","label":"قطر شفت در محل آب‌بندی (mm)"},{"name":"rpm","label":"دور شفت (rpm)"}], "mode":"seal"}
    }
    cfg = configs.get(component)
    if not cfg:
        return "محاسبه‌گر مورد نظر پیدا نشد", 404
    result = None
    if request.method == "POST":
        try:
            vals = {k: float(request.form[k]) for k in [f["name"] for f in cfg["fields"]]}
            if any(v <= 0 for v in vals.values()):
                result = {"error":"همه مقادیر باید بزرگ‌تر از صفر باشند."}
            elif cfg["mode"] == "speed":
                import math
                result = {"سرعت خطی تسمه (m/s)": round(math.pi * vals["D"] * vals["rpm"] / 60, 4)}
            elif cfg["mode"] == "pulley":
                result = {"سرعت پولی متحرک (rpm)": round(vals["n1"] * vals["D1"] / vals["D2"], 3), "نسبت انتقال n1/n2": round(vals["D2"] / vals["D1"], 4)}
            elif cfg["mode"] == "chain":
                result = {"سرعت زنجیر (m/s)": round((vals["p"] / 1000) * vals["z"] * vals["rpm"] / 60, 4), "قطر گام چرخ زنجیر (mm)": round((vals["p"] / 1000) / __import__('math').sin(__import__('math').pi / vals["z"]) * 1000, 3)}
            elif cfg["mode"] == "seal":
                result = {"سرعت محیطی شفت در محل آب‌بندی (m/s)": round(__import__('math').pi * (vals["d"] / 1000) * vals["rpm"] / 60, 4)}
        except (ValueError, KeyError, ZeroDivisionError):
            result = {"error":"ورودی‌ها معتبر نیستند."}
    return render_template("mechanical_calculator.html", title=cfg["title"], fields=cfg["fields"], result=result)


@app.route("/components/<component>")
def component_collection(component):
    """Unified collection for each mechanical part: database, knowledge, calculations and standards."""
    collections = {
        "bearing": {"title":"برینگ و یاتاقان", "icon":"🔩", "knowledge":"/knowledge/bearing", "database":"/bearings", "calculator":"/bearing/calculator", "standard":"/component-standards/bearing"},
        "gearbox": {"title":"گیربکس", "icon":"⚙", "knowledge":"/knowledge/gearbox", "database":"/gearboxes", "calculator":None, "standard":"/component-standards/{component}"},
        "coupling": {"title":"کوپلینگ", "icon":"🔗", "knowledge":"/knowledge/coupling", "database":"/couplings", "calculator":None, "standard":"/component-standards/{component}"},
        "shaft": {"title":"شفت", "icon":"🔧", "knowledge":"/knowledge/shaft", "database":"/search?q=شفت", "calculator":None, "standard":"/component-standards/shaft"},
        "belt": {"title":"تسمه", "icon":"🛞", "knowledge":"/knowledge/belt", "database":"/search?q=تسمه", "calculator":"/mechanical-calculator/belt", "standard":"/component-standards/{component}"},
        "chain": {"title":"زنجیر صنعتی", "icon":"⛓", "knowledge":"/knowledge/chain", "database":"/search?q=زنجیر", "calculator":"/mechanical-calculator/chain", "standard":"/component-standards/{component}"},
        "pulley": {"title":"پولی", "icon":"🛞", "knowledge":"/knowledge/pulley", "database":"/search?q=پولی", "calculator":"/mechanical-calculator/pulley", "standard":"/component-standards/{component}"},
        "seal": {"title":"آب‌بندها", "icon":"⭕", "knowledge":"/knowledge/seal", "database":"/search?q=آب%20بند", "calculator":"/mechanical-calculator/seal", "standard":"/component-standards/{component}"},
    }
    item = collections.get(component)
    if not item:
        return "مجموعه قطعه پیدا نشد", 404
    item = dict(item)
    item["standard"] = item["standard"].replace("{component}", component)
    return render_template("component_collection.html", item=item)


MECHANICAL_STANDARD_INFO = {
    "bearing": ("استانداردهای برینگ و یاتاقان", ["ISO 15", "ISO 281", "ISO 492", "ISO 199", "ISO 5753", "DIN 625"]),
    "gearbox": ("استانداردهای گیربکس", ["ISO 6336", "ISO 10825", "AGMA 6011", "AGMA 9000", "DIN 3990"]),
    "coupling": ("استانداردهای کوپلینگ", ["ISO 14691", "API 671", "DIN 740", "AGMA 9000"]),
    "shaft": ("استانداردهای شفت و خار", ["DIN 6885", "ISO 286", "ISO 2768", "DIN 748"]),
    "belt": ("استانداردهای تسمه", ["ISO 4184", "ISO 1813", "ISO 1081", "DIN 2215", "DIN 2217", "ISO 5296"]),
    "chain": ("استانداردهای زنجیر صنعتی", ["ISO 606", "ISO 1275", "DIN 8187", "DIN 8188", "ANSI B29.1"]),
    "pulley": ("استانداردهای پولی و شیو", ["ISO 4183", "ISO 4184", "DIN 2211", "DIN 2217", "ISO 1081"]),
    "seal": ("استانداردهای آب‌بند", ["ISO 6194", "ISO 3601", "DIN 3760", "DIN 3771", "ISO 16589"]),
}

@app.route("/component-standards/<component>")
def component_standards(component):
    info = MECHANICAL_STANDARD_INFO.get(component)
    if not info:
        return "استانداردهای قطعه پیدا نشد", 404
    title, codes = info
    return render_template("component_standards.html", title=title, codes=codes, component=component)


# مجموعه مستقل تأسیسات، مشابه قطعات مکانیکی
@app.route("/facility-collection/<category>")
def facility_collection(category):
    with open(FACILITIES_SEED, "r", encoding="utf-8") as f:
        data = json.load(f)
    cat = next((x for x in data.get("categories", []) if x[0] == category), None)
    if not cat:
        return "دسته تأسیسات پیدا نشد", 404
    slug, title, description, subtypes = cat
    return render_template("facility_collection.html", item={
        "slug": slug, "title": title, "icon": FACILITY_ICONS.get(slug, "🏢"), "description": description, "subtypes": subtypes
    })


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


# ===================== ماژول کامل تأسیسات =====================

FACILITY_ICONS = {
    'pump':'💧','fan':'🌀','compressor':'💨','chiller':'❄️','boiler':'🔥','hvac':'🌬️',
    'valve':'🔧','heat_exchanger':'♨️','tank':'🛢️','pipe':'➰','fire_fighting':'🚒',
    'water_treatment':'🚰','cooling_tower':'🏭'
}

@app.route('/facilities')
def facilities_home():
    conn=get_db()
    categories=conn.execute("""SELECT c.*, COUNT(f.id) AS count FROM facility_categories c LEFT JOIN facilities f ON f.category_id=c.id GROUP BY c.id ORDER BY c.id""").fetchall()
    total=conn.execute('SELECT COUNT(*) FROM facilities').fetchone()[0]
    standards_count=conn.execute('SELECT COUNT(*) FROM facility_standards').fetchone()[0]
    calc_count=conn.execute('SELECT COUNT(*) FROM facility_calculators').fetchone()[0]
    conn.close()
    return render_template('facilities_index.html', categories=categories, total=total, standards_count=standards_count, calc_count=calc_count)

@app.route('/facilities/<category>')
def facilities_category(category):
    q=request.args.get('q','').strip()
    conn=get_db()
    cat=conn.execute('SELECT * FROM facility_categories WHERE slug=?',(category,)).fetchone()
    if not cat:
        conn.close(); return 'دسته تأسیسات پیدا نشد',404
    sql="""SELECT f.*, c.name_fa, c.slug, c.icon FROM facilities f JOIN facility_categories c ON f.category_id=c.id WHERE c.slug=?"""
    params=[category]
    if q:
        sql += " AND (f.name LIKE ? OR f.brand LIKE ? OR f.model LIKE ? OR f.description LIKE ?)"
        params += [f'%{q}%']*4
    sql += ' ORDER BY f.id'
    items=conn.execute(sql,params).fetchall(); conn.close()
    return render_template('facilities_category.html', category=cat, items=items, search=q)

@app.route('/facility/<int:id>')
def facility_detail(id):
    conn=get_db()
    item=conn.execute("""SELECT f.*, c.name_fa, c.slug, c.icon FROM facilities f JOIN facility_categories c ON f.category_id=c.id WHERE f.id=?""",(id,)).fetchone()
    if not item: conn.close(); return 'تجهیز تأسیسات پیدا نشد',404
    specs=conn.execute('SELECT * FROM facility_specifications WHERE facility_id=? ORDER BY id',(id,)).fetchall()
    failures=conn.execute('SELECT * FROM facility_failures WHERE facility_id=? ORDER BY id',(id,)).fetchall()
    alternatives=conn.execute('SELECT * FROM facility_alternatives WHERE facility_id=? ORDER BY id',(id,)).fetchall()
    conn.close()
    return render_template('facility_detail.html', item=item, specs=specs, failures=failures, alternatives=alternatives)

@app.route('/facility-systems')
def facility_systems():
    conn=get_db(); systems=conn.execute('SELECT * FROM facility_systems ORDER BY id').fetchall(); conn.close()
    return render_template('facility_systems.html', systems=systems)

@app.route('/facility-knowledge')
def facility_knowledge():
    path=os.path.join(BASE_DIR,'database','facilities_seed.json')
    with open(path,'r',encoding='utf-8') as f: data=json.load(f)
    items=[]
    for slug,_,_,_ in data['categories']:
        k=data['knowledge'].get(slug)
        if k: items.append({'slug':slug,'title':k['title'],'intro':k['intro'],'sections':k['sections']})
    return render_template('facility_knowledge.html', items=items)

@app.route('/facility-knowledge/<slug>')
def facility_knowledge_detail(slug):
    with open(FACILITIES_SEED,'r',encoding='utf-8') as f: data=json.load(f)
    k=data['knowledge'].get(slug)
    if not k: return 'دانشنامه تأسیسات پیدا نشد',404
    return render_template('facility_knowledge_detail.html', knowledge=k, slug=slug)

FACILITY_STANDARD_CODES = {
    'pump': ['API 610','API 674','ISO 9906','NFPA 20'],
    'fan': ['ISO 5801','ASHRAE 62.1','ASHRAE 55','ASHRAE 90.1'],
    'compressor': ['API 617','ISO 8573','ISO 4126','ASHRAE 90.1'],
    'chiller': ['AHRI 550/590','EN 378','IEC 60335-2-40','ASHRAE 90.1'],
    'boiler': ['ISO 4126','ASHRAE 90.1','EN 13445'],
    'hvac': ['ASHRAE 62.1','ASHRAE 55','ASHRAE 90.1','IEC 60335-2-40'],
    'valve': ['ISO 4126','ASME B31.9','ASME B16.5'],
    'heat_exchanger': ['ASME B31.9','ASME B16.5','ISO 4126','EN 13445'],
    'tank': ['EN 13445','API 650','NFPA 22','ISO 12944'],
    'pipe': ['ASME B31.9','ASME B16.5','ASME B16.9','NFPA 24'],
    'fire_fighting': ['NFPA 13','NFPA 20','NFPA 25','NFPA 72','NFPA 22','NFPA 24','EN 12845'],
    'water_treatment': ['ASME B31.9','ASME B16.5','ISO 4126','ISO 12944'],
    'cooling_tower': ['ASHRAE 90.1','ASHRAE 62.1','ASHRAE 55','ISO 12944'],
}

@app.route('/facility-standards')
def facility_standards():
    q=request.args.get('q','').strip()
    category=request.args.get('category','').strip()
    conn=get_db()
    params=[]
    clauses=[]
    if category in FACILITY_STANDARD_CODES:
        placeholders=','.join(['?']*len(FACILITY_STANDARD_CODES[category]))
        clauses.append(f'code IN ({placeholders})')
        params.extend(FACILITY_STANDARD_CODES[category])
    if q:
        clauses.append('(code LIKE ? OR name LIKE ? OR description LIKE ?)')
        params.extend([f'%{q}%']*3)
    where=(' WHERE '+ ' AND '.join(clauses)) if clauses else ''
    rows=conn.execute('SELECT * FROM facility_standards'+where+' ORDER BY id', params).fetchall()
    cat=conn.execute('SELECT * FROM facility_categories WHERE slug=?',(category,)).fetchone() if category else None
    conn.close()
    return render_template('facility_standards.html', rows=rows, search=q, category=cat, category_slug=category)

@app.route('/facility-pump-selection', methods=['GET','POST'])
def facility_pump_selection():
    result = None
    error = None
    if request.method == 'POST':
        try:
            q = float(request.form.get('q', 0))
            head = float(request.form.get('head', 0))
            rho = float(request.form.get('rho', 1000))
            eta = float(request.form.get('eta', 70)) / 100
            npsha = float(request.form.get('npsha', 0))
            npshr = float(request.form.get('npshr', 0))
            if q <= 0 or head <= 0 or rho <= 0 or eta <= 0 or eta > 1:
                raise ValueError()
            # Q is entered in m3/h. Hydraulic power P(kW)=rho*g*(Q/3600)*H/eta.
            power_kw = rho * 9.81 * (q / 3600) * head / eta / 1000
            npsh_margin = npsha - npshr if npsha > 0 and npshr > 0 else None
            if npsh_margin is not None and npsh_margin <= 0:
                verdict = 'نامناسب از نظر NPSH: NPSHA باید از NPSHR بیشتر باشد.'
            elif npsh_margin is not None and npsh_margin < 0.5:
                verdict = 'نیازمند بررسی: حاشیه NPSH کم است و باید شرایط مکش با دیتاشیت سازنده کنترل شود.'
            else:
                verdict = 'از نظر Q/H و توان، این نقطه برای مقایسه پمپ‌ها آماده است؛ منحنی سازنده و BEP را حتماً بررسی کنید.'
            result = {'q': q, 'head': head, 'power': round(power_kw, 2), 'npsh_margin': None if npsh_margin is None else round(npsh_margin, 2), 'verdict': verdict}
        except Exception:
            error = 'همه مقادیر عددی را صحیح و بزرگ‌تر از صفر وارد کنید.'
    return render_template('facility_pump_selection.html', result=result, error=error)

@app.route('/facility-calculations', methods=['GET','POST'])
def facility_calculations():
    result=None; error=None; selected=request.form.get('calc','pump_head') if request.method=='POST' else request.args.get('calc','pump_head')
    try:
        def f(name, default=0.0): return float(request.form.get(name,default))
        if request.method=='POST':
            if selected=='pump_head': result={'label':'هد کل','value':round(f('hstatic')+f('hfriction')+f('hminor')+f('hresidual'),3),'unit':'m'}
            elif selected=='pump_power':
                q=f('q_m3s'); rho=f('rho',1000); h=f('head'); eta=f('eta',0.7)/100
                result={'label':'توان هیدرولیکی/ورودی تقریبی','value':round(rho*9.81*q*h/eta/1000,3),'unit':'kW'}
            elif selected=='pipe_diameter': result={'label':'قطر داخلی تقریبی','value':round(math.sqrt(4*f('q_m3s')/(math.pi*f('velocity')))*1000,2),'unit':'mm'}
            elif selected=='flow_velocity': result={'label':'سرعت جریان','value':round(4*f('q_m3s')/(math.pi*(f('diameter_mm')/1000)**2),3),'unit':'m/s'}
            elif selected=='pressure_drop': result={'label':'افت فشار','value':round(f('friction')*f('length')/(f('diameter')/1000)*(f('rho',1000)*f('velocity')**2/2),2),'unit':'Pa'}
            elif selected=='heat_load': result={'label':'بار حرارتی','value':round(f('mass_flow')*f('cp',4.186)*f('delta_t'),3),'unit':'kW'}
            elif selected=='airflow_ach': result={'label':'دبی هوا','value':round(f('ach')*f('volume')/3600,3),'unit':'m³/s'}
            elif selected=='chiller_tr': result={'label':'ظرفیت چیلر','value':round(f('kw')/3.517,3),'unit':'TR'}
            elif selected=='tank_volume': result={'label':'حجم مخزن','value':round(f('length')*f('width')*f('height'),3),'unit':'m³'}
            elif selected=='water_flow': result={'label':'دبی','value':round(f('m3h')/3.6,3),'unit':'L/s'}
            elif selected=='compressor_air': result={'label':'ظرفیت پیشنهادی کمپرسور','value':round(f('consumption')*(1+f('reserve',20)/100),3),'unit':'m³/min'}
    except Exception as e: error='مقادیر ورودی را بررسی کنید.'
    conn=get_db(); calculators=conn.execute('SELECT * FROM facility_calculators ORDER BY id').fetchall(); conn.close()
    return render_template('facility_calculations.html', calculators=calculators, selected=selected, result=result, error=error)


if __name__=="__main__":

    app.run()
    

