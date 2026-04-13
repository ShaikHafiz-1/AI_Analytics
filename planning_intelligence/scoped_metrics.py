"""
Scoped metrics computation for Planning Intelligence Copilot.

Key Principle: COMPUTE FIRST → FILTER SECOND → GENERATE LAST

This module ensures that:
1. Deltas are computed at record level (qtyDelta, rojDelta, etc.)
2. Change flags are computed AFTER filtering (not before)
3. Aggregates are computed on filtered data only
4. No global leakage into scoped queries
"""

from typing import Optional, List, Dict, Tuple
import logging


def normalize_location_id(location_id: str) -> str:
    """Normalize location ID for consistent comparison.
    
    Handles location code variations:
    - DSM18_F01C010 -> DSM18_F01C01 (removes trailing zeros)
    - Case-insensitive comparison
    """
    if not location_id:
        return ""
    normalized = location_id.upper().strip()
    # Remove trailing zeros from numeric parts but keep at least one digit
    parts = normalized.split('_')
    normalized_parts = []
    for part in parts:
        if part and part[-1].isdigit():
            # Remove trailing zeros but keep at least one
            part = part.rstrip('0') or '0'
        normalized_parts.append(part)
    return '_'.join(normalized_parts)


def compute_scoped_metrics(
    records: List[Dict],
    location_id: Optional[str] = None,
    supplier: Optional[str] = None,
    material_group: Optional[str] = None,
    change_type: Optional[str] = None
) -> Dict:
    """
    Compute metrics for a scoped set of records.
    
    Process:
    1. Filter records by provided scope (location, supplier, material, change_type)
    2. Compute change flags on filtered data
    3. Aggregate metrics
    
    Args:
        records: List of normalized records
        location_id: Filter by location (e.g., "CYS20_F01C01")
        supplier: Filter by supplier (e.g., "9999_AMER")
        material_group: Filter by material group (e.g., "LVS")
        change_type: Filter by change type ("design", "supplier", "quantity", "schedule")
    
    Returns:
        Dict with scoped metrics
    """
    # Step 1: Filter records
    filtered = records
    
    if location_id:
        normalized_target = normalize_location_id(location_id)
        filtered = [r for r in filtered if normalize_location_id(r.get("locationId", "")) == normalized_target]
    
    if supplier:
        filtered = [r for r in filtered if r.get("supplier") == supplier]
    
    if material_group:
        filtered = [r for r in filtered if r.get("materialGroup") == material_group]
    
    # Step 2: Compute change flags on filtered data
    total_records = len(filtered)
    
    # Count records with each type of change
    qty_changed_count = sum(1 for r in filtered if r.get("qtyChanged", False))
    supplier_changed_count = sum(1 for r in filtered if r.get("supplierChanged", False))
    design_changed_count = sum(1 for r in filtered if r.get("designChanged", False))
    roj_changed_count = sum(1 for r in filtered if r.get("rojChanged", False))
    
    # Any change
    any_changed_count = sum(1 for r in filtered if r.get("changed", False))
    
    # Step 3: Compute aggregates
    qty_deltas = [r.get("qtyDelta", 0) for r in filtered if r.get("qtyDelta") is not None]
    total_qty_delta = sum(qty_deltas)
    avg_qty_delta = total_qty_delta / len(qty_deltas) if qty_deltas else 0
    
    roj_deltas = [r.get("rojDelta", 0) for r in filtered if r.get("rojDelta") is not None]
    total_roj_delta = sum(roj_deltas)
    avg_roj_delta = total_roj_delta / len(roj_deltas) if roj_deltas else 0
    
    # Compute change rate
    change_rate = (any_changed_count / total_records * 100) if total_records > 0 else 0
    
    # Get unique entities
    unique_suppliers = set(r.get("supplier") for r in filtered if r.get("supplier"))
    unique_materials = set(r.get("materialGroup") for r in filtered if r.get("materialGroup"))
    unique_locations = set(r.get("locationId") for r in filtered if r.get("locationId"))
    
    # Get top affected suppliers/materials
    supplier_impact = {}
    material_impact = {}
    for r in filtered:
        if r.get("changed"):
            supplier = r.get("supplier", "Unknown")
            material = r.get("materialGroup", "Unknown")
            supplier_impact[supplier] = supplier_impact.get(supplier, 0) + 1
            material_impact[material] = material_impact.get(material, 0) + 1
    
    top_suppliers = sorted(supplier_impact.items(), key=lambda x: x[1], reverse=True)[:5]
    top_materials = sorted(material_impact.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "totalRecords": total_records,
        "changedRecords": any_changed_count,
        "changeRate": round(change_rate, 1),
        "qtyChangedCount": qty_changed_count,
        "supplierChangedCount": supplier_changed_count,
        "designChangedCount": design_changed_count,
        "rojChangedCount": roj_changed_count,
        "totalQtyDelta": total_qty_delta,
        "averageQtyDelta": round(avg_qty_delta, 1),
        "totalRojDelta": total_roj_delta,
        "averageRojDelta": round(avg_roj_delta, 1),
        "uniqueSuppliers": len(unique_suppliers),
        "uniqueMaterials": len(unique_materials),
        "uniqueLocations": len(unique_locations),
        "topSuppliers": top_suppliers,
        "topMaterials": top_materials,
        "suppliers": sorted(list(unique_suppliers)),
        "materials": sorted(list(unique_materials)),
        "locations": sorted(list(unique_locations)),
    }


def get_location_metrics(records: List[Dict], location_id: str) -> Dict:
    """Get metrics for a specific location."""
    return compute_scoped_metrics(records, location_id=location_id)


def get_supplier_metrics(records: List[Dict], supplier: str) -> Dict:
    """Get metrics for a specific supplier."""
    return compute_scoped_metrics(records, supplier=supplier)


def get_material_metrics(records: List[Dict], material_group: str) -> Dict:
    """Get metrics for a specific material group."""
    return compute_scoped_metrics(records, material_group=material_group)


def get_design_changes(records: List[Dict], location_id: Optional[str] = None) -> Dict:
    """
    Get design change metrics, optionally scoped to a location.
    
    Design changes = ZCOIBODVER changed OR ZCOIFORMFACT changed
    """
    # Filter by location if provided
    filtered = records
    if location_id:
        filtered = [r for r in filtered if r.get("locationId") == location_id]
    
    # Get records with design changes
    design_changed = [r for r in filtered if r.get("designChanged", False)]
    
    if not design_changed:
        return {
            "designChangedCount": 0,
            "totalRecords": len(filtered),
            "affectedSuppliers": [],
            "affectedMaterials": [],
            "topSuppliers": [],
            "topMaterials": [],
        }
    
    # Get unique suppliers and materials with design changes
    suppliers = set(r.get("supplier") for r in design_changed if r.get("supplier"))
    materials = set(r.get("materialGroup") for r in design_changed if r.get("materialGroup"))
    
    # Get top affected
    supplier_impact = {}
    material_impact = {}
    for r in design_changed:
        supplier = r.get("supplier", "Unknown")
        material = r.get("materialGroup", "Unknown")
        supplier_impact[supplier] = supplier_impact.get(supplier, 0) + 1
        material_impact[material] = material_impact.get(material, 0) + 1
    
    top_suppliers = sorted(supplier_impact.items(), key=lambda x: x[1], reverse=True)[:5]
    top_materials = sorted(material_impact.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "designChangedCount": len(design_changed),
        "totalRecords": len(filtered),
        "affectedSuppliers": sorted(list(suppliers)),
        "affectedMaterials": sorted(list(materials)),
        "topSuppliers": top_suppliers,
        "topMaterials": top_materials,
    }


def get_supplier_changes(records: List[Dict], location_id: Optional[str] = None) -> Dict:
    """
    Get supplier change metrics, optionally scoped to a location.
    
    Supplier changes = LOCFR changed
    """
    # Filter by location if provided
    filtered = records
    if location_id:
        filtered = [r for r in filtered if r.get("locationId") == location_id]
    
    # Get records with supplier changes
    supplier_changed = [r for r in filtered if r.get("supplierChanged", False)]
    
    if not supplier_changed:
        return {
            "supplierChangedCount": 0,
            "totalRecords": len(filtered),
            "affectedSuppliers": [],
            "affectedMaterials": [],
        }
    
    # Get unique suppliers and materials with supplier changes
    suppliers = set(r.get("supplier") for r in supplier_changed if r.get("supplier"))
    materials = set(r.get("materialGroup") for r in supplier_changed if r.get("materialGroup"))
    
    return {
        "supplierChangedCount": len(supplier_changed),
        "totalRecords": len(filtered),
        "affectedSuppliers": sorted(list(suppliers)),
        "affectedMaterials": sorted(list(materials)),
    }


def get_quantity_changes(records: List[Dict], location_id: Optional[str] = None) -> Dict:
    """
    Get quantity change metrics, optionally scoped to a location.
    
    Quantity changes = GSCFSCTQTY changed
    """
    # Filter by location if provided
    filtered = records
    if location_id:
        filtered = [r for r in filtered if r.get("locationId") == location_id]
    
    # Get records with quantity changes
    qty_changed = [r for r in filtered if r.get("qtyChanged", False)]
    
    if not qty_changed:
        return {
            "qtyChangedCount": 0,
            "totalRecords": len(filtered),
            "totalQtyDelta": 0,
            "averageQtyDelta": 0,
        }
    
    # Compute deltas
    qty_deltas = [r.get("qtyDelta", 0) for r in qty_changed if r.get("qtyDelta") is not None]
    total_qty_delta = sum(qty_deltas)
    avg_qty_delta = total_qty_delta / len(qty_deltas) if qty_deltas else 0
    
    return {
        "qtyChangedCount": len(qty_changed),
        "totalRecords": len(filtered),
        "totalQtyDelta": total_qty_delta,
        "averageQtyDelta": round(avg_qty_delta, 1),
    }


def get_roj_changes(records: List[Dict], location_id: Optional[str] = None) -> Dict:
    """
    Get ROJ (Release of Judgment) schedule change metrics, optionally scoped to a location.
    
    ROJ changes = GSCCONROJDATE changed
    """
    # Filter by location if provided
    filtered = records
    if location_id:
        filtered = [r for r in filtered if r.get("locationId") == location_id]
    
    # Get records with ROJ changes
    roj_changed = [r for r in filtered if r.get("rojChanged", False)]
    
    if not roj_changed:
        return {
            "rojChangedCount": 0,
            "totalRecords": len(filtered),
            "totalRojDelta": 0,
            "averageRojDelta": 0,
        }
    
    # Compute deltas
    roj_deltas = [r.get("rojDelta", 0) for r in roj_changed if r.get("rojDelta") is not None]
    total_roj_delta = sum(roj_deltas)
    avg_roj_delta = total_roj_delta / len(roj_deltas) if roj_deltas else 0
    
    return {
        "rojChangedCount": len(roj_changed),
        "totalRecords": len(filtered),
        "totalRojDelta": total_roj_delta,
        "averageRojDelta": round(avg_roj_delta, 1),
    }


def compare_locations(records: List[Dict], location1: str, location2: str) -> Dict:
    """
    Compare metrics between two locations.
    
    Returns scoped metrics for each location and highlights differences.
    """
    metrics1 = get_location_metrics(records, location1)
    metrics2 = get_location_metrics(records, location2)
    
    # Compute differences
    record_diff = metrics2["totalRecords"] - metrics1["totalRecords"]
    change_diff = metrics2["changedRecords"] - metrics1["changedRecords"]
    design_diff = metrics2["designChangedCount"] - metrics1["designChangedCount"]
    supplier_diff = metrics2["supplierChangedCount"] - metrics1["supplierChangedCount"]
    qty_diff = metrics2["totalQtyDelta"] - metrics1["totalQtyDelta"]
    
    return {
        "location1": location1,
        "location1Metrics": metrics1,
        "location2": location2,
        "location2Metrics": metrics2,
        "differences": {
            "recordCount": record_diff,
            "changedRecords": change_diff,
            "designChanges": design_diff,
            "supplierChanges": supplier_diff,
            "qtyDelta": qty_diff,
        }
    }


def get_top_locations(records: List[Dict], limit: int = 5) -> List[Tuple[str, int]]:
    """Get top locations ranked by change count."""
    location_changes = {}
    for r in records:
        if r.get("changed"):
            loc = r.get("locationId", "Unknown")
            location_changes[loc] = location_changes.get(loc, 0) + 1
    
    return sorted(location_changes.items(), key=lambda x: x[1], reverse=True)[:limit]


def get_top_suppliers(records: List[Dict], limit: int = 5) -> List[Tuple[str, int]]:
    """Get top suppliers ranked by change count."""
    supplier_changes = {}
    for r in records:
        if r.get("changed"):
            sup = r.get("supplier", "Unknown")
            supplier_changes[sup] = supplier_changes.get(sup, 0) + 1
    
    return sorted(supplier_changes.items(), key=lambda x: x[1], reverse=True)[:limit]


def get_top_materials(records: List[Dict], limit: int = 5) -> List[Tuple[str, int]]:
    """Get top materials ranked by change count."""
    material_changes = {}
    for r in records:
        if r.get("changed"):
            mat = r.get("materialGroup", "Unknown")
            material_changes[mat] = material_changes.get(mat, 0) + 1
    
    return sorted(material_changes.items(), key=lambda x: x[1], reverse=True)[:limit]
