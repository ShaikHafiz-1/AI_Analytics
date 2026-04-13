"""
Generative response layer for Planning Intelligence Copilot.

Converts metrics into natural, contextual, business-meaningful responses.
Supports multiple response styles to avoid repetition.
"""

import random
from typing import Dict, Optional, List


class GenerativeResponseBuilder:
    """Build natural language responses from metrics."""
    
    def __init__(self):
        """Initialize response templates and patterns."""
        self.health_templates = [
            "Planning health is {health}/100 ({status}). {changed_count} of {total_count} records have changed ({change_rate}%). Primary drivers: {drivers}.",
            "Current planning status: {status} ({health}/100). {change_rate}% of records show changes ({changed_count}/{total_count}). Key changes: {drivers}.",
            "Planning assessment: {status} health ({health}/100). {changed_count} records affected ({change_rate}%). Main change types: {drivers}.",
        ]
        
        self.location_templates = [
            "At {location}, {total_count} materials are tracked. {changed_count} show recent changes ({change_rate}%). Suppliers involved: {suppliers}.",
            "Location {location}: {total_count} records with {changed_count} recent changes ({change_rate}%). Key suppliers: {suppliers}.",
            "{location} shows {changed_count} changes across {total_count} materials ({change_rate}%). Active suppliers: {suppliers}.",
        ]
        
        self.design_templates = [
            "{count} records have design changes (BOD or Form Factor). Affected suppliers: {suppliers}. Materials: {materials}.",
            "Design changes detected in {count} records. Suppliers impacted: {suppliers}. Materials affected: {materials}.",
            "{count} records show design modifications. Key suppliers: {suppliers}. Key materials: {materials}.",
        ]
        
        self.forecast_templates = [
            "{count} records have forecast quantity changes. Total delta: {total_delta} units. Average change: {avg_delta} units per record.",
            "Forecast quantity changes in {count} records. Net delta: {total_delta} units ({avg_delta} avg). Trend: {trend}.",
            "{count} records show quantity forecast updates. Total adjustment: {total_delta} units. Per-record average: {avg_delta} units.",
        ]
        
        self.risk_templates = [
            "Risk level is {risk_level}. {high_risk_count} high-risk records ({high_risk_pct}%). Highest risk type: {risk_type}.",
            "Risk assessment: {risk_level} ({high_risk_count}/{total_count} records at high risk, {high_risk_pct}%). Primary concern: {risk_type}.",
            "{risk_level} risk detected. {high_risk_count} records flagged ({high_risk_pct}%). Main risk driver: {risk_type}.",
        ]
        
        self.comparison_templates = [
            "{loc1} shows {changes1} changes across {records1} materials. {loc2} shows {changes2} changes across {records2} materials. {difference}",
            "Comparison: {loc1} ({records1} materials, {changes1} changes) vs {loc2} ({records2} materials, {changes2} changes). {difference}",
            "{loc1}: {records1} materials with {changes1} changes. {loc2}: {records2} materials with {changes2} changes. {difference}",
        ]
        
        self.impact_templates = [
            "Top suppliers affected: {top_suppliers}. Top materials: {top_materials}. Total impact: {total_changes} changes across {unique_suppliers} suppliers.",
            "Impact analysis: {top_suppliers} are most affected. Materials: {top_materials}. Scope: {unique_suppliers} suppliers, {total_changes} total changes.",
            "Highest impact: {top_suppliers}. Key materials: {top_materials}. Breadth: {unique_suppliers} suppliers involved, {total_changes} changes.",
        ]
    
    def build_health_response(self, metrics: Dict) -> str:
        """Build health status response."""
        health_score = metrics.get("planningHealth", 50)
        status = self._get_health_status(health_score)
        changed = metrics.get("changedRecordCount", 0)
        total = metrics.get("totalRecords", 1)
        change_rate = (changed / total * 100) if total > 0 else 0
        
        # Get primary drivers
        drivers = []
        if metrics.get("designChanges", 0) > 0:
            drivers.append(f"Design ({metrics['designChanges']})")
        if metrics.get("supplierChanges", 0) > 0:
            drivers.append(f"Supplier ({metrics['supplierChanges']})")
        if metrics.get("qtyChanges", 0) > 0:
            drivers.append(f"Quantity ({metrics['qtyChanges']})")
        
        drivers_str = ", ".join(drivers) if drivers else "Multiple factors"
        
        template = random.choice(self.health_templates)
        return template.format(
            health=health_score,
            status=status,
            changed_count=changed,
            total_count=total,
            change_rate=round(change_rate, 1),
            drivers=drivers_str
        )
    
    def build_location_response(self, location: str, metrics: Dict) -> str:
        """Build location-specific response."""
        total = metrics.get("totalRecords", 0)
        changed = metrics.get("changedRecords", 0)
        change_rate = (changed / total * 100) if total > 0 else 0
        suppliers = ", ".join(metrics.get("suppliers", [])[:3]) or "Multiple"
        
        template = random.choice(self.location_templates)
        return template.format(
            location=location,
            total_count=total,
            changed_count=changed,
            change_rate=round(change_rate, 1),
            suppliers=suppliers
        )
    
    def build_design_response(self, metrics: Dict) -> str:
        """Build design change response."""
        count = metrics.get("designChangedCount", 0)
        suppliers = ", ".join(metrics.get("affectedSuppliers", [])[:3]) or "Multiple"
        materials = ", ".join(metrics.get("affectedMaterials", [])[:3]) or "Multiple"
        
        template = random.choice(self.design_templates)
        return template.format(
            count=count,
            suppliers=suppliers,
            materials=materials
        )
    
    def build_forecast_response(self, metrics: Dict) -> str:
        """Build forecast response."""
        count = metrics.get("qtyChangedCount", 0)
        total_delta = metrics.get("totalQtyDelta", 0)
        avg_delta = metrics.get("averageQtyDelta", 0)
        trend = "Downward" if total_delta < 0 else "Upward" if total_delta > 0 else "Stable"
        
        template = random.choice(self.forecast_templates)
        return template.format(
            count=count,
            total_delta=total_delta,
            avg_delta=avg_delta,
            trend=trend
        )
    
    def build_risk_response(self, metrics: Dict) -> str:
        """Build risk assessment response."""
        risk_level = metrics.get("riskLevel", "NORMAL")
        high_risk_count = metrics.get("highRiskCount", 0)
        total = metrics.get("totalRecords", 1)
        high_risk_pct = (high_risk_count / total * 100) if total > 0 else 0
        risk_type = metrics.get("highestRiskLevel", "Multiple factors")
        
        template = random.choice(self.risk_templates)
        return template.format(
            risk_level=risk_level,
            high_risk_count=high_risk_count,
            total_count=total,
            high_risk_pct=round(high_risk_pct, 1),
            risk_type=risk_type
        )
    
    def build_comparison_response(self, loc1: str, metrics1: Dict, loc2: str, metrics2: Dict) -> str:
        """Build comparison response."""
        records1 = metrics1.get("totalRecords", 0)
        changes1 = metrics1.get("changedRecords", 0)
        records2 = metrics2.get("totalRecords", 0)
        changes2 = metrics2.get("changedRecords", 0)
        
        # Determine difference narrative
        if changes1 > changes2:
            difference = f"{loc1} shows more activity ({changes1} vs {changes2} changes)."
        elif changes2 > changes1:
            difference = f"{loc2} shows more activity ({changes2} vs {changes1} changes)."
        else:
            difference = "Both locations show similar activity levels."
        
        template = random.choice(self.comparison_templates)
        return template.format(
            loc1=loc1,
            records1=records1,
            changes1=changes1,
            loc2=loc2,
            records2=records2,
            changes2=changes2,
            difference=difference
        )
    
    def build_impact_response(self, metrics: Dict) -> str:
        """Build impact analysis response."""
        top_suppliers = metrics.get("topSuppliers", [])
        top_materials = metrics.get("topMaterials", [])
        unique_suppliers = metrics.get("uniqueSuppliers", 0)
        total_changes = metrics.get("changedRecords", 0)
        
        # Format top suppliers
        supplier_str = ", ".join([f"{s[0]} ({s[1]})" for s in top_suppliers[:3]]) or "Multiple"
        material_str = ", ".join([f"{m[0]} ({m[1]})" for m in top_materials[:3]]) or "Multiple"
        
        template = random.choice(self.impact_templates)
        return template.format(
            top_suppliers=supplier_str,
            top_materials=material_str,
            unique_suppliers=unique_suppliers,
            total_changes=total_changes
        )
    
    @staticmethod
    def _get_health_status(score: int) -> str:
        """Convert health score to status."""
        if score >= 80:
            return "Healthy"
        elif score >= 60:
            return "Acceptable"
        elif score >= 40:
            return "Concerning"
        else:
            return "Critical"
    
    @staticmethod
    def _get_risk_level(high_risk_pct: float) -> str:
        """Convert risk percentage to level."""
        if high_risk_pct >= 30:
            return "CRITICAL"
        elif high_risk_pct >= 20:
            return "HIGH"
        elif high_risk_pct >= 10:
            return "MEDIUM"
        else:
            return "LOW"


def build_contextual_response(
    question: str,
    metrics: Dict,
    response_type: str,
    location: Optional[str] = None
) -> str:
    """
    Build a contextual response based on question type and metrics.
    
    Args:
        question: Original user question
        metrics: Computed metrics
        response_type: Type of response (health, location, design, forecast, risk, comparison, impact)
        location: Optional location context
    
    Returns:
        Natural language response
    """
    builder = GenerativeResponseBuilder()
    
    if response_type == "health":
        return builder.build_health_response(metrics)
    elif response_type == "location":
        return builder.build_location_response(location or "Unknown", metrics)
    elif response_type == "design":
        return builder.build_design_response(metrics)
    elif response_type == "forecast":
        return builder.build_forecast_response(metrics)
    elif response_type == "risk":
        return builder.build_risk_response(metrics)
    elif response_type == "comparison":
        # For comparison, metrics should have location1, location2, metrics1, metrics2
        loc1 = metrics.get("location1", "Location 1")
        loc2 = metrics.get("location2", "Location 2")
        m1 = metrics.get("location1Metrics", {})
        m2 = metrics.get("location2Metrics", {})
        return builder.build_comparison_response(loc1, m1, loc2, m2)
    elif response_type == "impact":
        return builder.build_impact_response(metrics)
    else:
        return "Unable to generate response for this query type."


def ask_for_clarification(question: str, context: Optional[str] = None) -> str:
    """
    Generate a clarification request when query is ambiguous.
    
    Args:
        question: Original question
        context: Optional context about what's ambiguous
    
    Returns:
        Clarification request
    """
    clarifications = [
        "Would you like to analyze this by location, supplier, or material group?",
        "Should I focus on a specific location or supplier?",
        "Would you like to see results for a particular location or across all locations?",
        "Do you want to analyze by location, supplier, or overall impact?",
    ]
    
    return random.choice(clarifications)
