"""Build the bundled SKF-compatible ISO dimension catalogue.
This file generates designation/dimension records from the project's ISO 15/ISO 355 tables.
It intentionally labels boundary dimensions as ISO-standard compatibility data; SKF suffixes/options
remain designation-specific and should be verified against the current SKF catalogue for load/speed ratings.
"""
import ast, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEED = ROOT / 'seed_bearing_standards.py'
OUT = pathlib.Path(__file__).resolve().parent / 'bearings_data.json'

src = ast.parse(SEED.read_text(encoding='utf-8'))
tables = {}
for node in src.body:
    if isinstance(node, ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0], ast.Name):
        name=node.targets[0].id
        if name in {'deep_groove','angular','cylindrical','tapered'}:
            tables[name]=ast.literal_eval(node.value)

existing=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else []
# Preserve non-SKF brands and use existing SKF records as a source for spherical/pillow families.
non_skf=[x for x in existing if x.get('brand')!='SKF']
base={x['name']:x for x in existing if x.get('brand')=='SKF'}

def rec(code,d,D,B,btype,series,seal='Open',clearance='Normal'):
    return {
      'name':f'SKF {code}', 'brand':'SKF','bearing_type':btype,'series':series,
      'bore':f'{d} mm','outer_diameter':f'{D} mm','width':f'{B} mm',
      'dynamic_load':'طبق کاتالوگ SKF','static_load':'طبق کاتالوگ SKF','max_rpm':'طبق کاتالوگ SKF',
      'clearance':clearance,'seal':seal,'lubrication':'طبق نوع و شرایط کاربرد',
      'applications':'Motor,Pump,Fan,Gearbox,Industrial Machine',
      'failures':'Heat,Vibration,Wear,Contamination',
      'equivalent':'SKF / ISO boundary dimensions'
    }

catalog=[]
# Deep-groove: full ISO dimension rows + common designation variants.
for code,(d,D,B) in tables['deep_groove'].items():
    series=code[:2]
    for suffix,seal,clr in [('', 'Open','Normal'),('-2RS1','2RS1','Normal'),('-2Z','2Z','Normal'),('/C3','Open','C3')]:
        item=rec(code+suffix,d,D,B,'بلبرینگ شیار عمیق',series,seal,clr)
        catalog.append(item)
# Angular contact
for code,(d,D,B) in tables['angular'].items():
    catalog.append(rec(code,d,D,B,'بلبرینگ تماس زاویه‌ای',code[:2]))
# Cylindrical NU/NJ + NUP compatibility dimensions
for code,(d,D,B) in tables['cylindrical'].items():
    prefix=''.join(c for c in code if c.isalpha())
    suffix=''.join(c for c in code if c.isdigit())
    for p in ([prefix] if prefix not in {'NU','NJ'} else ['NU','NJ','NUP']):
        catalog.append(rec(p+suffix,d,D,B,'رولبرینگ استوانه‌ای',p))
# Tapered
for code,(d,D,B) in tables['tapered'].items():
    catalog.append(rec(code,d,D,B,'رولبرینگ مخروطی',code[:3]))

# Keep existing SKF families not represented by the ISO seed (e.g. spherical roller / pillow block),
# but normalize duplicates by designation.
for x in existing:
    if x.get('brand')=='SKF' and x['name'] not in {r['name'] for r in catalog}:
        catalog.append(x)

# Deduplicate by name and sort by family/series/bore/designation.
unique={x['name']:x for x in catalog}
def key(x):
    try: bore=float(str(x.get('bore','')).split()[0])
    except: bore=999999
    return (x.get('bearing_type',''),x.get('series',''),bore,x['name'])
skf=sorted(unique.values(),key=key)
OUT.write_text(json.dumps(skf+non_skf,ensure_ascii=False,indent=2),encoding='utf-8')
print('SKF records:',len(skf),'Total:',len(skf)+len(non_skf))
