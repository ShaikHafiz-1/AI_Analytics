# LLM System Architecture - Complete Overview

## System Flow

```
User Question
    ↓
Frontend Dashboard
    ↓
Azure Functions (explain endpoint)
    ↓
Question Classification
    ↓
Metrics Computation
    ↓
Blob Data Loading (13,148 records)
    ↓
LLM Service
    ├─ System Prompt (with business rules)
    ├─ Field Definitions (SAP schema)
    ├─ Sample Records (10 records from blob)
    ├─ Computed Metrics
    └─ Response Guidelines
    ↓
ChatGPT API
    ↓
Natural Language Response
    ↓
Frontend Display
```

## LLM Service Components

### 1. System Prompt (`_build_system_prompt()`)
Injected into every ChatGPT request:

```
You are a Planning Intelligence Copilot...

BUSINESS RULES & DOMAIN KNOWLEDGE:
- Composite Key: LOCID + GSCEQUIPCAT + PRDID
- Design Change Detection: ZCOIBODVER or ZCOIFORMFACT changed
- Forecast Trend: GSCFSCTQTY - GSCPREVFCSTQTY
- Supplier Analysis: Group by LOCFR
- ROJ Schedule: NBD_DeltaDays calculation
- Exclusion Rules: Exclude Is_New Demand, Is_cancelled

SAP FIELD DEFINITIONS:
- LOCID: Location ID (facility identifier)
- PRDID: Material ID (product identifier)
- GSCEQUIPCAT: Equipment Category
- LOCFR: Supplier
- ZCOIBODVER: BOD Version (design change indicator)
- ZCOIFORMFACT: Form Factor (design change indicator)
- GSCFSCTQTY: Current Forecast Quantity
- GSCPREVFCSTQTY: Previous Forecast Quantity
- GSCCONROJDATE: Current ROJ Date
- GSCPREVROJNBD: Previous ROJ Date
- NBD_DeltaDays: ROJ Shift in Days
- GSCSUPLDATE: Supplier Date
- Is_SupplierDateMissing: Supplier Date Missing Flag
- Is_New Demand: New Demand Flag (exclude)
- Is_cancelled: Cancelled Demand Flag (exclude)

RESPONSE REQUIREMENTS:
- Explain WHY changes happened (business context)
- Connect forecast, supplier, design, and schedule impacts
- Use natural, conversational tone
- Never compute values - use provided metrics
- Never hallucinate data or logic
- Always respect SAP field definitions
```

### 2. User Prompt (`_build_user_prompt()`)
Includes:
- User's question
- Computed metrics (health, changes, risks, etc.)
- Sample records from blob data (10 records)
- Field definitions for each record

Example:
```
User Question: What's the current planning health status?

Data Context:
- Planning Health: 37/100
- Changed Records: 2,951/13,148
- Design Changes: 1,926
- Supplier Changes: 1,499

Sample Records from Blob Data:
Record 1:
  Location ID (LOCID): CYS20_F01C01
  Material ID (PRDID): ACC
  Supplier (LOCFR): 10_AMER
  Current Forecast (GSCFSCTQTY): 1,000
  Previous Forecast (GSCPREVFCSTQTY): 800
  BOD Version (ZCOIBODVER): 2.0
  Form Factor (ZCOIFORMFACT): Standard
  Current ROJ Date (GSCCONROJDATE): 2026-05-15
  Previous ROJ Date (GSCPREVROJNBD): 2026-05-10
  ROJ Shift (NBD_DeltaDays): 5
  Design Changed: Yes
  Supplier Changed: No
  Quantity Changed: Yes

... and 13,138 more records
```

### 3. Response Generation
ChatGPT generates response with:
1. Natural greeting
2. Direct answer
3. Key metrics
4. Business impact explanation
5. Suggested actions

Example:
```
"Hi! Your planning health is currently at 37/100 (Critical). 
2,951 of 13,148 records (22.4%) have changed since the last period.

The primary drivers are:
- Design changes (1,926 records): Materials with BOD version or form factor updates
- Supplier changes (1,499 records): Supplier transitions or date updates

This indicates significant supply chain activity. Design changes require engineering review, 
and supplier transitions need coordination to ensure delivery timelines are met.

I recommend:
1. Prioritize design change reviews with engineering
2. Coordinate with affected suppliers on transition timelines
3. Monitor ROJ dates for any schedule impacts
4. Review forecast changes for procurement planning"
```

## Data Flow

### Input Data
- **Blob Storage**: 13,148 planning records (current.csv + previous.csv)
- **User Question**: Natural language query
- **Context**: Optional additional context from frontend

### Processing
1. **Question Classification**: Determine question type (health, risk, forecast, etc.)
2. **Metrics Computation**: Calculate relevant metrics from blob data
3. **Record Normalization**: Standardize field names and types
4. **Sample Selection**: Select 10 representative records
5. **LLM Prompt Building**: Inject business rules, field definitions, and data

### Output
- **Natural Language Response**: ChatGPT-generated answer
- **Supporting Metrics**: Structured data for frontend display
- **MCP Context**: Additional context for future requests

## Business Rules Enforcement

### Design Change Detection
```python
if (ZCOIBODVER changed) OR (ZCOIFORMFACT changed):
    if Is_New Demand != TRUE and Is_cancelled != TRUE:
        design_change = TRUE
```

### Forecast Trend Calculation
```python
trend = GSCFSCTQTY - GSCPREVFCSTQTY
if trend > 0:
    interpretation = "Forecast increased (higher procurement requirements)"
elif trend < 0:
    interpretation = "Forecast decreased (lower procurement requirements)"
else:
    interpretation = "Forecast stable"
```

### Supplier Analysis
```python
suppliers = group_by(LOCFR)
for supplier in suppliers:
    risk_indicators = [
        GSCSUPLDATE changes,
        Is_SupplierDateMissing,
        multiple design changes,
        multiple forecast changes
    ]
```

### ROJ Schedule Analysis
```python
nbd_delta = GSCCONROJDATE - GSCPREVROJNBD
if nbd_delta > 0:
    interpretation = "Schedule delayed (material needed later)"
elif nbd_delta < 0:
    interpretation = "Schedule accelerated (material needed sooner)"
else:
    interpretation = "Schedule unchanged"
```

## Constraints & Safeguards

### Never Compute
- ChatGPT never calculates metrics
- All metrics provided by backend
- ChatGPT only interprets provided data

### Never Hallucinate
- ChatGPT only references actual records
- No invented suppliers, materials, or locations
- No made-up business logic

### Always Use Context
- Business rules injected into every prompt
- Field definitions included in every request
- Sample records provided for reference

### Always Respect Schema
- SAP field definitions are authoritative
- Business rules are enforced
- Exclusion rules are applied

## Error Handling

### LLM Failures
- If ChatGPT fails: Fall back to template-based response
- If API key missing: Use mock responses
- If timeout: Return cached response

### Data Issues
- If no records: Return error message
- If invalid question: Request clarification
- If computation fails: Return partial response

## Performance Optimization

### Prompt Size
- System prompt: ~2KB (business rules + field definitions)
- User prompt: ~5KB (metrics + 10 sample records)
- Total: ~7KB per request (well within limits)

### Response Time
- Question classification: <10ms
- Metrics computation: <100ms
- LLM API call: 1-3 seconds
- Total: 1-3 seconds per request

### Caching
- Business rules cached in memory
- Field definitions cached in memory
- Sample records selected on-demand

## Testing Strategy

### Unit Tests
- Business rules validation
- Field definition completeness
- Response guideline enforcement

### Integration Tests
- End-to-end question → response flow
- LLM prompt building
- Error handling

### Validation Tests
- Field explanation accuracy
- Business rule interpretation
- Response quality and tone

## Deployment Checklist

- [ ] Deploy `business_rules.py`
- [ ] Deploy updated `llm_service.py`
- [ ] Run `test_business_rules_llm.py`
- [ ] Test field explanations
- [ ] Test design change analysis
- [ ] Test forecast trend explanation
- [ ] Test supplier analysis
- [ ] Test ROJ schedule analysis
- [ ] Verify response quality
- [ ] Check Azure Insights logs
- [ ] Confirm response times

## Success Metrics

✅ ChatGPT understands all SAP fields
✅ ChatGPT explains business rules correctly
✅ ChatGPT provides business context in responses
✅ ChatGPT includes suggested actions
✅ Responses are conversational and professional
✅ No hallucinated data or logic
✅ All responses respect business rules
✅ Response time < 3 seconds
✅ Error rate < 1%
✅ User satisfaction > 90%

## Future Enhancements

1. **Multi-turn Conversations**: Remember context across questions
2. **Predictive Insights**: Forecast future issues based on trends
3. **Automated Alerts**: Notify users of critical changes
4. **Custom Reports**: Generate formatted reports from responses
5. **Feedback Loop**: Learn from user feedback to improve responses
6. **Advanced Analytics**: Deeper analysis of supplier and material trends
