"""
Planning Intelligence Azure Functions - Ollama Integration
Minimal endpoints for production use:
- planning-dashboard-v2: Blob-backed dashboard
- planning_intelligence_nlp: NLP query processing
- explain: Explainability endpoint
- debug-snapshot: Debug endpoint
- daily-refresh: Background refresh

LLM Integration: Uses Ollama (local models) instead of Azure OpenAI
Models supported: Mistral, Llama 2, Neural Chat
"""

import json
import logging
from typing import Optional, List
import azure.functions as func
import os

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
from context_optimizer import extract_record_keys

# Import async Ollama service for non-blocking LLM calls
# These functions trigger background LLM generation and retrieve cached responses
from async_ollama_service import trigger_async_generation, get_enhanced_answer

# Import Ollama service
try:
    from ollama_llm_service import get_ollama_service
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Ollama service not available, will use fallback responses")

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logger = logging.getLogger(__name__)


# ============================================================================
# LLM SERVICE HELPER
# ============================================================================

def get_llm_service():
    """
    Get LLM service - uses Ollama only (local models, no API costs)
    
    Returns:
        OllamaLLMService instance
    
    Raises:
        Exception if Ollama is not available
    """
    
    if not OLLAMA_AVAILABLE:
        raise Exception("Ollama service not available. Install with: pip install ollama_llm_service")
    
    try:
        model = os.getenv("OLLAMA_MODEL", "mistral")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))  # 120 seconds default
        
        logger.info(f"Initializing Ollama service with model: {model}, timeout: {timeout}s")
        service = get_ollama_service(model=model, base_url=base_url, timeout=timeout)
        
        # Check if Ollama is available
        if service.is_available():
            logger.info(f"✓ Ollama service ready with model: {model}")
            return service
        else:
            error_msg = f"Ollama not running at {base_url}. Start Ollama with: ollama serve"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    except Exception as e:
        error_msg = f"Failed to initialize Ollama service: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


# ============================================================================
# SUPPORTING METRICS HELPER
# ============================================================================

def _build_supporting_metrics(detail_records: list, context: dict, **kwargs) -> dict:
    """
    Build standardized supporting metrics for all answer functions.
    Ensures consistent structure for frontend display.
    """
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    metrics = {
        "planningHealth": context.get("planningHealth", 0),
        "changedRecordCount": changed,
        "totalRecords": total,
        "trendDelta": context.get("trendDelta", 0),
        "status": context.get("status", "Unknown"),
        "trendDirection": context.get("trendDirection", "Stable"),
    }
    
    # Add any additional metrics passed in
    metrics.update(kwargs)
    
    return metrics


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
    - GSCROJNBDLASTCHANGEDDATE → rojLastChangedDate
    - GSCROJNBDCREATIONDATE → rojCreationDate
    - NBD_DeltaDays → rojDelta
    - NBD_Change Type → changeType
    - ZCOIBODVER → bodCurrent
    - ZCOIFORMFACT → ffCurrent
    - GSCSUPLDATE → supplierDate
    - GSCPREVSUPLDATE → supplierDatePrevious
    
    Computed Fields:
    - qtyDelta = forecastQty - forecastQtyPrevious
    - rojDelta = NBD_DeltaDays or days between rojCurrent and rojPrevious
    - qtyChanged = qtyDelta != 0
    - supplierChanged = supplier != supplierPrevious
    - designChanged = bodCurrent != bodPrevious OR ffCurrent != ffPrevious
    - rojChanged = determined by precedence (see below)
    
    ROJ Change Precedence:
    1. If rojChanged already set, preserve it
    2. Else if scheduleChanged set, map to rojChanged
    3. Else if NBD_DeltaDays exists and non-zero, set rojChanged = True
    4. Else if rojCurrent and rojPrevious differ, set rojChanged = True
    5. Else rojChanged = False
    """
    if not records:
        return []
    
    normalized = []
    roj_stats = {
        "with_rojCurrent": 0,
        "with_rojPrevious": 0,
        "with_rojLastChangedDate": 0,
        "with_rojCreationDate": 0,
        "with_nonzero_rojDelta": 0,
        "with_rojChanged_true": 0,
        "with_scheduleChanged_true": 0,
    }
    
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
                
                # ROJ fields - explicit extraction from CSV columns
                roj_current = r.get("rojCurrent") or r.get("GSCCONROJDATE") or r.get("roj_current")
                roj_previous = r.get("rojPrevious") or r.get("GSCPREVROJNBD") or r.get("roj_previous")
                roj_last_changed_date = r.get("rojLastChangedDate") or r.get("GSCROJNBDLASTCHANGEDDATE") or r.get("roj_last_changed_date")
                roj_creation_date = r.get("rojCreationDate") or r.get("GSCROJNBDCREATIONDATE") or r.get("roj_creation_date")
                
                # Track ROJ field population
                if roj_current:
                    roj_stats["with_rojCurrent"] += 1
                if roj_previous:
                    roj_stats["with_rojPrevious"] += 1
                if roj_last_changed_date:
                    roj_stats["with_rojLastChangedDate"] += 1
                if roj_creation_date:
                    roj_stats["with_rojCreationDate"] += 1
                
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
                
                # ROJ delta - use NBD_DeltaDays if available, otherwise compute from dates
                roj_delta = None
                nbd_delta_days = r.get("NBD_DeltaDays") or r.get("nbd_delta_days")
                
                if nbd_delta_days is not None:
                    try:
                        roj_delta = int(nbd_delta_days)
                    except (ValueError, TypeError):
                        roj_delta = None
                
                # If no NBD_DeltaDays, compute from dates
                if roj_delta is None and roj_current and roj_previous:
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
                
                if roj_delta and roj_delta != 0:
                    roj_stats["with_nonzero_rojDelta"] += 1
                
                # Determine change flags
                qty_changed = qty_delta != 0
                supplier_changed = supplier and supplier_previous and supplier != supplier_previous
                design_changed = (bod_current and bod_previous and bod_current != bod_previous) or \
                                (ff_current and ff_previous and ff_current != ff_previous)
                
                # ROJ change precedence (CRITICAL)
                roj_changed = False
                
                # 1. If rojChanged already set, preserve it
                if "rojChanged" in r and r.get("rojChanged") is True:
                    roj_changed = True
                # 2. Else if scheduleChanged set, map to rojChanged
                elif "scheduleChanged" in r and r.get("scheduleChanged") is True:
                    roj_changed = True
                    roj_stats["with_scheduleChanged_true"] += 1
                # 3. Else if NBD_DeltaDays exists and non-zero, set rojChanged = True
                elif roj_delta and roj_delta != 0:
                    roj_changed = True
                # 4. Else if rojCurrent and rojPrevious both exist and differ, set rojChanged = True
                elif roj_current and roj_previous and roj_current != roj_previous:
                    roj_changed = True
                # 5. Else rojChanged = False (default)
                
                if roj_changed:
                    roj_stats["with_rojChanged_true"] += 1
                
                changed = qty_changed or supplier_changed or design_changed or roj_changed
                
                # Validate required fields
                if not location_id:
                    logging.warning(f"Record missing locationId: {r}")
                    continue
                
                # Extract changeType from NBD_Change Type or fallback
                change_type = r.get("changeType") or r.get("NBD_Change Type") or r.get("change_type") or "Unchanged"
                
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
                    "rojLastChangedDate": roj_last_changed_date or None,
                    "rojCreationDate": roj_creation_date or None,
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
                    "changeType": change_type,
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
                
                # ROJ fields from object attributes
                roj_current = getattr(r, "roj_current", None)
                roj_previous = getattr(r, "roj_previous", None)
                roj_last_changed_date = getattr(r, "roj_last_changed_date", None)
                roj_creation_date = getattr(r, "roj_creation_date", None)
                
                # Track ROJ field population
                if roj_current:
                    roj_stats["with_rojCurrent"] += 1
                if roj_previous:
                    roj_stats["with_rojPrevious"] += 1
                if roj_last_changed_date:
                    roj_stats["with_rojLastChangedDate"] += 1
                if roj_creation_date:
                    roj_stats["with_rojCreationDate"] += 1
                
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
                
                # ROJ delta - use NBD_DeltaDays if available, otherwise compute from dates
                roj_delta = None
                nbd_delta_days = getattr(r, "nbd_delta_days", None)
                
                if nbd_delta_days is not None:
                    try:
                        roj_delta = int(nbd_delta_days)
                    except (ValueError, TypeError):
                        roj_delta = None
                
                # If no NBD_DeltaDays, compute from dates
                if roj_delta is None and roj_current and roj_previous:
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
                
                if roj_delta and roj_delta != 0:
                    roj_stats["with_nonzero_rojDelta"] += 1
                
                # Determine change flags
                qty_changed = qty_delta != 0
                supplier_changed = supplier and supplier_previous and supplier != supplier_previous
                design_changed = (bod_current and bod_previous and bod_current != bod_previous) or \
                                (ff_current and ff_previous and ff_current != ff_previous)
                
                # ROJ change precedence (CRITICAL)
                roj_changed = False
                
                # 1. If rojChanged already set, preserve it
                if hasattr(r, "rojChanged") and getattr(r, "rojChanged") is True:
                    roj_changed = True
                # 2. Else if scheduleChanged set, map to rojChanged
                elif hasattr(r, "scheduleChanged") and getattr(r, "scheduleChanged") is True:
                    roj_changed = True
                    roj_stats["with_scheduleChanged_true"] += 1
                # 3. Else if NBD_DeltaDays exists and non-zero, set rojChanged = True
                elif roj_delta and roj_delta != 0:
                    roj_changed = True
                # 4. Else if rojCurrent and rojPrevious both exist and differ, set rojChanged = True
                elif roj_current and roj_previous and roj_current != roj_previous:
                    roj_changed = True
                # 5. Else rojChanged = False (default)
                
                if roj_changed:
                    roj_stats["with_rojChanged_true"] += 1
                
                changed = qty_changed or supplier_changed or design_changed or roj_changed
                
                if not location_id:
                    logging.warning(f"Record missing locationId: {r}")
                    continue
                
                # Extract changeType
                change_type = getattr(r, "change_type", "Unchanged") or "Unchanged"
                
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
                    "rojLastChangedDate": roj_last_changed_date or None,
                    "rojCreationDate": roj_creation_date or None,
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
                    "changeType": change_type,
                    "dcSite": getattr(r, "dc_site", None),
                    "metro": getattr(r, "metro", None),
                    "country": getattr(r, "country", None),
                    "isSupplierDateMissing": getattr(r, "is_supplier_date_missing", False),
                }
                normalized.append(norm)
        except Exception as e:
            logging.warning(f"Failed to normalize record: {e}. Skipping.")
            continue
    
    # Log ROJ normalization statistics
    logging.info(f"[NORMALIZATION] Normalized {len(normalized)} records from {len(records)} input records")
    logging.info(f"[NORMALIZATION] ROJ field population:")
    logging.info(f"  - Records with rojCurrent: {roj_stats['with_rojCurrent']}")
    logging.info(f"  - Records with rojPrevious: {roj_stats['with_rojPrevious']}")
    logging.info(f"  - Records with rojLastChangedDate: {roj_stats['with_rojLastChangedDate']}")
    logging.info(f"  - Records with rojCreationDate: {roj_stats['with_rojCreationDate']}")
    logging.info(f"  - Records with non-zero rojDelta: {roj_stats['with_nonzero_rojDelta']}")
    logging.info(f"  - Records with rojChanged=True: {roj_stats['with_rojChanged_true']}")
    logging.info(f"  - Records with scheduleChanged=True: {roj_stats['with_scheduleChanged_true']}")
    
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


@app.route(route="initialize-copilot", methods=["POST", "OPTIONS"])
def initialize_copilot(req: func.HttpRequest) -> func.HttpResponse:
    """
    Initialize copilot with LLM analysis of the full dataset.
    Called once when the UI loads to cache the LLM's analysis.
    Subsequent questions will use this cached analysis for fast responses.
    """
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    logging.info("Initializing copilot with LLM analysis...")
    
    try:
        # Load snapshot with all data
        snap = load_snapshot()
        if not snap:
            return _error("No snapshot available. Run daily-refresh first.", 404)
        
        detail_records = snap.get("detailRecords", [])
        if not detail_records:
            return _error("No detail records in snapshot.", 404)
        
        logging.info(f"Generating initial LLM analysis for {len(detail_records)} records...")
        
        # Generate initial analysis
        from llm_analysis_cache import generate_initial_analysis, set_cached_analysis
        llm_service = get_llm_service()
        analysis = generate_initial_analysis(llm_service, detail_records, snap)
        
        # Cache the analysis
        snapshot_date = snap.get("lastRefreshedAt", "current")
        set_cached_analysis(snapshot_date, analysis)
        
        logging.info("Copilot initialization complete")
        
        return _cors_response(json.dumps({
            "status": "initialized",
            "message": "Copilot analysis cached and ready",
            "analysisLength": len(analysis),
            "recordsAnalyzed": len(detail_records),
            "timestamp": snapshot_date
        }, default=str))
    
    except Exception as e:
        error_msg = f"Copilot initialization failed: {str(e)}"
        logging.error(error_msg)
        return _error(error_msg, 500)


@app.route(route="daily-refresh", methods=["POST", "OPTIONS"])
def daily_refresh(req: func.HttpRequest) -> func.HttpResponse:
    """
    Triggers daily refresh from CSV files (or Blob Storage if CSV_USE_BLOB=true).
    Loads planning data, runs analytics pipeline, and saves snapshot.
    """
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    # Check if we should use Blob Storage instead of CSV
    use_csv = os.environ.get("CSV_USE_BLOB", "false").lower() != "true"
    data_source = "CSV files" if use_csv else "Blob Storage"
    
    logging.info(f"Daily refresh triggered — loading from {data_source}.")
    try:
        from run_daily_refresh import run_daily_refresh
        result = run_daily_refresh(use_csv=use_csv)
        return _cors_response(json.dumps({
            "status": "ok",
            "dataSource": data_source,
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
    0. Transform: "table", "tabular", "format", "show as", "display as", "convert to" (CHECK FIRST - deterministic)
    1. Greeting: "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"
    2. Comparison: "compare", "vs", "versus", "difference", "between"
    3. Impact: "impact", "most impact", "most affected", "most changed", "consequence", "which" + "most"
    4. Schedule/ROJ: "roj", "schedule", "nbd", "need by", "release of judgment", "judgment" (CHECK BEFORE generic change)
    5. Entity: "list", "which" + entity keywords, "supplier", "material", "location", "group"
    6. Change: "change", "changed", "changes" (but not in entity/impact context)
    7. Design: "design", "bod", "form factor", "ff"
    8. Forecast: "forecast", "trend", "delta", "increase", "decrease", "units"
    9. Location: "location", "locations", "datacenter", "site", "dc", "facility"
    10. Risk: "risk", "risks", "risky", "danger", "dangerous", "issue", "main issue"
    11. Health: "health", "status", "score", "critical", "stable", "planning"
    12. General: fallback
    """
    q_lower = question.lower()
    
    # 0. Transform questions - CHECK FIRST (deterministic, no LLM needed)
    # These should NOT call LLM, just format cached response
    transform_keywords = [
        "transform to table",
        "tabular form",
        "tabular",
        "show in table",
        "convert to table",
        "format as table",
        "structured table",
        "show as table",
        "display as table",
        "show as",
        "display as",
        "convert to",
        "format as",
        "in table",
        "as table",
        "spreadsheet",
        "csv"
    ]
    
    for keyword in transform_keywords:
        if keyword in q_lower:
            return "transform"
    
    # 1. Greeting questions - CHECK FIRST (simple greetings should route to ChatGPT)
    if any(word in q_lower for word in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
        # Make sure it's actually a greeting (short, simple message)
        if len(question.split()) <= 3:  # Greetings are typically 1-3 words
            return "greeting"
    
    # 2. Comparison questions - CHECK FIRST (most specific)
    if any(word in q_lower for word in ["compare", "vs", "versus", "difference", "between"]):
        return "comparison"
    
    # 3. Impact questions - CHECK EARLY (before change which uses "changes")
    # Impact questions ask about impact, most affected, most changed, consequences
    if any(word in q_lower for word in ["impact", "consequence", "affected by"]):
        return "impact"
    
    # Check for "which" + "most" (most affected, most changed, most impact, most changes)
    if "which" in q_lower and "most" in q_lower:
        return "impact"
    
    # 4. Schedule/ROJ questions - CHECK BEFORE generic change detection
    # This prevents "summary of ROJ changes" from being classified as "change"
    if any(word in q_lower for word in ["roj", "schedule", "nbd", "need by", "release of judgment", "judgment"]):
        return "schedule"
    
    # 5. Entity questions - CHECK AFTER SCHEDULE (to catch "supplier changes", "material changes", etc.)
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
    
    # 6. Change questions - CHECK AFTER SCHEDULE/ROJ (to avoid misclassifying ROJ changes)
    # Change questions ask about what changed, how many changed, quantity changes, design changes, etc.
    # But NOT when it's part of an entity or impact question
    if any(word in q_lower for word in ["change", "changed", "changes"]):
        # Exclude if it's part of an entity question (e.g., "Which suppliers have design changes?")
        if not ("which" in q_lower and any(word in q_lower for word in ["supplier", "material", "location", "group"])):
            # Exclude if it's part of an impact question (e.g., "Which supplier has the most changes?")
            if not ("which" in q_lower and "most" in q_lower):
                return "change"
    
    # 7. Design questions
    if any(word in q_lower for word in ["design", "bod", "form factor", "ff"]):
        return "design"
    
    # 8. Forecast questions
    if any(word in q_lower for word in ["forecast", "trend", "delta", "increase", "decrease", "units"]):
        return "forecast"
    
    # 9. Location questions
    if any(word in q_lower for word in ["location", "locations", "datacenter", "site", "dc", "facility"]):
        return "location"
    
    # 10. Risk questions - CHECK BEFORE HEALTH (health uses "status" which is too broad)
    if any(word in q_lower for word in ["risk", "risks", "risky", "danger", "dangerous", "high-risk", "top risk", "issue", "main issue"]):
        return "risk"
    
    # 11. Health questions
    if any(word in q_lower for word in ["health", "status", "score", "critical", "stable", "planning"]):
        return "health"
    
    # 12. Default
    else:
        return "general"


def generate_health_answer(detail_records: list, context: dict, use_llm: bool = True) -> dict:
    """Generate answer for health-related questions using ASYNC LLM"""
    health = context.get("planningHealth", 0)
    status = context.get("status", "Unknown")
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    pct_changed = (changed / total * 100) if total > 0 else 0
    
    risk_summary = context.get("riskSummary", {})
    design_changes = risk_summary.get("designChangedCount", 0)
    supplier_changes = risk_summary.get("supplierChangedCount", 0)
    
    # Build template response (returned immediately)
    template_answer = f"Planning health is {health}/100 ({status}). {changed:,} of {total:,} records have changed ({pct_changed:.1f}%). "
    template_answer += f"Primary drivers: Design changes ({design_changes}), Supplier changes ({supplier_changes})."
    
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
        "trendDelta": context.get("trendDelta", 0),
        "riskLevel": risk_summary.get("level", "Unknown")
    }
    
    # Trigger async LLM generation (non-blocking)
    if use_llm:
        try:
            question = "What is the current planning health status?"
            trigger_async_generation(question, supporting_metrics, detail_records)
            logging.info(f"[ASYNC] Health answer LLM generation triggered")
        except Exception as e:
            logging.warning(f"Could not trigger async LLM: {e}")
    
    # Return template immediately (LLM will enhance it in background)
    answer = get_enhanced_answer(template_answer, "What is the current planning health status?", supporting_metrics)
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


def generate_forecast_answer(detail_records: list, context: dict, question: str = "", use_llm: bool = True) -> dict:
    """Generate answer for forecast-related questions using ASYNC LLM"""
    forecast_new = context.get("forecastNew", 0)
    forecast_old = context.get("forecastOld", 0)
    delta = context.get("trendDelta", 0)
    trend = context.get("trendDirection", "Stable")
    
    pct_change = (delta / forecast_old * 100) if forecast_old > 0 else 0
    
    # Build template response (returned immediately)
    template_answer = f"Current forecast is {forecast_new:,.0f} units. Previous was {forecast_old:,.0f} units. "
    template_answer += f"Change: {delta:+,.0f} units ({pct_change:+.1f}%). Trend: {trend}."
    
    # Build consistent supporting metrics
    supporting_metrics = _build_supporting_metrics(
        detail_records, context,
        forecastNew=forecast_new,
        forecastOld=forecast_old,
        percentChange=pct_change
    )
    
    # Trigger async LLM generation (non-blocking)
    if use_llm:
        try:
            forecast_question = question or "What is the forecast for the next period?"
            trigger_async_generation(forecast_question, supporting_metrics, detail_records)
            logging.info(f"[ASYNC] Forecast answer LLM generation triggered")
        except Exception as e:
            logging.warning(f"Could not trigger async LLM: {e}")
    
    # Return template immediately (LLM will enhance it in background)
    forecast_question = question or "What is the forecast for the next period?"
    answer = get_enhanced_answer(template_answer, forecast_question, supporting_metrics)
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


def generate_risk_answer(detail_records: list, context: dict, use_llm: bool = True) -> dict:
    """Generate answer for risk-related questions using LLM service (synchronous)"""
    risk_summary = context.get("riskSummary", {})
    level = risk_summary.get("level", "Unknown")
    highest = risk_summary.get("highestRiskLevel", "Unknown")
    high_risk_count = risk_summary.get("highRiskCount", 0)
    total = len(detail_records)
    
    pct_high_risk = (high_risk_count / total * 100) if total > 0 else 0
    
    # Build template response (fallback)
    template_answer = f"Risk level is {level}. "
    template_answer += f"Highest risk type: {highest}. "
    template_answer += f"{high_risk_count:,} high-risk records out of {total:,} total ({pct_high_risk:.1f}%). "
    breakdown = risk_summary.get("riskBreakdown", {})
    if breakdown:
        template_answer += f"Breakdown: "
        for risk_type, count in breakdown.items():
            template_answer += f"{risk_type} ({count}), "
        template_answer = template_answer.rstrip(", ") + "."
    
    # Build consistent supporting metrics
    supporting_metrics = _build_supporting_metrics(
        detail_records, context,
        riskLevel=level,
        highestRiskLevel=highest,
        highRiskCount=high_risk_count,
        percentHighRisk=pct_high_risk,
        riskBreakdown=breakdown
    )
    
    # Call LLM synchronously with limited sample records
    answer = template_answer
    if use_llm:
        try:
            llm_service = get_llm_service()
            question = "What are the top risks in our supply chain?"
            prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
            # Pass only first 10 records to avoid timeout
            sample_records = detail_records[:10]
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context,
                detail_records=sample_records
            )
            logging.info(f"LLM generated risk answer: {answer[:100]}...")
        except Exception as e:
            logging.warning(f"LLM call failed: {str(e)}. Using template.")
            answer = template_answer
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


def generate_change_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for change-related questions using LLM service (synchronous)"""
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    risk_summary = context.get("riskSummary", {})
    design_changes = risk_summary.get("designChangedCount", 0)
    supplier_changes = risk_summary.get("supplierChangedCount", 0)
    quantity_changes = risk_summary.get("quantityChangedCount", 0)
    
    pct_changed = (changed / total * 100) if total > 0 else 0
    
    # Build template response (fallback)
    template_answer = f"{changed:,} records have changed out of {total:,} total ({pct_changed:.1f}%). "
    template_answer += f"Breakdown: Design ({design_changes}), Supplier ({supplier_changes}), Quantity ({quantity_changes})."
    
    # Build consistent supporting metrics
    supporting_metrics = _build_supporting_metrics(
        detail_records, context,
        percentChanged=pct_changed,
        designChanges=design_changes,
        supplierChanges=supplier_changes,
        quantityChanges=quantity_changes
    )
    
    # Call LLM synchronously with limited sample records
    answer = template_answer
    try:
        llm_service = get_llm_service()
        question = "How many records have changed?"
        prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
        # Pass only first 10 records to avoid timeout
        sample_records = detail_records[:10]
        answer = llm_service.generate_response(
            prompt=prompt,
            context=context,
            detail_records=sample_records
        )
        logging.info(f"LLM generated change answer: {answer[:100]}...")
    except Exception as e:
        logging.warning(f"LLM call failed: {str(e)}. Using template.")
        answer = template_answer
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


def generate_general_answer(detail_records: list, context: dict) -> dict:
    """Generate general answer when question type is unclear using LLM service (synchronous)"""
    health = context.get("planningHealth", 0)
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    # Build template response (fallback)
    template_answer = f"Planning health is {health}/100. {changed:,} of {total:,} records have changed. "
    template_answer += "Ask about health, forecast, risks, or changes for more details."
    
    # Build consistent supporting metrics
    supporting_metrics = _build_supporting_metrics(detail_records, context)
    
    # Call LLM synchronously with limited sample records
    answer = template_answer
    try:
        llm_service = get_llm_service()
        question = "What is the current planning status?"
        prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
        # Pass only first 10 records to avoid timeout
        sample_records = detail_records[:10]
        answer = llm_service.generate_response(
            prompt=prompt,
            context=context,
            detail_records=sample_records
        )
        logging.info(f"LLM generated general answer: {answer[:100]}...")
    except Exception as e:
        logging.warning(f"LLM call failed: {str(e)}. Using template.")
        answer = template_answer
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


def generate_greeting_answer(detail_records: list, context: dict, question: str) -> dict:
    """
    Generate greeting answer using cached LLM analysis.
    Routes simple greetings to LLM for natural, conversational responses.
    """
    from llm_analysis_cache import get_cached_analysis, build_prompt_with_analysis
    
    try:
        snapshot_date = context.get("lastRefreshedAt", "current")
        cached_analysis = get_cached_analysis(snapshot_date)
        
        if cached_analysis:
            # Use cached analysis for greeting
            llm_service = get_llm_service()
            prompt = build_prompt_with_analysis(question, cached_analysis, context)
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context,
                detail_records=None
            )
        else:
            # Fallback to generic greeting if no cached analysis
            logging.warning("No cached analysis available, using generic greeting")
            answer = f"Hello! I'm your Planning Intelligence Copilot. "
            answer += f"Currently, planning health is {context.get('planningHealth', 0)}/100. "
            answer += "Ask me about health, forecast, risks, or changes for more details."
        
        return {
            "answer": answer,
            "supportingMetrics": _build_supporting_metrics(detail_records, context)
        }
    except Exception as e:
        logging.error(f"Error generating greeting answer: {str(e)}")
        # Fallback to generic greeting if LLM fails
        answer = f"Hello! I'm your Planning Intelligence Copilot. "
        answer += f"Currently, planning health is {context.get('planningHealth', 0)}/100. "
        answer += "Ask me about health, forecast, risks, or changes for more details."
        
        return {
            "answer": answer,
            "supportingMetrics": _build_supporting_metrics(detail_records, context)
        }


def generate_design_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for design change questions using LLM service (synchronous)"""
    from copilot_helpers import get_records_by_change_type, get_unique_suppliers, get_unique_materials
    
    design_records = get_records_by_change_type(detail_records, "design")
    if not design_records:
        return {
            "answer": "No design changes detected in the current data.",
            "supportingMetrics": {"designChangedCount": 0, "totalRecords": len(detail_records)}
        }
    
    suppliers = get_unique_suppliers(design_records)
    materials = get_unique_materials(design_records)
    
    # Build template response (fallback)
    template_answer = f"{len(design_records)} records have design changes (BOD or Form Factor). "
    if suppliers:
        template_answer += f"Affected suppliers: {', '.join(suppliers[:3])}. "
    if materials:
        template_answer += f"Affected materials: {', '.join(materials[:3])}."
    
    # Build consistent supporting metrics
    supporting_metrics = {
        "designChangedCount": len(design_records),
        "totalRecords": len(detail_records),
        "affectedSuppliers": suppliers,
        "affectedMaterials": materials
    }
    
    # Call LLM synchronously with limited sample records
    answer = template_answer
    try:
        llm_service = get_llm_service()
        prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
        # Pass only first 10 records to avoid timeout
        sample_records = design_records[:10]
        answer = llm_service.generate_response(
            prompt=prompt,
            context=context,
            detail_records=sample_records
        )
        logging.info(f"LLM generated design answer: {answer[:100]}...")
    except Exception as e:
        logging.warning(f"LLM call failed: {str(e)}. Using template.")
        answer = template_answer
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


def generate_schedule_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for ROJ/schedule change questions using async LLM pattern"""
    from copilot_helpers import (
        compute_roi_metrics, 
        extract_time_window, 
        filter_records_by_time_window,
        get_top_locations_by_change,
        get_top_materials_by_change,
        extract_record_keys
    )
    from async_ollama_service import trigger_async_generation, get_enhanced_answer
    
    # Extract time window from question if present
    time_window = extract_time_window(question)
    logging.info(f"[SCHEDULE] Question: {question}")
    logging.info(f"[SCHEDULE] Extracted time window: {time_window}")
    
    # Filter to ROJ-changed records
    schedule_records = [r for r in detail_records if r.get("rojChanged", r.get("scheduleChanged", False))]
    logging.info(f"[SCHEDULE] ROJ-changed records: {len(schedule_records)} / {len(detail_records)}")
    
    # Apply time-window filtering if requested (uses improved date field priority)
    if time_window:
        schedule_records, date_field, before, after = filter_records_by_time_window(schedule_records, time_window)
        logging.info(f"[SCHEDULE] After time-window filter: {after} records (field: {date_field})")
    
    # Check if we have any records after filtering
    if not schedule_records:
        safe_message = "No ROJ schedule changes were found"
        if time_window:
            safe_message += f" for the requested time window ({time_window['value']} {time_window['type']})."
        else:
            safe_message += "."
        
        return {
            "answer": safe_message,
            "supportingMetrics": {
                "planningHealth": context.get("planningHealth", 0),
                "changedRecordCount": 0,
                "totalRecords": len(detail_records),
                "trendDelta": 0,
                "status": "No Changes",
                "trendDirection": "Stable",
                "roiChangedCount": 0,
                "averageRoiDelta": 0,
                "filteredRecordCount": 0,
                "timeWindow": time_window
            },
            "recordKeys": []
        }
    
    # Compute ROJ metrics
    metrics = compute_roi_metrics(schedule_records)
    
    # Get top impacted locations and materials
    top_locations = get_top_locations_by_change(schedule_records, limit=3)
    top_materials = get_top_materials_by_change(schedule_records, limit=3)
    
    # Determine trend direction
    trend_direction = "delay" if metrics['averageRoiDelta'] > 0 else "acceleration"
    
    # Build compact template response
    template_answer = f"{metrics['roiChangedCount']} records have ROJ schedule changes. "
    if metrics['averageRoiDelta'] != 0:
        template_answer += f"Average ROJ shift: {metrics['averageRoiDelta']:+.1f} days ({trend_direction}). "
    
    if top_locations:
        locs = ", ".join([loc[0] for loc in top_locations[:2]])
        template_answer += f"Top affected locations: {locs}. "
    
    if time_window:
        template_answer += f"Time window: last {time_window['value']} {time_window['type']}."
    
    # Build compact context for LLM
    compact_context = {
        "planningHealth": context.get("planningHealth", 0),
        "totalRecords": len(detail_records),
        "changedRecordCount": len(schedule_records),
        "roiChangedCount": metrics['roiChangedCount'],
        "averageRoiDelta": metrics['averageRoiDelta'],
        "trendDirection": trend_direction,
        "topLocations": [loc[0] for loc in top_locations[:3]],
        "topMaterials": [mat[0] for mat in top_materials[:3]]
    }
    
    # Trigger async LLM generation (non-blocking)
    trigger_async_generation(question, compact_context, schedule_records)
    logging.info(f"[SCHEDULE] Async LLM generation triggered")
    
    # Get enhanced answer from cache if available, otherwise return template
    answer = get_enhanced_answer(template_answer, question, compact_context)
    logging.info(f"[SCHEDULE] Using {'cached' if answer != template_answer else 'template'} answer")
    
    # Log prompt size for monitoring
    prompt_size = len(question) + len(str(compact_context))
    logging.info(f"[SCHEDULE] Prompt size: {prompt_size} chars")
    
    # Extract record keys for drill-down traceability
    record_keys = extract_record_keys(schedule_records, limit=50)
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "planningHealth": context.get("planningHealth", 0),
            "changedRecordCount": len(schedule_records),
            "totalRecords": len(detail_records),
            "trendDelta": metrics.get('averageRoiDelta', 0),
            "status": "Delay" if metrics.get('averageRoiDelta', 0) > 0 else "Acceleration",
            "trendDirection": trend_direction,
            "roiChangedCount": metrics['roiChangedCount'],
            "averageRoiDelta": metrics['averageRoiDelta'],
            "filteredRecordCount": len(schedule_records),
            "timeWindow": time_window,
            "topLocations": [loc[0] for loc in top_locations[:3]],
            "topMaterials": [mat[0] for mat in top_materials[:3]]
        },
        "recordKeys": record_keys
    }




def generate_location_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for location-specific questions using LLM service (synchronous)"""
    from copilot_helpers import extract_location_id, filter_records_by_location, get_top_locations_by_change
    
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
        
        # Build template response (fallback)
        template_answer = f"Location {location_id}: {len(location_records)} records total, {changed} changed."
        
        # Build consistent supporting metrics
        supporting_metrics = {
            "location": location_id,
            "recordCount": len(location_records),
            "changedCount": changed
        }
        
        # Call LLM synchronously with limited sample records
        answer = template_answer
        try:
            llm_service = get_llm_service()
            prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
            # Pass only first 10 records to avoid timeout
            sample_records = location_records[:10]
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context,
                detail_records=sample_records
            )
            logging.info(f"LLM generated location answer: {answer[:100]}...")
        except Exception as e:
            logging.warning(f"LLM call failed: {str(e)}. Using template.")
            answer = template_answer
        
        return {
            "answer": answer,
            "supportingMetrics": supporting_metrics
        }
    else:
        # Top locations query
        top_locations = get_top_locations_by_change(detail_records, limit=5)
        if not top_locations:
            return {
                "answer": "No location changes detected.",
                "supportingMetrics": {"topLocations": []}
            }
        
        # Build template response (fallback)
        template_answer = "Top locations by change count: "
        template_answer += ", ".join([f"{loc[0]} ({loc[1]} changes)" for loc in top_locations]) + "."
        
        # Build consistent supporting metrics
        supporting_metrics = {"topLocations": top_locations}
        
        # Call LLM synchronously with limited sample records
        answer = template_answer
        try:
            llm_service = get_llm_service()
            prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
            # Pass only first 10 records to avoid timeout
            sample_records = detail_records[:10]
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context,
                detail_records=sample_records
            )
            logging.info(f"LLM generated location answer: {answer[:100]}...")
        except Exception as e:
            logging.warning(f"LLM call failed: {str(e)}. Using template.")
            answer = template_answer
        
        return {
            "answer": answer,
            "supportingMetrics": supporting_metrics
        }


def generate_material_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for material-specific questions using LLM service (synchronous)"""
    from copilot_helpers import extract_material_id, filter_records_by_change_type, get_top_materials_by_change
    
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
        
        # Build template response (fallback)
        template_answer = f"Material {material_id}: {len(material_records)} records total, {changed} changed."
        
        # Build consistent supporting metrics
        supporting_metrics = {
            "material": material_id,
            "recordCount": len(material_records),
            "changedCount": changed
        }
        
        # Call LLM synchronously with limited sample records
        answer = template_answer
        try:
            llm_service = get_llm_service()
            prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
            # Pass only first 10 records to avoid timeout
            sample_records = material_records[:10]
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context,
                detail_records=sample_records
            )
            logging.info(f"LLM generated material answer: {answer[:100]}...")
        except Exception as e:
            logging.warning(f"LLM call failed: {str(e)}. Using template.")
            answer = template_answer
        
        return {
            "answer": answer,
            "supportingMetrics": supporting_metrics
        }
    else:
        # Top materials query
        top_materials = get_top_materials_by_change(detail_records, limit=5)
        if not top_materials:
            return {
                "answer": "No material changes detected.",
                "supportingMetrics": {"topMaterials": []}
            }
        
        # Build template response (fallback)
        template_answer = "Top materials by change count: "
        template_answer += ", ".join([f"{mat[0]} ({mat[1]} changes)" for mat in top_materials]) + "."
        
        # Build consistent supporting metrics
        supporting_metrics = {"topMaterials": top_materials}
        
        # Call LLM synchronously with limited sample records
        answer = template_answer
        try:
            llm_service = get_llm_service()
            prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
            # Pass only first 10 records to avoid timeout
            sample_records = detail_records[:10]
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context,
                detail_records=sample_records
            )
            logging.info(f"LLM generated material answer: {answer[:100]}...")
        except Exception as e:
            logging.warning(f"LLM call failed: {str(e)}. Using template.")
            answer = template_answer
        
        return {
            "answer": answer,
            "supportingMetrics": supporting_metrics
        }


def generate_entity_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for entity questions (suppliers, materials, locations) using LLM service (synchronous)"""
    from copilot_helpers import extract_location_id, filter_records_by_location, get_unique_suppliers, get_unique_materials, get_impact_ranking
    
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
        
        # Build template response (fallback)
        template_answer = f"Location {location_id}: {len(location_records)} records. "
        if suppliers:
            template_answer += f"Suppliers: {', '.join(suppliers[:5])}. "
        if materials:
            template_answer += f"Materials: {', '.join(materials[:5])}. "
        template_answer += f"Changed: {changed}."
        
        # Build consistent supporting metrics
        supporting_metrics = {
            "location": location_id,
            "recordCount": len(location_records),
            "suppliers": suppliers,
            "materials": materials,
            "changedCount": changed
        }
        
        # Call LLM synchronously with limited sample records (not all)
        answer = template_answer
        try:
            llm_service = get_llm_service()
            prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
            # Pass only first 10 records to avoid timeout
            sample_records = location_records[:10]
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context,
                detail_records=sample_records
            )
            logging.info(f"LLM generated entity answer: {answer[:100]}...")
        except Exception as e:
            logging.warning(f"LLM call failed: {str(e)}. Using template.")
            answer = template_answer
        
        return {
            "answer": answer,
            "supportingMetrics": supporting_metrics
        }
    else:
        # General entity question
        impact = get_impact_ranking(detail_records)
        top_suppliers = impact["suppliers"][:5]
        top_materials = impact["materials"][:5]
        
        # Build template response (fallback)
        template_answer = "Top affected suppliers: "
        if top_suppliers:
            template_answer += ", ".join([f"{s[0]} ({s[1]} changes)" for s in top_suppliers]) + ". "
        else:
            template_answer += "No supplier data available. "
        template_answer += "Top affected materials: "
        if top_materials:
            template_answer += ", ".join([f"{m[0]} ({m[1]} changes)" for m in top_materials]) + "."
        else:
            template_answer += "No material data available."
        
        # Build consistent supporting metrics
        supporting_metrics = {
            "topSuppliers": top_suppliers,
            "topMaterials": top_materials
        }
        
        # Call LLM synchronously with limited sample records (not all)
        answer = template_answer
        try:
            llm_service = get_llm_service()
            prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
            # Pass only first 10 records to avoid timeout
            sample_records = detail_records[:10]
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context,
                detail_records=sample_records
            )
            logging.info(f"LLM generated entity answer: {answer[:100]}...")
        except Exception as e:
            logging.warning(f"LLM call failed: {str(e)}. Using template.")
            answer = template_answer
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "topSuppliers": top_suppliers,
                "topMaterials": top_materials
            }
        }


def generate_comparison_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for comparison questions using LLM service (synchronous)"""
    import re
    from copilot_helpers import filter_records_by_location
    
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
    
    # Build template response (fallback)
    template_answer = f"Comparison: {loc1} vs {loc2}. "
    template_answer += f"{loc1}: {len(records1)} records, {changed1} changed. "
    template_answer += f"{loc2}: {len(records2)} records, {changed2} changed."
    
    # Build consistent supporting metrics
    supporting_metrics = {
        "location1": loc1,
        "location1Records": len(records1),
        "location1Changed": changed1,
        "location2": loc2,
        "location2Records": len(records2),
        "location2Changed": changed2
    }
    
    # Call LLM synchronously with limited sample records
    answer = template_answer
    try:
        llm_service = get_llm_service()
        prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
        # Pass only first 10 records to avoid timeout
        sample_records = detail_records[:10]
        answer = llm_service.generate_response(
            prompt=prompt,
            context=context,
            detail_records=sample_records
        )
        logging.info(f"LLM generated comparison answer: {answer[:100]}...")
    except Exception as e:
        logging.warning(f"LLM call failed: {str(e)}. Using template.")
        answer = template_answer
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


def generate_impact_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for impact questions using LLM service (synchronous)"""
    from copilot_helpers import get_impact_ranking
    
    impact = get_impact_ranking(detail_records)
    top_suppliers = impact["suppliers"][:3]
    top_materials = impact["materials"][:3]
    
    # Build template response (fallback)
    template_answer = "Impact analysis: "
    if top_suppliers:
        template_answer += "Top suppliers affected: "
        template_answer += ", ".join([f"{s[0]} ({s[1]} changes)" for s in top_suppliers]) + ". "
    if top_materials:
        template_answer += "Top materials affected: "
        template_answer += ", ".join([f"{m[0]} ({m[1]} changes)" for m in top_materials]) + "."
    
    # Build consistent supporting metrics
    supporting_metrics = {
        "topSuppliers": top_suppliers,
        "topMaterials": top_materials
    }
    
    # Call LLM synchronously with limited sample records
    answer = template_answer
    try:
        llm_service = get_llm_service()
        question = "What is the impact of changes?"
        prompt = f"User asked: {question}\n\nData: {json.dumps(supporting_metrics)}"
        # Pass only first 10 records to avoid timeout
        sample_records = detail_records[:10]
        answer = llm_service.generate_response(
            prompt=prompt,
            context=context,
            detail_records=sample_records
        )
        logging.info(f"LLM generated impact answer: {answer[:100]}...")
    except Exception as e:
        logging.warning(f"LLM call failed: {str(e)}. Using template.")
        answer = template_answer
    
    return {
        "answer": answer,
        "supportingMetrics": supporting_metrics
    }


@app.route(route="explain", methods=["POST", "OPTIONS"])
def explain(req: func.HttpRequest) -> func.HttpResponse:
    """
    Explainability endpoint - provides detailed explanations for dashboard insights.
    
    Response Policy:
    - For analysis queries: Returns final LLM-generated answer (not template)
    - For transform queries: Returns deterministic formatted output (no LLM call)
    - Template answer used only as fallback if LLM fails
    
    Optimized: Uses only record keys instead of full records for LLM context.
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
    
    # Get session ID for context persistence
    session_id = body.get("sessionId", "default")
    logging.info(f"Session ID: {session_id}")
    
    # Import session memory functions
    from session_memory import (
        get_or_create_session,
        detect_transform_intent,
        handle_transform_request,
        update_session_after_response,
        format_response_as_table
    )
    
    # Validate question length
    if len(question) > 500:
        return _error("Question too long (max 500 characters)", 400)
    
    # Classify question
    q_type = classify_question(question)
    logging.info(f"Question type: {q_type}")
    
    # HANDLE TRANSFORM QUERIES DETERMINISTICALLY (no LLM, no recomputation)
    if q_type == "transform":
        logging.info("[TRANSFORM] Transform intent detected - using cached response")
        
        transformed_response = handle_transform_request(session_id, question)
        if transformed_response:
            logging.info("[TRANSFORM] Successfully formatted cached response as table")
            return _cors_response(json.dumps(transformed_response, default=str))
        else:
            logging.warning("[TRANSFORM] No cached response available")
            return _error("No previous result is available to transform. Please ask a question first.", 400)
    
    # HANDLE ANALYSIS QUERIES (deterministic compute + LLM)
    
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
    
    # Generate answer based on question type
    answer = None
    supporting_metrics = {}
    record_keys = []
    
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
        
        # Extract final answer (LLM-generated, not template)
        answer = result.get("answer", "Unable to generate answer")
        supporting_metrics = result.get("supportingMetrics", {})
        record_keys = result.get("recordKeys", [])
        
        logging.info(f"[LLM] Generated final answer: {answer[:100]}...")
        
    except Exception as e:
        logging.error(f"[ERROR] Error generating answer: {str(e)}")
        # Fallback to template only on error
        answer = "Unable to generate answer. Please try a different question."
        supporting_metrics = {}
        record_keys = []
    
    # Update session memory with this response (for future transform requests)
    response_for_cache = {
        "answer": answer,
        "supportingMetrics": supporting_metrics,
        "recordKeys": record_keys
    }
    update_session_after_response(session_id, question, response_for_cache, q_type)
    
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
        "recordKeys": record_keys,
        "mcpContext": mcp_context,
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
        "sessionId": session_id
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


@app.route(route="get-prompt-catalog", methods=["GET", "OPTIONS"])
def get_prompt_catalog(req: func.HttpRequest) -> func.HttpResponse:
    """
    Prompt Catalog endpoint — returns structured business prompts for UI consumption.
    
    Supports optional filtering by category or intent.
    Query parameters:
    - category: Filter by category (e.g., "supply_chain", "operations")
    - intent: Filter by intent (e.g., "schedule", "risk", "forecast")
    - search: Search prompts by keyword
    """
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    logging.info("Get prompt catalog endpoint triggered.")
    
    try:
        from planning_intelligence.prompt_catalog import (
            get_prompt_catalog as get_catalog,
            get_prompts_by_category,
            get_prompts_by_intent,
            search_prompts,
            get_catalog_summary
        )
        
        # Get query parameters
        category = req.params.get("category")
        intent = req.params.get("intent")
        search_keyword = req.params.get("search")
        
        # Route to appropriate function based on parameters
        if search_keyword:
            logging.info(f"Searching prompts for keyword: {search_keyword}")
            result = search_prompts(search_keyword)
        elif category:
            logging.info(f"Fetching prompts for category: {category}")
            result = get_prompts_by_category(category)
        elif intent:
            logging.info(f"Fetching prompts for intent: {intent}")
            result = get_prompts_by_intent(intent)
        else:
            # Return full catalog with summary
            logging.info("Fetching full prompt catalog")
            catalog = get_catalog()
            summary = get_catalog_summary()
            result = {
                "catalog": catalog,
                "summary": summary
            }
        
        return _cors_response(json.dumps(result, default=str))
    
    except Exception as e:
        logging.error(f"Error in get_prompt_catalog: {str(e)}")
        return _error(f"Failed to retrieve prompt catalog: {str(e)}", 500)


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
