"""
Phase 2: Answer Templates - Comprehensive Test Suite

Tests for:
- Comparison answer generation
- Root cause answer generation
- Why-not answer generation
- Traceability answer generation
- Summary answer generation
- Response building
"""

import pytest
from phase2_answer_templates import AnswerTemplates, ResponseBuilder


class TestAnswerTemplates:
    """Test answer template generation."""
    
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
    
    @pytest.fixture
    def sample_scoped_metrics(self):
        """Create sample scoped metrics for testing."""
        return {
            "LOC001": {
                "filteredRecordsCount": 50,
                "changedCount": 25,
                "changeRate": 50.0,
                "scopedContributionBreakdown": {
                    "quantity": 60.0,
                    "supplier": 30.0,
                    "design": 10.0,
                    "schedule": 0.0,
                },
                "scopedDrivers": {
                    "primary": "quantity",
                    "changedCount": 25,
                    "totalCount": 50,
                },
                "topContributingRecords": [
                    {
                        "LOCID": "LOC001",
                        "GSCEQUIPCAT": "UPS",
                        "PRDID": "MAT001",
                        "qtyDelta": 500,
                        "Risk_Flag": True,
                    },
                    {
                        "LOCID": "LOC001",
                        "GSCEQUIPCAT": "PUMP",
                        "PRDID": "MAT002",
                        "qtyDelta": 300,
                        "Risk_Flag": False,
                    },
                ],
            },
            "LOC002": {
                "filteredRecordsCount": 50,
                "changedCount": 10,
                "changeRate": 20.0,
                "scopedContributionBreakdown": {
                    "quantity": 40.0,
                    "supplier": 50.0,
                    "design": 10.0,
                    "schedule": 0.0,
                },
                "scopedDrivers": {
                    "primary": "supplier",
                    "changedCount": 10,
                    "totalCount": 50,
                },
                "topContributingRecords": [],
            },
        }
    
    def test_generate_comparison_answer(self, sample_context, sample_scoped_metrics):
        """Test comparison answer generation."""
        answer = AnswerTemplates.generate_comparison_answer(
            question="Compare LOC001 vs LOC002",
            ctx=sample_context,
            entities=["LOC001", "LOC002"],
            scoped_metrics=sample_scoped_metrics
        )
        
        assert "LOC001" in answer
        assert "LOC002" in answer
        assert "50.0" in answer  # LOC001 change rate
        assert "20.0" in answer  # LOC002 change rate
        assert "more changes" in answer
    
    def test_comparison_answer_identifies_higher_change(self, sample_context, sample_scoped_metrics):
        """Test that comparison identifies entity with more changes."""
        answer = AnswerTemplates.generate_comparison_answer(
            question="Compare LOC001 vs LOC002",
            ctx=sample_context,
            entities=["LOC001", "LOC002"],
            scoped_metrics=sample_scoped_metrics
        )
        
        # LOC001 has 25 changes, LOC002 has 10 changes
        assert "LOC001" in answer and "more changes" in answer
    
    def test_generate_root_cause_answer(self, sample_context, sample_scoped_metrics):
        """Test root cause answer generation."""
        answer = AnswerTemplates.generate_root_cause_answer(
            question="Why is LOC001 risky?",
            ctx=sample_context,
            scope_type="location",
            scope_value="LOC001",
            scoped_metrics=sample_scoped_metrics["LOC001"]
        )
        
        assert "LOC001" in answer
        assert "risky" in answer.lower()
        assert "50.0" in answer  # Change rate
        assert "Recommended action" in answer
    
    def test_root_cause_answer_includes_action(self, sample_context, sample_scoped_metrics):
        """Test that root cause answer includes recommended action."""
        answer = AnswerTemplates.generate_root_cause_answer(
            question="Why is LOC001 risky?",
            ctx=sample_context,
            scope_type="location",
            scope_value="LOC001",
            scoped_metrics=sample_scoped_metrics["LOC001"]
        )
        
        # Should include one of the recommended actions
        assert any(action in answer for action in sample_context["recommendedActions"])
    
    def test_generate_why_not_answer_stable(self, sample_context):
        """Test why-not answer for stable entity."""
        metrics = {
            "filteredRecordsCount": 50,
            "changedCount": 0,
            "changeRate": 0.0,
        }
        
        answer = AnswerTemplates.generate_why_not_answer(
            question="Why is LOC001 not risky?",
            ctx=sample_context,
            scope_type="location",
            scope_value="LOC001",
            scoped_metrics=metrics
        )
        
        assert "LOC001" in answer
        assert "stable" in answer.lower()
        assert "no records changed" in answer.lower()
    
    def test_generate_why_not_answer_low_change(self, sample_context):
        """Test why-not answer for low change rate."""
        metrics = {
            "filteredRecordsCount": 50,
            "changedCount": 3,
            "changeRate": 6.0,
        }
        
        answer = AnswerTemplates.generate_why_not_answer(
            question="Why is LOC001 not risky?",
            ctx=sample_context,
            scope_type="location",
            scope_value="LOC001",
            scoped_metrics=metrics
        )
        
        assert "LOC001" in answer
        assert "6.0" in answer
        assert "stable" in answer.lower()
    
    def test_generate_traceability_answer(self, sample_context, sample_scoped_metrics):
        """Test traceability answer generation."""
        answer = AnswerTemplates.generate_traceability_answer(
            question="Show top contributing records",
            ctx=sample_context,
            scoped_metrics=sample_scoped_metrics["LOC001"]
        )
        
        assert "Top" in answer
        assert "contributing records" in answer
        assert "MAT001" in answer
        assert "MAT002" in answer
        assert "500" in answer  # First delta
        assert "300" in answer  # Second delta
    
    def test_traceability_answer_includes_risk_flags(self, sample_context, sample_scoped_metrics):
        """Test that traceability answer includes risk flags."""
        answer = AnswerTemplates.generate_traceability_answer(
            question="Show top contributing records",
            ctx=sample_context,
            scoped_metrics=sample_scoped_metrics["LOC001"]
        )
        
        assert "🔴 High Risk" in answer  # First record is high risk
        assert "🟢 Normal" in answer  # Second record is normal
    
    def test_generate_summary_answer(self, sample_context):
        """Test summary answer generation."""
        answer = AnswerTemplates.generate_summary_answer(
            question="What is the overall status?",
            ctx=sample_context
        )
        
        assert "Planning health" in answer
        assert "Critical" in answer
        assert "25.0" in answer  # Change rate
        assert "50" in answer  # Changed count
        assert "200" in answer  # Total records
    
    def test_summary_answer_risk_level_high(self, sample_context):
        """Test summary answer with high risk level."""
        ctx = sample_context.copy()
        ctx["changedRecordCount"] = 100  # 50% change rate
        ctx["totalRecords"] = 200
        
        answer = AnswerTemplates.generate_summary_answer(
            question="What is the overall status?",
            ctx=ctx
        )
        
        assert "High" in answer  # Risk level
    
    def test_summary_answer_risk_level_medium(self, sample_context):
        """Test summary answer with medium risk level."""
        ctx = sample_context.copy()
        ctx["changedRecordCount"] = 40  # 20% change rate
        ctx["totalRecords"] = 200
        
        answer = AnswerTemplates.generate_summary_answer(
            question="What is the overall status?",
            ctx=ctx
        )
        
        assert "Medium" in answer  # Risk level
    
    def test_summary_answer_risk_level_low(self, sample_context):
        """Test summary answer with low risk level."""
        ctx = sample_context.copy()
        ctx["changedRecordCount"] = 10  # 5% change rate
        ctx["totalRecords"] = 200
        
        answer = AnswerTemplates.generate_summary_answer(
            question="What is the overall status?",
            ctx=ctx
        )
        
        assert "Low" in answer  # Risk level


class TestResponseBuilder:
    """Test response building."""
    
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
        }
    
    @pytest.fixture
    def sample_scoped_metrics(self):
        """Create sample scoped metrics for testing."""
        return {
            "filteredRecordsCount": 50,
            "changedCount": 25,
            "changeRate": 50.0,
            "scopedContributionBreakdown": {
                "quantity": 60.0,
                "supplier": 30.0,
                "design": 10.0,
                "schedule": 0.0,
            },
            "scopedDrivers": {
                "primary": "quantity",
                "changedCount": 25,
                "totalCount": 50,
            },
            "topContributingRecords": [],
        }
    
    def test_build_response_summary_mode(self, sample_context):
        """Test building response in summary mode."""
        response = ResponseBuilder.build_response(
            question="What is the overall status?",
            answer="Planning health is critical",
            query_type="summary",
            answer_mode="summary",
            ctx=sample_context
        )
        
        assert response["question"] == "What is the overall status?"
        assert response["answer"] == "Planning health is critical"
        assert response["queryType"] == "summary"
        assert response["answerMode"] == "summary"
        assert "investigateMode" not in response
    
    def test_build_response_investigate_mode(self, sample_context, sample_scoped_metrics):
        """Test building response in investigate mode."""
        response = ResponseBuilder.build_response(
            question="Why is LOC001 risky?",
            answer="LOC001 is risky because 50% changed",
            query_type="root_cause",
            answer_mode="investigate",
            ctx=sample_context,
            scope_type="location",
            scope_value="LOC001",
            scoped_metrics=sample_scoped_metrics
        )
        
        assert response["answerMode"] == "investigate"
        assert "investigateMode" in response
        assert response["investigateMode"]["scopeType"] == "location"
        assert response["investigateMode"]["scopeValue"] == "LOC001"
        assert response["investigateMode"]["filteredRecordsCount"] == 50
    
    def test_response_includes_supporting_metrics(self, sample_context):
        """Test that response includes supporting metrics."""
        response = ResponseBuilder.build_response(
            question="What is the overall status?",
            answer="Planning health is critical",
            query_type="summary",
            answer_mode="summary",
            ctx=sample_context
        )
        
        assert "supportingMetrics" in response
        assert response["supportingMetrics"]["changedRecordCount"] == 50
        assert response["supportingMetrics"]["totalRecords"] == 200
    
    def test_response_includes_explainability(self, sample_context):
        """Test that response includes explainability metadata."""
        response = ResponseBuilder.build_response(
            question="What is the overall status?",
            answer="Planning health is critical",
            query_type="summary",
            answer_mode="summary",
            ctx=sample_context
        )
        
        assert "explainability" in response
        assert "confidence" in response["explainability"]
        assert "freshness" in response["explainability"]
    
    def test_response_includes_suggested_actions(self, sample_context):
        """Test that response includes suggested actions."""
        response = ResponseBuilder.build_response(
            question="What is the overall status?",
            answer="Planning health is critical",
            query_type="summary",
            answer_mode="summary",
            ctx=sample_context
        )
        
        assert "suggestedActions" in response
        assert len(response["suggestedActions"]) > 0
    
    def test_response_includes_follow_ups(self, sample_context):
        """Test that response includes follow-up questions."""
        response = ResponseBuilder.build_response(
            question="What is the overall status?",
            answer="Planning health is critical",
            query_type="summary",
            answer_mode="summary",
            ctx=sample_context
        )
        
        assert "followUpQuestions" in response
        assert len(response["followUpQuestions"]) > 0


class TestResponseVariety:
    """Test that different answer types produce different responses."""
    
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
    
    @pytest.fixture
    def sample_scoped_metrics(self):
        """Create sample scoped metrics for testing."""
        return {
            "LOC001": {
                "filteredRecordsCount": 50,
                "changedCount": 25,
                "changeRate": 50.0,
                "scopedContributionBreakdown": {
                    "quantity": 60.0,
                    "supplier": 30.0,
                    "design": 10.0,
                    "schedule": 0.0,
                },
                "scopedDrivers": {
                    "primary": "quantity",
                    "changedCount": 25,
                    "totalCount": 50,
                },
                "topContributingRecords": [
                    {
                        "LOCID": "LOC001",
                        "GSCEQUIPCAT": "UPS",
                        "PRDID": "MAT001",
                        "qtyDelta": 500,
                        "Risk_Flag": True,
                    },
                ],
            },
            "LOC002": {
                "filteredRecordsCount": 50,
                "changedCount": 10,
                "changeRate": 20.0,
                "scopedContributionBreakdown": {
                    "quantity": 40.0,
                    "supplier": 50.0,
                    "design": 10.0,
                    "schedule": 0.0,
                },
                "scopedDrivers": {
                    "primary": "supplier",
                    "changedCount": 10,
                    "totalCount": 50,
                },
                "topContributingRecords": [],
            },
        }
    
    def test_comparison_vs_summary_different(self, sample_context, sample_scoped_metrics):
        """Test that comparison and summary answers are different."""
        comparison = AnswerTemplates.generate_comparison_answer(
            question="Compare LOC001 vs LOC002",
            ctx=sample_context,
            entities=["LOC001", "LOC002"],
            scoped_metrics=sample_scoped_metrics
        )
        
        summary = AnswerTemplates.generate_summary_answer(
            question="What is the overall status?",
            ctx=sample_context
        )
        
        assert comparison != summary
        assert "vs" in comparison or "comparison" in comparison.lower()
        assert "Planning health" in summary
    
    def test_root_cause_vs_why_not_different(self, sample_context, sample_scoped_metrics):
        """Test that root cause and why-not answers are different."""
        root_cause = AnswerTemplates.generate_root_cause_answer(
            question="Why is LOC001 risky?",
            ctx=sample_context,
            scope_type="location",
            scope_value="LOC001",
            scoped_metrics=sample_scoped_metrics["LOC001"]
        )
        
        why_not = AnswerTemplates.generate_why_not_answer(
            question="Why is LOC001 not risky?",
            ctx=sample_context,
            scope_type="location",
            scope_value="LOC001",
            scoped_metrics=sample_scoped_metrics["LOC001"]
        )
        
        assert root_cause != why_not
        assert "risky" in root_cause.lower()
        assert "stable" in why_not.lower() or "not risky" in why_not.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
