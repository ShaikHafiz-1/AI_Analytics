"""
Session Memory Manager - Stores conversation context for follow-up queries

Maintains:
- Last question asked
- Last response generated
- Last intent detected
- Last supporting metrics
- Last record keys

Enables:
- Transform intent detection (table/tabular/format)
- Instant response formatting without recomputation
- Context-aware follow-up queries
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Global session storage (in production, use Redis or similar)
_session_store: Dict[str, Dict[str, Any]] = {}

# Session timeout: 30 minutes
SESSION_TIMEOUT_MINUTES = 30


class SessionContext:
    """Stores conversation context for a session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.last_question: Optional[str] = None
        self.last_response: Optional[Dict[str, Any]] = None
        self.last_intent: Optional[str] = None
        self.last_timestamp: Optional[datetime] = None
    
    def update(
        self,
        question: str,
        response: Dict[str, Any],
        intent: str
    ) -> None:
        """
        Update session context with new response.
        
        Args:
            question: User question
            response: Generated response with answer, supportingMetrics, recordKeys
            intent: Detected intent
        """
        self.last_question = question
        self.last_response = response
        self.last_intent = intent
        self.last_timestamp = datetime.now()
        
        logger.info(f"[SESSION] Updated context - intent: {intent}, question: {question[:50]}")
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        if not self.last_timestamp:
            return True
        
        elapsed = datetime.now() - self.last_timestamp
        return elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    
    def get_last_response(self) -> Optional[Dict[str, Any]]:
        """Get last response if session is still valid."""
        if self.is_expired():
            logger.info(f"[SESSION] Session expired for {self.session_id}")
            return None
        
        return self.last_response
    
    def clear(self) -> None:
        """Clear session context."""
        self.last_question = None
        self.last_response = None
        self.last_intent = None
        self.last_timestamp = None
        logger.info(f"[SESSION] Cleared context for {self.session_id}")


def get_or_create_session(session_id: str) -> SessionContext:
    """
    Get or create session context.
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        SessionContext: Session context object
    """
    if session_id not in _session_store:
        _session_store[session_id] = SessionContext(session_id)
        logger.info(f"[SESSION] Created new session: {session_id}")
    
    return _session_store[session_id]


def detect_transform_intent(question: str) -> bool:
    """
    Detect if question is asking for format transformation.
    
    Looks for keywords like:
    - table
    - tabular
    - format
    - convert
    - show as
    - display as
    - structured
    
    Args:
        question: User question
    
    Returns:
        bool: True if transform intent detected
    """
    question_lower = question.lower()
    
    transform_keywords = [
        "transform to table",
        "tabular form",
        "tabular",
        "format",
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
        "csv",
        "columns",
        "rows"
    ]
    
    for keyword in transform_keywords:
        if keyword in question_lower:
            logger.info(f"[TRANSFORM] Detected transform intent - keyword: '{keyword}'")
            return True
    
    return False


def format_response_as_table(response: Dict[str, Any]) -> str:
    """
    Format response data as a markdown table.
    
    Args:
        response: Response with answer, supportingMetrics, recordKeys
    
    Returns:
        str: Formatted table string
    """
    answer = response.get("answer", "")
    metrics = response.get("supportingMetrics", {})
    record_keys = response.get("recordKeys", [])
    
    # Start with answer summary
    table = f"## Summary\n{answer}\n\n"
    
    # Build metrics table
    if metrics:
        table += "## Metrics\n"
        table += "|Metric|Value|\n"
        table += "|---|---|\n"
        
        for key, value in metrics.items():
            # Format key as readable
            readable_key = key.replace("_", " ").title()
            table += f"|{readable_key}|{value}|\n"
        
        table += "\n"
    
    # Build record keys table
    if record_keys:
        table += "## Top Impacted Records\n"
        
        # Determine columns from first record
        if len(record_keys) > 0:
            first_record = record_keys[0]
            columns = list(first_record.keys())
            
            # Build header
            table += "|" + "|".join(columns) + "|\n"
            table += "|" + "|".join(["---"] * len(columns)) + "|\n"
            
            # Build rows (top 10)
            for record in record_keys[:10]:
                values = [str(record.get(col, "N/A")) for col in columns]
                table += "|" + "|".join(values) + "|\n"
    
    logger.info(f"[TRANSFORM] Formatted response as table")
    
    return table


def handle_transform_request(
    session_id: str,
    question: str
) -> Optional[Dict[str, Any]]:
    """
    Handle transform request using cached response.
    
    Args:
        session_id: Session identifier
        question: User question
    
    Returns:
        dict: Transformed response or None if no cached response
    """
    session = get_or_create_session(session_id)
    
    # Get last response
    last_response = session.get_last_response()
    if not last_response:
        logger.warning(f"[TRANSFORM] No cached response available for session {session_id}")
        return None
    
    # Format as table
    table_answer = format_response_as_table(last_response)
    
    # Return transformed response
    transformed = {
        "answer": table_answer,
        "supportingMetrics": last_response.get("supportingMetrics", {}),
        "recordKeys": last_response.get("recordKeys", []),
        "isTransformed": True,
        "originalQuestion": session.last_question,
        "transformedQuestion": question
    }
    
    logger.info(f"[TRANSFORM] Handled transform request - returned cached response as table")
    
    return transformed


def update_session_after_response(
    session_id: str,
    question: str,
    response: Dict[str, Any],
    intent: str
) -> None:
    """
    Update session after generating response.
    
    Args:
        session_id: Session identifier
        question: User question
        response: Generated response
        intent: Detected intent
    """
    session = get_or_create_session(session_id)
    session.update(question=question, response=response, intent=intent)


def clear_session(session_id: str) -> None:
    """
    Clear session context.
    
    Args:
        session_id: Session identifier
    """
    if session_id in _session_store:
        _session_store[session_id].clear()
        del _session_store[session_id]
        logger.info(f"[SESSION] Cleared session: {session_id}")
