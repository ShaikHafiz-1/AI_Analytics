"""
Phase 3: Integration - Comprehensive Test Suite

Tests for:
- End-to-end question processing through Phase 1-2
- Integration with function_app.py
- Response building with all required fields
"""

import pytest
from phase3_integration import Phase3Integration


class TestPhase3Integration:
    """Test Phase 3 integration."""
    
    @pytest.fixture
    def sample_detail_records(self):
        """Create sample detail records for testing."""
        return [
            {
                "LOCID": "LOC001",
                "LOCFR": "SUP001",
                "GSCEQUIPCAT": "UPS",
                "PRDID": "MAT001",
                "Risk_Flag": False,
                "changed": True,
                "qtyChanged": True,
                "supplierChanged": False,
                "designChanged": False,
                "scheduleChanged": False,
                "qtyDelta": 100,
            },
            {
                "LOCID": "LOC001",
                "LOCFR": "SUP001",
                "GSCEQUIPCAT": "UPS",
                "PRDID": "MAT002",
                "Risk_Flag": False,
                "changed": False,
                "qtyChanged": False,
                "supplierChanged": False,
                "designChanged": False,
                "scheduleChanged": False,
                "qtyDelta": 0,
            },
            {
                "LOCID": "LOC002",
                "LOCFR": "SUP002",
                "GSCEQUIPCAT": "PUMP",
                "PRDID": "MAT003",
                "Risk_Flag": True,
                "changed": True,
                "qtyChanged": False,
                "supplierChanged": True,
                "designChanged": False,
                "scheduleChanged": False,
                "qtyDelta": -50,
            },
        ]
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context for testing."""
        return {
            "aiInsight": "Planning health is critical",
            "rootCause": "Supplier changes",
            "recommendedActions": ["Review supplier contracts"],
            "planningHealth": "Critical",
            "dataMode": "cached",
            "lastRefreshedAt": "2024-01-15T10:00:00Z",
            "changedRecordCount": 50,
            "totalRecords": 200,
            "trendDelta": 25.0,
            "drivers": {"quantity": 30, "supplier": 15, "design": 5},
        }
    
    def test_process_comparison_question(self, sample_detail_records, sample_context):
        """Test processing a comparison question."""
        response = Phase3Integration.process_question_with_phases(
            question="Compare LOC001 vs LOC002",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert response["question"] == "Compare LOC001 vs LOC002"
        assert response["queryType"] == "comparison"
        assert response["answerMode"] == "investigate"
        assert "LOC001" in response["answer"]
        assert "LOC002" in response["answer"]
        assert response["phase1Processed"] is True
        assert response["phase2Processed"] is True
    
    def test_process_root_cause_question(self, sample_detail_records, sample_context):
        """Test processing a root cause question."""
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert response["question"] == "Why is LOC001 risky?"
        assert response["queryType"] == "root_cause"
        assert response["answerMode"] == "investigate"
        assert response["scopeType"] == "location"
        assert response["scopeValue"] == "LOC001"
        assert "LOC001" in response["answer"]
        assert "investigateMode" in response
    
    def test_process_why_not_question(self, sample_detail_records, sample_context):
        """Test processing a why-not question."""
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 not risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert response["question"] == "Why is LOC001 not risky?"
        assert response["queryType"] == "why_not"
        assert response["answerMode"] == "investigate"
        assert response["scopeType"] == "location"
        assert response["scopeValue"] == "LOC001"
    
    def test_process_traceability_question(self, sample_detail_records, sample_context):
        """Test processing a traceability question."""
        response = Phase3Integration.process_question_with_phases(
            question="Show top contributing records",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert response["question"] == "Show top contributing records"
        assert response["queryType"] == "traceability"
        assert response["answerMode"] == "investigate"
        assert "Top" in response["answer"]
    
    def test_process_summary_question(self, sample_detail_records, sample_context):
        """Test processing a summary question."""
        response = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert response["question"] == "What is the overall status?"
        assert response["queryType"] == "summary"
        assert response["answerMode"] == "summary"
        assert "investigateMode" not in response
    
    def test_response_includes_all_required_fields(self, sample_detail_records, sample_context):
        """Test that response includes all required fields."""
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        # Required fields
        assert "question" in response
        assert "answer" in response
        assert "queryType" in response
        assert "answerMode" in response
        assert "supportingMetrics" in response
        assert "explainability" in response
        assert "suggestedActions" in response
        assert "followUpQuestions" in response
        
        # Phase 1-2 metadata
        assert "scopeType" in response
        assert "scopeValue" in response
        assert "phase1Processed" in response
        assert "phase2Processed" in response
    
    def test_investigate_mode_includes_scoped_metrics(self, sample_detail_records, sample_context):
        """Test that investigate mode includes scoped metrics."""
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert response["answerMode"] == "investigate"
        assert "investigateMode" in response
        
        investigate = response["investigateMode"]
        assert "filteredRecordsCount" in investigate
        assert "scopedContributionBreakdown" in investigate
        assert "scopedDrivers" in investigate
        assert "topContributingRecords" in investigate
        assert investigate["scopeType"] == "location"
        assert investigate["scopeValue"] == "LOC001"
    
    def test_summary_mode_excludes_investigate_fields(self, sample_detail_records, sample_context):
        """Test that summary mode excludes investigate fields."""
        response = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert response["answerMode"] == "summary"
        assert "investigateMode" not in response
    
    def test_backward_compatibility_extract_scope(self):
        """Test backward compatibility for scope extraction."""
        scope_type, scope_value = Phase3Integration.extract_scope_from_question("Why is LOC001 risky?")
        assert scope_type == "location"
        assert scope_value == "LOC001"
    
    def test_backward_compatibility_classify_question(self):
        """Test backward compatibility for question classification."""
        query_type = Phase3Integration.classify_question("Why is LOC001 risky?")
        assert query_type == "root_cause"
    
    def test_backward_compatibility_determine_answer_mode(self):
        """Test backward compatibility for answer mode determination."""
        mode = Phase3Integration.determine_answer_mode("root_cause", "location")
        assert mode == "investigate"
    
    def test_backward_compatibility_compute_scoped_metrics(self, sample_detail_records):
        """Test backward compatibility for scoped metrics computation."""
        metrics = Phase3Integration.compute_scoped_metrics(
            sample_detail_records, "location", "LOC001"
        )
        
        assert metrics["filteredRecordsCount"] == 2
        assert metrics["changedCount"] == 1


class TestPhase3EndToEnd:
    """End-to-end tests for Phase 3 integration."""
    
    @pytest.fixture
    def sample_detail_records(self):
        """Create sample detail records for testing."""
        records = []
        for i in range(100):
            records.append({
                "LOCID": f"LOC{(i % 5):03d}",
                "LOCFR": f"SUP{i % 3}",
                "GSCEQUIPCAT": ["UPS", "PUMP", "VALVE"][i % 3],
                "PRDID": f"MAT{i}",
                "Risk_Flag": i % 10 < 3,
                "changed": i % 5 == 0,
                "qtyChanged": i % 7 == 0,
                "supplierChanged": i % 11 == 0,
                "designChanged": i % 13 == 0,
                "scheduleChanged": i % 17 == 0,
                "qtyDelta": (i % 100) - 50,
            })
        return records
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context for testing."""
        return {
            "aiInsight": "Planning health is critical",
            "rootCause": "Supplier changes",
            "recommendedActions": ["Review supplier contracts", "Adjust forecasts"],
            "planningHealth": "Critical",
            "dataMode": "cached",
            "lastRefreshedAt": "2024-01-15T10:00:00Z",
            "changedRecordCount": 50,
            "totalRecords": 200,
            "trendDelta": 25.0,
            "drivers": {"quantity": 30, "supplier": 15, "design": 5},
        }
    
    def test_e2e_comparison_flow(self, sample_detail_records, sample_context):
        """Test end-to-end comparison flow."""
        response = Phase3Integration.process_question_with_phases(
            question="Compare LOC001 vs LOC002",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        # Verify complete response
        assert response["queryType"] == "comparison"
        assert response["answerMode"] == "investigate"
        assert len(response["answer"]) > 0
        assert "LOC001" in response["answer"]
        assert "LOC002" in response["answer"]
        assert response["investigateMode"]["scopeType"] in ["location", None]
    
    def test_e2e_root_cause_flow(self, sample_detail_records, sample_context):
        """Test end-to-end root cause flow."""
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        # Verify complete response
        assert response["queryType"] == "root_cause"
        assert response["answerMode"] == "investigate"
        assert len(response["answer"]) > 0
        assert "LOC001" in response["answer"]
        assert response["investigateMode"]["filteredRecordsCount"] > 0
    
    def test_e2e_summary_flow(self, sample_detail_records, sample_context):
        """Test end-to-end summary flow."""
        response = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        # Verify complete response
        assert response["queryType"] == "summary"
        assert response["answerMode"] == "summary"
        assert len(response["answer"]) > 0
        assert "investigateMode" not in response
    
    def test_e2e_response_determinism(self, sample_detail_records, sample_context):
        """Test that same question produces same answer (determinism)."""
        response1 = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        response2 = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        # Same question should produce same answer
        assert response1["answer"] == response2["answer"]
        assert response1["queryType"] == response2["queryType"]
        assert response1["answerMode"] == response2["answerMode"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
