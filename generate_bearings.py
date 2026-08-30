import json


brands = [
    "SKF",
    "FAG",
    "NSK",
    "NTN"
]


bearings = []


# -------------------------
# Deep Groove Ball Bearings
# -------------------------

ball_series = [

("6000",10,26,8),
("6001",12,28,8),
("6002",15,32,9),
("6003",17,35,10),
("6004",20,42,12),
("6005",25,47,12),
("6006",30,55,13),
("6007",35,62,14),
("6008",40,68,15),
("6009",45,75,16),

("6200",10,30,9),
("6201",12,32,10),
("6202",15,35,11),
("6203",17,40,12),
("6204",20,47,14),
("6205",25,52,15),
("6206",30,62,16),
("6207",35,72,17),
("6208",40,80,18),
("6209",45,85,19),
("6210",50,90,20),

("6305",25,62,17),
("6306",30,72,19),
("6307",35,80,21),
("6308",40,90,23),
("6309",45,100,25),
("6310",50,110,27),

("6405",25,80,21),
("6406",30,90,23),
("6407",35,100,25),
("6408",40,110,27)

]


for brand in brands:

    for code,d,D,B in ball_series:

        bearings.append({

            "name":f"{brand} {code}-2RS",

            "brand":brand,

            "bearing_type":
            "Deep Groove Ball Bearing",

            "series":code[:2]+"00",

            "bore":f"{d} mm",

            "outer_diameter":f"{D} mm",

            "width":f"{B} mm",

            "dynamic_load":"Standard",

            "static_load":"Standard",

            "max_rpm":"8000-15000 RPM",

            "clearance":"C3",

            "seal":"2RS",

            "lubrication":"Grease",

            "applications":
            "Motor,Pump,Fan,Gearbox",

            "failures":
            "Heat,Vibration,Wear",

            "equivalent":
            "SKF/FAG/NSK/NTN"

        })



# -------------------------
# Cylindrical Roller Bearings
# -------------------------

roller_series = [

"NU205",
"NU206",
"NU207",
"NU208",
"NU209",
"NU210",

"NJ205",
"NJ206",
"NJ207",
"NJ208",
"NJ209",
"NJ210",

"NUP205",
"NUP206",
"NUP207",
"NUP208"

]


for brand in brands:

    for model in roller_series:

        bearings.append({

        "name":f"{brand} {model}",

        "brand":brand,

        "bearing_type":
        "Cylindrical Roller Bearing",

        "series":model[:2],

        "bore":"Standard",

        "outer_diameter":"Standard",

        "width":"Standard",

        "dynamic_load":"High",

        "static_load":"High",

        "max_rpm":"6000 RPM",

        "clearance":"C3",

        "seal":"Open",

        "lubrication":"Oil",

        "applications":
        "Gearbox,Compressor,Industrial Machine",

        "failures":
        "Roller Wear,Overload",

        "equivalent":
        "SKF/FAG/NSK/NTN"

        })



# -------------------------
# Spherical Roller Bearings
# -------------------------

spherical=[

"22205",
"22206",
"22207",
"22208",
"22209",
"22210",
"22305",
"22306",
"22307",
"22308"

]


for brand in brands:

    for model in spherical:

        bearings.append({

        "name":f"{brand} {model}",

        "brand":brand,

        "bearing_type":
        "Spherical Roller Bearing",

        "series":
        model[:3],

        "bore":"Standard",

        "outer_diameter":"Standard",

        "width":"Standard",

        "dynamic_load":"Very High",

        "static_load":"Very High",

        "max_rpm":"3000 RPM",

        "clearance":"C3",

        "seal":"Open",

        "lubrication":"Grease",

        "applications":
        "Crusher,Conveyor,Heavy Machinery",

        "failures":
        "Misalignment,Fatigue",

        "equivalent":
        "SKF/FAG/NSK/NTN"

        })



# -------------------------
# Tapered Roller Bearings
# -------------------------

tapered=[

"30205",
"30206",
"30207",
"30208",
"30209",
"30305",
"30306",
"30307",
"30308"

]


for brand in brands:

    for model in tapered:

        bearings.append({

        "name":f"{brand} {model}",

        "brand":brand,

        "bearing_type":
        "Tapered Roller Bearing",

        "series":
        model[:3],

        "bore":"Standard",

        "outer_diameter":"Standard",

        "width":"Standard",

        "dynamic_load":"High",

        "static_load":"High",

        "max_rpm":"4000 RPM",

        "clearance":"Normal",

        "seal":"Open",

        "lubrication":"Grease",

        "applications":
        "Gearbox,Vehicle,Machine",

        "failures":
        "Wear,Overload",

        "equivalent":
        "SKF/FAG/NSK/NTN"

        })



# -------------------------
# Pillow Block
# -------------------------

uc_models=[

"UCP205",
"UCP206",
"UCP207",
"UCP208",
"UCF205",
"UCF206",
"UCF207"

]


for brand in brands:

    for model in uc_models:

        bearings.append({

        "name":f"{brand} {model}",

        "brand":brand,

        "bearing_type":
        "Pillow Block Bearing",

        "series":"UC",

        "bore":"Standard",

        "outer_diameter":"Housing",

        "width":"Standard",

        "dynamic_load":"Medium",

        "static_load":"Medium",

        "max_rpm":"5000 RPM",

        "clearance":"Normal",

        "seal":"Rubber",

        "lubrication":"Grease",

        "applications":
        "Conveyor,Fan,Machinery",

        "failures":
        "Looseness,Wear",

        "equivalent":
        "SKF/FAG/NSK/NTN"

        })



with open(
"database/bearings_data.json",
"w",
encoding="utf-8"
) as f:

    json.dump(
        bearings,
        f,
        indent=4,
        ensure_ascii=False
    )



print(
len(bearings),
"bearing records created"
)
