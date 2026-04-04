import json
import logging
from typing import Optional, List
import azure.functions as func

from normalizer import normalize_rows
from filters import filter_records
from comparator import compare_records
from analytics import (
    build_summary,
    build_location_material_list,
    filter_by_supplier_design_change,
    changes_by_location,
    changes_by_material_group,
    change_driver_analysis,
    high_risk_records,
)
from trend_analyzer import (
    analyze_trends,
    build_trend_summary,
    get_consistently_increasing,
    get_recurring_changes,
    get_one_off_spikes,
    get_change_streaks,
)
from dashboard_builder import build_dashboard_response
from response_builder import build_response
from snapshot_store import load_snapshot, snapshot_exists, get_last_updated_time

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="planning-intelligence", methods=["POST"])
def planning_intelligence(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Planning Intelligence function triggered.")

    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON body.", 400)

    query_type = body.get("query_type", "summary")
    current_rows: List[dict] = body.get("current_rows", [])
    previous_rows: List[dict] = body.get("previous_rows", [])
    snapshots_input: List[dict] = body.get("snapshots", [])
    location_id: Optional[str] = body.get("location_id")
    material_group: Optional[str] = body.get("material_group")
    min_streak: int = int(body.get("min_streak", 2))
    recurring_threshold: int = int(body.get("recurring_threshold", 3))

    # --- Trend queries (multi-snapshot path) ---
    if query_type in (
        "trend_analysis", "consistently_increasing",
        "recurring_changes", "one_off_spikes", "change_streaks",
    ):
        if not snapshots_input:
            return _error("'snapshots' array is required for trend queries.", 400)

        trends = analyze_trends(snapshots_input, location_id, material_group, recurring_threshold)

        if query_type == "trend_analysis":
            result = build_trend_summary(trends)
        elif query_type == "consistently_increasing":
            result = {"consistently_increasing": get_consistently_increasing(trends)}
        elif query_type == "recurring_changes":
            result = {"recurring_changes": get_recurring_changes(trends)}
        elif query_type == "one_off_spikes":
            result = {"one_off_spikes": get_one_off_spikes(trends)}
        elif query_type == "change_streaks":
            result = {"change_streaks": get_change_streaks(trends, min_streak)}

        return func.HttpResponse(
            json.dumps(result, default=str),
            mimetype="application/json",
            status_code=200,
        )

    # --- Two-snapshot queries (existing path) ---
    if not current_rows:
        return _error("'current_rows' is required.", 400)

    # Normalize
    current_records = normalize_rows(current_rows, is_current=True)
    previous_records = normalize_rows(previous_rows, is_current=False)

    # Filter
    current_filtered = filter_records(current_records, location_id, material_group)
    previous_filtered = filter_records(previous_records, location_id, material_group)

    # Compare
    compared = compare_records(current_filtered, previous_filtered)

    # Route query
    if query_type == "list_locations_and_groups":
        result = build_location_material_list(compared)

    elif query_type == "changed_records":
        summary = build_summary(compared)
        result = {
            "changed_record_count": summary["changed_record_count"],
            "changed_records": summary["changed_records"],
        }

    elif query_type == "changed_count":
        result = {"changed_record_count": build_summary(compared)["changed_record_count"]}

    elif query_type == "changed_material_ids":
        result = {"changed_material_ids": build_summary(compared)["changed_material_ids"]}

    elif query_type == "supplier_design_changes":
        result = {"supplier_design_changes": filter_by_supplier_design_change(compared)}

    # --- New analytical queries ---
    elif query_type == "changes_by_location":
        # Q3: Which locations have the most changes?
        result = changes_by_location(compared)

    elif query_type == "changes_by_material_group":
        # Q4: Which material groups have changes?
        result = changes_by_material_group(compared)

    elif query_type == "change_driver_analysis":
        # Q5: Are changes qty-, supplier-, or design-driven?
        result = change_driver_analysis(compared)

    elif query_type == "high_risk_records":
        # Q6: Which records are high risk?
        result = high_risk_records(compared)

    else:  # default: full summary covering all six questions
        result = build_summary(compared)

    return func.HttpResponse(
        json.dumps(result, default=str),
        mimetype="application/json",
        status_code=200,
    )


def _error(message: str, status: int) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"error": message}),
        mimetype="application/json",
        status_code=status,
    )


@app.route(route="planning-dashboard", methods=["POST"])
def planning_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    """
    Dashboard endpoint — returns a fully shaped UI-ready JSON payload.
    Accepts same input as planning-intelligence but returns dashboard model.
    """
    logging.info("Planning Dashboard function triggered.")

    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON body.", 400)

    current_rows: List[dict] = body.get("current_rows", [])
    previous_rows: List[dict] = body.get("previous_rows", [])
    snapshots_input: List[dict] = body.get("snapshots", [])
    location_id: Optional[str] = body.get("location_id")
    material_group: Optional[str] = body.get("material_group")
    recurring_threshold: int = int(body.get("recurring_threshold", 3))

    if not current_rows:
        return _error("'current_rows' is required.", 400)

    # Normalize + filter + compare
    current_records = normalize_rows(current_rows, is_current=True)
    previous_records = normalize_rows(previous_rows, is_current=False)
    current_filtered = filter_records(current_records, location_id, material_group)
    previous_filtered = filter_records(previous_records, location_id, material_group)
    compared = compare_records(current_filtered, previous_filtered)

    # Optional trend analysis
    trends = []
    if snapshots_input:
        trends = analyze_trends(snapshots_input, location_id, material_group, recurring_threshold)

    result = build_dashboard_response(compared, trends, location_id, material_group)

    return func.HttpResponse(
        json.dumps(result, default=str),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="planning-dashboard-v2", methods=["POST"])
def planning_dashboard_v2(req: func.HttpRequest) -> func.HttpResponse:
    """
    Blob-first AI dashboard endpoint.
    Reads from cached snapshot first; falls back to live blob reload.
    """
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
        return func.HttpResponse(
            json.dumps(snap, default=str),
            mimetype="application/json",
            status_code=200,
        )

    # No snapshot — load from blob directly
    logging.info("No snapshot found, loading from blob.")
    try:
        from blob_loader import load_current_previous_from_blob
        current_rows, previous_rows = load_current_previous_from_blob()
    except Exception as e:
        return _error(f"Blob load failed: {str(e)}", 500)

    current_records = normalize_rows(current_rows, is_current=True)
    previous_records = normalize_rows(previous_rows, is_current=False)
    current_filtered = filter_records(current_records, location_id, material_group)
    previous_filtered = filter_records(previous_records, location_id, material_group)
    compared = compare_records(current_filtered, previous_filtered)

    result = build_response(
        compared, [], location_id, material_group,
        data_mode="blob",
    )

    return func.HttpResponse(
        json.dumps(result, default=str),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="daily-refresh", methods=["POST"])
def daily_refresh(req: func.HttpRequest) -> func.HttpResponse:
    """
    Triggers daily refresh from Azure Blob Storage and saves a snapshot.
    """
    logging.info("Daily refresh triggered — loading from Blob Storage.")
    try:
        from run_daily_refresh import run_daily_refresh
        result = run_daily_refresh()
        return func.HttpResponse(
            json.dumps({
                "status": "ok",
                "lastRefreshedAt": result.get("lastRefreshedAt"),
                "totalRecords": result.get("totalRecords"),
                "changedRecordCount": result.get("changedRecordCount"),
                "planningHealth": result.get("planningHealth"),
            }, default=str),
            mimetype="application/json",
            status_code=200,
        )
    except Exception as e:
        return _error(f"Daily refresh failed: {str(e)}", 500)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@app.route(route="explain", methods=["POST"])
def explain(req: func.HttpRequest) -> func.HttpResponse:
    """
    Focused insight endpoint. Accepts question + optional context object.
    When context is provided, uses it to ground the answer.
    Falls back to cached snapshot when no context and mode=cached.
    """
    logging.info("Explain endpoint triggered.")
    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON body.", 400)

    question: str = body.get("question", "").strip()
    if not question:
        return _error("question is required", 400)

    location_id: Optional[str] = body.get("location_id")
    material_group: Optional[str] = body.get("material_group")
    context: Optional[dict] = body.get("context")  # optional frontend DashboardContext

    # --- Context-grounded path ---
    if context:
        context_used = [k for k, v in context.items() if v is not None]
        query_type = _classify_question(question)
        answer = _generate_answer_from_context(question, context)
        explainability = _build_explainability(context, question)
        return func.HttpResponse(
            json.dumps({
                "question": question,
                "answer": answer,
                "queryType": query_type,
                "aiInsight": context.get("aiInsight"),
                "rootCause": context.get("rootCause"),
                "recommendedActions": context.get("recommendedActions", []),
                "planningHealth": context.get("planningHealth"),
                "dataMode": context.get("dataMode", "cached"),
                "lastRefreshedAt": context.get("lastRefreshedAt"),
                "supportingMetrics": {
                    "changedRecordCount": context.get("changedRecordCount"),
                    "totalRecords": context.get("totalRecords"),
                    "trendDelta": context.get("trendDelta"),
                    "planningHealth": context.get("planningHealth"),
                },
                "contextUsed": context_used,
                "explainability": explainability,
                "suggestedActions": _build_suggested_actions(question, context),
                "followUpQuestions": _build_follow_ups(question, context),
            }, default=str),
            mimetype="application/json",
            status_code=200,
        )

    # --- Cached snapshot path (blob-derived) ---
    snap = load_snapshot()
    if not snap:
        return _error("No cached snapshot available. Run daily-refresh to load data from Blob Storage.", 404)
    query_type = _classify_question(question)
    answer = _generate_answer_from_context(question, snap)
    explainability = _build_explainability(snap, question)
    return func.HttpResponse(
        json.dumps({
            "question": question,
            "answer": answer,
            "queryType": query_type,
            "aiInsight": snap.get("aiInsight"),
            "rootCause": snap.get("rootCause"),
            "recommendedActions": snap.get("recommendedActions", []),
            "alerts": snap.get("alerts"),
            "drivers": snap.get("drivers"),
            "planningHealth": snap.get("planningHealth"),
            "dataMode": "blob",
            "lastRefreshedAt": snap.get("lastRefreshedAt"),
            "supportingMetrics": {
                "changedRecordCount": snap.get("changedRecordCount"),
                "totalRecords": snap.get("totalRecords"),
                "trendDelta": snap.get("trendDelta"),
                "planningHealth": snap.get("planningHealth"),
            },
            "contextUsed": ["aiInsight", "rootCause", "planningHealth", "drivers"],
            "explainability": explainability,
            "suggestedActions": _build_suggested_actions(question, snap),
            "followUpQuestions": _build_follow_ups(question, snap),
        }, default=str),
        mimetype="application/json",
        status_code=200,
    )


def _generate_answer_from_context(question: str, ctx: dict) -> str:
    """Generate a grounded plain-language answer from available context, using detailRecords when available."""
    q = question.lower()
    health = ctx.get("planningHealth")
    status = ctx.get("status", "")
    changed = ctx.get("changedRecordCount", 0)
    total = ctx.get("totalRecords", 0)
    pct = round(changed / total * 100, 1) if total else 0
    ai_insight = ctx.get("aiInsight", "")
    root_cause = ctx.get("rootCause", "")
    actions = ctx.get("recommendedActions", [])
    drivers = ctx.get("drivers") or {}
    risk_summary = ctx.get("riskSummary") or {}
    risk = risk_summary.get("highestRiskLevel", "Normal")
    trend = ctx.get("trendDirection", "")
    trend_delta = ctx.get("trendDelta", 0)
    contrib = ctx.get("contributionBreakdown") or {}
    kpis = ctx.get("kpis") or {}
    details = ctx.get("detailRecords") or []
    dc_summary = ctx.get("datacenterSummary") or []
    mg_summary = ctx.get("materialGroupSummary") or []

    if any(w in q for w in ["health", "critical", "score", "low"]):
        contrib_text = ""
        if contrib:
            contrib_text = f" Breakdown: Qty {contrib.get('quantity', 0)}%, Supplier {contrib.get('supplier', 0)}%, Design {contrib.get('design', 0)}%, Schedule {contrib.get('schedule', 0)}%."
        return (
            f"Planning health is {health}/100 ({status}). "
            f"{pct}% of records changed ({changed}/{total}). "
            f"Risk level: {risk}.{contrib_text} {ai_insight}"
        )
    if any(w in q for w in ["changed", "change", "most", "what changed"]):
        loc = drivers.get("location", "N/A")
        change_type = drivers.get("changeType", "N/A")
        contrib_text = ""
        if contrib:
            contrib_text = f" Contribution: Qty {contrib.get('quantityCount', 0)}, Supplier {contrib.get('supplierCount', 0)}, Design {contrib.get('designCount', 0)}, Schedule {contrib.get('scheduleCount', 0)}."
        return (
            f"{changed} records changed ({pct}% of total). "
            f"Primary driver: {change_type}. Top location: {loc}.{contrib_text} "
            f"{root_cause}"
        )
    if any(w in q for w in ["forecast", "demand", "increase", "decrease", "trend"]):
        return (
            f"Forecast trend is {trend} with a delta of {trend_delta:+,.0f} units. "
            f"Demand volatility: {kpis.get('demandVolatility', 'N/A')}%. "
            f"{ai_insight}"
        )
    if any(w in q for w in ["action", "planner", "do next", "recommend"]):
        if actions:
            return "Recommended actions:\n" + "\n".join(f"• {a}" for a in actions)
        return "No specific actions recommended at this time."
    if any(w in q for w in ["location", "site", "datacenter"]):
        loc = drivers.get("location", "N/A")
        top_locs = ", ".join(f"{d.get('locationId', '?')}: {d.get('changed', 0)} changed" for d in dc_summary[:3]) if dc_summary else "N/A"
        return f"Top impacted location: {loc}. Top locations: {top_locs}. {root_cause}"
    if any(w in q for w in ["material", "group", "category", "equipment"]):
        top_mgs = ", ".join(f"{g.get('materialGroup', '?')}: {g.get('changed', 0)} changed" for g in mg_summary[:3]) if mg_summary else "N/A"
        return f"Top material groups: {top_mgs}. {root_cause}"
    if any(w in q for w in ["supplier"]):
        sup = drivers.get("supplier", "N/A")
        reliability = kpis.get("supplierReliability", "N/A")
        return f"Top impacted supplier: {sup}. Supplier reliability: {reliability}%. {root_cause}"
    if any(w in q for w in ["risk", "high risk"]):
        high_risk_count = risk_summary.get("highRiskCount", 0)
        risk_conc = kpis.get("riskConcentration", "N/A")
        return f"Risk level: {risk}. High-risk records: {high_risk_count}. Risk concentration: {risk_conc}%. {root_cause}"
    if any(w in q for w in ["design", "bod", "form factor"]):
        design_rate = kpis.get("designChangeRate", "N/A")
        return f"Design change rate: {design_rate}%. {root_cause}"
    if any(w in q for w in ["schedule", "roj", "delay"]):
        stability = kpis.get("scheduleStability", "N/A")
        return f"Schedule stability: {stability}%. {root_cause}"
    if any(w in q for w in ["new demand", "new record"]):
        new_ratio = kpis.get("newDemandRatio", "N/A")
        return f"New demand ratio: {new_ratio}%. {ctx.get('newRecordCount', 0)} new records this cycle."
    if any(w in q for w in ["cancel"]):
        cancel_rate = kpis.get("cancellationRate", "N/A")
        return f"Cancellation rate: {cancel_rate}%."
    if any(w in q for w in ["kpi", "metric", "score"]):
        parts = [f"Design change rate: {kpis.get('designChangeRate', 'N/A')}%",
                 f"Supplier reliability: {kpis.get('supplierReliability', 'N/A')}%",
                 f"Demand volatility: {kpis.get('demandVolatility', 'N/A')}%",
                 f"Schedule stability: {kpis.get('scheduleStability', 'N/A')}%",
                 f"Risk concentration: {kpis.get('riskConcentration', 'N/A')}%"]
        return "KPI Summary:\n" + "\n".join(f"• {p}" for p in parts)

    # --- COMPARISON MODE ---
    if any(w in q for w in ["compare", " vs ", "versus", "difference between"]):
        return _handle_comparison(q, ctx, dc_summary, mg_summary, details)

    # --- WHY-NOT REASONING ---
    if any(w in q for w in ["why not", "why isn't", "not risky", "not flagged", "not changed", "stable"]):
        return _handle_why_not(q, ctx, dc_summary, mg_summary, details)

    # --- TRACEABILITY / TOP RECORDS ---
    if any(w in q for w in ["top record", "contributing", "impacted material", "show record", "detail"]):
        return _handle_traceability(q, ctx, details)

    # Default: return full insight
    return ai_insight or root_cause or "No analysis available for this question."


def _handle_comparison(q: str, ctx: dict, dc_summary: list, mg_summary: list, details: list) -> str:
    """Handle comparison prompts by extracting two entities and comparing metrics."""
    import re
    # Try to extract two entities from "compare X vs Y" or "X versus Y"
    match = re.search(r'(?:compare\s+)?(\S+)\s+(?:vs\.?|versus|and)\s+(\S+)', q)
    if not match:
        return "Please specify two entities to compare, e.g., 'Compare LOC001 vs LOC002'."

    a, b = match.group(1).upper(), match.group(2).upper()

    # Try location comparison
    loc_a = next((d for d in dc_summary if d.get("locationId", "").upper() == a), None)
    loc_b = next((d for d in dc_summary if d.get("locationId", "").upper() == b), None)
    if loc_a and loc_b:
        pct_a = round(loc_a["changed"] / max(loc_a["total"], 1) * 100, 1)
        pct_b = round(loc_b["changed"] / max(loc_b["total"], 1) * 100, 1)
        return (
            f"📊 Comparison: {a} vs {b}\n\n"
            f"{a}: {loc_a['changed']}/{loc_a['total']} changed ({pct_a}%)\n"
            f"{b}: {loc_b['changed']}/{loc_b['total']} changed ({pct_b}%)\n\n"
            f"{'→ ' + a + ' has more changes.' if loc_a['changed'] > loc_b['changed'] else '→ ' + b + ' has more changes.' if loc_b['changed'] > loc_a['changed'] else '→ Both have equal changes.'}"
        )

    # Try material group comparison
    mg_a = next((g for g in mg_summary if g.get("materialGroup", "").upper() == a), None)
    mg_b = next((g for g in mg_summary if g.get("materialGroup", "").upper() == b), None)
    if mg_a and mg_b:
        return (
            f"📊 Comparison: {a} vs {b}\n\n"
            f"{a}: {mg_a.get('changed', 0)}/{mg_a.get('total', 0)} changed (Qty:{mg_a.get('qtyChanged', 0)} Design:{mg_a.get('designChanged', 0)} Supplier:{mg_a.get('supplierChanged', 0)})\n"
            f"{b}: {mg_b.get('changed', 0)}/{mg_b.get('total', 0)} changed (Qty:{mg_b.get('qtyChanged', 0)} Design:{mg_b.get('designChanged', 0)} Supplier:{mg_b.get('supplierChanged', 0)})\n\n"
            f"{'→ ' + a + ' is more impacted.' if mg_a.get('changed', 0) > mg_b.get('changed', 0) else '→ ' + b + ' is more impacted.'}"
        )

    return f"Could not find both {a} and {b} in the current dataset. Available locations: {', '.join(d.get('locationId', '') for d in dc_summary[:5])}."


def _handle_why_not(q: str, ctx: dict, dc_summary: list, mg_summary: list, details: list) -> str:
    """Handle why-not reasoning — explain absence of risk or change."""
    risk_summary = ctx.get("riskSummary") or {}
    drivers = ctx.get("drivers") or {}

    # Extract entity name from question
    words = q.split()
    entity = None
    for w in words:
        if w.upper() in [d.get("locationId", "").upper() for d in dc_summary]:
            entity = w.upper()
            break
        if w.upper() in [g.get("materialGroup", "").upper() for g in mg_summary]:
            entity = w.upper()
            break

    if entity:
        loc = next((d for d in dc_summary if d.get("locationId", "").upper() == entity), None)
        mg = next((g for g in mg_summary if g.get("materialGroup", "").upper() == entity), None)
        if loc:
            if loc["changed"] == 0:
                return f"📊 {entity} is stable because no records changed this cycle ({loc['total']} total records, 0 changed). No risk signals detected."
            pct = round(loc["changed"] / max(loc["total"], 1) * 100, 1)
            return f"📊 {entity} has {loc['changed']}/{loc['total']} changes ({pct}%). It {'is flagged' if pct > 25 else 'is below the risk threshold because change rate is low'}."
        if mg:
            if mg["changed"] == 0:
                return f"📊 {entity} is stable — no changes detected across {mg['total']} records."
            return f"📊 {entity} has {mg['changed']}/{mg['total']} changes. Design: {mg.get('designChanged', 0)}, Supplier: {mg.get('supplierChanged', 0)}. {'Low risk because no design/supplier changes.' if mg.get('designChanged', 0) == 0 and mg.get('supplierChanged', 0) == 0 else ''}"

    # Generic why-not
    if risk_summary.get("highRiskCount", 0) == 0:
        return "📊 No high-risk records detected this cycle. All changes are within normal parameters."
    return f"📊 Current risk level is {risk_summary.get('highestRiskLevel', 'Normal')}. {risk_summary.get('highRiskCount', 0)} records are flagged. Entities not mentioned are below risk thresholds."


def _handle_traceability(q: str, ctx: dict, details: list) -> str:
    """Return top contributing records for traceability."""
    if not details:
        return "📊 Detail records are not available in the current context. Run daily-refresh to populate."

    # Sort by absolute qty_delta descending
    sorted_details = sorted(details, key=lambda r: abs(r.get("qtyDelta") or 0), reverse=True)
    top = sorted_details[:5]
    lines = []
    for r in top:
        delta = r.get("qtyDelta")
        delta_str = f"{delta:+,.0f}" if delta is not None else "N/A"
        lines.append(f"  {r.get('locationId', '?')} / {r.get('materialGroup', '?')} / {r.get('materialId', '?')} — Δ{delta_str} [{r.get('changeType', '?')}] [{r.get('riskLevel', '?')}]")
    return f"📊 Top {len(top)} contributing records (by forecast delta):\n" + "\n".join(lines)


def _classify_question(question: str) -> str:
    """Classify question type for routing and explainability."""
    q = question.lower()
    if any(w in q for w in ["compare", " vs ", "versus", "difference between"]): return "comparison"
    if any(w in q for w in ["why not", "why isn't", "not risky", "not flagged", "not changed", "stable"]): return "why_not"
    if any(w in q for w in ["top record", "contributing", "impacted material", "show record", "detail"]): return "traceability"
    if any(w in q for w in ["why", "cause", "reason", "root"]): return "root_cause"
    if any(w in q for w in ["risk", "high risk", "danger"]): return "risk"
    if any(w in q for w in ["action", "do next", "recommend", "planner"]): return "action"
    if any(w in q for w in ["source", "blob", "mock", "refresh", "stale", "provenance"]): return "provenance"
    return "summary"


def _build_explainability(ctx: dict, question: str) -> dict:
    """Build explainability metadata for the response."""
    from datetime import datetime, timezone
    last_refreshed = ctx.get("lastRefreshedAt")
    freshness_minutes = None
    is_stale = False
    if last_refreshed:
        try:
            refreshed_dt = datetime.fromisoformat(last_refreshed.replace("Z", "+00:00"))
            freshness_minutes = round((datetime.now(timezone.utc) - refreshed_dt).total_seconds() / 60, 1)
            is_stale = freshness_minutes > 1440  # stale if > 24 hours
        except (ValueError, TypeError):
            pass

    total = ctx.get("totalRecords", 0)
    changed = ctx.get("changedRecordCount", 0)
    data_coverage = round(changed / max(total, 1) * 100, 1)

    # Confidence based on data availability
    fields_present = sum(1 for k in ["aiInsight", "rootCause", "drivers", "riskSummary", "contributionBreakdown", "kpis"] if ctx.get(k))
    confidence = min(round(fields_present / 6 * 100), 100)

    return {
        "confidenceScore": confidence,
        "dataCoverage": data_coverage,
        "dataSource": ctx.get("dataMode", "unknown"),
        "lastRefreshedAt": last_refreshed,
        "dataFreshnessMinutes": freshness_minutes,
        "isStale": is_stale,
        "queryType": _classify_question(question),
        "fieldsUsed": [k for k in ["aiInsight", "rootCause", "drivers", "riskSummary", "contributionBreakdown", "kpis", "detailRecords"] if ctx.get(k)],
    }


def _build_suggested_actions(question: str, ctx: dict) -> list:
    """Build actionable suggestions based on question and context."""
    q = question.lower()
    actions = []
    if any(w in q for w in ["risk", "high risk"]):
        actions.append({"action": "filter_dashboard", "label": "Show high-risk records", "filter": "risk"})
    if any(w in q for w in ["supplier"]):
        actions.append({"action": "open_drill_down", "label": "Review supplier details", "type": "supplier"})
    if any(w in q for w in ["design", "bod"]):
        actions.append({"action": "open_drill_down", "label": "Show design changes", "type": "material"})
    if any(w in q for w in ["location", "datacenter"]):
        actions.append({"action": "open_drill_down", "label": "Drill into location", "type": "location"})
    if any(w in q for w in ["schedule", "roj", "delay"]):
        actions.append({"action": "filter_dashboard", "label": "Show delayed ROJ records", "filter": "roj"})
    if not actions:
        actions.append({"action": "open_copilot", "label": "Ask a follow-up question"})
    return actions


def _build_follow_ups(question: str, ctx: dict) -> list:
    """Generate contextual follow-up questions."""
    q = question.lower()
    drivers = ctx.get("drivers") or {}
    follow_ups = []
    if any(w in q for w in ["health", "critical"]):
        follow_ups = ["What is driving the risk?", "Which locations are most impacted?", "What actions should be taken?"]
    elif any(w in q for w in ["change", "driver"]):
        follow_ups = ["Is this demand-driven or design-driven?", "Show top risk areas", "What should the planner do?"]
    elif any(w in q for w in ["supplier"]):
        follow_ups = ["Which materials are affected?", "Is there a schedule delay?", "What is the supplier reliability?"]
    elif any(w in q for w in ["location"]):
        follow_ups = ["Which material groups changed here?", "What is the forecast delta?", "Any design changes?"]
    elif any(w in q for w in ["forecast", "demand"]):
        follow_ups = ["Is this a spike or a trend?", "Which locations drive the increase?", "What actions are recommended?"]
    elif any(w in q for w in ["not", "why not", "isn't"]):
        follow_ups = ["What IS driving changes?", "Show current risk level", "What changed most?"]
    else:
        follow_ups = ["What changed most?", "Show KPI summary", "What should the planner do next?"]
    return follow_ups[:3]


def _filter_snapshot(snap: dict, location_id: Optional[str], material_group: Optional[str]) -> dict:
    """Filter detailRecords in a cached snapshot by location/material group."""
    if not snap.get("detailRecords"):
        return snap
    loc = location_id.strip().lower() if location_id else None
    mg = material_group.strip().lower() if material_group else None
    snap["detailRecords"] = [
        r for r in snap["detailRecords"]
        if (not loc or r.get("locationId", "").lower() == loc)
        and (not mg or r.get("materialGroup", "").lower() == mg)
    ]
    return snap


@app.route(route="debug-snapshot", methods=["POST"])
def debug_snapshot(req: func.HttpRequest) -> func.HttpResponse:
    """
    Debug endpoint — returns raw intermediate analytics values for validation.
    Accepts optional mode, location_id, material_group to scope the analysis.
    """
    logging.info("Debug snapshot endpoint triggered.")
    try:
        body = req.get_json()
    except ValueError:
        body = {}

    mode: str = (body.get("mode") or "cached").lower()
    location_id: Optional[str] = body.get("location_id")
    material_group: Optional[str] = body.get("material_group")

    try:
        if mode == "cached":
            snap = load_snapshot()
            if not snap:
                return _error("No cached snapshot available. Run daily refresh first.", 404)
            # Return debug info derived from snapshot
            changed = snap.get("changedRecordCount", 0)
            total = snap.get("totalRecords", 0)
            risk_summary = snap.get("riskSummary", {})
            return func.HttpResponse(
                json.dumps({
                    "normalizedCount": total,
                    "filteredCount": total,
                    "comparedCount": total,
                    "changedCount": changed,
                    "healthScoreInputs": {
                        "total": total,
                        "changed": changed,
                        "riskCounts": risk_summary.get("riskBreakdown", {}),
                        "designCount": risk_summary.get("designChangedCount", 0),
                        "supplierCount": risk_summary.get("supplierChangedCount", 0),
                        "highestRisk": risk_summary.get("highestRiskLevel", "Normal"),
                        "deductions": {
                            "changeRatio": round((changed / max(total, 1)) * 40),
                            "riskLevel": 25 if "Design + Supplier" in risk_summary.get("highestRiskLevel", "") else 15 if any(x in risk_summary.get("highestRiskLevel", "") for x in ["Design", "Supplier"]) else 10 if "Spike" in risk_summary.get("highestRiskLevel", "") else 0,
                            "designPenalty": min(risk_summary.get("designChangedCount", 0) * 2, 10),
                            "supplierPenalty": min(risk_summary.get("supplierChangedCount", 0) * 2, 10),
                        },
                    },
                    "dashboardResponse": snap,
                }, default=str),
                mimetype="application/json",
                status_code=200,
            )

        elif mode == "blob":
            from blob_loader import load_current_previous_from_blob
            current_rows, previous_rows = load_current_previous_from_blob()

        else:
            return _error("Only blob and cached modes are supported.", 400)

        # Run pipeline capturing intermediate counts
        current_records = normalize_rows(current_rows, is_current=True)
        previous_records = normalize_rows(previous_rows, is_current=False)
        current_filtered = filter_records(current_records, location_id, material_group)
        previous_filtered = filter_records(previous_records, location_id, material_group)
        compared = compare_records(current_filtered, previous_filtered)

        from analytics import is_changed
        changed_records = [r for r in compared if is_changed(r)]
        changed_count = len(changed_records)
        total_count = len(compared)

        from collections import Counter
        risk_counts = Counter(r.risk_level for r in changed_records if r.risk_level != "Normal")
        design_count = sum(1 for r in changed_records if r.design_changed)
        supplier_count = sum(1 for r in changed_records if r.supplier_changed)
        highest_risk = next((r for r in ["Design + Supplier Change Risk", "Design Change Risk", "Supplier Change Risk", "High Demand Spike"] if r in risk_counts), "Normal")

        change_ratio_ded = round((changed_count / max(total_count, 1)) * 40)
        risk_ded = 25 if "Design + Supplier" in highest_risk else 15 if any(x in highest_risk for x in ["Design", "Supplier"]) else 10 if "Spike" in highest_risk else 0
        design_ded = min(design_count * 2, 10)
        supplier_ded = min(supplier_count * 2, 10)

        result = build_response(compared, [], location_id, material_group, data_mode=mode)

        return func.HttpResponse(
            json.dumps({
                "normalizedCount": len(current_records),
                "filteredCount": len(current_filtered),
                "comparedCount": total_count,
                "changedCount": changed_count,
                "healthScoreInputs": {
                    "total": total_count,
                    "changed": changed_count,
                    "riskCounts": dict(risk_counts),
                    "designCount": design_count,
                    "supplierCount": supplier_count,
                    "highestRisk": highest_risk,
                    "deductions": {
                        "changeRatio": change_ratio_ded,
                        "riskLevel": risk_ded,
                        "designPenalty": design_ded,
                        "supplierPenalty": supplier_ded,
                    },
                },
                "dashboardResponse": result,
            }, default=str),
            mimetype="application/json",
            status_code=200,
        )

    except Exception as e:
        logging.exception("Debug snapshot failed")
        return _error(f"Debug snapshot failed: {str(e)}", 500)
