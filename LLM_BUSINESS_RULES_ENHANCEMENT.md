# LLM Business Rules Enhancement

## Overview
Enhanced ChatGPT to understand your complete business rules, SAP schema, and domain knowledge. Now ChatGPT can explain WHY changes happened, not just report numbers.

## What Was Added

### 1. Business Rules Module (`planning_intelligence/business_rules.py`)
Complete business logic that ChatGPT now understands:

**Composite Key:**
- LOCID + GSCEQUIPCAT + PRDID = unique record identifier

**Design Change Detection:**
- Design Change = TRUE if (ZCOIBODVER changed) OR (ZCOIFORMFACT changed)
- EXCLUDE: Is_New Demand = TRUE, Is_cancelled = TRUE

**Forecast Trend Analysis:**
- Formula: Trend = GSCFSCTQTY - GSCPREVFCSTQTY
- Positive → Forecast increased (higher procurement requirements)
- Negative → Forecast decreased (lower procurement requirements)

**Supplier Analysis:**
- Group records by LOCFR (Supplier)
- Risk indicators: GSCSUPLDATE changes, Is_SupplierDateMissing, multiple changes

**ROJ / Schedule Analysis:**
- NBD_DeltaDays = days between GSCCONROJDATE and GSCPREVROJNBD
- Positive → Schedule delayed
- Negative → Schedule accelerated

**Exclusion Rules:**
- EXCLUDE if Is_New Demand = TRUE
- EXCLUDE if Is_cancelled = TRUE

### 2. Enhanced System Prompt (`llm_service.py`)
Updated `_build_system_prompt()` to inject:
- Complete business rules context
- SAP field definitions with business context
- Response generation guidelines
- Critical constraints (never compute, never hallucinate, always use context)

### 3. Enhanced Record Formatting (`llm_service.py`)
Updated `_format_sample_records()` to:
- Include field names and business context
- Format values appropriately (booleans as Yes/No, numbers with commas)
- Show actual blob data with proper field interpretation

## SAP Field Dictionary

ChatGPT now understands all fields:

| Field | Name | Business Context |
|-------|------|------------------|
| LOCID | Location ID | Facility identifier, part of composite key |
| PRDID | Material ID | Product identifier, part of composite key |
| GSCEQUIPCAT | Equipment Category | Equipment type, part of composite key |
| LOCFR | Supplier | Supplier code, used for supplier analysis |
| ZCOIBODVER | BOD Version | Design version, change = design modification |
| ZCOIFORMFACT | Form Factor | Physical form, change = design modification |
| GSCFSCTQTY | Current Forecast | Latest demand forecast |
| GSCPREVFCSTQTY | Previous Forecast | Previous demand forecast |
| GSCCONROJDATE | Current ROJ Date | When material is needed |
| GSCPREVROJNBD | Previous ROJ Date | Previous delivery target |
| NBD_DeltaDays | ROJ Shift | Days schedule has shifted |
| GSCSUPLDATE | Supplier Date | Supplier data freshness |
| Is_SupplierDateMissing | Supplier Date Missing | Data quality flag |
| Is_New Demand | New Demand | Exclude from change analysis |
| Is_cancelled | Cancelled Demand | Exclude from change analysis |

## Response Generation Guidelines

ChatGPT now generates responses with:

1. **Greeting** (optional): Natural greeting
2. **Direct Answer**: Answer the question
3. **Key Metrics**: Specific numbers and percentages
4. **Explanation**: WHY changes happened (business context)
5. **Business Impact**: What it means for the business
6. **Suggested Actions**: What should be done

## Example Responses

### Before Enhancement
```
"Forecast analysis shows 1 records with quantity changes. Total forecast adjustments detected across..."
```

### After Enhancement
```
"Hi! I found that forecast demand has increased by 500 units (from 800 to 1,300). This indicates higher procurement requirements, which may impact supplier capacity and delivery timelines. I recommend coordinating with suppliers to confirm they can meet the increased demand by the ROJ date."
```

## Deployment Steps

### Step 1: Deploy Files
```bash
cd planning_intelligence
func azure functionapp publish pi-planning-intelligence --build remote
```

Files deployed:
- `planning_intelligence/business_rules.py` (NEW)
- `planning_intelligence/llm_service.py` (UPDATED)

### Step 2: Test Business Rules Understanding

**Test 1: Field Explanation**
```
Question: "What is ZCOIBODVER?"
Expected: "ZCOIBODVER represents the BOD (Bill of Design) version. When this changes, it indicates a design modification to the material. Design changes require engineering review and may impact supplier capacity and delivery timelines."
```

**Test 2: Design Change Analysis**
```
Question: "What design changes have been detected?"
Expected: Response explains ZCOIBODVER and ZCOIFORMFACT changes, business impact, and recommended actions
```

**Test 3: Forecast Trend**
```
Question: "What's the forecast?"
Expected: Response explains forecast delta, procurement impact, and supplier coordination needs
```

**Test 4: Supplier Analysis**
```
Question: "List suppliers for UPS at CYS20"
Expected: Response lists suppliers, explains their role, and recommends supplier coordination
```

**Test 5: ROJ Schedule**
```
Question: "What's the ROJ?"
Expected: Response explains ROJ dates, schedule shifts, and procurement timing impact
```

## Validation Checklist

- [ ] Deploy `business_rules.py` and updated `llm_service.py`
- [ ] Test field explanation (ZCOIBODVER, GSCFSCTQTY, etc.)
- [ ] Test design change analysis
- [ ] Test forecast trend explanation
- [ ] Test supplier analysis
- [ ] Test ROJ schedule analysis
- [ ] Verify responses include business context
- [ ] Verify responses include suggested actions
- [ ] Check Azure Insights logs for errors
- [ ] Confirm response times are acceptable

## Expected Improvements

✅ ChatGPT explains WHY changes happened (business context)
✅ Responses connect forecast, supplier, design, and schedule impacts
✅ Responses include business impact and recommended actions
✅ Field explanations are accurate and domain-aware
✅ Responses feel conversational and intelligent
✅ No hallucinated logic or computed values
✅ All responses respect SAP field definitions and business rules

## Rollback Plan

If issues occur:
1. Revert `llm_service.py` to previous version
2. Delete `business_rules.py`
3. Redeploy to Azure Functions

## Notes

- Business rules are injected into every ChatGPT prompt
- Field definitions are included in sample records
- All constraints are enforced (never compute, never hallucinate)
- Mock mode still works for testing without API key
- Graceful fallback to templates if ChatGPT fails
