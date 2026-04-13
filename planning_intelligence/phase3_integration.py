"""
Phase 3: Integration - Integrate Phase 1 and Phase 2 with function_app.py

This module provides the integration layer that:
1. Uses Phase 1 scope extraction and classification
2. Uses Phase 2 answer templates
3. Integrates with the existing explain() endpoint
4. Builds responses with investigate mode fields
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

from phase1_core_functions import (
    ScopeExtractor,
    QuestionClassifier,
    AnswerModeDecider,
    ScopedMetricsComputer
)
from phase2_answer_templates import AnswerTemplates, ResponseBuilder

logger = logging.getLogger(__name__)


class Phase3Integration:
    """Integration layer for Phase 1-2 with function_app.py"""
    
    @staticmethod
    def process_question_with_phases(
        question: str,
        detail_records: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process question through Phase 1-2 pipeline.
        
        Returns: {
            "question": str,
            "answer": str,
            "queryType": str,
            "answerMode": str,
            "scopeType": Optional[str],
            "scopeValue": Optional[str],
            "investigateMode": Optional[Dict],
            "supportingMetrics": Dict,
            "explainability": Dict,
            "suggestedActions": List[str],
            "followUpQuestions": List[str],
        }
        """
        logger.info(f"Processing question through Phase 1-2: {question}")
        
        # Ensure context has detailRecords
        if context is None:
            context = {}
        context["detailRecords"] = detail_records
        
        # Phase 1: Classification and Scope Extraction
        query_type, scope_type, scope_value = QuestionClassifier.classify_with_scope(question)
        logger.info(f"Phase 1 Classification: query_type={query_type}, scope_type={scope_type}, scope_value={scope_value}")
        
        # Phase 1: Answer Mode Determination
        answer_mode = AnswerModeDecider.determine_answer_mode(query_type, scope_type)
        logger.info(f"Phase 1 Answer Mode: {answer_mode}")
        
        # Phase 1: Scoped Metrics Computation (if needed)
        scoped_metrics = None
        if answer_mode == "investigate" and scope_type and scope_value:
            scoped_metrics = ScopedMetricsComputer.compute_scoped_metrics(
                detail_records, scope_type, scope_value
            )
            logger.info(f"Phase 1 Scoped Metrics: {scoped_metrics['filteredRecordsCount']} records")
        
        # Phase 2: Answer Generation
        answer = Phase3Integration._generate_answer(
            question=question,
            query_type=query_type,
            answer_mode=answer_mode,
            scope_type=scope_type,
            scope_value=scope_value,
            scoped_metrics=scoped_metrics,
            context=context
        )
        logger.info(f"Phase 2 Answer Generated: {len(answer)} chars")
        
        # Phase 2: Response Building
        response = ResponseBuilder.build_response(
            question=question,
            answer=answer,
            query_type=query_type,
            answer_mode=answer_mode,
            ctx=context,
            scope_type=scope_type,
            scope_value=scope_value,
            scoped_metrics=scoped_metrics
        )
        
        # Add Phase 1-2 metadata
        response["scopeType"] = scope_type
        response["scopeValue"] = scope_value
        response["phase1Processed"] = True
        response["phase2Processed"] = True
        
        logger.info(f"Phase 3 Integration Complete: {response['answerMode']} mode")
        return response
    
    @staticmethod
    def _generate_answer(
        question: str,
        query_type: str,
        answer_mode: str,
        scope_type: Optional[str],
        scope_value: Optional[str],
        scoped_metrics: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """Generate answer using Phase 2 templates."""
        
        if query_type == "comparison":
            # Extract comparison entities
            entities = ScopeExtractor.extract_comparison_entities(question)
            if len(entities) >= 2:
                # Build scoped metrics for each entity
                scoped_metrics_dict = {}
                for entity in entities[:2]:
                    metrics = ScopedMetricsComputer.compute_scoped_metrics(
                        context.get("detailRecords", []),
                        scope_type or "location",
                        entity
                    )
                    scoped_metrics_dict[entity] = metrics
                
                return AnswerTemplates.generate_comparison_answer(
                    question=question,
                    ctx=context,
                    entities=entities[:2],
                    scoped_metrics=scoped_metrics_dict
                )
        
        elif query_type == "root_cause":
            if scope_value and scoped_metrics:
                return AnswerTemplates.generate_root_cause_answer(
                    question=question,
                    ctx=context,
                    scope_type=scope_type,
                    scope_value=scope_value,
                    scoped_metrics=scoped_metrics
                )
        
        elif query_type == "why_not":
            if scope_value and scoped_metrics:
                return AnswerTemplates.generate_why_not_answer(
                    question=question,
                    ctx=context,
                    scope_type=scope_type,
                    scope_value=scope_value,
                    scoped_metrics=scoped_metrics
                )
        
        elif query_type == "traceability":
            # For traceability, compute global metrics if no scope
            if not scoped_metrics:
                # Compute global metrics for all records
                detail_records = context.get("detailRecords", [])
                if detail_records:
                    scoped_metrics = {
                        "filteredRecordsCount": len(detail_records),
                        "changedCount": sum(1 for r in detail_records if r.get("changed", False)),
                        "changeRate": round(
                            sum(1 for r in detail_records if r.get("changed", False)) / max(len(detail_records), 1) * 100, 1
                        ),
                        "scopedContributionBreakdown": {},
                        "scopedDrivers": {},
                        "topContributingRecords": sorted(
                            detail_records,
                            key=lambda r: abs(r.get("qtyDelta", 0)),
                            reverse=True
                        )[:5]
                    }
            
            if scoped_metrics:
                return AnswerTemplates.generate_traceability_answer(
                    question=question,
                    ctx=context,
                    scoped_metrics=scoped_metrics
                )
        
        # Default to summary
        return AnswerTemplates.generate_summary_answer(
            question=question,
            ctx=context
        )
    
    @staticmethod
    def extract_scope_from_question(question: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract scope from question (for backward compatibility)."""
        return ScopeExtractor.extract_scope(question)
    
    @staticmethod
    def classify_question(question: str) -> str:
        """Classify question (for backward compatibility)."""
        query_type, _, _ = QuestionClassifier.classify_with_scope(question)
        return query_type
    
    @staticmethod
    def determine_answer_mode(query_type: str, scope_type: Optional[str]) -> str:
        """Determine answer mode (for backward compatibility)."""
        return AnswerModeDecider.determine_answer_mode(query_type, scope_type)
    
    @staticmethod
    def compute_scoped_metrics(
        detail_records: List[Dict[str, Any]],
        scope_type: str,
        scope_value: str
    ) -> Dict[str, Any]:
        """Compute scoped metrics (for backward compatibility)."""
        return ScopedMetricsComputer.compute_scoped_metrics(
            detail_records, scope_type, scope_value
        )
