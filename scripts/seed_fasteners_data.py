import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mi_engineering.settings.dev")
django.setup()

from products.models import Category, Standard, Material, Application

CATEGORIES_DATA = [
    {
        "name": "Bolts and Nuts",
        "description": "High-tensile and stainless steel hexagon head bolts, heavy hex nuts, flange bolts, nylon insert lock nuts, and square bolts manufactured to DIN, ISO, and ASTM standards.",
        "meta_title": "Bolts and Nuts Manufacturer & Supplier | DIN, ISO, ASTM | M.I. Engineering Works",
        "meta_description": "Manufacturer and exporter of industrial bolts and nuts in Mumbai. Hex head bolts, heavy hex nuts, flange bolts in Grade 8.8, 10.9, 12.9, SS304, and SS316.",
        "meta_keywords": "bolts and nuts manufacturer, hex bolts, heavy hex nuts, DIN 933, DIN 934, industrial fasteners Mumbai",
    },
    {
        "name": "Stud Bolts",
        "description": "Continuous-thread stud bolts and double-end studs engineered to ASTM A193 Grade B7, B7M, B8, and B8M for high-temperature and high-pressure flange connections.",
        "meta_title": "ASTM A193 B7 / B7M Stud Bolts Manufacturer | M.I. Engineering Works",
        "meta_description": "Precision ASTM A193 B7, B7M, B8, and B8M stud bolts with ASTM A194 2H nuts for pipeline flanges, pressure vessels, and refinery applications.",
        "meta_keywords": "stud bolts manufacturer, ASTM A193 B7 stud bolts, B7M studs, flange stud bolts, A194 2H nuts India",
    },
    {
        "name": "Screws and Washers",
        "description": "Precision socket head cap screws, countersunk screws, machine screws, flat plain washers (DIN 125), and spring lock washers (DIN 127) for industrial machinery assemblies.",
        "meta_title": "Industrial Screws & Washers | Socket Cap, Flat & Spring Washers | M.I. Engineering",
        "meta_description": "High-precision socket cap screws, machine screws, DIN 125 flat washers, and DIN 127 spring lock washers in stainless steel and high tensile alloy steel.",
        "meta_keywords": "industrial screws, socket head cap screws, DIN 125 flat washers, DIN 127 spring washers, machine screws",
    },
    {
        "name": "Threaded Rods",
        "description": "Full-thread industrial threaded rods (DIN 975 / DIN 976) from M3 to M64 in standard 1m, 2m, and 3m lengths or custom cut-to-size dimensions.",
        "meta_title": "Threaded Rods (M3 to M64) DIN 975 / DIN 976 Manufacturer | M.I. Engineering Works",
        "meta_description": "Full thread tie rods and stud rods in Grade 4.6, 8.8, 10.9, SS 304, and SS 316. Available in 1-meter, 2-meter, 3-meter cut lengths.",
        "meta_keywords": "threaded rods manufacturer, DIN 975 threaded bar, DIN 976 stud rod, all thread rod, M3 to M64 tie rod",
    },
    {
        "name": "Anchor Fasteners",
        "description": "Heavy-duty wedge anchors, chemical capsule anchors, sleeve anchors, and drop-in anchors for concrete, masonry, and structural steel anchoring.",
        "meta_title": "Heavy Duty Anchor Fasteners | Wedge, Chemical & Sleeve Anchors | M.I. Engineering",
        "meta_description": "Industrial concrete anchor bolts, wedge anchors, chemical stud anchors, and expansion fasteners engineered for seismic and heavy structural installations.",
        "meta_keywords": "anchor fasteners manufacturer, wedge anchors, chemical anchors, concrete anchor bolts, expansion anchors",
    },
    {
        "name": "Rivets and Pins",
        "description": "Precision solid rivets, blind pop rivets, hardened dowel pins, taper pins, and split cotter pins for mechanical alignment and permanent joints.",
        "meta_title": "Industrial Rivets and Precision Pins Manufacturer | M.I. Engineering Works",
        "meta_description": "Manufacturer of hardened steel dowel pins, taper pins, split cotter pins, and solid rivets for automotive and machine tool assemblies.",
        "meta_keywords": "industrial rivets, dowel pins, taper pins, split pins, precision mechanical pins Mumbai",
    },
    {
        "name": "Pipe Fittings and Flanges",
        "description": "High-pressure forged pipe fittings, slip-on flanges, weld neck flanges, blind flanges, and socket weld fittings manufactured to ASME B16.5 and B16.11.",
        "meta_title": "Forged Pipe Fittings & Industrial Flanges | ASME B16.5 | M.I. Engineering Works",
        "meta_description": "Precision forged pipe fittings and industrial flanges in carbon steel, stainless steel, and alloy steel for oil, gas, and chemical pipelines.",
        "meta_keywords": "pipe fittings manufacturer, ASME B16.5 flanges, weld neck flange, slip on flange, forged steel fittings",
    },
    {
        "name": "Stainless Steel Fasteners",
        "description": "Corrosion-resistant fasteners in AISI 304, 304L, 316, 316L, 310S, and 321 for marine, chemical, food processing, and architectural applications.",
        "meta_title": "Stainless Steel Fasteners (SS 304, 316, 316L) Manufacturer | M.I. Engineering",
        "meta_description": "High-grade stainless steel fasteners in A2-70 (SS304) and A4-70 / A4-80 (SS316). Marine-grade corrosion resistance with EN 10204 3.1 certification.",
        "meta_keywords": "stainless steel fasteners, SS304 bolts, SS316 fasteners, marine fasteners, A2-70, A4-80 bolts Mumbai",
    },
    {
        "name": "Alloy Steel Fasteners",
        "description": "High-tensile alloy fasteners in Grade 8.8, 10.9, 12.9, ASTM A193 B7/B7M, and ASTM A320 L7 for high-stress and low-temperature engineering service.",
        "meta_title": "Alloy Steel Fasteners (Grade 8.8, 10.9, 12.9, B7) | M.I. Engineering Works",
        "meta_description": "Manufacturer of high tensile alloy steel fasteners, quenched and tempered bolts for structural and heavy machinery applications.",
        "meta_keywords": "alloy steel fasteners, Grade 8.8 bolts, Grade 10.9 bolts, Grade 12.9 screws, high tensile bolts India",
    },
    {
        "name": "Duplex and Super Duplex Fasteners",
        "description": "High-strength, chloride pitting-resistant fasteners in Duplex 2205 (UNS S31803 / S32205) and Super Duplex 2507 (UNS S32750) for offshore oil and gas.",
        "meta_title": "Duplex 2205 & Super Duplex 2507 Fasteners Manufacturer | M.I. Engineering Works",
        "meta_description": "Duplex 2205 and Super Duplex 2507 bolts, nuts, and stud bolts for offshore platforms, desalination plants, and marine chemical tankers.",
        "meta_keywords": "duplex fasteners, super duplex 2507 bolts, 2205 stud bolts, UNS S31803 fasteners, offshore fasteners Mumbai",
    },
    {
        "name": "Inconel and Monel Fasteners",
        "description": "Special nickel alloy fasteners in Inconel 600, 625, 718, Monel 400, and Monel K500 for extreme chemical, aerospace, and marine environments.",
        "meta_title": "Inconel 625/718 & Monel 400 Fasteners Manufacturer | M.I. Engineering Works",
        "meta_description": "Exotic nickel alloy fasteners in Inconel 625, Inconel 718, and Monel 400/K500 designed for extreme temperature, acid, and sea water resistance.",
        "meta_keywords": "Inconel fasteners, Monel 400 bolts, Inconel 625 studs, nickel alloy fasteners, exotic metal fasteners India",
    },
    {
        "name": "Special and Custom Fasteners",
        "description": "Bespoke fasteners and precision turned machine components manufactured strictly to client technical drawings, CAD files, and non-standard thread pitches.",
        "meta_title": "Custom Fasteners & Drawing-Based Machined Components | M.I. Engineering Works",
        "meta_description": "Custom fastener manufacturing in Mumbai. Non-standard sizes, CNC turned parts, custom threading, and specialized head geometries made to drawing.",
        "meta_keywords": "custom fasteners manufacturer, drawing based bolts, CNC turned fasteners, non standard bolts Mumbai",
    },
]

STANDARDS_DATA = [
    {"name": "DIN 933", "description": "Hexagon head bolts with thread up to head (full thread). Metric thread M3 to M64."},
    {"name": "DIN 931", "description": "Hexagon head bolts with shank (partial thread). Metric thread M3 to M64."},
    {"name": "DIN 934", "description": "Hexagon nuts with metric coarse and fine pitch thread, Property Class 8, 10, 12, A2-70, A4-80."},
    {"name": "DIN 975", "description": "Threaded rods, standard length 1000mm, 2000mm, and 3000mm in carbon steel and stainless steel."},
    {"name": "DIN 976", "description": "Threaded stud bolts and tie rods for engineering construction and assembly."},
    {"name": "DIN 125", "description": "Plain washers for normal diameter hexagon bolts and screws without chamfer."},
    {"name": "DIN 127", "description": "Spring lock washers with square or flat ends for anti-vibration bolt locking."},
    {"name": "DIN 912", "description": "Hexagon socket head cap screws (allen bolts) in alloy steel Grade 8.8, 10.9, 12.9 and SS316."},
    {"name": "ASTM A193", "description": "Alloy-steel and stainless steel bolting materials for high-temperature or high-pressure service (Grades B7, B7M, B16, B8, B8M)."},
    {"name": "ASTM A194", "description": "Carbon and alloy steel nuts for bolts for high pressure or high temperature service (Grades 2H, 7, 7M, 8, 8M)."},
    {"name": "ASTM A325", "description": "Structural bolts, steel, heat treated, 120/105 ksi minimum tensile strength for structural steel joints."},
    {"name": "ASTM A490", "description": "High-strength structural steel bolts, 150 ksi minimum tensile strength for heavy civil and building joints."},
    {"name": "ISO 4014", "description": "Hexagon head bolts - Product grades A and B (partially threaded metric)."},
    {"name": "ISO 4017", "description": "Hexagon head screws - Product grades A and B (fully threaded metric)."},
    {"name": "ASME B16.5", "description": "Pipe flanges and flanged fittings: NPS 1/2 through NPS 24 metric/inch standard."},
]

MATERIALS_DATA = [
    {"name": "Stainless Steel 304 (A2-70)", "description": "Standard 18/8 austenitic chrome-nickel stainless steel providing excellent general atmospheric and industrial corrosion resistance."},
    {"name": "Stainless Steel 316 / 316L (A4-70 / A4-80)", "description": "Molybdenum-bearing austenitic stainless steel offering superior pitting resistance against chlorides, acids, and marine seawater."},
    {"name": "High Tensile Alloy Steel Grade 8.8", "description": "Medium carbon quenched and tempered steel with minimum tensile strength of 800 MPa for robust machinery joints."},
    {"name": "High Tensile Alloy Steel Grade 10.9", "description": "High tensile alloy steel with minimum 1040 MPa tensile strength for automotive, structural, and heavy equipment."},
    {"name": "Alloy Steel ASTM A193 B7", "description": "Chromium-molybdenum AISI 4140/4142 quenched and tempered steel for high-temperature pressure piping and heat exchangers."},
    {"name": "Alloy Steel ASTM A193 B7M", "description": "Hardness-controlled (max 235 HB) Cr-Mo steel designed for sour gas NACE MR0175 / ISO 15156 environments."},
    {"name": "Duplex 2205 (UNS S31803 / S32205)", "description": "Austenitic-ferritic duplex stainless steel combining high yield strength with exceptional chloride stress corrosion cracking resistance."},
    {"name": "Super Duplex 2507 (UNS S32750)", "description": "25% chromium super duplex alloy with PREN > 42 for extreme offshore, desalination, and subsea oil & gas operations."},
    {"name": "Inconel 625 / 718", "description": "High-nickel superalloys offering outstanding high-temperature oxidation resistance and extreme cryogenic toughness."},
    {"name": "Monel 400 / K500", "description": "Nickel-copper solid solution alloy with superior immunity to seawater corrosion, marine biofouling, and hydrofluoric acid."},
    {"name": "Mild Steel / Carbon Steel (IS 2062)", "description": "General engineering carbon steel available in zinc-plated, hot-dip galvanized (HDG), and black oxide finishes."},
]

APPLICATIONS_DATA = [
    {"name": "Oil, Gas & Petrochemical Refineries", "description": "High-pressure, sour-service pipeline flanges, heat exchangers, valves, and offshore platform bolting."},
    {"name": "Heavy Machinery & Mechanical Plant", "description": "Quenched & tempered high-tensile fasteners for machine frames, hydraulic presses, gearboxes, and power drives."},
    {"name": "Marine, Shipbuilding & Offshore", "description": "Chloride-resistant SS316, Duplex 2205, and Monel fasteners for hull fixtures, submerged valves, and harbor equipment."},
    {"name": "Power Generation & Renewable Energy", "description": "High-temperature studs, anchor bolts for wind turbines, thermal power boilers, and solar mounting structures."},
    {"name": "Civil Construction & Structural Steel", "description": "ASTM A325/A490 structural bolts, foundation anchor bolts, and threaded tie rods for steel buildings and bridges."},
    {"name": "Chemical & Fertilizer Plants", "description": "Acid and alkali-resistant fastener systems in SS316L, Hastelloy, and Duplex alloys for reactor vessels and pumps."},
]

def seed():
    print("Seeding 12 Categories...")
    for item in CATEGORIES_DATA:
        cat, created = Category.objects.update_or_create(
            name=item["name"],
            defaults={
                "description": item["description"],
                "meta_title": item["meta_title"],
                "meta_description": item["meta_description"],
                "meta_keywords": item["meta_keywords"],
                "is_active": True,
            }
        )
        print(f"  Category: {cat.name} ({'Created' if created else 'Updated'})")

    print("\nSeeding Standards...")
    for item in STANDARDS_DATA:
        std, created = Standard.objects.update_or_create(
            name=item["name"],
            defaults={"description": item["description"]}
        )
        print(f"  Standard: {std.name} ({'Created' if created else 'Updated'})")

    print("\nSeeding Materials...")
    for item in MATERIALS_DATA:
        mat, created = Material.objects.update_or_create(
            name=item["name"],
            defaults={"description": item["description"]}
        )
        print(f"  Material: {mat.name} ({'Created' if created else 'Updated'})")

    print("\nSeeding Applications...")
    for item in APPLICATIONS_DATA:
        app, created = Application.objects.update_or_create(
            name=item["name"],
            defaults={"description": item["description"]}
        )
        print(f"  Application: {app.name} ({'Created' if created else 'Updated'})")

    print("\nDone! All foundational catalog data successfully populated.")

if __name__ == "__main__":
    seed()
