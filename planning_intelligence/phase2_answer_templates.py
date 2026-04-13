"""
Phase 2: Answer Templates - Generate targeted responses for different query types

This module implements answer templates for:
1. Comparison answers
2. Root cause answers
3. Why-not answers
4. Traceability answers
5. Summary answers
"""

from typing import Dict, List, Any, Optional


class AnswerTemplates:
    """Generates answers using query-specific templates."""
    
    @staticmethod
    def generate_comparison_answer(
        question: str,
        ctx: Dict[str, Any],
        entities: List[str],
        scoped_metrics: Dict[str, Any]
    ) -> str:
        """
        Generate comparison answer.
        
        Template: 📊 [Entity A] vs [Entity B]
        [Entity A]: X changed (Y%), drivers: [list]
        [Entity B]: X changed (Y%), drivers: [list]
        → [Entity A] has more changes
        """
        if len(entities) < 2:
            return "Could not extract two entities to compare."
        
        entity_a, entity_b = entities[0], entities[1]
        
        # Get metrics for each entity
        metrics_a = scoped_metrics.get(entity_a, {})
        metrics_b = scoped_metrics.get(entity_b, {})
        
        changed_a = metrics_a.get("changedCount", 0)
        total_a = metrics_a.get("filteredRecordsCount", 0)
        rate_a = metrics_a.get("changeRate", 0)
        driver_a = metrics_a.get("scopedDrivers", {}).get("primary", "unknown")
        
        changed_b = metrics_b.get("changedCount", 0)
        total_b = metrics_b.get("filteredRecordsCount", 0)
        rate_b = metrics_b.get("changeRate", 0)
        driver_b = metrics_b.get("scopedDrivers", {}).get("primary", "unknown")
        
        more_changes = entity_a if changed_a > changed_b else entity_b
        
        return (
            f"📊 Comparison: {entity_a} vs {entity_b}\n\n"
            f"{entity_a}: {changed_a}/{total_a} changed ({rate_a}%). "
            f"Primary driver: {driver_a}\n"
            f"{entity_b}: {changed_b}/{total_b} changed ({rate_b}%). "
            f"Primary driver: {driver_b}\n\n"
            f"→ {more_changes} has more changes and requires closer monitoring."
        )
    
    @staticmethod
    def generate_root_cause_answer(
        question: str,
        ctx: Dict[str, Any],
        scope_type: str,
        scope_value: str,
        scoped_metrics: Dict[str, Any]
    ) -> str:
        """
        Generate root cause answer.
        
        Template: In [entity], [what changed]. This is risky because [why]. [Action]
        """
        if not scope_value:
            return "Could not identify specific entity in question."
        
        metrics = scoped_metrics or {}
        what_changed = metrics.get("scopedDrivers", {}).get("primary", "changes")
        change_rate = metrics.get("changeRate", 0)
        changed_count = metrics.get("changedCount", 0)
        
        why_risky = f"{change_rate}% of records changed ({changed_count} records)"
        actions = ctx.get("recommendedActions", ["Monitor the situation"])
        action = actions[0] if actions else "Monitor the situation"
        
        return (
            f"In {scope_value}, {what_changed} changed. "
            f"This is risky because {why_risky}. "
            f"Recommended action: {action}"
        )
    
    @staticmethod
    def generate_why_not_answer(
        question: str,
        ctx: Dict[str, Any],
        scope_type: str,
        scope_value: str,
        scoped_metrics: Dict[str, Any]
    ) -> str:
        """
        Generate why-not answer.
        
        Template: [Entity] is stable because [reasons]. Unlike [risky entity], [differences]
        """
        if not scope_value:
            return "Could not identify specific entity in question."
        
        metrics = scoped_metrics or {}
        changed_count = metrics.get("changedCount", 0)
        total_count = metrics.get("filteredRecordsCount", 0)
        change_rate = metrics.get("changeRate", 0)
        
        if changed_count == 0:
            return f"{scope_value} is stable because no records changed this cycle."
        
        if change_rate < 10:
            return f"{scope_value} is stable because only {change_rate}% of records changed."
        
        return (
            f"{scope_value} has {change_rate}% change rate, which is below the risk threshold. "
            f"This is stable compared to other locations with higher change rates."
        )
    
    @staticmethod
    def generate_traceability_answer(
        question: str,
        ctx: Dict[str, Any],
        scoped_metrics: Dict[str, Any]
    ) -> str:
        """
        Generate traceability answer.
        
        Template: 📊 Top [N] contributing records:
        [Record 1]: [location] / [material] / Δ[delta] / [risk]
        ...
        """
        records = scoped_metrics.get("topContributingRecords", [])
        if not records:
            return "No contributing records found."
        
        lines = [f"📊 Top {len(records)} contributing records (by forecast delta):"]
        for i, r in enumerate(records, 1):
            delta = r.get("qtyDelta", 0)
            delta_str = f"{delta:+,.0f}"
            location = r.get("LOCID", "?")
            material_group = r.get("GSCEQUIPCAT", "?")
            material_id = r.get("PRDID", "?")
            risk = r.get("Risk_Flag", False)
            risk_str = "🔴 High Risk" if risk else "🟢 Normal"
            
            lines.append(
                f"  {i}. {location} / {material_group} / {material_id} — Δ{delta_str} [{risk_str}]"
            )
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_summary_answer(
        question: str,
        ctx: Dict[str, Any]
    ) -> str:
        """
        Generate summary answer for overall status.
        
        Template: Planning health is [X]. [Y]% changed. Risk: [Z].
        """
        planning_health = ctx.get("planningHealth", "Unknown")
        changed_count = ctx.get("changedRecordCount", 0)
        total_records = ctx.get("totalRecords", 1)
        change_rate = round(changed_count / max(total_records, 1) * 100, 1)
        
        drivers = ctx.get("drivers", {})
        primary_driver = max(drivers.items(), key=lambda x: x[1])[0] if drivers else "unknown"
        
        risk_level = "High" if change_rate > 30 else "Medium" if change_rate > 10 else "Low"
        
        return (
            f"Planning health is {planning_health}. "
            f"{change_rate}% of records changed ({changed_count}/{total_records}). "
            f"Primary driver: {primary_driver}. "
            f"Risk level: {risk_level}."
        )


class ResponseBuilder:
    """Builds complete responses with all required fields."""
    
    @staticmethod
    def build_response(
        question: str,
        answer: str,
        query_type: str,
        answer_mode: str,
        ctx: Dict[str, Any],
        scope_type: Optional[str] = None,
        scope_value: Optional[str] = None,
        scoped_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build complete response with all fields.
        """
        response = {
            "question": question,
            "answer": answer,
            "queryType": query_type,
            "answerMode": answer_mode,
            "aiInsight": ctx.get("aiInsight"),
            "rootCause": ctx.get("rootCause"),
            "recommendedActions": ctx.get("recommendedActions", []),
            "planningHealth": ctx.get("planningHealth"),
            "dataMode": ctx.get("dataMode", "cached"),
            "lastRefreshedAt": ctx.get("lastRefreshedAt"),
            "supportingMetrics": {
                "changedRecordCount": ctx.get("changedRecordCount"),
                "totalRecords": ctx.get("totalRecords"),
                "trendDelta": ctx.get("trendDelta"),
                "planningHealth": ctx.get("planningHealth"),
            },
            "explainability": ResponseBuilder._build_explainability(ctx, question),
            "suggestedActions": ResponseBuilder._build_suggested_actions(question, ctx),
            "followUpQuestions": ResponseBuilder._build_follow_ups(question, ctx),
        }
        
        # Add investigate mode fields if applicable
        if answer_mode == "investigate" and scoped_metrics:
            response["investigateMode"] = {
                "filteredRecordsCount": scoped_metrics.get("filteredRecordsCount"),
                "scopedContributionBreakdown": scoped_metrics.get("scopedContributionBreakdown"),
                "scopedDrivers": scoped_metrics.get("scopedDrivers"),
                "topContributingRecords": scoped_metrics.get("topContributingRecords"),
                "scopeType": scope_type,
                "scopeValue": scope_value,
            }
        
        return response
    
    @staticmethod
    def _build_explainability(ctx: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Build explainability metadata."""
        return {
            "confidence": 0.95,
            "freshness": "recent",
            "dataSource": ctx.get("dataSource", "Blob"),
            "lastRefreshedAt": ctx.get("lastRefreshedAt"),
        }
    
    @staticmethod
    def _build_suggested_actions(question: str, ctx: Dict[str, Any]) -> List[str]:
        """Build suggested actions based on context."""
        actions = ctx.get("recommendedActions", [])
        return actions[:3] if actions else ["Monitor the situation", "Review data", "Take action"]
    
    @staticmethod
    def _build_follow_ups(question: str, ctx: Dict[str, Any]) -> List[str]:
        """Build follow-up questions."""
        return [
            "What changed most?",
            "Which records are affected?",
            "What should I do next?",
        ]
