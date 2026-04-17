#!/usr/bin/env python3
"""
Generate 2000 sample planning records for testing
Creates realistic SAP planning data with all required fields
"""

import csv
from datetime import datetime, timedelta
import random

# Configuration
OUTPUT_FILE = "sample_data/planning_data_10000_records.csv"
NUM_RECORDS = 10000

# Data pools
LOCATIONS = [
    "CYS20_F01C01", "CYS20_F01C02", "CYS20_F02C01", "CYS20_F02C02",
    "DAL_F02C01", "DAL_F02C02", "DAL_F03C01", "DAL_F03C02",
    "HOU_F03C01", "HOU_F03C02", "HOU_F04C01", "HOU_F04C02",
    "PHX_F04C01", "PHX_F04C02", "PHX_F05C01", "PHX_F05C02",
    "LAX_F05C01", "LAX_F05C02", "LAX_F06C01", "LAX_F06C02",
    "CHI_F06C01", "CHI_F06C02", "CHI_F07C01", "CHI_F07C02",
    "ATL_F07C01", "ATL_F07C02", "ATL_F08C01", "ATL_F08C02",
    "BOS_F08C01", "BOS_F08C02", "BOS_F09C01", "BOS_F09C02"
]

MATERIALS = [
    "ACC", "BAT", "CAP", "DIO", "ELE", "FIL", "GAS", "HEA",
    "IND", "JUN", "KEY", "LED", "MOT", "NUT", "OIL", "PAD",
    "QUA", "RES", "SEN", "TRA", "UPS", "VAL", "WIR", "XFM",
    "YOK", "ZEN", "AMP", "BRK", "CIR", "DRV"
]

EQUIPMENT_CATEGORIES = ["UPS", "Mechanical", "Hydraulic", "Pneumatic", "Electronics"]

SUPPLIERS = [
    "10_AMER", "130_AMER", "1690_AMER", "210_AMER", "320_AMER",
    "410_AMER", "520_AMER", "630_AMER", "740_AMER", "850_AMER",
    "960_AMER", "1070_AMER", "1180_AMER", "1290_AMER", "1400_AMER"
]

SUPPLIER_NAMES = [
    "Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E",
    "Supplier F", "Supplier G", "Supplier H", "Supplier I", "Supplier J",
    "Supplier K", "Supplier L", "Supplier M", "Supplier N", "Supplier O"
]

DC_SITES = ["DC01", "DC02", "DC03", "DC04", "DC05", "DC06", "DC07", "DC08", "DC09", "DC10"]

METROS = ["NYC", "DAL", "HOU", "PHX", "LAX", "CHI", "ATL", "BOS", "DEN", "SEA"]

BOD_VERSIONS = ["1.0", "1.5", "2.0", "2.5", "3.0"]

FORM_FACTORS = ["Standard", "Compact", "Extended", "Mini", "Modular"]

CHANGE_TYPES = ["SHIFT", "ACCELERATION", "DELAY", "NONE"]

APPROVAL_VALUES = ["APPROVED", "PENDING", "REJECTED", "DRAFT"]

def generate_date(base_date, days_offset_range):
    """Generate a date with random offset"""
    offset = random.randint(days_offset_range[0], days_offset_range[1])
    return (base_date + timedelta(days=offset)).strftime("%Y-%m-%d")

def generate_record(record_id):
    """Generate a single planning record"""
    base_date = datetime(2026, 4, 1)
    
    location = random.choice(LOCATIONS)
    material = random.choice(MATERIALS)
    equipment_cat = random.choice(EQUIPMENT_CATEGORIES)
    supplier = random.choice(SUPPLIERS)
    supplier_name = random.choice(SUPPLIER_NAMES)
    dc_site = random.choice(DC_SITES)
    metro = random.choice(METROS)
    
    # Forecast quantities
    prev_qty = random.randint(300, 1500)
    qty_change = random.randint(-300, 500)
    curr_qty = max(100, prev_qty + qty_change)
    
    # ROJ dates
    prev_roj_offset = random.randint(30, 60)
    curr_roj_offset = prev_roj_offset + random.randint(-10, 10)
    prev_roj = (base_date + timedelta(days=prev_roj_offset)).strftime("%Y-%m-%d")
    curr_roj = (base_date + timedelta(days=curr_roj_offset)).strftime("%Y-%m-%d")
    roj_delta = curr_roj_offset - prev_roj_offset
    
    # Supplier dates
    prev_supp_date = generate_date(base_date, [-5, 0])
    curr_supp_date = generate_date(base_date, [0, 5])
    
    # Design versions
    bod_version = random.choice(BOD_VERSIONS)
    form_factor = random.choice(FORM_FACTORS)
    
    # Change flags
    qty_changed = 1 if qty_change != 0 else 0
    design_changed = random.randint(0, 1)
    roj_changed = 1 if roj_delta != 0 else 0
    supplier_changed = random.randint(0, 1)
    is_new_demand = random.randint(0, 1) if random.random() < 0.05 else 0
    is_cancelled = random.randint(0, 1) if random.random() < 0.02 else 0
    is_supplier_date_missing = random.randint(0, 1) if random.random() < 0.03 else 0
    risk_flag = 1 if (design_changed or qty_changed or supplier_changed) else 0
    
    change_type = random.choice(CHANGE_TYPES)
    
    return {
        'SCNID': record_id,
        'LOCID': location,
        'PRDID': material,
        'GSCEQUIPCAT': equipment_cat,
        'LOCFR': supplier,
        'GSCPREVFCSTQTY': prev_qty,
        'GSCFSCTQTY': curr_qty,
        'GSCPREVROJNBD': prev_roj,
        'GSCCONROJDATE': curr_roj,
        'GSCPREVSUPLDATE': prev_supp_date,
        'GSCSUPLDATE': curr_supp_date,
        'ZCOIBODVERZ': bod_version,
        'ZCOIFORMFACTZ': form_factor,
        'ZCOICIDZ': dc_site,
        'ZCOIMETROIDZ': metro,
        'ZCOICOUNTRY': 'US',
        'LOCFRDESCR': supplier_name,
        'GSCPLANNINGEXCEPTIONZ': 'NONE' if random.random() > 0.1 else 'EXCEPTION',
        'GSCROJDATEREASONCODEZ': 'DEMAND_CHANGE' if roj_changed else 'NONE',
        'GSCDATASTEWARDNOTESZ': 'Verified',
        'GSCPLNRVWNOTESZ': 'Reviewed',
        'GSCROJNBDLASTCHANGEDDATE': generate_date(base_date, [0, 10]),
        'GSCSCPBODVERSIONZ': bod_version,
        'GSCSENDFCSTSCPFIRSTPUBLISHDATEZ': generate_date(base_date, [-30, 0]),
        'GSCTRACKLASTPUBLISHDATEZ': generate_date(base_date, [0, 10]),
        'GSCSENDFCSTSCPLASTREMOVEDDATEZ': generate_date(base_date, [-5, 0]),
        'GSCSCPFORMFACTORZ': form_factor,
        'GSCSENDFCSTSCPLASTCHANGEDDATEZ': generate_date(base_date, [0, 10]),
        'GSCCMAPPROVALFIRSTDATEZ': generate_date(base_date, [-30, 0]),
        'GSCCMAPPROVALLASTCHANGEDDATEZ': generate_date(base_date, [0, 10]),
        'GSCCMAPPROVALLASTCHANGEDVALUEZ': random.choice(APPROVAL_VALUES),
        'TINVALID': 0,
        'GSCROJNBDCREATIONDATE': generate_date(base_date, [-30, 0]),
        'LASTMODIFIEDBY': 'USER001',
        'LASTMODIFIEDDATE': generate_date(base_date, [0, 10]),
        'CREATEDBY': 'USER001',
        'CREATEDDATE': generate_date(base_date, [-30, 0]),
        '#Version': 1,
        'ROC': 'AMER',
        'NBD_Change Type': change_type,
        'NBD_DeltaDays': roj_delta,
        'FCST_Delta Qty': qty_change,
        'Is_New Demand': is_new_demand,
        'Is_cancelled': is_cancelled,
        'Is_SupplierDateMissing': is_supplier_date_missing,
        'Risk_Flag': risk_flag
    }

def main():
    """Generate and write CSV file"""
    print(f"Generating {NUM_RECORDS} planning records...")
    
    # Define CSV headers
    headers = [
        'SCNID', 'LOCID', 'PRDID', 'GSCEQUIPCAT', 'LOCFR', 'GSCPREVFCSTQTY', 'GSCFSCTQTY',
        'GSCPREVROJNBD', 'GSCCONROJDATE', 'GSCPREVSUPLDATE', 'GSCSUPLDATE', 'ZCOIBODVERZ',
        'ZCOIFORMFACTZ', 'ZCOICIDZ', 'ZCOIMETROIDZ', 'ZCOICOUNTRY', 'LOCFRDESCR',
        'GSCPLANNINGEXCEPTIONZ', 'GSCROJDATEREASONCODEZ', 'GSCDATASTEWARDNOTESZ',
        'GSCPLNRVWNOTESZ', 'GSCROJNBDLASTCHANGEDDATE', 'GSCSCPBODVERSIONZ',
        'GSCSENDFCSTSCPFIRSTPUBLISHDATEZ', 'GSCTRACKLASTPUBLISHDATEZ',
        'GSCSENDFCSTSCPLASTREMOVEDDATEZ', 'GSCSCPFORMFACTORZ', 'GSCSENDFCSTSCPLASTCHANGEDDATEZ',
        'GSCCMAPPROVALFIRSTDATEZ', 'GSCCMAPPROVALLASTCHANGEDDATEZ', 'GSCCMAPPROVALLASTCHANGEDVALUEZ',
        'TINVALID', 'GSCROJNBDCREATIONDATE', 'LASTMODIFIEDBY', 'LASTMODIFIEDDATE',
        'CREATEDBY', 'CREATEDDATE', '#Version', 'ROC', 'NBD_Change Type', 'NBD_DeltaDays',
        'FCST_Delta Qty', 'Is_New Demand', 'Is_cancelled', 'Is_SupplierDateMissing', 'Risk_Flag'
    ]
    
    # Generate and write records
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for i in range(1, NUM_RECORDS + 1):
            record = generate_record(i)
            writer.writerow(record)
            
            if i % 100 == 0:
                print(f"  Generated {i}/{NUM_RECORDS} records...")
    
    print(f"\n✅ Successfully generated {NUM_RECORDS} records")
    print(f"📁 File saved to: {OUTPUT_FILE}")
    print(f"📊 File size: {get_file_size(OUTPUT_FILE)}")

def get_file_size(filepath):
    """Get file size in human-readable format"""
    import os
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

if __name__ == "__main__":
    main()
