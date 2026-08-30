import json
import os


# ==========================================
# تنظیمات
# ==========================================

OUTPUT_FILE = "database/couplings_data.json"

TARGET_COUNT = 240


# ==========================================
# برندها و سری‌ها
# ==========================================

brands = {

    "KTR": [
        "ROTEX",
        "POLY",
        "RADEX-N",
        "GEARex",
        "MINEX",
        "REVOLEX"
    ],

    "Lovejoy": [
        "L",
        "LF",
        "S-Flex",
        "Jaw",
        "Disc",
        "Grid"
    ],

    "Rexnord": [
        "Falk Steelflex",
        "Falk Wrapflex",
        "Falk Lifelign",
        "Thomas",
        "Omega"
    ],

    "Flender": [
        "N-EUPEX",
        "RUPEX",
        "ARPEX",
        "BIPEX",
        "ELPEX"
    ],

    "Siemens": [
        "N-EUPEX",
        "FLUDEX",
        "ARPEX"
    ],

    "SKF": [
        "Flex",
        "OK",
        "Grid"
    ],

    "Timken": [
        "Flexible",
        "Disc",
        "Gear"
    ],

    "NBK": [
        "MJC",
        "MJT",
        "MKS",
        "MSX",
        "SJC"
    ],

    "Tsubaki": [
        "Disc",
        "Gear",
        "Chain",
        "Flexible"
    ],

    "Renold": [
        "Chain",
        "Gear",
        "Disc",
        "Flexible"
    ]
}


# ==========================================
# انواع کوپلینگ
# ==========================================

coupling_types = [

    ("Jaw", "فکی"),

    ("Elastomeric", "الاستومری"),

    ("Oldham", "اولدهام"),

    ("Disc", "دیسکی"),

    ("Grid", "گرید"),

    ("Gear", "دنده‌ای"),

    ("Chain", "زنجیری"),

    ("Beam", "بیمی"),

    ("Bellows", "بلوزی"),

    ("Flanged", "فلنجی"),

    ("Rigid", "صلب"),

    ("Tyre", "لاستیکی"),

    ("Universal", "چهارشاخ"),

    ("Fluid", "هیدرودینامیکی")

]


# ==========================================
# قطر سوراخ شفت
# ==========================================

bores = [

    "6-10 mm",
    "8-14 mm",
    "10-16 mm",
    "12-20 mm",
    "14-25 mm",
    "16-30 mm",
    "20-35 mm",
    "25-40 mm",
    "30-50 mm",
    "35-55 mm",
    "40-65 mm",
    "45-70 mm",
    "50-80 mm",
    "60-90 mm",
    "70-100 mm",
    "80-120 mm"

]


# ==========================================
# دور مجاز
# ==========================================

max_rpms = [

    750,
    1000,
    1200,
    1500,
    1800,
    2400,
    3000,
    3600,
    4500,
    6000,
    7500,
    10000

]


# ==========================================
# گشتاور نامی
# ==========================================

nominal_torques = [

    5,
    10,
    20,
    30,
    50,
    75,
    100,
    150,
    200,
    300,
    500,
    750,
    1000,
    1500,
    2000,
    3000,
    5000,
    7500,
    10000,
    15000,
    20000

]


# ==========================================
# جنس
# ==========================================

materials = [

    "فولاد",

    "آلیاژ آلومینیوم",

    "چدن",

    "فولاد کربنی",

    "فولاد آلیاژی",

    "استیل",

    "آلومینیوم",

    "پلی‌آمید",

    "لاستیک NBR",

    "پلی‌یورتان"

]


# ==========================================
# کاربرد
# ==========================================

applications = [

    "موتور و پمپ",

    "کمپرسور",

    "فن صنعتی",

    "نوار نقاله",

    "گیربکس",

    "ماشین‌آلات CNC",

    "ماشین‌آلات بسته‌بندی",

    "ماشین‌آلات نساجی",

    "ماشین‌آلات فولاد",

    "ماشین‌آلات معدنی",

    "صنایع سیمان",

    "صنایع غذایی",

    "پمپ‌های سانتریفیوژ",

    "میکسر صنعتی",

    "ماشین‌آلات کاغذ",

    "ماشین‌آلات چوب",

    "تجهیزات انتقال قدرت",

    "خطوط تولید"

]


# ==========================================
# روانکاری
# ==========================================

lubrications = [

    "بدون نیاز به روانکاری",

    "گریس",

    "روغن",

    "روغن صنعتی",

    "گریس EP"

]


# ==========================================
# ساخت رکوردها
# ==========================================

records = []

counter = 1


for brand, series_list in brands.items():

    for series in series_list:

        for variant in range(1, 5):

            if len(records) >= TARGET_COUNT:
                break


            coupling_type, coupling_type_fa = coupling_types[
                counter % len(coupling_types)
            ]


            bore = bores[
                counter % len(bores)
            ]


            max_rpm = max_rpms[
                counter % len(max_rpms)
            ]


            nominal_torque = nominal_torques[
                counter % len(nominal_torques)
            ]


            # گشتاور حداکثر
            max_torque = round(
                nominal_torque * 1.8,
                2
            )


            material = materials[
                counter % len(materials)
            ]


            application = applications[
                counter % len(applications)
            ]


            lubrication = lubrications[
                counter % len(lubrications)
            ]


            name = (

                f"{brand} "

                f"{series} "

                f"{variant:02d}"

            )


            description = (

                f"کوپلینگ {coupling_type_fa} "

                f"برند {brand}، سری {series}. "

                f"مناسب برای انتقال گشتاور بین دو شفت "

                f"با قطر سوراخ {bore}. "

                f"حداکثر سرعت مجاز {max_rpm} RPM "

                f"و گشتاور نامی {nominal_torque} N.m."

            )


            record = {

                "name": name,

                "brand": brand,

                "coupling_type": coupling_type,

                "series": series,

                "bore": bore,

                "max_rpm": max_rpm,

                "nominal_torque": nominal_torque,

                "max_torque": max_torque,

                "material": material,

                "application": application,

                "lubrication": lubrication,

                "description": description

            }


            records.append(record)


            counter += 1


        if len(records) >= TARGET_COUNT:
            break


    if len(records) >= TARGET_COUNT:
        break


# ==========================================
# ایجاد پوشه database
# ==========================================

os.makedirs(

    "database",

    exist_ok=True

)


# ==========================================
# ذخیره JSON
# ==========================================

with open(

    OUTPUT_FILE,

    "w",

    encoding="utf-8"

) as f:

    json.dump(

        records,

        f,

        ensure_ascii=False,

        indent=2

    )


# ==========================================
# نمایش نتیجه
# ==========================================

print()

print("=" * 50)

print(
    f"✅ {len(records)} رکورد کوپلینگ ساخته شد"
)

print(
    f"📁 فایل: {OUTPUT_FILE}"
)

print("=" * 50)

print()
