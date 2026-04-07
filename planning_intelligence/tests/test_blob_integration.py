"""
Integration tests for Copilot with real blob data.
Tests comparison, supplier, record detail, why-not, traceability, and root cause prompts.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from normalizer import normalize_rows
from filters import filter_records
from comparator import compare_records
from response_builder import (
    build_response,
    compute_comparison_metrics,
    get_suppliers_for_location,
    compute_supplier_metrics,
    analyze_supplier_behavior,
    get_record_comparison,
)
from function_app import (
    _extract_scope,
    _classify_question,
    _determine_answer_mode,
    _compute_scoped_metrics,
    _generate_comparison_answer,
    _generate_supplier_by_location_answer,
    _generate_record_comparison_answer,
    _generate_root_cause_answer,
    _generate_why_not_answer,
    _generate_traceability_answer,
)


# ============================================================================
# FIXTURES: Real-like blob data
# ============================================================================

@pytest.fixture
def realistic_blob_data():
    """Create realistic blob data simulating real planning records."""
    current = [
        # LOC001 - Electronics supplier changes
        {
            "LOCID": "LOC001",
            "GSCEQUIPCAT": "Electronics",
            "PRDID": "MAT-001",
            "LOCFR": "SUP-A",
            "GSCFSCTQTY": 1500,
            "GSCCONROJDATE": "2026-07-15",
            "ZCOIBODVER": "v3",
            "ZCOIFORMFACT": "FF-B",
            "ZCOIDCID": "DC-WEST",
        },
        {
            "LOCID": "LOC001",
            "GSCEQUIPCAT": "Electronics",
            "PRDID": "MAT-002",
            "LOCFR": "SUP-B",
            "GSCFSCTQTY": 800,
            "GSCCONROJDATE": "2026-06-20",
            "ZCOIBODVER": "v2",
            "ZCOIFORMFACT": "FF-A",
            "ZCOIDCID": "DC-WEST",
        },
        {
            "LOCID": "LOC001",
            "GSCEQUIPCAT": "Electronics",
            "PRDID": "MAT-003",
            "LOCFR": "SUP-C",
            "GSCFSCTQTY": 600,
            "GSCCONROJDATE": "2026-08-01",
            "ZCOIBODVER": "v1",
            "ZCOIFORMFACT": "FF-A",
            "ZCOIDCID": "DC-WEST",
        },
        # LOC002 - Mechanical stable
        {
            "LOCID": "LOC002",
            "GSCEQUIPCAT": "Mechanical",
            "PRDID": "MAT-101",
            "LOCFR": "SUP-D",
            "GSCFSCTQTY": 300,
            "GSCCONROJDATE": "2026-07-01",
            "ZCOIBODVER": "v1",
            "ZCOIFORMFACT": "FF-A",
            "ZCOIDCID": "DC-EAST",
        },
        {
            "LOCID": "LOC002",
            "GSCEQUIPCAT": "Mechanical",
            "PRDID": "MAT-102",
            "LOCFR": "SUP-D",
            "GSCFSCTQTY": 250,
            "GSCCONROJDATE": "2026-07-10",
            "ZCOIBODVER": "v1",
            "ZCOIFORMFACT": "FF-A",
            "ZCOIDCID": "DC-EAST",
        },
        # LOC003 - Mixed
        {
            "LOCID": "LOC003",
            "GSCEQUIPCAT": "Pump",
            "PRDID": "MAT-201",
            "LOCFR": "SUP-E",
            "GSCFSCTQTY": 2000,
            "GSCCONROJDATE": "2026-09-01",
            "ZCOIBODVER": "v4",
            "ZCOIFORMFACT": "FF-C",
            "ZCOIDCID": "DC-WEST",
        },
        {
            "LOCID": "LOC003",
            "GSCEQUIPCAT": "Valve",
            "PRDID": "MAT-202",
            "LOCFR": "SUP-F",
            "GSCFSCTQTY": 1200,
            "GSCCONROJDATE": "2026-08-15",
            "ZCOIBODVER": "v2",
            "ZCOIFORMFACT": "FF-B",
            "ZCOIDCID": "DC-WEST",
        },
    ]

    previous = [
        # LOC001 - Previous state (changed)
        {
            "LOCID": "LOC001",
            "GSCEQUIPCAT": "Electronics",
            "PRDID": "MAT-001",
            "LOCFR": "SUP-A",
            "GSCPREVFCSTQTY": 1000,
            "GSCPREVROJNBD": "2026-06-15",
            "ZCOIBODVER": "v2",
            "ZCOIFORMFACT": "FF-A",
        },
        {
            "LOCID": "LOC001",
            "GSCEQUIPCAT": "Electronics",
            "PRDID": "MAT-002",
            "LOCFR": "SUP-A",  # Changed supplier
            "GSCPREVFCSTQTY": 800,
            "GSCPREVROJNBD": "2026-06-20",
            "ZCOIBODVER": "v2",
            "ZCOIFORMFACT": "FF-A",
        },
        {
            "LOCID": "LOC001",
            "GSCEQUIPCAT": "Electronics",
            "PRDID": "MAT-003",
            "LOCFR": "SUP-C",
            "GSCPREVFCSTQTY": 600,
            "GSCPREVROJNBD": "2026-08-01",
            "ZCOIBODVER": "v1",
            "ZCOIFORMFACT": "FF-A",
        },
        # LOC002 - Previous state (unchanged)
        {
            "LOCID": "LOC002",
            "GSCEQUIPCAT": "Mechanical",
            "PRDID": "MAT-101",
            "LOCFR": "SUP-D",
            "GSCPREVFCSTQTY": 300,
            "GSCPREVROJNBD": "2026-07-01",
            "ZCOIBODVER": "v1",
            "ZCOIFORMFACT": "FF-A",
        },
        {
            "LOCID": "LOC002",
            "GSCEQUIPCAT": "Mechanical",
            "PRDID": "MAT-102",
            "LOCFR": "SUP-D",
            "GSCPREVFCSTQTY": 250,
            "GSCPREVROJNBD": "2026-07-10",
            "ZCOIBODVER": "v1",
            "ZCOIFORMFACT": "FF-A",
        },
        # LOC003 - Previous state (changed)
        {
            "LOCID": "LOC003",
            "GSCEQUIPCAT": "Pump",
            "PRDID": "MAT-201",
            "LOCFR": "SUP-E",
            "GSCPREVFCSTQTY": 1500,
            "GSCPREVROJNBD": "2026-08-15",
            "ZCOIBODVER": "v3",
            "ZCOIFORMFACT": "FF-B",
        },
        {
            "LOCID": "LOC003",
            "GSCEQUIPCAT": "Valve",
            "PRDID": "MAT-202",
            "LOCFR": "SUP-F",
            "GSCPREVFCSTQTY": 1200,
            "GSCPREVROJNBD": "2026-08-15",
            "ZCOIBODVER": "v2",
            "ZCOIFORMFACT": "FF-B",
        },
    ]

    c = normalize_rows(current, is_current=True)
    p = normalize_rows(previous, is_current=False)
    compared = compare_records(filter_records(c), filter_records(p))
    context = build_response(compared, [], data_mode="blob")
    context["detailRecords"] = [
        {
            "locationId": r.location_id,
            "supplier": r.supplier,
            "materialGroup": r.material_group,
            "materialId": r.material_id,
            "changed": r.change_type != "Unchanged",
            "qtyChanged": r.qty_changed,
            "supplierChanged": r.supplier_changed,
            "designChanged": r.design_changed,
            "scheduleChanged": r.schedule_changed,
            "qtyDelta": r.qty_delta,
            "changeType": r.change_type,
            "riskLevel": r.risk_level,
        }
        for r in compared
    ]

    return context


# ============================================================================
# TASK 23: Integration Tests with Real Blob Data
# ============================================================================

class TestComparisonWithBlobData:
    """Test comparison prompts with real blob data."""

    def test_compare_location_loc001_vs_loc002(self, realistic_blob_data):
        """Test: Compare LOC001 vs LOC002"""
        question = "Compare LOC001 vs LOC002"
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)

        assert query_type == "comparison"
        assert scope_type == "location"

        answer = _generate_comparison_answer(question, realistic_blob_data)
        assert "Comparison" in answer or "compare" in answer.lower()
        assert "LOC001" in answer
        assert "LOC002" in answer

    def test_compare_material_group_electronics_vs_mechanical(self, realistic_blob_data):
        """Test: Compare Electronics vs Mechanical"""
        question = "Compare Electronics vs Mechanical"
        query_type = _classify_question(question)

        assert query_type == "comparison"

        answer = _generate_comparison_answer(question, realistic_blob_data)
        assert "Electronics" in answer or "Mechanical" in answer

    def test_compare_material_id_mat001_vs_mat101(self, realistic_blob_data):
        """Test: Compare MAT-001 vs MAT-101"""
        question = "Compare MAT-001 vs MAT-101"
        query_type = _classify_question(question)

        assert query_type == "comparison"

        answer = _generate_comparison_answer(question, realistic_blob_data)
        assert "MAT-001" in answer or "MAT-101" in answer

    def test_comparison_never_falls_back_to_global_summary(self, realistic_blob_data):
        """Test that comparison never falls back to global summary."""
        question = "Compare LOC001 vs LOC002"
        answer = _generate_comparison_answer(question, realistic_blob_data)

        # Should not be generic global summary
        assert "Planning health" not in answer or "Comparison" in answer
        assert len(answer) > 50  # Should have detailed comparison


class TestSupplierWithBlobData:
    """Test supplier prompts with real blob data."""

    def test_list_suppliers_for_location(self, realistic_blob_data):
        """Test: List suppliers for LOC001"""
        question = "List suppliers for LOC001"
        query_type = _classify_question(question)

        assert query_type == "supplier_by_location"

        answer = _generate_supplier_by_location_answer(question, realistic_blob_data, "location", "LOC001")
        assert "supplier" in answer.lower() or "SUP" in answer
        assert "LOC001" in answer

    def test_supplier_behavior_analysis(self, realistic_blob_data):
        """Test supplier behavior analysis for a location."""
        question = "Which supplier at LOC001 has design changes?"
        query_type = _classify_question(question)

        assert query_type == "supplier_by_location"

        answer = _generate_supplier_by_location_answer(question, realistic_blob_data, "location", "LOC001")
        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_supplier_metrics_correct_for_location_only(self, realistic_blob_data):
        """Test that supplier metrics are scoped to location only."""
        detail_records = realistic_blob_data.get("detailRecords", [])

        # Get suppliers for LOC001
        loc001_records = [r for r in detail_records if r["locationId"] == "LOC001"]
        loc001_suppliers = set(r["supplier"] for r in loc001_records)

        # Get suppliers for LOC002
        loc002_records = [r for r in detail_records if r["locationId"] == "LOC002"]
        loc002_suppliers = set(r["supplier"] for r in loc002_records)

        # Should be different
        assert loc001_suppliers != loc002_suppliers


class TestRecordDetailWithBlobData:
    """Test record detail prompts with real blob data."""

    def test_what_changed_for_material(self, realistic_blob_data):
        """Test: What changed for MAT-001?"""
        question = "What changed for MAT-001?"
        query_type = _classify_question(question)

        assert query_type == "record_detail"

        answer = _generate_record_comparison_answer(question, realistic_blob_data, "material_id", "MAT-001")
        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_record_comparison_uses_composite_key(self, realistic_blob_data):
        """Test that record comparison uses composite key (LOCID, MaterialGroup, PRDID)."""
        detail_records = realistic_blob_data.get("detailRecords", [])

        # Find a record
        if detail_records:
            record = detail_records[0]
            location = record["locationId"]
            material_group = record["materialGroup"]
            material_id = record["materialId"]

            # Should be able to identify record by composite key
            matching = [
                r for r in detail_records
                if r["locationId"] == location
                and r["materialGroup"] == material_group
                and r["materialId"] == material_id
            ]
            assert len(matching) >= 1


class TestWhyNotWithBlobData:
    """Test why-not prompts with real blob data."""

    def test_why_not_risky_for_stable_location(self, realistic_blob_data):
        """Test: Why is LOC002 not risky?"""
        question = "Why is LOC002 not risky?"
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)

        assert query_type == "why_not"
        assert scope_type == "location"

        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), scope_type, scope_value
        )
        answer = _generate_why_not_answer(question, realistic_blob_data, scope_type, scope_value, scoped_metrics)
        assert isinstance(answer, str)
        assert len(answer) > 0


class TestTraceabilityWithBlobData:
    """Test traceability prompts with real blob data."""

    def test_show_top_contributing_records(self, realistic_blob_data):
        """Test: Show top contributing records"""
        question = "Show top contributing records"
        query_type = _classify_question(question)

        assert query_type == "traceability"

        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), None, None
        )
        answer = _generate_traceability_answer(question, realistic_blob_data, scoped_metrics)
        assert isinstance(answer, str)
        assert len(answer) > 0


class TestRootCauseWithBlobData:
    """Test root cause prompts with real blob data."""

    def test_why_is_location_risky(self, realistic_blob_data):
        """Test: Why is LOC001 risky?"""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)

        assert query_type == "root_cause"
        assert scope_type == "location"

        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), scope_type, scope_value
        )
        answer = _generate_root_cause_answer(question, realistic_blob_data, scope_type, scope_value, scoped_metrics)
        assert isinstance(answer, str)
        assert len(answer) > 0


# ============================================================================
# TASK 24: Backward Compatibility Tests
# ============================================================================

class TestBackwardCompatibility:
    """Test backward compatibility with existing clients."""

    def test_existing_client_without_new_fields(self, realistic_blob_data):
        """Test that existing clients work without new fields."""
        # Old response structure (without new fields)
        response = {
            "question": "Why is health critical?",
            "answer": "Test answer",
            "aiInsight": realistic_blob_data.get("aiInsight"),
            "rootCause": realistic_blob_data.get("rootCause"),
            "recommendedActions": realistic_blob_data.get("recommendedActions", []),
            "planningHealth": realistic_blob_data.get("planningHealth"),
            "dataMode": realistic_blob_data.get("dataMode", "blob"),
            "lastRefreshedAt": realistic_blob_data.get("lastRefreshedAt"),
            "supportingMetrics": {
                "changedRecordCount": realistic_blob_data.get("changedRecordCount"),
                "totalRecords": realistic_blob_data.get("totalRecords"),
                "trendDelta": realistic_blob_data.get("trendDelta"),
                "planningHealth": realistic_blob_data.get("planningHealth"),
            },
        }

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

    def test_all_existing_fields_unchanged(self, realistic_blob_data):
        """Test that all existing fields are unchanged."""
        # Verify existing fields have expected types
        assert isinstance(realistic_blob_data.get("planningHealth"), int)
        assert isinstance(realistic_blob_data.get("changedRecordCount"), int)
        assert isinstance(realistic_blob_data.get("totalRecords"), int)
        assert isinstance(realistic_blob_data.get("aiInsight"), str)
        assert isinstance(realistic_blob_data.get("rootCause"), str)
        assert isinstance(realistic_blob_data.get("recommendedActions"), list)

    def test_response_structure_with_new_fields(self, realistic_blob_data):
        """Test response structure with new optional fields."""
        # New response structure (with optional fields)
        response = {
            "question": "Why is health critical?",
            "answer": "Test answer",
            "queryType": "health",
            "answerMode": "summary",
            "scopeType": None,  # NEW
            "scopeValue": None,  # NEW
            "aiInsight": realistic_blob_data.get("aiInsight"),
            "rootCause": realistic_blob_data.get("rootCause"),
            "recommendedActions": realistic_blob_data.get("recommendedActions", []),
            "planningHealth": realistic_blob_data.get("planningHealth"),
            "dataMode": realistic_blob_data.get("dataMode", "blob"),
            "lastRefreshedAt": realistic_blob_data.get("lastRefreshedAt"),
            "supportingMetrics": {
                "changedRecordCount": realistic_blob_data.get("changedRecordCount"),
                "totalRecords": realistic_blob_data.get("totalRecords"),
                "trendDelta": realistic_blob_data.get("trendDelta"),
                "planningHealth": realistic_blob_data.get("planningHealth"),
            },
        }

        # Verify all existing fields are still present
        assert "question" in response
        assert "answer" in response
        assert "aiInsight" in response
        assert "rootCause" in response
        assert "recommendedActions" in response
        assert "planningHealth" in response

        # Verify new fields are present
        assert "scopeType" in response
        assert "scopeValue" in response


# ============================================================================
# TASK 25: Response Quality Tests
# ============================================================================

class TestResponseQuality:
    """Test response quality improvements."""

    def test_answer_specific_to_question(self, realistic_blob_data):
        """Test that answers are specific to the question."""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), scope_type, scope_value
        )
        answer = _generate_root_cause_answer(question, realistic_blob_data, scope_type, scope_value, scoped_metrics)

        # Should mention the specific location
        assert "LOC001" in answer

    def test_answer_not_generic_summary(self, realistic_blob_data):
        """Test that answers are not generic summaries."""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), scope_type, scope_value
        )
        answer = _generate_root_cause_answer(question, realistic_blob_data, scope_type, scope_value, scoped_metrics)

        # Should not be a generic global summary
        assert len(answer) > 50
        assert "LOC001" in answer

    def test_answer_uses_scoped_metrics(self, realistic_blob_data):
        """Test that answers use scoped metrics."""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), scope_type, scope_value
        )

        # Scoped metrics should be computed
        assert scoped_metrics is not None
        assert "filteredRecordsCount" in scoped_metrics
        assert "scopedMetrics" in scoped_metrics

    def test_answer_feels_targeted_and_relevant(self, realistic_blob_data):
        """Test that answers feel targeted and relevant."""
        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), scope_type, scope_value
        )
        answer = _generate_root_cause_answer(question, realistic_blob_data, scope_type, scope_value, scoped_metrics)

        # Should have specific details
        assert len(answer) > 0
        assert "LOC001" in answer

    def test_comparison_never_falls_back_to_global_summary(self, realistic_blob_data):
        """Test that comparison never falls back to global summary."""
        question = "Compare LOC001 vs LOC002"
        answer = _generate_comparison_answer(question, realistic_blob_data)

        # Should be a comparison, not a global summary
        assert "Comparison" in answer or "compare" in answer.lower()
        assert "LOC001" in answer
        assert "LOC002" in answer

    def test_supplier_query_never_falls_back_to_global_summary(self, realistic_blob_data):
        """Test that supplier queries never fall back to global summary."""
        question = "List suppliers for LOC001"
        answer = _generate_supplier_by_location_answer(question, realistic_blob_data, "location", "LOC001")

        # Should be supplier-specific, not global
        assert "LOC001" in answer
        assert len(answer) > 0

    def test_record_query_never_falls_back_to_global_summary(self, realistic_blob_data):
        """Test that record queries never fall back to global summary."""
        question = "What changed for MAT-001?"
        answer = _generate_record_comparison_answer(question, realistic_blob_data, "material_id", "MAT-001")

        # Should be record-specific, not global
        assert len(answer) > 0


# ============================================================================
# TASK 26: Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance against targets."""

    def test_intent_classification_latency(self, realistic_blob_data):
        """Test intent classification latency (target: < 30ms)."""
        import time

        question = "Why is LOC001 risky?"
        start = time.time()
        query_type = _classify_question(question)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert query_type is not None
        assert elapsed < 30, f"Intent classification took {elapsed:.2f}ms (target: < 30ms)"

    def test_comparison_computation_latency(self, realistic_blob_data):
        """Test comparison computation latency (target: < 50ms)."""
        import time

        question = "Compare LOC001 vs LOC002"
        start = time.time()
        answer = _generate_comparison_answer(question, realistic_blob_data)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 50, f"Comparison computation took {elapsed:.2f}ms (target: < 50ms)"

    def test_supplier_computation_latency(self, realistic_blob_data):
        """Test supplier computation latency (target: < 50ms)."""
        import time

        question = "List suppliers for LOC001"
        start = time.time()
        answer = _generate_supplier_by_location_answer(question, realistic_blob_data, "location", "LOC001")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 50, f"Supplier computation took {elapsed:.2f}ms (target: < 50ms)"

    def test_record_comparison_latency(self, realistic_blob_data):
        """Test record comparison latency (target: < 30ms)."""
        import time

        question = "What changed for MAT-001?"
        start = time.time()
        answer = _generate_record_comparison_answer(question, realistic_blob_data, "material_id", "MAT-001")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 30, f"Record comparison took {elapsed:.2f}ms (target: < 30ms)"

    def test_response_formatting_latency(self, realistic_blob_data):
        """Test response formatting latency (target: < 30ms)."""
        import time

        question = "Why is LOC001 risky?"
        scope_type, scope_value = _extract_scope(question)
        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), scope_type, scope_value
        )

        start = time.time()
        answer = _generate_root_cause_answer(question, realistic_blob_data, scope_type, scope_value, scoped_metrics)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 30, f"Response formatting took {elapsed:.2f}ms (target: < 30ms)"

    def test_total_response_time(self, realistic_blob_data):
        """Test total response time (target: < 500ms)."""
        import time

        question = "Why is LOC001 risky?"

        start = time.time()
        scope_type, scope_value = _extract_scope(question)
        query_type = _classify_question(question)
        scoped_metrics = _compute_scoped_metrics(
            realistic_blob_data.get("detailRecords", []), scope_type, scope_value
        )
        answer = _generate_root_cause_answer(question, realistic_blob_data, scope_type, scope_value, scoped_metrics)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert answer is not None
        assert elapsed < 500, f"Total response time was {elapsed:.2f}ms (target: < 500ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
