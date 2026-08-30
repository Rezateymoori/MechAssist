import json
import os

# ==========================================
# تنظیمات
# ==========================================

OUTPUT_FILE = "database/gearboxes_data.json"

TARGET_COUNT = 220


# ==========================================
# برندها و سری‌ها
# ==========================================

brands = {
    "SEW-Eurodrive": [
        "R", "F", "K", "S", "W", "X"
    ],

    "Bonfiglioli": [
        "C", "A", "F", "VF", "W", "S"
    ],

    "NORD": [
        "NORDBLOC", "UNICASE", "SK", "MAXXDRIVE"
    ],

    "Motovario": [
        "H", "B", "S", "NMRV", "SW"
    ],

    "Siemens": [
        "SIMOGEAR", "FLENDER"
    ],

    "Sumitomo": [
        "Cyclo", "Hansen", "Bevel"
    ],

    "Flender": [
        "K", "B", "F", "H"
    ],

    "Lenze": [
        "g500", "m550", "GST"
    ],

    "Rossi": [
        "MR", "G", "EP"
    ],

    "David Brown": [
        "H", "C", "K"
    ]
}


# ==========================================
# انواع گیربکس
# ==========================================

gearbox_types = [
    ("Helical", "هلیکال"),
    ("Worm", "حلزونی"),
    ("Helical Bevel", "هلیکال-بویل"),
    ("Bevel", "مخروطی"),
    ("Planetary", "سیاره‌ای"),
    ("Shaft Mounted", "شفت‌نصب"),
    ("Right Angle", "زاویه‌دار"),
    ("Inline", "کواکسیال")
]


# ==========================================
# کاربردها
# ==========================================

applications = [

    "نوار نقاله",

    "پمپ صنعتی",

    "فن صنعتی",

    "میکسر",

    "ماشین‌آلات بسته‌بندی",

    "ماشین‌آلات معدنی",

    "خط تولید",

    "بالابر",

    "ماشین‌آلات فولاد",

    "صنایع غذایی",

    "کمپرسور",

    "سیستم انتقال مواد",

    "ماشین‌آلات سیمان",

    "ماشین‌آلات کاغذ",

    "ماشین‌آلات نساجی",

    "جرثقیل صنعتی",

    "آسیاب صنعتی",

    "خردکن صنعتی",

    "اکسترودر",

    "ماشین‌آلات کشاورزی"
]


# ==========================================
# روانکاری
# ==========================================

lubrications = [

    "روغن صنعتی",

    "روغن دنده EP",

    "روغن سنتتیک",

    "گریس صنعتی"

]


# ==========================================
# نسبت تبدیل
# ==========================================

ratios = [

    3,
    4,
    5,
    6,
    7.5,
    10,
    12.5,
    15,
    20,
    25,
    30,
    40,
    50,
    60,
    80,
    100,
    120
]


# ==========================================
# توان
# ==========================================

powers = [

    0.18,
    0.25,
    0.37,
    0.55,
    0.75,
    1.1,
    1.5,
    2.2,
    3,
    4,
    5.5,
    7.5,
    11,
    15,
    18.5,
    22,
    30,
    37,
    45,
    55,
    75,
    90
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

            gearbox_type, gearbox_type_fa = gearbox_types[
                counter % len(gearbox_types)
            ]

            ratio = ratios[
                counter % len(ratios)
            ]

            power = powers[
                counter % len(powers)
            ]

            # سرعت ورودی
            if power <= 15:
                input_speed = 1500

            elif power <= 45:
                input_speed = 1000

            else:
                input_speed = 750


            # سرعت خروجی
            output_speed = round(
                input_speed / ratio,
                2
            )


            # گشتاور تقریبی
            torque = round(
                (9550 * power / input_speed)
                * ratio
                * 0.94,
                2
            )


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
                f"گیربکس {gearbox_type_fa} صنعتی "
                f"برند {brand}، سری {series}، "
                f"با نسبت تبدیل {ratio}:1 و توان "
                f"{power} kW. مناسب برای "
                f"{application}."
            )


            record = {

                "name": name,

                "brand": brand,

                "gearbox_type": gearbox_type,

                "series": series,

                "ratio": ratio,

                "power": power,

                "input_speed": input_speed,

                "output_speed": output_speed,

                "torque": torque,

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
# نتیجه
# ==========================================

print()
print("=" * 45)

print(
    f"✅ {len(records)} رکورد گیربکس ساخته شد"
)

print(
    f"📁 فایل: {OUTPUT_FILE}"
)

print("=" * 45)
