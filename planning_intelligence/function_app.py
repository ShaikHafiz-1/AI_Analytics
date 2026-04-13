"""
Planning Intelligence Azure Functions - Cleaned Version
Minimal endpoints for production use:
- planning-dashboard-v2: Blob-backed dashboard
- planning_intelligence_nlp: NLP query processing
- explain: Explainability endpoint
- debug-snapshot: Debug endpoint
- daily-refresh: Background refresh
"""

import json
import logging
from typing import Optional, List
import azure.functions as func

from normalizer import normalize_rows
from filters import filter_records
from comparator import compare_records
from analytics import build_summary
from dashboard_builder import build_dashboard_response
from response_builder import build_response
from snapshot_store import load_snapshot, snapshot_exists, get_last_updated_time
from nlp_endpoint import handle_nlp_query
from copilot_helpers import (
    extract_location_id,
    filter_records_by_location,
    filter_records_by_change_type,
    get_unique_suppliers,
    get_unique_materials,
    get_impact_ranking
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# ============================================================================
# DATA NORMALIZATION UTILITY
# ============================================================================

def _normalize_detail_records(records: list) -> list:
    """
    Normalize detailRecords to consistent format.
    
    Handles:
    - Raw CSV dicts with field names like LOCID, LOCFR, GSCFSCTQTY
    - ComparedRecord objects with attributes like location_id, supplier
    - Already-normalized dicts with keys like locationId, supplier
    
    Required Fields (from blob):
    - LOCID → locationId
    - PRDID → materialId
    - GSCEQUIPCAT → materialGroup
    - LOCFR → supplier
    - GSCFSCTQTY → forecastQty
    - GSCPREVFCSTQTY → forecastQtyPrevious
    - GSCCONROJDATE → rojCurrent
    - GSCPREVROJNBD → rojPrevious
    - ZCOIBODVER → bodCurrent
    - ZCOIFORMFACT → ffCurrent
    - GSCSUPLDATE → supplierDate
    - GSCPREVSUPLDATE → supplierDatePrevious
    
    Computed Fields:
    - qtyDelta = forecastQty - forecastQtyPrevious
    - rojDelta = days between rojCurrent and rojPrevious
    - qtyChanged = qtyDelta != 0
    - supplierChanged = supplier != supplierPrevious
    - designChanged = bodCurrent != bodPrevious OR ffCurrent != ffPrevious
    - rojChanged = rojCurrent != rojPrevious
    """
    if not records:
        return []
    
    normalized = []
    for r in records:
        try:
            if isinstance(r, dict):
                # Extract all fields with proper fallbacks
                location_id = r.get("locationId") or r.get("LOCID") or r.get("location_id")
                material_id = r.get("materialId") or r.get("PRDID") or r.get("material_id")
                material_group = r.get("materialGroup") or r.get("GSCEQUIPCAT") or r.get("material_group")
                supplier = r.get("supplier") or r.get("LOCFR") or r.get("supplier_current")
                supplier_previous = r.get("supplierPrevious") or r.get("supplier_previous")
                
                forecast_qty = r.get("forecastQty") or r.get("GSCFSCTQTY") or r.get("forecast_qty_current")
                forecast_qty_prev = r.get("forecastQtyPrevious") or r.get("GSCPREVFCSTQTY") or r.get("forecast_qty_previous")
                
                roj_current = r.get("rojCurrent") or r.get("GSCCONROJDATE") or r.get("roj_current")
                roj_previous = r.get("rojPrevious") or r.get("GSCPREVROJNBD") or r.get("roj_previous")
                
                bod_current = r.get("bodCurrent") or r.get("ZCOIBODVER") or r.get("bod_current")
                bod_previous = r.get("bodPrevious") or r.get("bod_previous")
                
                ff_current = r.get("ffCurrent") or r.get("ZCOIFORMFACT") or r.get("ff_current")
                ff_previous = r.get("ffPrevious") or r.get("ff_previous")
                
                supplier_date = r.get("supplierDate") or r.get("GSCSUPLDATE") or r.get("supplier_date")
                supplier_date_prev = r.get("supplierDatePrevious") or r.get("GSCPREVSUPLDATE") or r.get("supplier_date_previous")
                
                # Compute deltas
                qty_delta = 0
                if forecast_qty is not None and forecast_qty_prev is not None:
                    try:
                        qty_delta = int(forecast_qty) - int(forecast_qty_prev)
                    except (ValueError, TypeError):
                        qty_delta = 0
                
                # Compute ROJ delta in days
                roj_delta = None
                if roj_current and roj_previous:
                    try:
                        from datetime import datetime
                        if isinstance(roj_current, str):
                            roj_current_dt = datetime.fromisoformat(roj_current.replace('Z', '+00:00'))
                        else:
                            roj_current_dt = roj_current
                        
                        if isinstance(roj_previous, str):
                            roj_previous_dt = datetime.fromisoformat(roj_previous.replace('Z', '+00:00'))
                        else:
                            roj_previous_dt = roj_previous
                        
                        roj_delta = (roj_current_dt - roj_previous_dt).days
                    except (ValueError, TypeError, AttributeError):
                        roj_delta = None
                
                # Determine change flags
                qty_changed = qty_delta != 0
                supplier_changed = supplier and supplier_previous and supplier != supplier_previous
                design_changed = (bod_current and bod_previous and bod_current != bod_previous) or \
                                (ff_current and ff_previous and ff_current != ff_previous)
                roj_changed = roj_current and roj_previous and roj_current != roj_previous
                
                changed = qty_changed or supplier_changed or design_changed or roj_changed
                
                # Validate required fields
                if not location_id:
                    logging.warning(f"Record missing locationId: {r}")
                    continue
                
                norm = {
                    "locationId": location_id or None,
                    "materialId": material_id or None,
                    "materialGroup": material_group or None,
                    "supplier": supplier or None,
                    "supplierPrevious": supplier_previous or None,
                    "forecastQty": forecast_qty,
                    "forecastQtyPrevious": forecast_qty_prev,
                    "rojCurrent": roj_current or None,
                    "rojPrevious": roj_previous or None,
                    "bodCurrent": bod_current or None,
                    "bodPrevious": bod_previous or None,
                    "ffCurrent": ff_current or None,
                    "ffPrevious": ff_previous or None,
                    "supplierDate": supplier_date or None,
                    "supplierDatePrevious": supplier_date_prev or None,
                    "qtyDelta": qty_delta,
                    "rojDelta": roj_delta,
                    "qtyChanged": qty_changed,
                    "supplierChanged": supplier_changed,
                    "designChanged": design_changed,
                    "rojChanged": roj_changed,
                    "changed": changed,
                    "riskLevel": r.get("riskLevel") or r.get("risk_level") or "Normal",
                    "changeType": r.get("changeType") or r.get("change_type") or "Unchanged",
                    "dcSite": r.get("dcSite") or r.get("ZCOIDCID") or r.get("dc_site") or None,
                    "metro": r.get("metro") or r.get("ZCOIMETROID") or None,
                    "country": r.get("country") or r.get("ZCOICOUNTRY") or None,
                    "isSupplierDateMissing": r.get("isSupplierDateMissing") or r.get("Is_SupplierDateMissing") or False,
                }
                normalized.append(norm)
            else:
                # Handle object attributes
                location_id = getattr(r, "location_id", None) or getattr(r, "locationId", None)
                material_id = getattr(r, "material_id", None) or getattr(r, "materialId", None)
                material_group = getattr(r, "material_group", None) or getattr(r, "materialGroup", None)
                supplier = getattr(r, "supplier_current", None) or getattr(r, "supplier", None)
                supplier_previous = getattr(r, "supplier_previous", None)
                
                forecast_qty = getattr(r, "forecast_qty_current", None)
                forecast_qty_prev = getattr(r, "forecast_qty_previous", None)
                
                roj_current = getattr(r, "roj_current", None)
                roj_previous = getattr(r, "roj_previous", None)
                
                bod_current = getattr(r, "bod_current", None)
                bod_previous = getattr(r, "bod_previous", None)
                
                ff_current = getattr(r, "ff_current", None)
                ff_previous = getattr(r, "ff_previous", None)
                
                supplier_date = getattr(r, "supplier_date", None)
                supplier_date_prev = getattr(r, "supplier_date_previous", None)
                
                # Compute deltas
                qty_delta = 0
                if forecast_qty is not None and forecast_qty_prev is not None:
                    try:
                        qty_delta = int(forecast_qty) - int(forecast_qty_prev)
                    except (ValueError, TypeError):
                        qty_delta = 0
                
                roj_delta = None
                if roj_current and roj_previous:
                    try:
                        from datetime import datetime
                        if isinstance(roj_current, str):
                            roj_current_dt = datetime.fromisoformat(roj_current.replace('Z', '+00:00'))
                        else:
                            roj_current_dt = roj_current
                        
                        if isinstance(roj_previous, str):
                            roj_previous_dt = datetime.fromisoformat(roj_previous.replace('Z', '+00:00'))
                        else:
                            roj_previous_dt = roj_previous
                        
                        roj_delta = (roj_current_dt - roj_previous_dt).days
                    except (ValueError, TypeError, AttributeError):
                        roj_delta = None
                
                # Determine change flags
                qty_changed = qty_delta != 0
                supplier_changed = supplier and supplier_previous and supplier != supplier_previous
                design_changed = (bod_current and bod_previous and bod_current != bod_previous) or \
                                (ff_current and ff_previous and ff_current != ff_previous)
                roj_changed = roj_current and roj_previous and roj_current != roj_previous
                
                changed = qty_changed or supplier_changed or design_changed or roj_changed
                
                if not location_id:
                    logging.warning(f"Record missing locationId: {r}")
                    continue
                
                norm = {
                    "locationId": location_id or None,
                    "materialId": material_id or None,
                    "materialGroup": material_group or None,
                    "supplier": supplier or None,
                    "supplierPrevious": supplier_previous or None,
                    "forecastQty": forecast_qty,
                    "forecastQtyPrevious": forecast_qty_prev,
                    "rojCurrent": roj_current or None,
                    "rojPrevious": roj_previous or None,
                    "bodCurrent": bod_current or None,
                    "bodPrevious": bod_previous or None,
                    "ffCurrent": ff_current or None,
                    "ffPrevious": ff_previous or None,
                    "supplierDate": supplier_date or None,
                    "supplierDatePrevious": supplier_date_prev or None,
                    "qtyDelta": qty_delta,
                    "rojDelta": roj_delta,
                    "qtyChanged": qty_changed,
                    "supplierChanged": supplier_changed,
                    "designChanged": design_changed,
                    "rojChanged": roj_changed,
                    "changed": changed,
                    "riskLevel": getattr(r, "risk_level", "Normal") or "Normal",
                    "changeType": getattr(r, "change_type", "Unchanged") or "Unchanged",
                    "dcSite": getattr(r, "dc_site", None),
                    "metro": getattr(r, "metro", None),
                    "country": getattr(r, "country", None),
                    "isSupplierDateMissing": getattr(r, "is_supplier_date_missing", False),
                }
                normalized.append(norm)
        except Exception as e:
            logging.warning(f"Failed to normalize record: {e}. Skipping.")
            continue
    
    logging.info(f"Normalized {len(normalized)} records from {len(records)} input records")
    return normalized


def _error(message: str, status: int) -> func.HttpResponse:
    """Helper to create error response with CORS headers."""
    response = func.HttpResponse(
        json.dumps({"error": message}),
        mimetype="application/json",
        status_code=status,
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def _cors_response(data: str, status: int = 200, mimetype: str = "application/json") -> func.HttpResponse:
    """Helper to create HTTP response with CORS headers."""
    response = func.HttpResponse(
        data,
        mimetype=mimetype,
        status_code=status,
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ============================================================================
# ACTIVE ENDPOINTS
# ============================================================================

@app.route(route="planning_intelligence_nlp", methods=["POST", "OPTIONS"])
def planning_intelligence_nlp(req: func.HttpRequest) -> func.HttpResponse:
    """
    Natural Language Processing endpoint for Copilot UI.
    
    Accepts natural language questions and processes them through the NLP pipeline.
    """
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    logging.info("Planning Intelligence NLP endpoint triggered.")
    return handle_nlp_query(req)


@app.route(route="planning-dashboard-v2", methods=["POST", "OPTIONS"])
def planning_dashboard_v2(req: func.HttpRequest) -> func.HttpResponse:
    """
    Blob-first AI dashboard endpoint.
    Reads from cached snapshot first; falls back to blob reload if no snapshot.
    """
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    logging.info("Planning Dashboard v2 triggered.")

    try:
        body = req.get_json()
    except ValueError:
        body = {}

    location_id: Optional[str] = body.get("location_id") if body else None
    material_group: Optional[str] = body.get("material_group") if body else None

    # Try cached snapshot first (fast path)
    snap = load_snapshot()
    if snap:
        if location_id or material_group:
            snap = _filter_snapshot(snap, location_id, material_group)
        return _cors_response(json.dumps(snap, default=str))

    # No snapshot — load from blob directly
    logging.info("No snapshot found, loading from blob.")
    try:
        from blob_loader import load_current_previous_from_blob
        current_rows, previous_rows = load_current_previous_from_blob()
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Blob load failed: {error_msg}")
        return _error(f"Blob load failed: {error_msg}", 500)

    current_records = normalize_rows(current_rows, is_current=True)
    previous_records = normalize_rows(previous_rows, is_current=False)
    current_filtered = filter_records(current_records, location_id, material_group)
    previous_filtered = filter_records(previous_records, location_id, material_group)
    compared = compare_records(current_filtered, previous_filtered)

    result = build_response(
        compared, [], location_id, material_group,
        data_mode="blob",
    )

    return _cors_response(json.dumps(result, default=str))


@app.route(route="daily-refresh", methods=["POST", "OPTIONS"])
def daily_refresh(req: func.HttpRequest) -> func.HttpResponse:
    """
    Triggers daily refresh from Azure Blob Storage and saves a snapshot.
    """
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    logging.info("Daily refresh triggered — loading from Blob Storage.")
    try:
        from run_daily_refresh import run_daily_refresh
        result = run_daily_refresh()
        return _cors_response(json.dumps({
            "status": "ok",
            "lastRefreshedAt": result.get("lastRefreshedAt"),
            "totalRecords": result.get("totalRecords"),
            "changedRecordCount": result.get("changedRecordCount"),
            "planningHealth": result.get("planningHealth"),
        }, default=str))
    except Exception as e:
        return _error(f"Daily refresh failed: {str(e)}", 500)


# ============================================================================
# COPILOT: Question Classification & Answer Generation
# ============================================================================

def classify_question(question: str) -> str:
    """
    Classify the question type to determine how to answer it.
    
    Classification Priority (check in this order):
    0. Greeting: "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"
    1. Comparison: "compare", "vs", "versus", "difference", "between"
    2. Impact: "impact", "most impact", "most affected", "most changed", "consequence", "which" + "most"
    3. Entity: "list", "which" + entity keywords, "supplier", "material", "location", "group"
    4. Change: "change", "changed", "changes" (but not in entity/impact context)
    5. Design: "design", "bod", "form factor", "ff"
    6. Schedule: "roj", "schedule", "date", "release", "judgment"
    7. Forecast: "forecast", "trend", "delta", "increase", "decrease", "units"
    8. Location: "location", "locations", "datacenter", "site", "dc", "facility"
    9. Risk: "risk", "risks", "risky", "danger", "dangerous", "issue", "main issue"
    10. Health: "health", "status", "score", "critical", "stable", "planning"
    11. General: fallback
    """
    q_lower = question.lower()
    
    # 0. Greeting questions - CHECK FIRST (simple greetings should route to ChatGPT)
    if any(word in q_lower for word in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
        # Make sure it's actually a greeting (short, simple message)
        if len(question.split()) <= 3:  # Greetings are typically 1-3 words
            return "greeting"
    
    # 1. Comparison questions - CHECK FIRST (most specific)
    if any(word in q_lower for word in ["compare", "vs", "versus", "difference", "between"]):
        return "comparison"
    
    # 2. Impact questions - CHECK EARLY (before change which uses "changes")
    # Impact questions ask about impact, most affected, most changed, consequences
    if any(word in q_lower for word in ["impact", "consequence", "affected by"]):
        return "impact"
    
    # Check for "which" + "most" (most affected, most changed, most impact, most changes)
    if "which" in q_lower and "most" in q_lower:
        return "impact"
    
    # 3. Change questions - CHECK BEFORE ENTITY (to catch "supplier changes", "material changes", etc.)
    # Change questions ask about what changed, how many changed, quantity changes, design changes, etc.
    # But NOT when it's part of an entity or impact question
    if any(word in q_lower for word in ["change", "changed", "changes"]):
        # Exclude if it's part of an entity question (e.g., "Which suppliers have design changes?")
        if not ("which" in q_lower and any(word in q_lower for word in ["supplier", "material", "location", "group"])):
            # Exclude if it's part of an impact question (e.g., "Which supplier has the most changes?")
            if not ("which" in q_lower and "most" in q_lower):
                return "change"
    
    # 4. Entity questions - CHECK AFTER CHANGE
    # Entity questions ask for lists of suppliers, materials, locations
    if any(word in q_lower for word in ["list", "supplier", "suppliers"]):
        return "entity"
    
    # Check for "which" with entity context (which suppliers, which materials, which locations, which groups)
    if "which" in q_lower and any(word in q_lower for word in ["supplier", "material", "location", "group"]):
        return "entity"
    
    # Check for "materials" or "materials are affected" (but not "most affected")
    if "material" in q_lower and "most" not in q_lower:
        return "entity"
    
    # Check for "groups" (entity context, not design)
    if "group" in q_lower and "most" not in q_lower:
        return "entity"
    
    # 5. Design questions
    if any(word in q_lower for word in ["design", "bod", "form factor", "ff"]):
        return "design"
    
    # 6. Schedule/ROJ questions
    if any(word in q_lower for word in ["roj", "schedule", "date", "release", "judgment"]):
        return "schedule"
    
    # 7. Forecast questions
    if any(word in q_lower for word in ["forecast", "trend", "delta", "increase", "decrease", "units"]):
        return "forecast"
    
    # 8. Location questions
    if any(word in q_lower for word in ["location", "locations", "datacenter", "site", "dc", "facility"]):
        return "location"
    
    # 9. Risk questions - CHECK BEFORE HEALTH (health uses "status" which is too broad)
    if any(word in q_lower for word in ["risk", "risks", "risky", "danger", "dangerous", "high-risk", "top risk", "issue", "main issue"]):
        return "risk"
    
    # 10. Health questions
    if any(word in q_lower for word in ["health", "status", "score", "critical", "stable", "planning"]):
        return "health"
    
    # 11. Default
    else:
        return "general"


def generate_health_answer(detail_records: list, context: dict, use_llm: bool = True) -> dict:
    """Generate answer for health-related questions"""
    health = context.get("planningHealth", 0)
    status = context.get("status", "Unknown")
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    pct_changed = (changed / total * 100) if total > 0 else 0
    
    risk_summary = context.get("riskSummary", {})
    design_changes = risk_summary.get("designChangedCount", 0)
    supplier_changes = risk_summary.get("supplierChangedCount", 0)
    
    # Build consistent supporting metrics
    supporting_metrics = {
        "planningHealth": health,
        "status": status,
        "changedRecordCount": changed,
        "totalRecords": total,
        "changePercentage": round(pct_changed, 1),
        "designChanges": design_changes,
        "supplierChanges": supplier_changes,
        "trendDirection": context.get("trendDirection", "Stable"),
        "riskLevel": risk_summary.get("level", "Unknown")
    }
    
    # Try to use LLM with blob data context
    if use_llm:
        try:
            from generative_responses import GenerativeResponseBuilder
            builder = GenerativeResponseBuilder(use_llm=True, detail_records=detail_records)
            answer = builder.build_health_response(supporting_metrics)
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = f"Planning health is {health}/100 ({status}). {changed:,} of {total:,} records have changed ({pct_changed:.1f}%). "
            answer += f"Primary drivers: Design changes ({design_changes}), Supplier changes ({supplier_changes})."
    else:
        answer = f"Planning health is {health}/100 ({status}). {changed:,} of {total:,} records have changed ({pct_changed:.1f}%). "
        answer += f"Primary drivers: Design changes ({design_changes}), Supplier changes ({supplier_changes})."
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


def generate_forecast_answer(detail_records: list, context: dict, question: str = "", use_llm: bool = True) -> dict:
    """Generate answer for forecast-related questions"""
    forecast_new = context.get("forecastNew", 0)
    forecast_old = context.get("forecastOld", 0)
    delta = context.get("trendDelta", 0)
    trend = context.get("trendDirection", "Stable")
    
    pct_change = (delta / forecast_old * 100) if forecast_old > 0 else 0
    
    # Try to use LLM with blob data context
    if use_llm:
        try:
            from generative_responses import GenerativeResponseBuilder
            metrics = {
                "forecastNew": forecast_new,
                "forecastOld": forecast_old,
                "trendDelta": delta,
                "trendDirection": trend,
                "percentChange": pct_change,
                "qtyChangedCount": sum(1 for r in detail_records if r.get("qtyChanged")),
                "totalQtyDelta": delta,
                "averageQtyDelta": delta / len(detail_records) if detail_records else 0
            }
            builder = GenerativeResponseBuilder(use_llm=True, detail_records=detail_records)
            answer = builder.build_forecast_response(metrics)
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = f"Current forecast is {forecast_new:,.0f} units. Previous was {forecast_old:,.0f} units. "
            answer += f"Change: {delta:+,.0f} units ({pct_change:+.1f}%). Trend: {trend}."
    else:
        answer = f"Current forecast is {forecast_new:,.0f} units. Previous was {forecast_old:,.0f} units. "
        answer += f"Change: {delta:+,.0f} units ({pct_change:+.1f}%). Trend: {trend}."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "forecastNew": forecast_new,
            "forecastOld": forecast_old,
            "trendDelta": delta,
            "trendDirection": trend,
            "percentChange": pct_change
        }
    }


def generate_risk_answer(detail_records: list, context: dict, use_llm: bool = True) -> dict:
    """Generate answer for risk-related questions"""
    risk_summary = context.get("riskSummary", {})
    level = risk_summary.get("level", "Unknown")
    highest = risk_summary.get("highestRiskLevel", "Unknown")
    high_risk_count = risk_summary.get("highRiskCount", 0)
    total = len(detail_records)
    
    pct_high_risk = (high_risk_count / total * 100) if total > 0 else 0
    
    # Try to use LLM with blob data context
    if use_llm:
        try:
            from generative_responses import GenerativeResponseBuilder
            metrics = {
                "riskLevel": level,
                "highestRiskLevel": highest,
                "highRiskCount": high_risk_count,
                "totalRecords": total,
                "percentHighRisk": pct_high_risk,
                "riskBreakdown": risk_summary.get("riskBreakdown", {})
            }
            builder = GenerativeResponseBuilder(use_llm=True, detail_records=detail_records)
            answer = builder.build_risk_response(metrics)
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = f"Risk level is {level}. "
            answer += f"Highest risk type: {highest}. "
            answer += f"{high_risk_count:,} high-risk records out of {total:,} total ({pct_high_risk:.1f}%). "
            breakdown = risk_summary.get("riskBreakdown", {})
            if breakdown:
                answer += f"Breakdown: "
                for risk_type, count in breakdown.items():
                    answer += f"{risk_type} ({count}), "
                answer = answer.rstrip(", ") + "."
    else:
        answer = f"Risk level is {level}. "
        answer += f"Highest risk type: {highest}. "
        answer += f"{high_risk_count:,} high-risk records out of {total:,} total ({pct_high_risk:.1f}%). "
        breakdown = risk_summary.get("riskBreakdown", {})
        if breakdown:
            answer += f"Breakdown: "
            for risk_type, count in breakdown.items():
                answer += f"{risk_type} ({count}), "
            answer = answer.rstrip(", ") + "."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "riskLevel": level,
            "highestRiskLevel": highest,
            "highRiskCount": high_risk_count,
            "totalRecords": total,
            "percentHighRisk": pct_high_risk,
            "riskBreakdown": risk_summary.get("riskBreakdown", {})
        }
    }


def generate_change_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for change-related questions using LLM with full blob context"""
    from llm_service import get_llm_service
    
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    risk_summary = context.get("riskSummary", {})
    design_changes = risk_summary.get("designChangedCount", 0)
    supplier_changes = risk_summary.get("supplierChangedCount", 0)
    quantity_changes = risk_summary.get("quantityChangedCount", 0)
    
    pct_changed = (changed / total * 100) if total > 0 else 0
    
    # Build context for LLM
    change_context = {
        "changedRecordCount": changed,
        "totalRecords": total,
        "percentChanged": pct_changed,
        "designChanges": design_changes,
        "supplierChanges": supplier_changes,
        "quantityChanges": quantity_changes
    }
    
    # Try to use LLM with full blob context
    try:
        llm_service = get_llm_service()
        answer = llm_service.generate_response(
            prompt="How many records have changed?",
            context=change_context,
            detail_records=detail_records  # Pass ALL blob records for full context
        )
    except Exception as e:
        logging.warning(f"LLM generation failed: {str(e)}. Using template.")
        answer = f"{changed:,} records have changed out of {total:,} total ({pct_changed:.1f}%). "
        answer += f"Breakdown: Design ({design_changes}), Supplier ({supplier_changes}), Quantity ({quantity_changes})."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "changedRecordCount": changed,
            "totalRecords": total,
            "percentChanged": pct_changed,
            "designChanges": design_changes,
            "supplierChanges": supplier_changes,
            "quantityChanges": quantity_changes
        }
    }


def generate_general_answer(detail_records: list, context: dict) -> dict:
    """Generate general answer when question type is unclear"""
    health = context.get("planningHealth", 0)
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    answer = f"Planning health is {health}/100. {changed:,} of {total:,} records have changed. "
    answer += "Ask about health, forecast, risks, or changes for more details."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "planningHealth": health,
            "changedRecordCount": changed,
            "totalRecords": total
        }
    }


def generate_greeting_answer(detail_records: list, context: dict, question: str) -> dict:
    """
    Generate greeting answer using ChatGPT with full blob context.
    Routes simple greetings to LLM for natural, conversational responses.
    Passes complete detail_records so ChatGPT understands the full data context.
    """
    try:
        from llm_service import get_llm_service
        
        # Build context with all available metrics
        health = context.get("planningHealth", 0)
        total = len(detail_records)
        changed = sum(1 for r in detail_records if r.get("changed"))
        
        # Create comprehensive context for LLM
        greeting_context = {
            "planningHealth": health,
            "totalRecords": total,
            "changedRecords": changed,
            "changeRate": round((changed / total * 100) if total > 0 else 0, 1),
            # Include all available context from the dashboard
            "drivers": context.get("drivers", {}),
            "riskSummary": context.get("riskSummary", {}),
            "supplierSummary": context.get("supplierSummary", {}),
            "materialSummary": context.get("materialSummary", {})
        }
        
        # Get LLM service and generate response with FULL detail_records
        llm_service = get_llm_service()
        answer = llm_service.generate_response(
            prompt=question,
            context=greeting_context,
            detail_records=detail_records  # Pass ALL blob records for full context
        )
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "planningHealth": health,
                "changedRecordCount": changed,
                "totalRecords": total
            }
        }
    except Exception as e:
        logging.error(f"Error generating greeting answer: {str(e)}")
        # Fallback to generic greeting if LLM fails
        health = context.get("planningHealth", 0)
        total = len(detail_records)
        changed = sum(1 for r in detail_records if r.get("changed"))
        
        answer = f"Hello! I'm your Planning Intelligence Copilot. "
        answer += f"Currently, planning health is {health}/100 with {changed:,} of {total:,} records changed. "
        answer += "Ask me about health, forecast, risks, or changes for more details."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "planningHealth": health,
                "changedRecordCount": changed,
                "totalRecords": total
            }
        }


def generate_design_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for design change questions using LLM with full blob context"""
    from copilot_helpers import get_records_by_change_type, get_unique_suppliers, get_unique_materials
    from llm_service import get_llm_service
    
    design_records = get_records_by_change_type(detail_records, "design")
    if not design_records:
        return {
            "answer": "No design changes detected in the current data.",
            "supportingMetrics": {"designChangedCount": 0, "totalRecords": len(detail_records)}
        }
    
    suppliers = get_unique_suppliers(design_records)
    materials = get_unique_materials(design_records)
    
    # Build context for LLM
    design_context = {
        "designChangedCount": len(design_records),
        "totalRecords": len(detail_records),
        "affectedSuppliers": suppliers,
        "affectedMaterials": materials,
        "question": question
    }
    
    # Try to use LLM with full blob context
    try:
        llm_service = get_llm_service()
        answer = llm_service.generate_response(
            prompt=question,
            context=design_context,
            detail_records=detail_records  # Pass ALL blob records for full context
        )
    except Exception as e:
        logging.warning(f"LLM generation failed: {str(e)}. Using template.")
        answer = f"{len(design_records)} records have design changes (BOD or Form Factor). "
        if suppliers:
            answer += f"Affected suppliers: {', '.join(suppliers[:3])}. "
        if materials:
            answer += f"Affected materials: {', '.join(materials[:3])}."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "designChangedCount": len(design_records),
            "totalRecords": len(detail_records),
            "affectedSuppliers": suppliers,
            "affectedMaterials": materials
        }
    }


def generate_schedule_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for ROJ/schedule change questions using LLM with full blob context"""
    from copilot_helpers import compute_roi_metrics
    from llm_service import get_llm_service
    
    schedule_records = [r for r in detail_records if r.get("rojChanged", False)]
    if not schedule_records:
        return {
            "answer": "No ROJ (Release of Judgment) schedule changes detected.",
            "supportingMetrics": {"roiChangedCount": 0, "totalRecords": len(detail_records)}
        }
    
    metrics = compute_roi_metrics(schedule_records)
    
    # Build context for LLM
    schedule_context = {
        "roiChangedCount": metrics.get("roiChangedCount", 0),
        "totalRecords": len(detail_records),
        "averageRoiDelta": metrics.get("averageRoiDelta", 0),
        "question": question
    }
    
    # Try to use LLM with full blob context
    try:
        llm_service = get_llm_service()
        answer = llm_service.generate_response(
            prompt=question,
            context=schedule_context,
            detail_records=detail_records  # Pass ALL blob records for full context
        )
    except Exception as e:
        logging.warning(f"LLM generation failed: {str(e)}. Using template.")
        answer = f"{metrics['roiChangedCount']} records have ROJ schedule changes. "
        if metrics['averageRoiDelta'] != 0:
            answer += f"Average ROJ delta: {metrics['averageRoiDelta']} days."
    
    return {
        "answer": answer,
        "supportingMetrics": metrics
    }




def generate_location_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for location-specific questions using LLM with full blob context"""
    from copilot_helpers import extract_location_id, filter_records_by_location, get_top_locations_by_change
    from llm_service import get_llm_service
    
    location_id = extract_location_id(question)
    
    if location_id:
        # Specific location query
        location_records = filter_records_by_location(detail_records, location_id)
        if not location_records:
            return {
                "answer": f"No records found for location {location_id}.",
                "supportingMetrics": {"location": location_id, "recordCount": 0}
            }
        
        changed = sum(1 for r in location_records if r.get("changed"))
        
        # Build context for LLM
        location_context = {
            "location": location_id,
            "recordCount": len(location_records),
            "changedCount": changed,
            "changeRate": round((changed / len(location_records) * 100) if location_records else 0, 1),
            "question": question
        }
        
        # Try to use LLM with full blob context
        try:
            llm_service = get_llm_service()
            answer = llm_service.generate_response(
                prompt=question,
                context=location_context,
                detail_records=detail_records  # Pass ALL blob records for full context
            )
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = f"Location {location_id}: {len(location_records)} records total, {changed} changed."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "location": location_id,
                "recordCount": len(location_records),
                "changedCount": changed
            }
        }
    else:
        # Top locations query
        top_locations = get_top_locations_by_change(detail_records, limit=5)
        if not top_locations:
            return {
                "answer": "No location changes detected.",
                "supportingMetrics": {"topLocations": []}
            }
        
        # Build context for LLM
        location_context = {
            "topLocations": top_locations,
            "totalRecords": len(detail_records),
            "question": question
        }
        
        # Try to use LLM with full blob context
        try:
            llm_service = get_llm_service()
            answer = llm_service.generate_response(
                prompt=question,
                context=location_context,
                detail_records=detail_records  # Pass ALL blob records for full context
            )
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = "Top locations by change count: "
            answer += ", ".join([f"{loc[0]} ({loc[1]} changes)" for loc in top_locations]) + "."
        
        return {
            "answer": answer,
            "supportingMetrics": {"topLocations": top_locations}
        }


def generate_material_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for material-specific questions using LLM with full blob context"""
    from copilot_helpers import extract_material_id, filter_records_by_change_type, get_top_materials_by_change
    from llm_service import get_llm_service
    
    material_id = extract_material_id(question)
    
    if material_id:
        # Specific material query
        material_records = [r for r in detail_records if r.get("materialGroup") == material_id]
        if not material_records:
            return {
                "answer": f"No records found for material {material_id}.",
                "supportingMetrics": {"material": material_id, "recordCount": 0}
            }
        
        changed = sum(1 for r in material_records if r.get("changed"))
        
        # Build context for LLM
        material_context = {
            "material": material_id,
            "recordCount": len(material_records),
            "changedCount": changed,
            "changeRate": round((changed / len(material_records) * 100) if material_records else 0, 1),
            "question": question
        }
        
        # Try to use LLM with full blob context
        try:
            llm_service = get_llm_service()
            answer = llm_service.generate_response(
                prompt=question,
                context=material_context,
                detail_records=detail_records  # Pass ALL blob records for full context
            )
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = f"Material {material_id}: {len(material_records)} records total, {changed} changed."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "material": material_id,
                "recordCount": len(material_records),
                "changedCount": changed
            }
        }
    else:
        # Top materials query
        top_materials = get_top_materials_by_change(detail_records, limit=5)
        if not top_materials:
            return {
                "answer": "No material changes detected.",
                "supportingMetrics": {"topMaterials": []}
            }
        
        # Build context for LLM
        material_context = {
            "topMaterials": top_materials,
            "totalRecords": len(detail_records),
            "question": question
        }
        
        # Try to use LLM with full blob context
        try:
            llm_service = get_llm_service()
            answer = llm_service.generate_response(
                prompt=question,
                context=material_context,
                detail_records=detail_records  # Pass ALL blob records for full context
            )
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = "Top materials by change count: "
            answer += ", ".join([f"{mat[0]} ({mat[1]} changes)" for mat in top_materials]) + "."
        
        return {
            "answer": answer,
            "supportingMetrics": {"topMaterials": top_materials}
        }


def generate_entity_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for entity questions (suppliers, materials, locations) using LLM with full blob context"""
    from copilot_helpers import extract_location_id, filter_records_by_location, get_unique_suppliers, get_unique_materials, get_impact_ranking
    from llm_service import get_llm_service
    
    location_id = extract_location_id(question)
    
    if location_id:
        # Filter to specific location
        location_records = filter_records_by_location(detail_records, location_id)
        if not location_records:
            return {
                "answer": f"No records found for location {location_id}.",
                "supportingMetrics": {"location": location_id, "recordCount": 0}
            }
        
        suppliers = get_unique_suppliers(location_records)
        materials = get_unique_materials(location_records)
        changed = sum(1 for r in location_records if r.get("changed"))
        
        # Build context for LLM
        entity_context = {
            "location": location_id,
            "recordCount": len(location_records),
            "suppliers": suppliers,
            "materials": materials,
            "changedCount": changed,
            "question": question
        }
        
        # Try to use LLM with full blob context
        try:
            llm_service = get_llm_service()
            answer = llm_service.generate_response(
                prompt=question,
                context=entity_context,
                detail_records=detail_records  # Pass ALL blob records for full context
            )
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = f"Location {location_id}: {len(location_records)} records. "
            if suppliers:
                answer += f"Suppliers: {', '.join(suppliers[:5])}. "
            if materials:
                answer += f"Materials: {', '.join(materials[:5])}. "
            answer += f"Changed: {changed}."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "location": location_id,
                "recordCount": len(location_records),
                "suppliers": suppliers,
                "materials": materials,
                "changedCount": changed
            }
        }
    else:
        # General entity question
        impact = get_impact_ranking(detail_records)
        top_suppliers = impact["suppliers"][:5]
        top_materials = impact["materials"][:5]
        
        # Build context for LLM
        entity_context = {
            "topSuppliers": top_suppliers,
            "topMaterials": top_materials,
            "totalRecords": len(detail_records),
            "question": question
        }
        
        # Try to use LLM with full blob context
        try:
            llm_service = get_llm_service()
            answer = llm_service.generate_response(
                prompt=question,
                context=entity_context,
                detail_records=detail_records  # Pass ALL blob records for full context
            )
        except Exception as e:
            logging.warning(f"LLM generation failed: {str(e)}. Using template.")
            answer = "Top affected suppliers: "
            if top_suppliers:
                answer += ", ".join([f"{s[0]} ({s[1]} changes)" for s in top_suppliers]) + ". "
            else:
                answer += "None. "
            answer += "Top affected materials: "
            if top_materials:
                answer += ", ".join([f"{m[0]} ({m[1]} changes)" for m in top_materials]) + "."
            else:
                answer += "None."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "topSuppliers": top_suppliers,
                "topMaterials": top_materials
            }
        }


def generate_comparison_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for comparison questions using LLM with full blob context"""
    import re
    from copilot_helpers import filter_records_by_location
    from llm_service import get_llm_service
    
    # Extract location IDs from question
    locations = re.findall(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', question)
    
    if len(locations) < 2:
        return {
            "answer": "Please specify two locations to compare (e.g., 'Compare CYS20_F01C01 vs DSM18_F01C01').",
            "supportingMetrics": {}
        }
    
    loc1, loc2 = locations[0], locations[1]
    records1 = filter_records_by_location(detail_records, loc1)
    records2 = filter_records_by_location(detail_records, loc2)
    
    changed1 = sum(1 for r in records1 if r.get("changed"))
    changed2 = sum(1 for r in records2 if r.get("changed"))
    
    # Build context for LLM
    comparison_context = {
        "location1": loc1,
        "location1Records": len(records1),
        "location1Changed": changed1,
        "location2": loc2,
        "location2Records": len(records2),
        "location2Changed": changed2,
        "question": question
    }
    
    # Try to use LLM with full blob context
    try:
        llm_service = get_llm_service()
        answer = llm_service.generate_response(
            prompt=question,
            context=comparison_context,
            detail_records=detail_records  # Pass ALL blob records for full context
        )
    except Exception as e:
        logging.warning(f"LLM generation failed: {str(e)}. Using template.")
        answer = f"Comparison: {loc1} vs {loc2}. "
        answer += f"{loc1}: {len(records1)} records, {changed1} changed. "
        answer += f"{loc2}: {len(records2)} records, {changed2} changed."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "location1": loc1,
            "location1Records": len(records1),
            "location1Changed": changed1,
            "location2": loc2,
            "location2Records": len(records2),
            "location2Changed": changed2
        }
    }


def generate_impact_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for impact questions using LLM with full blob context"""
    from copilot_helpers import get_impact_ranking
    from llm_service import get_llm_service
    
    impact = get_impact_ranking(detail_records)
    top_suppliers = impact["suppliers"][:3]
    top_materials = impact["materials"][:3]
    
    # Build context for LLM
    impact_context = {
        "topSuppliers": top_suppliers,
        "topMaterials": top_materials,
        "totalRecords": len(detail_records),
        "changedRecords": sum(1 for r in detail_records if r.get("changed"))
    }
    
    # Try to use LLM with full blob context
    try:
        llm_service = get_llm_service()
        answer = llm_service.generate_response(
            prompt="What is the impact of changes?",
            context=impact_context,
            detail_records=detail_records  # Pass ALL blob records for full context
        )
    except Exception as e:
        logging.warning(f"LLM generation failed: {str(e)}. Using template.")
        answer = "Impact analysis: "
        if top_suppliers:
            answer += "Top suppliers affected: "
            answer += ", ".join([f"{s[0]} ({s[1]} changes)" for s in top_suppliers]) + ". "
        if top_materials:
            answer += "Top materials affected: "
            answer += ", ".join([f"{m[0]} ({m[1]} changes)" for m in top_materials]) + "."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "topSuppliers": top_suppliers,
            "topMaterials": top_materials
        }
    }


@app.route(route="explain", methods=["POST", "OPTIONS"])
def explain(req: func.HttpRequest) -> func.HttpResponse:
    """
    Explainability endpoint - provides detailed explanations for dashboard insights.
    Analyzes questions and returns specific, data-driven answers.
    """
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    logging.info("Explain endpoint triggered.")
    
    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON body.", 400)
    
    question = body.get("question", "").strip()
    if not question:
        return _error("question is required", 400)
    
    logging.info(f"Question: {question}")
    
    # Get context from request
    context = body.get("context", {})
    detail_records = context.get("detailRecords", [])
    
    # If no records in context, try to load from snapshot
    if not detail_records:
        snap = load_snapshot()
        if snap:
            detail_records = snap.get("detailRecords", [])
            context = snap
    
    if not detail_records:
        logging.warning("No detail records available")
        return _error("No detail records available. Run daily-refresh first.", 404)
    
    logging.info(f"Processing question with {len(detail_records)} records")
    
    # Normalize records
    detail_records = _normalize_detail_records(detail_records)
    
    # Validate question length
    if len(question) > 500:
        return _error("Question too long (max 500 characters)", 400)
    
    # Classify question
    q_type = classify_question(question)
    logging.info(f"Question type: {q_type}")
    
    # Generate answer based on question type
    try:
        if q_type == "greeting":
            result = generate_greeting_answer(detail_records, context, question)
        elif q_type == "health":
            result = generate_health_answer(detail_records, context)
        elif q_type == "forecast":
            result = generate_forecast_answer(detail_records, context, question)
        elif q_type == "risk":
            result = generate_risk_answer(detail_records, context)
        elif q_type == "change":
            result = generate_change_answer(detail_records, context)
        elif q_type == "entity":
            result = generate_entity_answer(detail_records, context, question)
        elif q_type == "comparison":
            result = generate_comparison_answer(detail_records, context, question)
        elif q_type == "impact":
            result = generate_impact_answer(detail_records, context)
        elif q_type == "design":
            result = generate_design_answer(detail_records, context, question)
        elif q_type == "schedule":
            result = generate_schedule_answer(detail_records, context, question)
        elif q_type == "location":
            result = generate_location_answer(detail_records, context, question)
        elif q_type == "material":
            result = generate_material_answer(detail_records, context, question)
        else:
            result = generate_general_answer(detail_records, context)
        
        answer = result.get("answer", "Unable to generate answer")
        supporting_metrics = result.get("supportingMetrics", {})
        
        logging.info(f"Generated answer: {answer[:100]}...")
        
    except Exception as e:
        logging.error(f"Error generating answer: {str(e)}")
        answer = "Unable to generate answer. Please try a different question."
        supporting_metrics = {}
    
    # Build MCP context with computed metrics
    mcp_context = {
        "computedMetrics": {
            "totalRecords": len(detail_records),
            "changedRecords": sum(1 for r in detail_records if r.get("changed")),
            "changeRate": round((sum(1 for r in detail_records if r.get("changed")) / len(detail_records) * 100) if detail_records else 0, 1),
            "riskLevel": context.get("riskSummary", {}).get("level", "Unknown"),
            "healthScore": context.get("planningHealth", 0)
        },
        "drivers": context.get("drivers", {}),
        "riskSummary": context.get("riskSummary", {}),
        "supplierSummary": context.get("supplierSummary", {}),
        "materialSummary": context.get("materialSummary", {}),
        "blobFileName": "current.csv",
        "lastRefreshed": get_last_updated_time()
    }
    
    # Build response
    response = {
        "question": question,
        "answer": answer,
        "queryType": q_type,
        "supportingMetrics": supporting_metrics,
        "mcpContext": mcp_context,
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
    }
    
    logging.info("Explain endpoint returning response")
    return _cors_response(json.dumps(response, default=str))


@app.route(route="debug-snapshot", methods=["POST", "OPTIONS"])
def debug_snapshot(req: func.HttpRequest) -> func.HttpResponse:
    """
    Debug endpoint — returns snapshot with intermediate pipeline values.
    """
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    logging.info("Debug snapshot endpoint triggered.")
    
    try:
        body = req.get_json()
    except ValueError:
        body = {}
    
    location_id: Optional[str] = body.get("location_id") if body else None
    material_group: Optional[str] = body.get("material_group") if body else None
    
    snap = load_snapshot()
    if not snap:
        return _error("No snapshot available. Run daily-refresh first.", 404)
    
    if location_id or material_group:
        snap = _filter_snapshot(snap, location_id, material_group)
    
    return _cors_response(json.dumps(snap, default=str))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _filter_snapshot(snap: dict, location_id: Optional[str], material_group: Optional[str]) -> dict:
    """Filter snapshot by location and/or material group."""
    if not location_id and not material_group:
        return snap
    
    detail_records = snap.get("detailRecords", [])
    filtered = detail_records
    
    if location_id:
        filtered = [r for r in filtered if r.get("locationId") == location_id]
    
    if material_group:
        filtered = [r for r in filtered if r.get("materialGroup") == material_group]
    
    snap["detailRecords"] = filtered
    snap["totalRecords"] = len(filtered)
    snap["changedRecordCount"] = sum(1 for r in filtered if r.get("changed"))
    
    return snap
