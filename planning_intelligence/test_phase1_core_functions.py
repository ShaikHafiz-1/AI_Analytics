"""
Phase 1: Core Functions - Comprehensive Test Suite

Tests for:
- Scope extraction (location, supplier, material group, material ID, risk type)
- Question classification with scope
- Answer mode determination
- Scoped metrics computation
"""

import pytest
from phase1_core_functions import (
    ScopeExtractor,
    QuestionClassifier,
    AnswerModeDecider,
    ScopedMetricsComputer
)


class TestScopeExtractor:
    """Test scope extraction from questions."""
    
    def test_extract_location_code(self):
        """Test extraction of location codes (LOC001)."""
        scope_type, scope_value = ScopeExtractor.extract_scope("Why is LOC001 risky?")
        assert scope_type == "location"
        assert scope_value == "LOC001"
    
    def test_extract_location_named(self):
        """Test extraction of named locations."""
        scope_type, scope_value = ScopeExtractor.extract_scope("What about location Shanghai?")
        assert scope_type == "location"
        assert "SHANGHAI" in scope_value
    
    def test_extract_supplier_code(self):
        """Test extraction of supplier codes (SUP001)."""
        scope_type, scope_value = ScopeExtractor.extract_scope("Which supplier SUP001 has issues?")
        assert scope_type == "supplier"
        assert scope_value == "SUP001"
    
    def test_extract_supplier_named(self):
        """Test extraction of named suppliers."""
        scope_type, scope_value = ScopeExtractor.extract_scope("What about supplier Acme?")
        assert scope_type == "supplier"
        assert "ACME" in scope_value
    
    def test_extract_material_group(self):
        """Test extraction of material groups."""
        scope_type, scope_value = ScopeExtractor.extract_scope("Why is UPS changing?")
        assert scope_type == "material_group"
        assert scope_value == "UPS"
    
    def test_extract_material_id(self):
        """Test extraction of material IDs."""
        scope_type, scope_value = ScopeExtractor.extract_scope("What about MAT12345?")
        assert scope_type == "material_id"
        assert scope_value == "MAT12345"
    
    def test_extract_risk_type(self):
        """Test extraction of risk types."""
        scope_type, scope_value = ScopeExtractor.extract_scope("Show high risk items")
        assert scope_type == "risk_type"
    
    def test_no_scope(self):
        """Test when no scope is present."""
        scope_type, scope_value = ScopeExtractor.extract_scope("What is the overall status?")
        assert scope_type is None
        assert scope_value is None
    
    def test_extract_comparison_entities_locations(self):
        """Test extraction of comparison entities (locations)."""
        entities = ScopeExtractor.extract_comparison_entities("Compare LOC001 vs LOC002")
        assert len(entities) == 2
        assert "LOC001" in entities
        assert "LOC002" in entities
    
    def test_extract_comparison_entities_material_groups(self):
        """Test extraction of comparison entities (material groups)."""
        entities = ScopeExtractor.extract_comparison_entities("Compare UPS vs PUMP")
        assert len(entities) == 2
        assert "UPS" in entities
        assert "PUMP" in entities
    
    def test_extract_comparison_entities_suppliers(self):
        """Test extraction of comparison entities (suppliers)."""
        entities = ScopeExtractor.extract_comparison_entities("Compare SUP001 vs SUP002")
        assert len(entities) == 2
        assert "SUP001" in entities
        assert "SUP002" in entities
    
    def test_extract_comparison_entities_insufficient(self):
        """Test when insufficient entities for comparison."""
        entities = ScopeExtractor.extract_comparison_entities("What about LOC001?")
        assert len(entities) < 2


class TestQuestionClassifier:
    """Test question classification."""
    
    def test_classify_comparison(self):
        """Test classification of comparison questions."""
        query_type = QuestionClassifier.classify_question("Compare LOC001 vs LOC002")
        assert query_type == "comparison"
    
    def test_classify_comparison_versus(self):
        """Test classification with 'versus'."""
        query_type = QuestionClassifier.classify_question("What is the difference between UPS and PUMP?")
        assert query_type == "comparison"
    
    def test_classify_root_cause(self):
        """Test classification of root cause questions."""
        query_type = QuestionClassifier.classify_question("Why is LOC001 risky?")
        assert query_type == "root_cause"
    
    def test_classify_root_cause_reason(self):
        """Test classification with 'reason'."""
        query_type = QuestionClassifier.classify_question("What is the reason for the changes?")
        assert query_type == "root_cause"
    
    def test_classify_why_not(self):
        """Test classification of why-not questions."""
        query_type = QuestionClassifier.classify_question("Why is LOC001 not risky?")
        assert query_type == "why_not"
    
    def test_classify_why_not_stable(self):
        """Test classification of stability questions."""
        query_type = QuestionClassifier.classify_question("Why is LOC001 stable?")
        assert query_type == "why_not"
    
    def test_classify_traceability(self):
        """Test classification of traceability questions."""
        query_type = QuestionClassifier.classify_question("Show top contributing records")
        assert query_type == "traceability"
    
    def test_classify_traceability_impacted(self):
        """Test classification with 'impacted'."""
        query_type = QuestionClassifier.classify_question("Which records are impacted?")
        assert query_type == "traceability"
    
    def test_classify_summary(self):
        """Test classification of summary questions."""
        query_type = QuestionClassifier.classify_question("What is the overall status?")
        assert query_type == "summary"
    
    def test_classify_with_scope(self):
        """Test classification with scope extraction."""
        query_type, scope_type, scope_value = QuestionClassifier.classify_with_scope("Why is LOC001 risky?")
        assert query_type == "root_cause"
        assert scope_type == "location"
        assert scope_value == "LOC001"


class TestAnswerModeDecider:
    """Test answer mode determination."""
    
    def test_comparison_always_investigate(self):
        """Test that comparison always uses investigate mode."""
        mode = AnswerModeDecider.determine_answer_mode("comparison", None)
        assert mode == "investigate"
    
    def test_comparison_with_scope_investigate(self):
        """Test that comparison with scope uses investigate mode."""
        mode = AnswerModeDecider.determine_answer_mode("comparison", "location")
        assert mode == "investigate"
    
    def test_traceability_always_investigate(self):
        """Test that traceability always uses investigate mode."""
        mode = AnswerModeDecider.determine_answer_mode("traceability", None)
        assert mode == "investigate"
    
    def test_root_cause_scoped_investigate(self):
        """Test that scoped root cause uses investigate mode."""
        mode = AnswerModeDecider.determine_answer_mode("root_cause", "location")
        assert mode == "investigate"
    
    def test_root_cause_unscoped_summary(self):
        """Test that unscoped root cause uses summary mode."""
        mode = AnswerModeDecider.determine_answer_mode("root_cause", None)
        assert mode == "summary"
    
    def test_why_not_scoped_investigate(self):
        """Test that scoped why-not uses investigate mode."""
        mode = AnswerModeDecider.determine_answer_mode("why_not", "location")
        assert mode == "investigate"
    
    def test_why_not_unscoped_summary(self):
        """Test that unscoped why-not uses summary mode."""
        mode = AnswerModeDecider.determine_answer_mode("why_not", None)
        assert mode == "summary"
    
    def test_summary_always_summary(self):
        """Test that summary always uses summary mode."""
        mode = AnswerModeDecider.determine_answer_mode("summary", None)
        assert mode == "summary"
        
        mode = AnswerModeDecider.determine_answer_mode("summary", "location")
        assert mode == "summary"


class TestScopedMetricsComputer:
    """Test scoped metrics computation."""
    
    @pytest.fixture
    def sample_records(self):
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
    
    def test_compute_location_metrics(self, sample_records):
        """Test computing metrics for a specific location."""
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            sample_records, "location", "LOC001"
        )
        
        assert metrics["filteredRecordsCount"] == 2
        assert metrics["changedCount"] == 1
        assert metrics["changeRate"] == 50.0
        assert metrics["scopedDrivers"]["primary"] == "quantity"
    
    def test_compute_supplier_metrics(self, sample_records):
        """Test computing metrics for a specific supplier."""
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            sample_records, "supplier", "SUP001"
        )
        
        assert metrics["filteredRecordsCount"] == 2
        assert metrics["changedCount"] == 1
    
    def test_compute_material_group_metrics(self, sample_records):
        """Test computing metrics for a specific material group."""
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            sample_records, "material_group", "UPS"
        )
        
        assert metrics["filteredRecordsCount"] == 2
        assert metrics["changedCount"] == 1
    
    def test_compute_material_id_metrics(self, sample_records):
        """Test computing metrics for a specific material ID."""
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            sample_records, "material_id", "MAT001"
        )
        
        assert metrics["filteredRecordsCount"] == 1
        assert metrics["changedCount"] == 1
        assert metrics["changeRate"] == 100.0
    
    def test_compute_risk_type_metrics(self, sample_records):
        """Test computing metrics for high risk items."""
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            sample_records, "risk_type", "high"
        )
        
        assert metrics["filteredRecordsCount"] == 1
        assert metrics["changedCount"] == 1
    
    def test_empty_filtered_results(self, sample_records):
        """Test when no records match the scope."""
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            sample_records, "location", "LOC999"
        )
        
        assert metrics["filteredRecordsCount"] == 0
        assert metrics["changedCount"] == 0
        assert metrics["changeRate"] == 0.0
    
    def test_contribution_breakdown(self, sample_records):
        """Test contribution breakdown calculation."""
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            sample_records, "location", "LOC001"
        )
        
        breakdown = metrics["scopedContributionBreakdown"]
        assert breakdown["quantity"] == 100.0  # 1 out of 1 changed
        assert breakdown["supplier"] == 0.0
        assert breakdown["design"] == 0.0
        assert breakdown["schedule"] == 0.0
    
    def test_top_contributing_records(self, sample_records):
        """Test identification of top contributing records."""
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            sample_records, "location", "LOC001"
        )
        
        top_records = metrics["topContributingRecords"]
        assert len(top_records) <= 5
        assert top_records[0]["qtyDelta"] == 100  # Highest delta first
    
    def test_performance_large_dataset(self):
        """Test performance with large dataset (< 100ms)."""
        import time
        
        # Create 10,000 records
        records = [
            {
                "LOCID": f"LOC{(i % 100):03d}",  # LOC000, LOC001, etc.
                "LOCFR": f"SUP{i % 50}",
                "GSCEQUIPCAT": ["UPS", "PUMP", "VALVE"][i % 3],
                "PRDID": f"MAT{i}",
                "Risk_Flag": i % 10 == 0,
                "changed": i % 5 == 0,
                "qtyChanged": i % 7 == 0,
                "supplierChanged": i % 11 == 0,
                "designChanged": i % 13 == 0,
                "scheduleChanged": i % 17 == 0,
                "qtyDelta": (i % 1000) - 500,
            }
            for i in range(10000)
        ]
        
        start = time.time()
        metrics = ScopedMetricsComputer.compute_scoped_metrics(
            records, "location", "LOC001"
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert elapsed < 100, f"Performance test failed: {elapsed}ms > 100ms"
        assert metrics["filteredRecordsCount"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
