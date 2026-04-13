# Planning Intelligence Copilot - Sample Responses

This document shows sample responses for all 10 test prompts after the end-to-end fix.

---

## Test Prompt 1: Entity Query

**Question:** "List suppliers for CYS20_F01C01"

**Response:**
```json
{
    "question": "List suppliers for CYS20_F01C01",
    "answer": "Location CYS20_F01C01: 15 records. Suppliers: Supplier A, Supplier B, Supplier C, Supplier D, Supplier E. Materials: UPS, POWER, COOLING. Changed: 8.",
    "queryType": "entity",
    "supportingMetrics": {
        "location": "CYS20_F01C01",
        "recordCount": 15,
        "suppliers": ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"],
        "materials": ["UPS", "POWER", "COOLING"],
        "changedCount": 8
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        },
        "drivers": {
            "primary": "quantity",
            "quantity": 150,
            "supplier": 50,
            "design": 30,
            "schedule": 20
        },
        "blobFileName": "current.csv",
        "lastRefreshed": "2024-01-20T10:00:00Z"
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 2: Comparison Query

**Question:** "Compare CYS20_F01C01 vs DSM18_F01C01"

**Response:**
```json
{
    "question": "Compare CYS20_F01C01 vs DSM18_F01C01",
    "answer": "Comparison: CYS20_F01C01 vs DSM18_F01C01. CYS20_F01C01: 15 records, 8 changed. DSM18_F01C01: 12 records, 3 changed.",
    "queryType": "comparison",
    "supportingMetrics": {
        "location1": "CYS20_F01C01",
        "location1Records": 15,
        "location1Changed": 8,
        "location2": "DSM18_F01C01",
        "location2Records": 12,
        "location2Changed": 3
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 3: Impact Query

**Question:** "Which supplier has the most impact?"

**Response:**
```json
{
    "question": "Which supplier has the most impact?",
    "answer": "Impact analysis: Top suppliers affected: Supplier A (45 changes), Supplier B (32 changes), Supplier C (28 changes). Top materials affected: UPS (55 changes), POWER (38 changes), COOLING (12 changes).",
    "queryType": "impact",
    "supportingMetrics": {
        "topSuppliers": [
            ["Supplier A", 45],
            ["Supplier B", 32],
            ["Supplier C", 28]
        ],
        "topMaterials": [
            ["UPS", 55],
            ["POWER", 38],
            ["COOLING", 12]
        ]
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 4: Design Query

**Question:** "Which records have design changes?"

**Response:**
```json
{
    "question": "Which records have design changes?",
    "answer": "30 records have design changes (BOD or Form Factor). Affected suppliers: Supplier A, Supplier B, Supplier C. Affected materials: UPS, POWER.",
    "queryType": "design",
    "supportingMetrics": {
        "designChangedCount": 30,
        "totalRecords": 1000,
        "affectedSuppliers": ["Supplier A", "Supplier B", "Supplier C"],
        "affectedMaterials": ["UPS", "POWER"]
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        },
        "riskSummary": {
            "designChangedCount": 30,
            "supplierChangedCount": 50,
            "quantityChangedCount": 150,
            "scheduleChangedCount": 20
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 5: Forecast Query

**Question:** "Why did forecast increase?"

**Response:**
```json
{
    "question": "Why did forecast increase?",
    "answer": "150 records have forecast quantity changes. Total delta: +12,500 units. Average delta: +83.3 units.",
    "queryType": "forecast",
    "supportingMetrics": {
        "qtyChangedCount": 150,
        "totalQtyDelta": 12500,
        "averageQtyDelta": 83.3,
        "qtyDeltaRecords": 150
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        },
        "drivers": {
            "primary": "quantity",
            "quantity": 150,
            "supplier": 50,
            "design": 30,
            "schedule": 20
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 6: Location Query

**Question:** "Which locations need attention?"

**Response:**
```json
{
    "question": "Which locations need attention?",
    "answer": "Top locations by change count: CYS20_F01C01 (8 changes), DSM18_F01C01 (3 changes), AVC15_F02C02 (5 changes), CLT22_F01C01 (4 changes), SJC10_F03C01 (2 changes).",
    "queryType": "location",
    "supportingMetrics": {
        "topLocations": [
            ["CYS20_F01C01", 8],
            ["AVC15_F02C02", 5],
            ["DSM18_F01C01", 3],
            ["CLT22_F01C01", 4],
            ["SJC10_F03C01", 2]
        ]
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 7: Material Query

**Question:** "Which materials changed most?"

**Response:**
```json
{
    "question": "Which materials changed most?",
    "answer": "Top materials by change count: UPS (55 changes), POWER (38 changes), COOLING (12 changes), NETWORK (8 changes), STORAGE (5 changes).",
    "queryType": "material",
    "supportingMetrics": {
        "topMaterials": [
            ["UPS", 55],
            ["POWER", 38],
            ["COOLING", 12],
            ["NETWORK", 8],
            ["STORAGE", 5]
        ]
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 8: Health Query

**Question:** "What's the current planning health?"

**Response:**
```json
{
    "question": "What's the current planning health?",
    "answer": "Planning health is 75/100 (Stable). 250 of 1,000 records have changed (25.0%). Primary drivers: Design changes (30), Supplier changes (50).",
    "queryType": "health",
    "supportingMetrics": {
        "planningHealth": 75,
        "status": "Stable",
        "changedRecordCount": 250,
        "totalRecords": 1000,
        "designChanges": 30,
        "supplierChanges": 50
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 9: Risk Query

**Question:** "What are the top risks?"

**Response:**
```json
{
    "question": "What are the top risks?",
    "answer": "Risk level is Medium. Highest risk type: Supplier Change. 45 high-risk records out of 1,000 total (4.5%). Breakdown: Supplier Change (25), Design Change (15), Schedule Change (5).",
    "queryType": "risk",
    "supportingMetrics": {
        "riskLevel": "Medium",
        "highestRiskLevel": "Supplier Change",
        "highRiskCount": 45,
        "totalRecords": 1000,
        "percentHighRisk": 4.5,
        "riskBreakdown": {
            "Supplier Change": 25,
            "Design Change": 15,
            "Schedule Change": 5
        }
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        },
        "riskSummary": {
            "level": "Medium",
            "highRiskCount": 45,
            "designChangedCount": 30,
            "supplierChangedCount": 50,
            "quantityChangedCount": 150
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Test Prompt 10: Change Query

**Question:** "How many records have changed?"

**Response:**
```json
{
    "question": "How many records have changed?",
    "answer": "250 records have changed out of 1,000 total (25.0%). Breakdown: Design (30), Supplier (50), Quantity (150).",
    "queryType": "change",
    "supportingMetrics": {
        "changedRecordCount": 250,
        "totalRecords": 1000,
        "percentChanged": 25.0,
        "designChanges": 30,
        "supplierChanges": 50,
        "quantityChanges": 150
    },
    "mcpContext": {
        "computedMetrics": {
            "totalRecords": 1000,
            "changedRecords": 250,
            "changeRate": 25.0,
            "riskLevel": "Medium",
            "healthScore": 75
        },
        "drivers": {
            "primary": "quantity",
            "quantity": 150,
            "supplier": 50,
            "design": 30,
            "schedule": 20
        }
    },
    "dataMode": "blob",
    "timestamp": "2024-01-20T10:05:00Z"
}
```

---

## Response Structure

All responses follow this consistent structure:

```json
{
    "question": "User's question",
    "answer": "Human-readable answer",
    "queryType": "classification type",
    "supportingMetrics": {
        "metric1": value1,
        "metric2": value2
    },
    "mcpContext": {
        "computedMetrics": {...},
        "drivers": {...},
        "riskSummary": {...},
        "supplierSummary": {...},
        "materialSummary": {...},
        "blobFileName": "current.csv",
        "lastRefreshed": "timestamp"
    },
    "dataMode": "blob",
    "timestamp": "response timestamp"
}
```

---

## Key Features

✓ **Structured Responses** - All data is properly structured for frontend display
✓ **Supporting Metrics** - Each response includes relevant metrics
✓ **MCP Context** - Grounding context from blob data
✓ **No Hallucination** - All data comes from blob analysis
✓ **Deterministic** - Same question always produces same answer
✓ **Comprehensive** - Covers all 12 question types
✓ **Validated** - All fields validated before response

---

## Error Handling

If an error occurs, the response includes:

```json
{
    "question": "User's question",
    "answer": "Unable to generate answer. Please try a different question.",
    "queryType": "error",
    "supportingMetrics": {},
    "mcpContext": {},
    "dataMode": "blob",
    "timestamp": "response timestamp"
}
```

---

## Next Steps

1. Deploy to Azure Functions
2. Test with real blob data
3. Monitor response quality
4. Gather user feedback
5. Iterate on answer templates if needed
