"""
LLM Analysis Cache
Stores the LLM's initial analysis of the full dataset to avoid re-analyzing on every prompt.
This is done once when the UI loads, then reused for all subsequent questions.
"""

import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Global cache for LLM analysis
_analysis_cache: Dict[str, str] = {}


def get_cached_analysis(snapshot_date: str) -> Optional[str]:
    """
    Get cached LLM analysis for a specific snapshot date.
    
    Args:
        snapshot_date: Date of the snapshot (used as cache key)
    
    Returns:
        Cached analysis string or None if not cached
    """
    return _analysis_cache.get(snapshot_date)


def set_cached_analysis(snapshot_date: str, analysis: str) -> None:
    """
    Cache the LLM analysis for a specific snapshot date.
    
    Args:
        snapshot_date: Date of the snapshot (used as cache key)
        analysis: The LLM's analysis of the full dataset
    """
    _analysis_cache[snapshot_date] = analysis
    logger.info(f"Cached LLM analysis for snapshot {snapshot_date} ({len(analysis)} chars)")


def clear_cache() -> None:
    """Clear the analysis cache."""
    _analysis_cache.clear()
    logger.info("Cleared LLM analysis cache")


def generate_initial_analysis(llm_service, detail_records: list, context: dict) -> str:
    """
    Generate initial LLM analysis of the full dataset.
    This is called once when the UI loads.
    
    Args:
        llm_service: LLM service instance
        detail_records: All planning records
        context: Dashboard context with metrics
    
    Returns:
        LLM's analysis of the dataset
    """
    
    # Build comprehensive context for initial analysis
    analysis_context = {
        "totalRecords": len(detail_records),
        "changedRecords": sum(1 for r in detail_records if r.get("changed")),
        "planningHealth": context.get("planningHealth", 0),
        "status": context.get("status", "Unknown"),
        "forecastNew": context.get("forecastNew", 0),
        "forecastOld": context.get("forecastOld", 0),
        "trendDelta": context.get("trendDelta", 0),
        "trendDirection": context.get("trendDirection", "Stable"),
        "riskSummary": context.get("riskSummary", {}),
        "supplierSummary": context.get("supplierSummary", {}),
        "designSummary": context.get("designSummary", {}),
        "rojSummary": context.get("rojSummary", {}),
        "materialGroups": context.get("materialGroups", []),
        "datacenterCount": context.get("datacenterCount", 0),
        "kpis": context.get("kpis", {}),
    }
    
    # System prompt for initial analysis
    system_prompt = """You are a Planning Intelligence expert analyzing supply chain planning data.
Your task is to provide a comprehensive analysis of the entire dataset that will be used to answer user questions.

Analyze the data and provide:
1. Executive Summary - Overall planning health and key metrics
2. Key Drivers - What's causing changes (suppliers, design, forecast, schedule)
3. Risk Assessment - High-risk areas and concentrations
4. Trend Analysis - Direction and volatility of changes
5. Supplier Impact - Which suppliers are most affected
6. Material Impact - Which materials are most affected
7. Location Impact - Which locations are most affected
8. Recommendations - Top 3 actions to improve planning health

Be specific with numbers and percentages. Reference the actual data provided."""
    
    # User prompt for initial analysis
    user_prompt = f"""Please analyze this planning intelligence dataset:

{json.dumps(analysis_context, indent=2)}

Provide a comprehensive analysis that covers all aspects of the planning data.
This analysis will be used to answer user questions about the dataset."""
    
    # Call LLM with full context for one-time analysis
    try:
        logger.info("Generating initial LLM analysis of full dataset...")
        analysis = llm_service.generate_response(
            prompt=user_prompt,
            context=analysis_context,
            detail_records=detail_records,  # Pass full records for comprehensive analysis
            system_prompt=system_prompt
        )
        logger.info(f"Initial analysis generated ({len(analysis)} chars)")
        return analysis
    except Exception as e:
        logger.error(f"Failed to generate initial analysis: {str(e)}")
        raise


def build_prompt_with_analysis(user_question: str, cached_analysis: str, context: dict) -> str:
    """
    Build a prompt that uses the cached analysis to answer a user question.
    
    Args:
        user_question: The user's question
        cached_analysis: The cached LLM analysis from initial load
        context: Current dashboard context
    
    Returns:
        Prompt for the LLM to answer the question using the analysis
    """
    
    prompt = f"""You have previously analyzed a planning intelligence dataset and provided this analysis:

<DATASET_ANALYSIS>
{cached_analysis}
</DATASET_ANALYSIS>

Current Metrics:
- Planning Health: {context.get('planningHealth', 0)}/100
- Status: {context.get('status', 'Unknown')}
- Changed Records: {context.get('changedRecordCount', 0)}/{context.get('totalRecords', 0)}
- Trend: {context.get('trendDirection', 'Stable')}

User Question: {user_question}

Based on the analysis above and current metrics, answer the user's question directly and specifically.
Reference the analysis when relevant. Keep the answer concise and actionable."""
    
    return prompt
