import sqlite3
from pathlib import Path


DB_NAME = "mechassist.db"


# حذف دیتابیس قبلی (اختیاری)
if Path(DB_NAME).exists():
    Path(DB_NAME).unlink()


conn = sqlite3.connect(DB_NAME)

cursor = conn.cursor()


# ==========================
# جدول دسته بندی
# ==========================

cursor.execute("""
CREATE TABLE categories(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT NOT NULL,

name_fa TEXT NOT NULL

)
""")


# ==========================
# تجهیزات
# ==========================

cursor.execute("""
CREATE TABLE equipment(

id INTEGER PRIMARY KEY AUTOINCREMENT,

category_id INTEGER,

name TEXT NOT NULL,

brand TEXT,

description TEXT,

FOREIGN KEY(category_id)
REFERENCES categories(id)

)
""")


# ==========================
# مشخصات فنی
# ==========================

cursor.execute("""
CREATE TABLE specifications(

id INTEGER PRIMARY KEY AUTOINCREMENT,

equipment_id INTEGER,

parameter TEXT,

value TEXT,

unit TEXT,


FOREIGN KEY(equipment_id)
REFERENCES equipment(id)

)
""")


# ==========================
# خرابی ها
# ==========================

cursor.execute("""
CREATE TABLE failures(

id INTEGER PRIMARY KEY AUTOINCREMENT,

equipment_id INTEGER,

symptom TEXT,

cause TEXT,

solution TEXT,


FOREIGN KEY(equipment_id)
REFERENCES equipment(id)

)
""")


# ==========================
# جایگزین ها
# ==========================

cursor.execute("""
CREATE TABLE alternatives(

id INTEGER PRIMARY KEY AUTOINCREMENT,

equipment_id INTEGER,

alternative_name TEXT,

brand TEXT,


FOREIGN KEY(equipment_id)
REFERENCES equipment(id)

)
""")


# ==========================
# فرمول ها
# ==========================

cursor.execute("""
CREATE TABLE calculations(

id INTEGER PRIMARY KEY AUTOINCREMENT,

title TEXT,

formula TEXT,

description TEXT

)
""")


# ====================================
# دسته بندی ها
# ====================================

categories = [

("Bearing","برینگ و یاتاقان"),

("Gearbox","گیربکس"),

("Coupling","کوپلینگ"),

("Pump","پمپ"),

("Motor","موتور"),

("Hydraulic","هیدرولیک"),

("Pneumatic","پنوماتیک"),

("Seal","آب بند"),

("Valve","شیر صنعتی"),

("Compressor","کمپرسور")

]


cursor.executemany(
"""
INSERT INTO categories
(name,name_fa)

VALUES (?,?)
""",
categories
)



# ====================================
# تجهیزات
# ====================================


equipment = [

(1,
"SKF 6205 Deep Groove Bearing",
"SKF",
"بلبرینگ شیار عمیق پرکاربرد صنعتی"),


(1,
"SKF 6308 Bearing",
"SKF",
"برینگ مناسب بارهای متوسط"),


(2,
"Worm Gearbox",
"Bonfiglioli",
"گیربکس حلزونی صنعتی"),


(2,
"Helical Gearbox",
"SEW",
"گیربکس هلیکال صنعتی"),


(3,
"ROTEX Coupling",
"KTR",
"کوپلینگ انعطاف پذیر"),


(4,
"Centrifugal Pump",
"Grundfos",
"پمپ سانتریفیوژ صنعتی"),


(5,
"Three Phase Motor",
"Siemens",
"موتور القایی سه فاز")

]


cursor.executemany(
"""
INSERT INTO equipment
(category_id,name,brand,description)

VALUES (?,?,?,?)

""",
equipment
)



# ====================================
# مشخصات فنی
# ====================================


specifications = [

(1,"قطر داخلی","25","mm"),

(1,"قطر خارجی","52","mm"),

(1,"عرض","15","mm"),

(1,"حداکثر دور","12000","RPM"),


(2,"قطر داخلی","40","mm"),

(2,"حداکثر بار","29","kN"),


(3,"نسبت تبدیل","20:1",""),

(3,"روغن پیشنهادی","ISO VG 220",""),


(5,"گشتاور","250","Nm"),


(7,"توان","5.5","KW"),

(7,"دور موتور","1450","RPM")

]


cursor.executemany(

"""
INSERT INTO specifications

(equipment_id,parameter,value,unit)

VALUES (?,?,?,?)

""",

specifications

)



# ====================================
# خرابی ها
# ====================================


failures = [

(1,
"افزایش دما",

"کمبود گریس، بار زیاد، خرابی مسیر غلتش",

"بررسی روانکاری و تعویض برینگ"),


(1,
"لرزش",

"عدم بالانس، خرابی ساچمه",

"آنالیز ارتعاش انجام شود"),


(3,
"داغ شدن گیربکس",

"روغن نامناسب یا اضافه بار",

"بررسی روغن و شرایط کاری"),


(5,
"ضربه هنگام حرکت",

"خرابی لاستیک کوپلینگ",

"تعویض المان کوپلینگ"),


(6,
"کاهش فشار پمپ",

"هوا گرفتن یا سایش پروانه",

"بررسی مکش و پروانه")

]


cursor.executemany(

"""
INSERT INTO failures

(equipment_id,symptom,cause,solution)

VALUES (?,?,?,?)

""",

failures

)



# ====================================
# قطعات جایگزین
# ====================================


alternatives=[

(1,"6205","FAG"),

(1,"6205","NSK"),

(1,"6205","NTN"),

(2,"6308","SKF"),

(3,"Worm Gearbox 20:1","SEW")

]


cursor.executemany(

"""
INSERT INTO alternatives

(equipment_id,alternative_name,brand)

VALUES (?,?,?)

""",

alternatives

)



# ====================================
# فرمول های مهندسی
# ====================================


calculations=[


(
"توان مکانیکی",

"P=T×RPM/9550",

"محاسبه توان بر اساس گشتاور و دور"
),


(
"عمر برینگ",

"L10=(C/P)^3",

"محاسبه عمر تئوری برینگ"
),


(
"سرعت محیطی",

"V=πDN/60",

"سرعت خطی شفت"
)


]


cursor.executemany(

"""
INSERT INTO calculations

(title,formula,description)

VALUES (?,?,?)

""",

calculations

)






print("✅ Database created successfully:")
print(DB_NAME)

cursor.execute("""
CREATE TABLE IF NOT EXISTS bearings
(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT,

brand TEXT,

bearing_type TEXT,

series TEXT,


bore TEXT,

outer_diameter TEXT,

width TEXT,


dynamic_load TEXT,

static_load TEXT,


max_rpm TEXT,


clearance TEXT,

seal TEXT,


lubrication TEXT,


applications TEXT,


failures TEXT,


equivalent TEXT

)

""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS gearboxes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    brand TEXT,

    gearbox_type TEXT,

    series TEXT,

    ratio TEXT,

    power TEXT,

    input_speed TEXT,

    output_speed TEXT,

    torque TEXT,

    application TEXT,

    lubrication TEXT,

    description TEXT

)
""")


conn.commit()

conn.close()
