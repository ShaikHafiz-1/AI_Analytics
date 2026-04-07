"""
Test data and fixtures for Copilot Real-Time Answers tests.
Provides realistic sample data for testing all scenarios.
"""

# ============================================================================
# Sample Detail Records
# ============================================================================

SAMPLE_DETAIL_RECORDS = [
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
        "locationId": "LOC001",
        "supplier": "SUP001",
        "materialGroup": "Electronics",
        "materialId": "MAT003",
        "changed": True,
        "qtyChanged": False,
        "supplierChanged": False,
        "designChanged": True,
        "scheduleChanged": True,
        "qtyDelta": 200,
        "changeType": "Design Change",
        "riskLevel": "High Risk",
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
    {
        "locationId": "LOC002",
        "supplier": "SUP002",
        "materialGroup": "Mechanical",
        "materialId": "MAT005",
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
        "locationId": "LOC003",
        "supplier": "SUP003",
        "materialGroup": "Mechanical",
        "materialId": "MAT006",
        "changed": False,
        "qtyChanged": False,
        "supplierChanged": False,
        "designChanged": False,
        "scheduleChanged": False,
        "qtyDelta": 0,
        "changeType": "No Change",
        "riskLevel": "Low Risk",
    },
]

# ============================================================================
# Sample Context Objects
# ============================================================================

SAMPLE_CONTEXT_MINIMAL = {
    "detailRecords": SAMPLE_DETAIL_RECORDS,
    "planningHealth": 65,
    "changedRecordCount": 4,
    "totalRecords": 6,
}

SAMPLE_CONTEXT_FULL = {
    "detailRecords": SAMPLE_DETAIL_RECORDS,
    "planningHealth": 65,
    "status": "At Risk",
    "changedRecordCount": 4,
    "totalRecords": 6,
    "aiInsight": "Design changes are driving risk in LOC001 and LOC002",
    "rootCause": "Supplier changed design specs for Electronics materials",
    "recommendedActions": [
        "Review design change impact on schedule",
        "Monitor supplier reliability",
        "Validate new design specs",
    ],
    "drivers": {
        "location": "LOC001",
        "changeType": "Design",
        "supplier": "SUP001",
    },
    "riskSummary": {
        "highestRiskLevel": "Design + Supplier",
        "highRiskCount": 2,
        "riskBreakdown": {
            "High Risk": 2,
            "Medium Risk": 2,
            "Low Risk": 2,
        },
    },
    "contributionBreakdown": {
        "quantity": 25.0,
        "supplier": 25.0,
        "design": 50.0,
        "schedule": 0.0,
    },
    "kpis": {
        "designChangeRate": 50.0,
        "supplierReliability": 85.0,
        "demandVolatility": 15.0,
        "scheduleStability": 90.0,
        "riskConcentration": 33.0,
        "newDemandRatio": 10.0,
        "cancellationRate": 2.0,
    },
    "datacenterSummary": [
        {
            "locationId": "LOC001",
            "changed": 3,
            "total": 3,
        },
        {
            "locationId": "LOC002",
            "changed": 1,
            "total": 2,
        },
        {
            "locationId": "LOC003",
            "changed": 0,
            "total": 1,
        },
    ],
    "materialGroupSummary": [
        {
            "materialGroup": "Electronics",
            "changed": 3,
            "total": 3,
            "qtyChanged": 1,
            "designChanged": 2,
            "supplierChanged": 1,
        },
        {
            "materialGroup": "Mechanical",
            "changed": 1,
            "total": 3,
            "qtyChanged": 0,
            "designChanged": 1,
            "supplierChanged": 0,
        },
    ],
    "trendDirection": "Increasing",
    "trendDelta": 1500,
    "lastRefreshedAt": "2026-04-05T10:30:00Z",
    "dataMode": "cached",
}

# ============================================================================
# Test Scenarios
# ============================================================================

TEST_SCENARIOS = [
    {
        "name": "Comparison Question",
        "question": "Compare LOC001 vs LOC002",
        "expected_query_type": "comparison",
        "expected_answer_mode": "investigate",
        "expected_scope_type": "location",
        "expected_scope_value": "LOC001",
        "should_include_in_answer": ["Comparison", "LOC001", "LOC002", "changed"],
    },
    {
        "name": "Root Cause Question",
        "question": "Why is LOC001 risky?",
        "expected_query_type": "root_cause",
        "expected_answer_mode": "investigate",
        "expected_scope_type": "location",
        "expected_scope_value": "LOC001",
        "should_include_in_answer": ["LOC001", "risky", "Recommended action"],
    },
    {
        "name": "Why-Not Question",
        "question": "Why is LOC003 not risky?",
        "expected_query_type": "why_not",
        "expected_answer_mode": "investigate",
        "expected_scope_type": "location",
        "expected_scope_value": "LOC003",
        "should_include_in_answer": ["LOC003", "stable"],
    },
    {
        "name": "Traceability Question",
        "question": "Show top contributing records",
        "expected_query_type": "traceability",
        "expected_answer_mode": "investigate",
        "expected_scope_type": None,
        "expected_scope_value": None,
        "should_include_in_answer": ["Top", "contributing records", "📊"],
    },
    {
        "name": "Supplier Comparison",
        "question": "Compare SUP001 vs SUP002",
        "expected_query_type": "comparison",
        "expected_answer_mode": "investigate",
        "expected_scope_type": "supplier",
        "expected_scope_value": "SUP001",
        "should_include_in_answer": ["Comparison", "SUP001", "SUP002"],
    },
    {
        "name": "Material Group Question",
        "question": "Why is material group Electronics risky?",
        "expected_query_type": "root_cause",
        "expected_answer_mode": "investigate",
        "expected_scope_type": "material_group",
        "expected_scope_value": "MATERIAL GROUP ELECTRONICS",
        "should_include_in_answer": ["Electronics", "risky"],
    },
    {
        "name": "Summary Question",
        "question": "What is the planning health?",
        "expected_query_type": "summary",
        "expected_answer_mode": "summary",
        "expected_scope_type": None,
        "expected_scope_value": None,
        "should_include_in_answer": ["Planning health", "65"],
    },
    {
        "name": "Risk Question",
        "question": "What is the risk level?",
        "expected_query_type": "risk",
        "expected_answer_mode": "summary",
        "expected_scope_type": None,
        "expected_scope_value": None,
        "should_include_in_answer": ["Risk"],
    },
    {
        "name": "Action Question",
        "question": "What should the planner do next?",
        "expected_query_type": "action",
        "expected_answer_mode": "summary",
        "expected_scope_type": None,
        "expected_scope_value": None,
        "should_include_in_answer": ["Recommended actions"],
    },
]

# ============================================================================
# Expected Responses
# ============================================================================

EXPECTED_RESPONSE_STRUCTURE = {
    "question": str,
    "answer": str,
    "queryType": str,
    "answerMode": str,
    "aiInsight": (str, type(None)),
    "rootCause": (str, type(None)),
    "recommendedActions": list,
    "planningHealth": (int, type(None)),
    "dataMode": str,
    "lastRefreshedAt": (str, type(None)),
    "supportingMetrics": dict,
    "contextUsed": list,
    "explainability": dict,
    "suggestedActions": list,
    "followUpQuestions": list,
}

EXPECTED_INVESTIGATE_MODE_STRUCTURE = {
    "filteredRecordsCount": int,
    "scopedContributionBreakdown": dict,
    "scopedDrivers": dict,
    "topContributingRecords": list,
    "scopeType": (str, type(None)),
    "scopeValue": (str, type(None)),
}

# ============================================================================
# Performance Benchmarks
# ============================================================================

PERFORMANCE_TARGETS = {
    "scoped_metrics_computation": 100,  # milliseconds
    "answer_generation": 50,  # milliseconds
    "total_response_time": 500,  # milliseconds
}

# ============================================================================
# Test Utilities
# ============================================================================

def validate_response_structure(response):
    """Validate that response has expected structure."""
    for key, expected_type in EXPECTED_RESPONSE_STRUCTURE.items():
        assert key in response, f"Missing key: {key}"
        if isinstance(expected_type, tuple):
            assert isinstance(response[key], expected_type), \
                f"Invalid type for {key}: expected {expected_type}, got {type(response[key])}"
        else:
            assert isinstance(response[key], expected_type), \
                f"Invalid type for {key}: expected {expected_type}, got {type(response[key])}"


def validate_investigate_mode(investigate_mode):
    """Validate that investigateMode has expected structure."""
    for key, expected_type in EXPECTED_INVESTIGATE_MODE_STRUCTURE.items():
        assert key in investigate_mode, f"Missing key in investigateMode: {key}"
        if isinstance(expected_type, tuple):
            assert isinstance(investigate_mode[key], expected_type), \
                f"Invalid type for {key}: expected {expected_type}, got {type(investigate_mode[key])}"
        else:
            assert isinstance(investigate_mode[key], expected_type), \
                f"Invalid type for {key}: expected {expected_type}, got {type(investigate_mode[key])}"


def validate_answer_content(answer, expected_content):
    """Validate that answer contains expected content."""
    for content in expected_content:
        assert content in answer, f"Expected '{content}' in answer, but not found"


if __name__ == "__main__":
    print("Test data module loaded successfully")
    print(f"Sample detail records: {len(SAMPLE_DETAIL_RECORDS)} records")
    print(f"Test scenarios: {len(TEST_SCENARIOS)} scenarios")
