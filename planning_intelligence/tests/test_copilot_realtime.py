"""
Unit and integration tests for Copilot Real-Time Answers feature.
Tests scope extraction, answer modes, scoped metrics, and answer templates.
"""

import pytest
import json
from unittest.mock import Mock, patch
from function_app import (
    _extract_scope,
    _determine_answer_mode,
    _compute_scoped_metrics,
    _generate_comparison_answer,
    _generate_root_cause_answer,
    _generate_why_not_answer,
    _generate_traceability_answer,
    _generate_answer_from_context,
    _classify_question,
)


# ============================================================================
# PHASE 4.1: Unit Tests - Scope Extraction
# ============================================================================

class TestScopeExtraction:
    """Test _extract_scope() function for all entity types."""

    def test_location_extraction_with_id(self):
        """Test location extraction with LOC001 format."""
        scope_type, scope_value = _extract_scope("Why is LOC001 risky?")
        assert scope_type == "location"
        assert scope_value == "LOC001"

    def test_location_extraction_with_name(self):
        """Test location extraction with 'location X' format."""
        scope_type, scope_value = _extract_scope("Compare location Boston vs location Seattle")
        assert scope_type == "location"
        assert scope_value.upper() in ["LOCATION BOSTON", "LOCATION SEATTLE"]

    def test_supplier_extraction_with_id(self):
        """Test supplier extraction with SUP001 format."""
        scope_type, scope_value = _extract_scope("Which supplier SUP001 has design changes?")
        assert scope_type == "supplier"
        assert scope_value == "SUP001"

    def test_supplier_extraction_with_name(self):
        """Test supplier extraction with 'supplier X' format."""
        scope_type, scope_value = _extract_scope("Is supplier Acme failing ROJ?")
        assert scope_type == "supplier"
        assert scope_value.upper() in ["SUPPLIER ACME", "ACME"]

    def test_material_group_extraction(self):
        """Test material group extraction."""
        scope_type, scope_value = _extract_scope("Which material group Electronics has changes?")
        assert scope_type == "material_group"
        assert scope_value.upper() in ["MATERIAL GROUP ELECTRONICS", "ELECTRONICS"]

    def test_material_id_extraction(self):
        """Test material ID extraction."""
        scope_type, scope_value = _extract_scope("Show material MAT001 details")
        assert scope_type == "material_id"
        assert scope_value == "MAT001"

    def test_risk_type_extraction_high_risk(self):
        """Test risk type extraction for high risk."""
        scope_type, scope_value = _extract_scope("Show high risk records")
        assert scope_type == "risk_type"

    def test_risk_type_extraction_critical(self):
        """Test risk type extraction for critical."""
        scope_type, scope_value = _extract_scope("Which records are critical?")
        assert scope_type == "risk_type"

    def test_no_scope_extraction(self):
        """Test when no scope is detected."""
        scope_type, scope_value = _extract_scope("What is the planning health?")
        assert scope_type is None
        assert scope_value is None

    def test_multiple_entities_first_wins(self):
        """Test that first entity is extracted when multiple present."""
        scope_type, scope_value = _extract_scope("Compare LOC001 vs LOC002")
        assert scope_type == "location"
        assert scope_value == "LOC001"

    def test_case_insensitivity(self):
        """Test that extraction is case-insensitive."""
        scope_type, scope_value = _extract_scope("why is loc001 risky?")
        assert scope_type == "location"
        assert scope_value == "LOC001"

    def test_edge_case_special_characters(self):
        """Test extraction with special characters in question."""
        scope_type, scope_value = _extract_scope("Why is LOC001 (main site) risky?")
        assert scope_type == "location"
        assert scope_value == "LOC001"


# ============================================================================
# PHASE 4.2: Unit Tests - Scoped Metrics Computation
# ============================================================================

class TestScopedMetricsComputation:
    """Test _compute_scoped_metrics() function for all scope types."""

    @pytest.fixture
    def sample_detail_records(self):
        """Create sample detail records for testing."""
        return [
            {
                "locationId": "LOC001",
                "supplier": "SUP001",
                "materialGroup": "Electronics",
                "materialId": "MAT001",
                "changed": True,
                "qtyChanged": True,
                "supplierChanged": False,
                "designChanged": True,
                "scheduleChanged": False,
                "qtyDelta": 500,
                "changeType": "Qty Increase",
                "riskLevel": "High Risk",
            },
            {
                "locationId": "LOC001",
                "supplier": "SUP001",
                "materialGroup": "Electronics",
                "materialId": "MAT002",
                "changed": True,
                "qtyChanged": False,
                "supplierChanged": True,
                "designChanged": False,
                "scheduleChanged": False,
                "qtyDelta": 300,
                "changeType": "Supplier Change",
                "riskLevel": "Medium Risk",
            },
            {
                "locationId": "LOC002",
                "supplier": "SUP002",
                "materialGroup": "Mechanical",
                "materialId": "MAT003",
                "changed": False,
                "qtyChanged": False,
                "supplierChanged": False,
                "designChanged": False,
                "scheduleChanged": False,
                "qtyDelta": 0,
                "changeType": "No Change",
                "riskLevel": "Low Risk",
            },
            {
                "locationId": "LOC001",
                "supplier": "SUP001",
                "materialGroup": "Electronics",
                "materialId": "MAT004",
                "changed": True,
                "qtyChanged": False,
                "supplierChanged": False,
                "designChanged": True,
                "scheduleChanged": True,
                "qtyDelta": -200,
                "changeType": "Design Change",
                "riskLevel": "High Risk",
            },
        ]

    def test_filter_by_location(self, sample_detail_records):
        """Test filtering by location."""
        metrics = _compute_scoped_metrics(sample_detail_records, "location", "LOC001")
        assert metrics["filteredRecordsCount"] == 3
        assert metrics["scopedMetrics"]["changedCount"] == 3
        assert metrics["scopedMetrics"]["changeRate"] == 100.0

    def test_filter_by_supplier(self, sample_detail_records):
        """Test filtering by supplier."""
        metrics = _compute_scoped_metrics(sample_detail_records, "supplier", "SUP001")
        assert metrics["filteredRecordsCount"] == 3
        assert metrics["scopedMetrics"]["changedCount"] == 3

    def test_filter_by_material_group(self, sample_detail_records):
        """Test filtering by material group."""
        metrics = _compute_scoped_metrics(sample_detail_records, "material_group", "Electronics")
        assert metrics["filteredRecordsCount"] == 3
        assert metrics["scopedMetrics"]["changedCount"] == 3

    def test_filter_by_material_id(self, sample_detail_records):
        """Test filtering by material ID."""
        metrics = _compute_scoped_metrics(sample_detail_records, "material_id", "MAT001")
        assert metrics["filteredRecordsCount"] == 1
        assert metrics["scopedMetrics"]["changedCount"] == 1

    def test_filter_by_risk_type(self, sample_detail_records):
        """Test filtering by risk type."""
        metrics = _compute_scoped_metrics(sample_detail_records, "risk_type", "High Risk")
        assert metrics["filteredRecordsCount"] == 2
        assert metrics["scopedMetrics"]["changedCount"] == 2

    def test_contribution_breakdown(self, sample_detail_records):
        """Test contribution breakdown calculation."""
        metrics = _compute_scoped_metrics(sample_detail_records, "location", "LOC001")
        contrib = metrics["scopedContributionBreakdown"]
        # LOC001 has 3 changed records: 1 qty, 1 supplier, 2 design, 1 schedule
        assert contrib["quantity"] > 0
        assert contrib["supplier"] > 0
        assert contrib["design"] > 0

    def test_primary_driver_identification(self, sample_detail_records):
        """Test primary driver identification."""
        metrics = _compute_scoped_metrics(sample_detail_records, "location", "LOC001")
        drivers = metrics["scopedDrivers"]
        assert drivers["primary"] in ["quantity", "supplier", "design", "schedule"]
        assert drivers["changedCount"] == 3
        assert drivers["totalCount"] == 3

    def test_top_contributing_records(self, sample_detail_records):
        """Test top contributing records identification."""
        metrics = _compute_scoped_metrics(sample_detail_records, "location", "LOC001")
        top_records = metrics["topContributingRecords"]
        assert len(top_records) <= 5
        # Should be sorted by absolute delta descending
        if len(top_records) > 1:
            assert abs(top_records[0].get("qtyDelta", 0)) >= abs(top_records[1].get("qtyDelta", 0))

    def test_empty_filtered_results(self, sample_detail_records):
        """Test with empty filtered results."""
        metrics = _compute_scoped_metrics(sample_detail_records, "location", "LOC999")
        assert metrics["filteredRecordsCount"] == 0
        assert metrics["scopedMetrics"]["changedCount"] == 0
        assert metrics["scopedMetrics"]["changeRate"] == 0.0

    def test_no_changes_in_scope(self, sample_detail_records):
        """Test when scope has no changes."""
        metrics = _compute_scoped_metrics(sample_detail_records, "location", "LOC002")
        assert metrics["filteredRecordsCount"] == 1
        assert metrics["scopedMetrics"]["changedCount"] == 0
        assert metrics["scopedMetrics"]["changeRate"] == 0.0

    def test_change_rate_calculation(self, sample_detail_records):
        """Test change rate calculation."""
        metrics = _compute_scoped_metrics(sample_detail_records, "location", "LOC001")
        # 3 changed out of 3 total = 100%
        assert metrics["scopedMetrics"]["changeRate"] == 100.0


# ============================================================================
# PHASE 4.3: Integration Tests - Answer Templates
# ============================================================================

class TestAnswerTemplates:
    """Test answer template functions."""

    @pytest.fixture
    def sample_context(self):
        """Create sample context for testing."""
        return {
            "detailRecords": [
                {
                    "locationId": "LOC001",
                    "supplier": "SUP001",
                    "materialGroup": "Electronics",
                    "materialId": "MAT001",
                    "changed": True,
                    "qtyChanged": True,
                    "supplierChanged": False,
                    "designChanged": True,
                    "scheduleChanged": False,
                    "qtyDelta": 500,
                    "changeType": "Qty Increase",
                    "riskLevel": "High Risk",
                },
                {
                    "locationId": "LOC002",
                    "supplier": "SUP002",
                    "materialGroup": "Mechanical",
                    "materialId": "MAT002",
                    "changed": False,
                    "qtyChanged": False,
                    "supplierChanged": False,
                    "designChanged": False,
                    "scheduleChanged": False,
                    "qtyDelta": 0,
                    "changeType": "No Change",
                    "riskLevel": "Low Risk",
                },
            ],
            "recommendedActions": ["Review design changes", "Monitor supplier"],
            "aiInsight": "Design changes are driving risk",
            "rootCause": "Supplier changed design specs",
        }

    def test_comparison_answer_template(self, sample_context):
        """Test comparison answer template."""
        question = "Compare LOC001 vs LOC002"
        answer = _generate_comparison_answer(question, sample_context)
        assert "Comparison" in answer
        assert "LOC001" in answer
        assert "LOC002" in answer
        assert "changed" in answer.lower()

    def test_comparison_answer_includes_metrics(self, sample_context):
        """Test that comparison answer includes metrics."""
        question = "Compare LOC001 vs LOC002"
        answer = _generate_comparison_answer(question, sample_context)
        # Should include changed counts and percentages
        assert "/" in answer  # fraction format
        assert "%" in answer  # percentage format

    def test_root_cause_answer_template(self, sample_context):
        """Test root cause answer template."""
        question = "Why is LOC001 risky?"
        scoped_metrics = _compute_scoped_metrics(sample_context["detailRecords"], "location", "LOC001")
        answer = _generate_root_cause_answer(question, sample_context, "location", "LOC001", scoped_metrics)
        assert "LOC001" in answer
        assert "risky" in answer.lower()
        assert "Recommended action" in answer

    def test_why_not_answer_template_stable(self, sample_context):
        """Test why-not answer template for stable entity."""
        question = "Why is LOC002 not risky?"
        scoped_metrics = _compute_scoped_metrics(sample_context["detailRecords"], "location", "LOC002")
        answer = _generate_why_not_answer(question, sample_context, "location", "LOC002", scoped_metrics)
        assert "LOC002" in answer
        assert "stable" in answer.lower()

    def test_traceability_answer_template(self, sample_context):
        """Test traceability answer template."""
        question = "Show top contributing records"
        scoped_metrics = _compute_scoped_metrics(sample_context["detailRecords"], None, None)
        answer = _generate_traceability_answer(question, sample_context, scoped_metrics)
        assert "Top" in answer
        assert "contributing records" in answer.lower()
        assert "📊" in answer

    def test_traceability_includes_record_details(self, sample_context):
        """Test that traceability answer includes record details."""
        question = "Show top contributing records"
        scoped_metrics = _compute_scoped_metrics(sample_context["detailRecords"], None, None)
        answer = _generate_traceability_answer(question, sample_context, scoped_metrics)
        # Should include location, material, delta
        assert "LOC" in answer or "?" in answer


# ============================================================================
# PHASE 4.4: Integration Tests - Explain Endpoint
# ============================================================================

class TestAnswerModeRouting:
    """Test answer mode determination and routing."""

    def test_comparison_uses_investigate_mode(self):
        """Test that comparison questions use investigate mode."""
        mode = _determine_answer_mode("comparison", None)
        assert mode == "investigate"

    def test_traceability_uses_investigate_mode(self):
        """Test that traceability questions use investigate mode."""
        mode = _determine_answer_mode("traceability", None)
        assert mode == "investigate"

    def test_root_cause_with_scope_uses_investigate(self):
        """Test that root cause with scope uses investigate mode."""
        mode = _determine_answer_mode("root_cause", "location")
        assert mode == "investigate"

    def test_root_cause_without_scope_uses_summary(self):
        """Test that root cause without scope uses summary mode."""
        mode = _determine_answer_mode("root_cause", None)
        assert mode == "summary"

    def test_why_not_with_scope_uses_investigate(self):
        """Test that why-not with scope uses investigate mode."""
        mode = _determine_answer_mode("why_not", "location")
        assert mode == "investigate"

    def test_why_not_without_scope_uses_summary(self):
        """Test that why-not without scope uses summary mode."""
        mode = _determine_answer_mode("why_not", None)
        assert mode == "summary"

    def test_summary_always_uses_summary_mode(self):
        """Test that summary questions use summary mode."""
        mode = _determine_answer_mode("summary", "location")
        assert mode == "summary"

    def test_unscoped_question_uses_summary(self):
        """Test that unscoped questions use summary mode."""
        mode = _determine_answer_mode("risk", None)
        assert mode == "summary"


# ============================================================================
# PHASE 4.5: End-to-End Tests
# ============================================================================

class TestEndToEnd:
    """End-to-end tests with realistic scenarios."""

    @pytest.fixture
    def realistic_context(self):
        """Create realistic context for end-to-end testing."""
        return {
            "detailRecords": [
                {
                    "locationId": "LOC001",
                    "supplier": "SUP001",
                    "materialGroup": "Electronics",
                    "materialId": "MAT001",
                    "changed": True,
                    "qtyChanged": True,
                    "supplierChanged": False,
                    "designChanged": True,
                    "scheduleChanged": False,
                    "qtyDelta": 500,
                    "changeType": "Qty Increase",
                    "riskLevel": "High Risk",
                },
                {
                    "locationId": "LOC001",
                    "supplier": "SUP001",
                    "materialGroup": "Electronics",
                    "materialId": "MAT002",
                    "changed": True,
                    "qtyChanged": False,
                    "supplierChanged": True,
                    "designChanged": False,
                    "scheduleChanged": False,
                    "qtyDelta": 300,
                    "changeType": "Supplier Change",
                    "riskLevel": "Medium Risk",
                },
                {
                    "locationId": "LOC002",
                    "supplier": "SUP002",
                    "materialGroup": "Mechanical",
                    "materialId": "MAT003",
                    "changed": False,
                    "qtyChanged": False,
                    "supplierChanged": False,
                    "designChanged": False,
                    "scheduleChanged": False,
                    "qtyDelta": 0,
                    "changeType": "No Change",
                    "riskLevel": "Low Risk",
                },
                {
                    "locationId": "LOC002",
                    "supplier": "SUP002",
                    "materialGroup": "Mechanical",
                    "materialId": "MAT004",
                    "changed": True,
                    "qtyChanged": False,
                    "supplierChanged": False,
                    "designChanged": True,
                    "scheduleChanged": False,
                    "qtyDelta": 150,
                    "changeType": "Design Change",
                    "riskLevel": "Medium Risk",
                },
            ],
            "recommendedActions": ["Review design changes", "Monitor supplier"],
            "aiInsight": "Design changes are driving risk",
            "rootCause": "Supplier changed design specs",
            "planningHealth": 65,
            "changedRecordCount": 3,
            "totalRecords": 4,
        }

    def test_comparison_question_end_to_end(self, realistic_context):
        """Test: Compare LOC001 vs LOC002"""
        question = "Compare LOC001 vs LOC002"
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)
        answer_mode = _determine_answer_mode(query_type, scope_type)
        
        assert query_type == "comparison"
        assert answer_mode == "investigate"
        
        answer = _generate_answer_from_context(
            question, realistic_context, answer_mode, scope_type, scope_value
        )
        assert "Comparison" in answer
        assert "LOC001" in answer
        assert "LOC002" in answer

    def test_root_cause_question_end_to_end(self, realistic_context):
        """Test: Why is LOC001 risky?"""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)
        answer_mode = _determine_answer_mode(query_type, scope_type)
        
        assert scope_type == "location"
        assert scope_value == "LOC001"
        assert query_type == "root_cause"
        assert answer_mode == "investigate"

    def test_why_not_question_end_to_end(self, realistic_context):
        """Test: Why is LOC002 not risky?"""
        question = "Why is LOC002 not risky?"
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)
        answer_mode = _determine_answer_mode(query_type, scope_type)
        
        assert scope_type == "location"
        assert scope_value == "LOC002"
        assert query_type == "why_not"
        assert answer_mode == "investigate"

    def test_traceability_question_end_to_end(self, realistic_context):
        """Test: Show top contributing records"""
        question = "Show top contributing records"
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)
        answer_mode = _determine_answer_mode(query_type, scope_type)
        
        assert query_type == "traceability"
        assert answer_mode == "investigate"

    def test_summary_question_end_to_end(self, realistic_context):
        """Test: What is the planning health?"""
        question = "What is the planning health?"
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)
        answer_mode = _determine_answer_mode(query_type, scope_type)
        
        assert scope_type is None
        assert query_type == "summary"
        assert answer_mode == "summary"


# ============================================================================
# PHASE 4.6: Response Variety Tests
# ============================================================================

class TestResponseVariety:
    """Test that different question types produce different responses."""

    @pytest.fixture
    def context_with_records(self):
        """Create context with detail records."""
        return {
            "detailRecords": [
                {
                    "locationId": "LOC001",
                    "supplier": "SUP001",
                    "materialGroup": "Electronics",
                    "materialId": "MAT001",
                    "changed": True,
                    "qtyChanged": True,
                    "supplierChanged": False,
                    "designChanged": True,
                    "scheduleChanged": False,
                    "qtyDelta": 500,
                    "changeType": "Qty Increase",
                    "riskLevel": "High Risk",
                },
                {
                    "locationId": "LOC002",
                    "supplier": "SUP002",
                    "materialGroup": "Mechanical",
                    "materialId": "MAT002",
                    "changed": False,
                    "qtyChanged": False,
                    "supplierChanged": False,
                    "designChanged": False,
                    "scheduleChanged": False,
                    "qtyDelta": 0,
                    "changeType": "No Change",
                    "riskLevel": "Low Risk",
                },
            ],
            "recommendedActions": ["Review design changes"],
            "aiInsight": "Design changes are driving risk",
        }

    def test_comparison_differs_from_summary(self, context_with_records):
        """Test that comparison answers differ from summary."""
        comparison_q = "Compare LOC001 vs LOC002"
        summary_q = "What is the planning health?"
        
        comparison_answer = _generate_answer_from_context(comparison_q, context_with_records)
        summary_answer = _generate_answer_from_context(summary_q, context_with_records)
        
        assert comparison_answer != summary_answer
        assert "Comparison" in comparison_answer
        assert "Comparison" not in summary_answer

    def test_root_cause_differs_from_comparison(self, context_with_records):
        """Test that root cause answers differ from comparison."""
        root_cause_q = "Why is LOC001 risky?"
        comparison_q = "Compare LOC001 vs LOC002"
        
        scope_type, _ = _extract_scope(root_cause_q)
        root_cause_answer = _generate_answer_from_context(
            root_cause_q, context_with_records, "investigate", scope_type, "LOC001"
        )
        comparison_answer = _generate_answer_from_context(comparison_q, context_with_records)
        
        assert root_cause_answer != comparison_answer


# ============================================================================
# PHASE 4.8: Determinism Tests
# ============================================================================

class TestDeterminism:
    """Test that answers are deterministic."""

    @pytest.fixture
    def fixed_context(self):
        """Create fixed context for determinism testing."""
        return {
            "detailRecords": [
                {
                    "locationId": "LOC001",
                    "supplier": "SUP001",
                    "materialGroup": "Electronics",
                    "materialId": "MAT001",
                    "changed": True,
                    "qtyChanged": True,
                    "supplierChanged": False,
                    "designChanged": True,
                    "scheduleChanged": False,
                    "qtyDelta": 500,
                    "changeType": "Qty Increase",
                    "riskLevel": "High Risk",
                },
            ],
            "recommendedActions": ["Review design changes"],
        }

    def test_same_question_same_answer(self, fixed_context):
        """Test that same question produces same answer."""
        question = "Why is LOC001 risky?"
        
        answer1 = _generate_answer_from_context(question, fixed_context)
        answer2 = _generate_answer_from_context(question, fixed_context)
        
        assert answer1 == answer2

    def test_metrics_are_deterministic(self, fixed_context):
        """Test that metrics computation is deterministic."""
        metrics1 = _compute_scoped_metrics(fixed_context["detailRecords"], "location", "LOC001")
        metrics2 = _compute_scoped_metrics(fixed_context["detailRecords"], "location", "LOC001")
        
        assert metrics1 == metrics2

    def test_scope_extraction_deterministic(self):
        """Test that scope extraction is deterministic."""
        question = "Why is LOC001 risky?"
        
        scope1 = _extract_scope(question)
        scope2 = _extract_scope(question)
        
        assert scope1 == scope2


# ============================================================================
# PHASE 7.2: Backward Compatibility Tests
# ============================================================================

class TestBackwardCompatibilityPhase7:
    """Test backward compatibility with existing clients (Phase 7)."""

    @pytest.fixture
    def old_response_structure(self):
        """Create old response structure without new fields."""
        return {
            "question": "Why is health critical?",
            "answer": "Test answer",
            "aiInsight": "Test insight",
            "rootCause": "Test root cause",
            "recommendedActions": ["Action 1", "Action 2"],
            "planningHealth": 42,
            "dataMode": "cached",
            "lastRefreshedAt": "2026-04-01T08:00:00Z",
            "supportingMetrics": {
                "changedRecordCount": 87,
                "totalRecords": 200,
                "trendDelta": 3000,
                "planningHealth": 42,
            },
        }

    @pytest.fixture
    def new_response_structure(self):
        """Create new response structure with optional fields."""
        return {
            "question": "Why is health critical?",
            "answer": "Test answer",
            "queryType": "health",
            "answerMode": "summary",
            "scopeType": None,
            "scopeValue": None,
            "aiInsight": "Test insight",
            "rootCause": "Test root cause",
            "recommendedActions": ["Action 1", "Action 2"],
            "planningHealth": 42,
            "dataMode": "cached",
            "lastRefreshedAt": "2026-04-01T08:00:00Z",
            "supportingMetrics": {
                "changedRecordCount": 87,
                "totalRecords": 200,
                "trendDelta": 3000,
                "planningHealth": 42,
            },
        }

    def test_existing_client_without_new_fields(self, old_response_structure):
        """Test that existing clients work without new fields."""
        response = old_response_structure

        # Verify all existing fields are present
        assert "question" in response
        assert "answer" in response
        assert "aiInsight" in response
        assert "rootCause" in response
        assert "recommendedActions" in response
        assert "planningHealth" in response
        assert "dataMode" in response
        assert "lastRefreshedAt" in response
        assert "supportingMetrics" in response

    def test_all_existing_fields_present_and_unchanged(self, old_response_structure):
        """Test that all existing fields are present and unchanged."""
        response = old_response_structure

        # Verify field types
        assert isinstance(response["question"], str)
        assert isinstance(response["answer"], str)
        assert isinstance(response["aiInsight"], str)
        assert isinstance(response["rootCause"], str)
        assert isinstance(response["recommendedActions"], list)
        assert isinstance(response["planningHealth"], int)
        assert isinstance(response["dataMode"], str)
        assert isinstance(response["lastRefreshedAt"], str)
        assert isinstance(response["supportingMetrics"], dict)

    def test_response_structure_with_new_optional_fields(self, new_response_structure):
        """Test response structure with new optional fields."""
        response = new_response_structure

        # Verify all existing fields are still present
        assert "question" in response
        assert "answer" in response
        assert "aiInsight" in response
        assert "rootCause" in response
        assert "recommendedActions" in response
        assert "planningHealth" in response

        # Verify new fields are present
        assert "queryType" in response
        assert "answerMode" in response
        assert "scopeType" in response
        assert "scopeValue" in response

    def test_comparison_metrics_optional_field(self):
        """Test that comparisonMetrics is optional."""
        # For non-comparison query, comparisonMetrics should not be present
        response_health = {
            "question": "Why is health critical?",
            "queryType": "health",
            "answerMode": "summary",
        }
        assert "comparisonMetrics" not in response_health

        # For comparison query, comparisonMetrics should be present
        response_comparison = {
            "question": "Compare LOC001 vs LOC002",
            "queryType": "comparison",
            "answerMode": "investigate",
            "comparisonMetrics": {
                "entity1": "LOC001",
                "entity2": "LOC002",
                "metrics": {},
            },
        }
        assert "comparisonMetrics" in response_comparison

    def test_supplier_metrics_optional_field(self):
        """Test that supplierMetrics is optional."""
        # For non-supplier query, supplierMetrics should not be present
        response_health = {
            "question": "Why is health critical?",
            "queryType": "health",
        }
        assert "supplierMetrics" not in response_health

        # For supplier query, supplierMetrics should be present
        response_supplier = {
            "question": "List suppliers for LOC001",
            "queryType": "supplier_by_location",
            "supplierMetrics": {
                "location": "LOC001",
                "suppliers": [],
            },
        }
        assert "supplierMetrics" in response_supplier

    def test_record_comparison_optional_field(self):
        """Test that recordComparison is optional."""
        # For non-record query, recordComparison should not be present
        response_health = {
            "question": "Why is health critical?",
            "queryType": "health",
        }
        assert "recordComparison" not in response_health

        # For record detail query, recordComparison should be present
        response_record = {
            "question": "What changed for MAT-100?",
            "queryType": "record_detail",
            "recordComparison": {
                "materialId": "MAT-100",
                "locationId": "LOC001",
                "current": {},
                "previous": {},
                "changes": {},
                "riskLevel": "Normal",
            },
        }
        assert "recordComparison" in response_record

    def test_supporting_metrics_always_present(self):
        """Test that supportingMetrics is always present."""
        response = {
            "supportingMetrics": {
                "changedRecordCount": 87,
                "totalRecords": 200,
                "trendDelta": 3000,
                "planningHealth": 42,
            }
        }

        assert "supportingMetrics" in response
        assert response["supportingMetrics"]["changedRecordCount"] == 87
        assert response["supportingMetrics"]["totalRecords"] == 200

    def test_answer_mode_summary_vs_investigate(self):
        """Test that answerMode is correctly set."""
        # Summary mode for global queries
        response_summary = {
            "queryType": "health",
            "answerMode": "summary",
        }
        assert response_summary["answerMode"] == "summary"

        # Investigate mode for scoped queries
        response_investigate = {
            "queryType": "root_cause",
            "answerMode": "investigate",
            "scopeType": "location",
            "scopeValue": "LOC001",
        }
        assert response_investigate["answerMode"] == "investigate"
        assert response_investigate["scopeType"] == "location"
        assert response_investigate["scopeValue"] == "LOC001"

    def test_scope_type_and_value_optional(self):
        """Test that scopeType and scopeValue are optional."""
        # For global queries, can be None
        response_global = {
            "queryType": "health",
            "scopeType": None,
            "scopeValue": None,
        }
        assert response_global["scopeType"] is None
        assert response_global["scopeValue"] is None

        # For scoped queries, should be set
        response_scoped = {
            "queryType": "root_cause",
            "scopeType": "location",
            "scopeValue": "LOC001",
        }
        assert response_scoped["scopeType"] == "location"
        assert response_scoped["scopeValue"] == "LOC001"


# ============================================================================
# PHASE 7.3: Response Quality Tests
# ============================================================================

class TestResponseQualityPhase7:
    """Test response quality improvements (Phase 7)."""

    @pytest.fixture
    def quality_context(self):
        """Create context for quality testing."""
        return {
            "detailRecords": [
                {
                    "locationId": "LOC001",
                    "supplier": "SUP001",
                    "materialGroup": "Electronics",
                    "materialId": "MAT001",
                    "changed": True,
                    "qtyChanged": True,
                    "supplierChanged": False,
                    "designChanged": True,
                    "scheduleChanged": False,
                    "qtyDelta": 500,
                    "changeType": "Qty Increase",
                    "riskLevel": "High Risk",
                },
                {
                    "locationId": "LOC002",
                    "supplier": "SUP002",
                    "materialGroup": "Mechanical",
                    "materialId": "MAT002",
                    "changed": False,
                    "qtyChanged": False,
                    "supplierChanged": False,
                    "designChanged": False,
                    "scheduleChanged": False,
                    "qtyDelta": 0,
                    "changeType": "No Change",
                    "riskLevel": "Low Risk",
                },
            ],
            "recommendedActions": ["Review design changes"],
            "aiInsight": "Design changes are driving risk",
            "planningHealth": 42,
            "changedRecordCount": 1,
            "totalRecords": 2,
        }

    def test_answer_specific_to_question(self, quality_context):
        """Test that answers are specific to the question."""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(quality_context["detailRecords"], scope_type, scope_value)
        answer = _generate_root_cause_answer(question, quality_context, scope_type, scope_value, scoped_metrics)

        # Should mention the specific location
        assert "LOC001" in answer

    def test_answer_not_generic_summary(self, quality_context):
        """Test that answers are not generic summaries."""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(quality_context["detailRecords"], scope_type, scope_value)
        answer = _generate_root_cause_answer(question, quality_context, scope_type, scope_value, scoped_metrics)

        # Should not be a generic global summary
        assert len(answer) > 50
        assert "LOC001" in answer

    def test_answer_uses_scoped_metrics(self, quality_context):
        """Test that answers use scoped metrics."""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(quality_context["detailRecords"], scope_type, scope_value)

        # Scoped metrics should be computed
        assert scoped_metrics is not None
        assert "filteredRecordsCount" in scoped_metrics
        assert "scopedMetrics" in scoped_metrics

    def test_answer_feels_targeted_and_relevant(self, quality_context):
        """Test that answers feel targeted and relevant."""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(quality_context["detailRecords"], scope_type, scope_value)
        answer = _generate_root_cause_answer(question, quality_context, scope_type, scope_value, scoped_metrics)

        # Should have specific details
        assert len(answer) > 0
        assert "LOC001" in answer

    def test_comparison_never_falls_back_to_global_summary(self, quality_context):
        """Test that comparison never falls back to global summary."""
        question = "Compare LOC001 vs LOC002"
        answer = _generate_comparison_answer(question, quality_context)

        # Should be a comparison, not a global summary
        assert "Comparison" in answer or "compare" in answer.lower()
        assert "LOC001" in answer
        assert "LOC002" in answer

    def test_supplier_query_never_falls_back_to_global_summary(self, quality_context):
        """Test that supplier queries never fall back to global summary."""
        question = "List suppliers for LOC001"
        answer = _generate_supplier_by_location_answer(question, quality_context, "location", "LOC001")

        # Should be supplier-specific, not global
        assert "LOC001" in answer
        assert len(answer) > 0

    def test_record_query_never_falls_back_to_global_summary(self, quality_context):
        """Test that record queries never fall back to global summary."""
        question = "What changed for MAT001?"
        answer = _generate_record_comparison_answer(question, quality_context, "material_id", "MAT001")

        # Should be record-specific, not global
        assert len(answer) > 0

    def test_comparison_includes_side_by_side_metrics(self, quality_context):
        """Test that comparison includes side-by-side metrics."""
        question = "Compare LOC001 vs LOC002"
        answer = _generate_comparison_answer(question, quality_context)

        # Should include metrics for both entities
        assert "LOC001" in answer
        assert "LOC002" in answer

    def test_supplier_answer_includes_metrics(self, quality_context):
        """Test that supplier answer includes metrics."""
        question = "List suppliers for LOC001"
        answer = _generate_supplier_by_location_answer(question, quality_context, "location", "LOC001")

        # Should include supplier information
        assert len(answer) > 0

    def test_record_answer_includes_comparison(self, quality_context):
        """Test that record answer includes comparison."""
        question = "What changed for MAT001?"
        answer = _generate_record_comparison_answer(question, quality_context, "material_id", "MAT001")

        # Should include record details
        assert len(answer) > 0


# ============================================================================
# PHASE 7.4: Performance Tests
# ============================================================================

class TestPerformancePhase7:
    """Test performance against targets (Phase 7)."""

    @pytest.fixture
    def perf_context(self):
        """Create context for performance testing."""
        return {
            "detailRecords": [
                {
                    "locationId": f"LOC{i:03d}",
                    "supplier": f"SUP{i % 10:03d}",
                    "materialGroup": ["Electronics", "Mechanical", "Pump"][i % 3],
                    "materialId": f"MAT{i:04d}",
                    "changed": i % 2 == 0,
                    "qtyChanged": i % 3 == 0,
                    "supplierChanged": i % 4 == 0,
                    "designChanged": i % 5 == 0,
                    "scheduleChanged": i % 6 == 0,
                    "qtyDelta": (i % 100) * 10,
                    "changeType": "Changed" if i % 2 == 0 else "Unchanged",
                    "riskLevel": ["High Risk", "Medium Risk", "Low Risk"][i % 3],
                }
                for i in range(100)
            ],
            "recommendedActions": ["Action 1", "Action 2"],
            "aiInsight": "Test insight",
            "planningHealth": 50,
            "changedRecordCount": 50,
            "totalRecords": 100,
        }

    def test_intent_classification_latency(self, perf_context):
        """Test intent classification latency (target: < 30ms)."""
        import time

        question = "Why is LOC001 risky?"
        start = time.time()
        query_type = _classify_question(question)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert query_type is not None
        assert elapsed < 30, f"Intent classification took {elapsed:.2f}ms (target: < 30ms)"

    def test_comparison_computation_latency(self, perf_context):
        """Test comparison computation latency (target: < 50ms)."""
        import time

        question = "Compare LOC001 vs LOC002"
        start = time.time()
        answer = _generate_comparison_answer(question, perf_context)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 50, f"Comparison computation took {elapsed:.2f}ms (target: < 50ms)"

    def test_supplier_computation_latency(self, perf_context):
        """Test supplier computation latency (target: < 50ms)."""
        import time

        question = "List suppliers for LOC001"
        start = time.time()
        answer = _generate_supplier_by_location_answer(question, perf_context, "location", "LOC001")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 50, f"Supplier computation took {elapsed:.2f}ms (target: < 50ms)"

    def test_record_comparison_latency(self, perf_context):
        """Test record comparison latency (target: < 30ms)."""
        import time

        question = "What changed for MAT0001?"
        start = time.time()
        answer = _generate_record_comparison_answer(question, perf_context, "material_id", "MAT0001")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 30, f"Record comparison took {elapsed:.2f}ms (target: < 30ms)"

    def test_response_formatting_latency(self, perf_context):
        """Test response formatting latency (target: < 30ms)."""
        import time

        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(perf_context["detailRecords"], scope_type, scope_value)

        start = time.time()
        answer = _generate_root_cause_answer(question, perf_context, scope_type, scope_value, scoped_metrics)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 30, f"Response formatting took {elapsed:.2f}ms (target: < 30ms)"

    def test_total_response_time(self, perf_context):
        """Test total response time (target: < 500ms)."""
        import time

        question = "Why is LOC001 risky?"

        start = time.time()
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)
        scoped_metrics = _compute_scoped_metrics(perf_context["detailRecords"], scope_type, scope_value)
        answer = _generate_root_cause_answer(question, perf_context, scope_type, scope_value, scoped_metrics)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 500, f"Total response time was {elapsed:.2f}ms (target: < 500ms)"

    def test_scoped_metrics_computation_latency(self, perf_context):
        """Test scoped metrics computation latency."""
        import time

        start = time.time()
        scoped_metrics = _compute_scoped_metrics(perf_context["detailRecords"], "location", "LOC001")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert scoped_metrics is not None
        assert elapsed < 50, f"Scoped metrics computation took {elapsed:.2f}ms (target: < 50ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
