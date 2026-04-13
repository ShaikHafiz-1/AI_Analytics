"""
Helper functions for Copilot question classification and answer generation.
These are utility functions, not Azure Functions endpoints.
"""

from typing import Optional


def extract_location_id(question: str) -> Optional[str]:
    """Extract location ID from question (e.g., 'CYS20_F01C01')"""
    import re
    # Pattern: uppercase letters followed by numbers and underscores
    match = re.search(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', question)
    return match.group(1) if match else None


def filter_records_by_location(records: list, location_id: str) -> list:
    """Filter records to specific location"""
    return [r for r in records if r.get("locationId") == location_id]


def filter_records_by_change_type(records: list, change_type: str) -> list:
    """Filter records by change type (Design, Supplier, Quantity)"""
    return [r for r in records if r.get("changeType") == change_type]


def get_unique_suppliers(records: list) -> list:
    """Get unique suppliers from records"""
    suppliers = set()
    for r in records:
        if r.get("supplier"):
            suppliers.add(r.get("supplier"))
    return sorted(list(suppliers))


def get_unique_materials(records: list) -> list:
    """Get unique materials from records"""
    materials = set()
    for r in records:
        if r.get("materialGroup"):
            materials.add(r.get("materialGroup"))
    return sorted(list(materials))


def get_impact_ranking(records: list) -> dict:
    """Get suppliers/materials ranked by impact (number of changes)"""
    supplier_impact = {}
    material_impact = {}
    
    for r in records:
        if r.get("changed"):
            supplier = r.get("supplier", "Unknown")
            material = r.get("materialGroup", "Unknown")
            
            supplier_impact[supplier] = supplier_impact.get(supplier, 0) + 1
            material_impact[material] = material_impact.get(material, 0) + 1
    
    return {
        "suppliers": sorted(supplier_impact.items(), key=lambda x: x[1], reverse=True),
        "materials": sorted(material_impact.items(), key=lambda x: x[1], reverse=True)
    }


def extract_supplier_name(question: str) -> Optional[str]:
    """Extract supplier name from question"""
    import re
    # Look for common supplier patterns or quoted text
    match = re.search(r'supplier[s]?\s+(?:named|called|is|are)?\s+["\']?([A-Za-z0-9\s\-]+)["\']?', question, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_material_id(question: str) -> Optional[str]:
    """Extract material ID from question"""
    import re
    # Look for material patterns (e.g., UPS, POWER, etc.)
    match = re.search(r'material[s]?\s+(?:named|called|is|are|group)?\s+["\']?([A-Z0-9\-]+)["\']?', question, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def get_records_by_change_type(records: list, change_type: str) -> list:
    """Get records filtered by specific change type"""
    if change_type.lower() == "design":
        return [r for r in records if r.get("designChanged", False)]
    elif change_type.lower() == "supplier":
        return [r for r in records if r.get("supplierChanged", False)]
    elif change_type.lower() == "quantity":
        return [r for r in records if r.get("qtyChanged", False)]
    elif change_type.lower() == "schedule":
        return [r for r in records if r.get("scheduleChanged", False)]
    else:
        return [r for r in records if r.get("changed", False)]


def compute_change_metrics(records: list) -> dict:
    """Compute detailed change metrics"""
    total = len(records)
    changed = sum(1 for r in records if r.get("changed", False))
    design_changed = sum(1 for r in records if r.get("designChanged", False))
    supplier_changed = sum(1 for r in records if r.get("supplierChanged", False))
    qty_changed = sum(1 for r in records if r.get("qtyChanged", False))
    schedule_changed = sum(1 for r in records if r.get("scheduleChanged", False))
    
    change_rate = (changed / total * 100) if total > 0 else 0
    
    return {
        "totalRecords": total,
        "changedRecords": changed,
        "changeRate": round(change_rate, 1),
        "designChanged": design_changed,
        "supplierChanged": supplier_changed,
        "qtyChanged": qty_changed,
        "scheduleChanged": schedule_changed
    }


def compute_roi_metrics(records: list) -> dict:
    """Compute ROJ (Release of Judgment) metrics"""
    roi_changed = sum(1 for r in records if r.get("scheduleChanged", False))
    
    # Compute average ROJ delta if available
    roi_deltas = []
    for r in records:
        if r.get("rojDelta") is not None:
            roi_deltas.append(r.get("rojDelta", 0))
    
    avg_roi_delta = sum(roi_deltas) / len(roi_deltas) if roi_deltas else 0
    
    return {
        "roiChangedCount": roi_changed,
        "averageRoiDelta": round(avg_roi_delta, 1),
        "roiDeltaRecords": len(roi_deltas)
    }


def compute_forecast_metrics(records: list) -> dict:
    """Compute forecast quantity metrics"""
    qty_changed = sum(1 for r in records if r.get("qtyChanged", False))
    
    # Compute total and average qty delta
    qty_deltas = []
    for r in records:
        if r.get("qtyDelta") is not None:
            qty_deltas.append(r.get("qtyDelta", 0))
    
    total_qty_delta = sum(qty_deltas)
    avg_qty_delta = total_qty_delta / len(qty_deltas) if qty_deltas else 0
    
    return {
        "qtyChangedCount": qty_changed,
        "totalQtyDelta": total_qty_delta,
        "averageQtyDelta": round(avg_qty_delta, 1),
        "qtyDeltaRecords": len(qty_deltas)
    }


def get_top_locations_by_change(records: list, limit: int = 5) -> list:
    """Get top locations ranked by change count"""
    location_changes = {}
    for r in records:
        if r.get("changed"):
            loc = r.get("locationId", "Unknown")
            location_changes[loc] = location_changes.get(loc, 0) + 1
    
    return sorted(location_changes.items(), key=lambda x: x[1], reverse=True)[:limit]


def get_top_materials_by_change(records: list, limit: int = 5) -> list:
    """Get top materials ranked by change count"""
    material_changes = {}
    for r in records:
        if r.get("changed"):
            mat = r.get("materialGroup", "Unknown")
            material_changes[mat] = material_changes.get(mat, 0) + 1
    
    return sorted(material_changes.items(), key=lambda x: x[1], reverse=True)[:limit]
