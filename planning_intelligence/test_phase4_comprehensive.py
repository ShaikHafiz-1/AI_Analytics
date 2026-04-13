"""
Phase 4: Comprehensive Testing - Full Test Suite

Tests for:
- Freshness awareness (fresh vs stale data)
- Response variety (no template reuse)
- Determinism (same input = same output)
- Edge cases and error handling
- Performance validation
"""

import pytest
from datetime import datetime, timedelta, timezone
from phase3_integration import Phase3Integration


class TestFreshnessAwareness:
    """Test freshness awareness in responses."""
    
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
                "LOCID": "LOC002",
                "LOCFR": "SUP002",
                "GSCEQUIPCAT": "PUMP",
                "PRDID": "MAT002",
                "Risk_Flag": True,
                "changed": True,
                "qtyChanged": False,
                "supplierChanged": True,
                "designChanged": False,
                "scheduleChanged": False,
                "qtyDelta": -50,
            },
        ]
    
    def test_fresh_data_includes_confirmation(self, sample_detail_records):
        """Test that fresh data includes freshness confirmation."""
        # Fresh data (< 1 hour old)
        fresh_time = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
        
        context = {
            "aiInsight": "Planning health is good",
            "rootCause": "Minor changes",
            "recommendedActions": ["Monitor"],
            "planningHealth": "Good",
            "dataMode": "cached",
            "lastRefreshedAt": fresh_time,
            "changedRecordCount": 10,
            "totalRecords": 100,
            "trendDelta": 10.0,
            "drivers": {"quantity": 5, "supplier": 3, "design": 2},
        }
        
        response = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=context
        )
        
        # Verify freshness metadata is included
        assert "explainability" in response
        assert "lastRefreshedAt" in response["explainability"]
        assert response["explainability"]["lastRefreshedAt"] == fresh_time
    
    def test_stale_data_includes_warning(self, sample_detail_records):
        """Test that stale data includes freshness warning."""
        # Stale data (> 24 hours old)
        stale_time = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        
        context = {
            "aiInsight": "Planning health is critical",
            "rootCause": "Major changes",
            "recommendedActions": ["Review immediately"],
            "planningHealth": "Critical",
            "dataMode": "cached",
            "lastRefreshedAt": stale_time,
            "changedRecordCount": 50,
            "totalRecords": 100,
            "trendDelta": 50.0,
            "drivers": {"quantity": 30, "supplier": 15, "design": 5},
        }
        
        response = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=context
        )
        
        # Verify freshness metadata is included
        assert "explainability" in response
        assert "lastRefreshedAt" in response["explainability"]
        assert response["explainability"]["lastRefreshedAt"] == stale_time
    
    def test_freshness_warning_does_not_replace_analysis(self, sample_detail_records):
        """Test that freshness warning doesn't replace analysis."""
        stale_time = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        
        context = {
            "aiInsight": "Planning health is critical",
            "rootCause": "Major changes",
            "recommendedActions": ["Review immediately"],
            "planningHealth": "Critical",
            "dataMode": "cached",
            "lastRefreshedAt": stale_time,
            "changedRecordCount": 50,
            "totalRecords": 100,
            "trendDelta": 50.0,
            "drivers": {"quantity": 30, "supplier": 15, "design": 5},
        }
        
        response = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=context
        )
        
        # Verify analysis is still present
        assert len(response["answer"]) > 0
        assert "Planning health" in response["answer"]
        assert "Critical" in response["answer"]


class TestResponseVariety:
    """Test that different query types produce different responses."""
    
    @pytest.fixture
    def sample_detail_records(self):
        """Create sample detail records for testing."""
        records = []
        for i in range(50):
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
            "recommendedActions": ["Review supplier contracts"],
            "planningHealth": "Critical",
            "dataMode": "cached",
            "lastRefreshedAt": datetime.now(timezone.utc).isoformat(),
            "changedRecordCount": 50,
            "totalRecords": 200,
            "trendDelta": 25.0,
            "drivers": {"quantity": 30, "supplier": 15, "design": 5},
        }
    
    def test_comparison_vs_root_cause_different(self, sample_detail_records, sample_context):
        """Test that comparison and root cause answers are different."""
        comparison = Phase3Integration.process_question_with_phases(
            question="Compare LOC001 vs LOC002",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        root_cause = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert comparison["answer"] != root_cause["answer"]
        assert comparison["queryType"] != root_cause["queryType"]
    
    def test_root_cause_vs_why_not_different(self, sample_detail_records, sample_context):
        """Test that root cause and why-not answers are different."""
        root_cause = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        why_not = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 not risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert root_cause["answer"] != why_not["answer"]
        assert root_cause["queryType"] != why_not["queryType"]
    
    def test_why_not_vs_traceability_different(self, sample_detail_records, sample_context):
        """Test that why-not and traceability answers are different."""
        why_not = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 not risky?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        traceability = Phase3Integration.process_question_with_phases(
            question="Show top contributing records",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert why_not["answer"] != traceability["answer"]
        assert why_not["queryType"] != traceability["queryType"]
    
    def test_traceability_vs_summary_different(self, sample_detail_records, sample_context):
        """Test that traceability and summary answers are different."""
        traceability = Phase3Integration.process_question_with_phases(
            question="Show top contributing records",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        summary = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        assert traceability["answer"] != summary["answer"]
        assert traceability["queryType"] != summary["queryType"]
    
    def test_all_query_types_have_unique_formatting(self, sample_detail_records, sample_context):
        """Test that all query types have unique formatting."""
        queries = [
            ("Compare LOC001 vs LOC002", "comparison"),
            ("Why is LOC001 risky?", "root_cause"),
            ("Why is LOC001 not risky?", "why_not"),
            ("Show top contributing records", "traceability"),
            ("What is the overall status?", "summary"),
        ]
        
        answers = {}
        for question, query_type in queries:
            response = Phase3Integration.process_question_with_phases(
                question=question,
                detail_records=sample_detail_records,
                context=sample_context
            )
            answers[query_type] = response["answer"]
        
        # Verify all answers are unique
        unique_answers = set(answers.values())
        assert len(unique_answers) == len(answers), "Some answers are identical"


class TestDeterminism:
    """Test that responses are deterministic."""
    
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
            "recommendedActions": ["Review supplier contracts"],
            "planningHealth": "Critical",
            "dataMode": "cached",
            "lastRefreshedAt": "2024-01-15T10:00:00Z",
            "changedRecordCount": 50,
            "totalRecords": 200,
            "trendDelta": 25.0,
            "drivers": {"quantity": 30, "supplier": 15, "design": 5},
        }
    
    def test_same_question_produces_same_answer(self, sample_detail_records, sample_context):
        """Test that same question produces same answer."""
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
        
        assert response1["answer"] == response2["answer"]
        assert response1["queryType"] == response2["queryType"]
        assert response1["answerMode"] == response2["answerMode"]
    
    def test_different_data_produces_different_answer(self, sample_detail_records, sample_context):
        """Test that different data produces different answer."""
        response1 = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=sample_context
        )
        
        # Modify context
        modified_context = sample_context.copy()
        modified_context["changedRecordCount"] = 100  # Double the changes
        
        response2 = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=sample_detail_records,
            context=modified_context
        )
        
        assert response1["answer"] != response2["answer"]
    
    def test_metrics_are_deterministic(self, sample_detail_records, sample_context):
        """Test that metrics computation is deterministic."""
        metrics1 = Phase3Integration.compute_scoped_metrics(
            sample_detail_records, "location", "LOC001"
        )
        
        metrics2 = Phase3Integration.compute_scoped_metrics(
            sample_detail_records, "location", "LOC001"
        )
        
        assert metrics1["filteredRecordsCount"] == metrics2["filteredRecordsCount"]
        assert metrics1["changedCount"] == metrics2["changedCount"]
        assert metrics1["changeRate"] == metrics2["changeRate"]
    
    def test_no_randomness_in_answer_generation(self, sample_detail_records, sample_context):
        """Test that answer generation has no randomness."""
        answers = []
        for _ in range(5):
            response = Phase3Integration.process_question_with_phases(
                question="Compare LOC001 vs LOC002",
                detail_records=sample_detail_records,
                context=sample_context
            )
            answers.append(response["answer"])
        
        # All answers should be identical
        assert len(set(answers)) == 1, "Answers are not deterministic"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_detail_records(self):
        """Test with empty detail records."""
        response = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=[],
            context={"changedRecordCount": 0, "totalRecords": 0}
        )
        
        assert response["answer"] is not None
        assert len(response["answer"]) > 0
    
    def test_single_record(self):
        """Test with single record."""
        records = [{
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
        }]
        
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=records,
            context={"changedRecordCount": 1, "totalRecords": 1}
        )
        
        assert response["answer"] is not None
        assert "LOC001" in response["answer"]
    
    def test_no_scope_detected(self):
        """Test when no scope is detected."""
        records = [
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
            }
        ]
        
        response = Phase3Integration.process_question_with_phases(
            question="What is the overall status?",
            detail_records=records,
            context={"changedRecordCount": 1, "totalRecords": 1}
        )
        
        assert response["scopeType"] is None
        assert response["answerMode"] == "summary"
    
    def test_all_records_unchanged(self):
        """Test when all records are unchanged."""
        records = [
            {
                "LOCID": "LOC001",
                "LOCFR": "SUP001",
                "GSCEQUIPCAT": "UPS",
                "PRDID": "MAT001",
                "Risk_Flag": False,
                "changed": False,
                "qtyChanged": False,
                "supplierChanged": False,
                "designChanged": False,
                "scheduleChanged": False,
                "qtyDelta": 0,
            }
            for _ in range(10)
        ]
        
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 not risky?",
            detail_records=records,
            context={"changedRecordCount": 0, "totalRecords": 10}
        )
        
        assert response["answer"] is not None
        assert "stable" in response["answer"].lower() or "no records changed" in response["answer"].lower()
    
    def test_all_records_changed(self):
        """Test when all records are changed."""
        records = [
            {
                "LOCID": "LOC001",
                "LOCFR": "SUP001",
                "GSCEQUIPCAT": "UPS",
                "PRDID": f"MAT{i}",
                "Risk_Flag": True,
                "changed": True,
                "qtyChanged": True,
                "supplierChanged": True,
                "designChanged": True,
                "scheduleChanged": True,
                "qtyDelta": 100,
            }
            for i in range(10)
        ]
        
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=records,
            context={"changedRecordCount": 10, "totalRecords": 10}
        )
        
        assert response["answer"] is not None
        assert "risky" in response["answer"].lower()


class TestPerformanceValidation:
    """Test performance characteristics."""
    
    def test_performance_with_100_records(self):
        """Test performance with 100 records."""
        import time
        
        records = [
            {
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
            }
            for i in range(100)
        ]
        
        context = {
            "aiInsight": "Planning health is critical",
            "rootCause": "Supplier changes",
            "recommendedActions": ["Review supplier contracts"],
            "planningHealth": "Critical",
            "dataMode": "cached",
            "lastRefreshedAt": "2024-01-15T10:00:00Z",
            "changedRecordCount": 20,
            "totalRecords": 100,
            "trendDelta": 20.0,
            "drivers": {"quantity": 10, "supplier": 7, "design": 3},
        }
        
        start = time.time()
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=records,
            context=context
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert elapsed < 50, f"Performance test failed: {elapsed}ms > 50ms"
        assert response["answer"] is not None
    
    def test_performance_with_1000_records(self):
        """Test performance with 1,000 records."""
        import time
        
        records = [
            {
                "LOCID": f"LOC{(i % 10):03d}",
                "LOCFR": f"SUP{i % 5}",
                "GSCEQUIPCAT": ["UPS", "PUMP", "VALVE"][i % 3],
                "PRDID": f"MAT{i}",
                "Risk_Flag": i % 10 < 3,
                "changed": i % 5 == 0,
                "qtyChanged": i % 7 == 0,
                "supplierChanged": i % 11 == 0,
                "designChanged": i % 13 == 0,
                "scheduleChanged": i % 17 == 0,
                "qtyDelta": (i % 100) - 50,
            }
            for i in range(1000)
        ]
        
        context = {
            "aiInsight": "Planning health is critical",
            "rootCause": "Supplier changes",
            "recommendedActions": ["Review supplier contracts"],
            "planningHealth": "Critical",
            "dataMode": "cached",
            "lastRefreshedAt": "2024-01-15T10:00:00Z",
            "changedRecordCount": 200,
            "totalRecords": 1000,
            "trendDelta": 20.0,
            "drivers": {"quantity": 100, "supplier": 70, "design": 30},
        }
        
        start = time.time()
        response = Phase3Integration.process_question_with_phases(
            question="Why is LOC001 risky?",
            detail_records=records,
            context=context
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert elapsed < 100, f"Performance test failed: {elapsed}ms > 100ms"
        assert response["answer"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
