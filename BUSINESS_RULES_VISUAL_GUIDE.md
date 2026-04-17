# Business Rules Visual Guide - How ChatGPT Gets Strong Insights

## The Journey of Business Rules to ChatGPT

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 1: Business Rules Defined in Python                        │
│                                                                   │
│  planning_intelligence/business_rules.py                         │
│  ├── SAP_FIELD_DICTIONARY (30+ fields)                           │
│  │   ├── LOCID: Location ID                                      │
│  │   ├── ZCOIBODVER: BOD Version                                 │
│  │   ├── GSCFSCTQTY: Current Forecast Quantity                   │
│  │   ├── GSCCONROJDATE: Current ROJ Date                         │
│  │   └── ... (26 more fields)                                    │
│  │                                                                │
│  ├── BUSINESS_RULES (6 rule categories)                          │
│  │   ├── composite_key: How records are uniquely identified      │
│  │   ├── design_change_detection: How to identify design changes │
│  │   ├── forecast_trend: How to calculate forecast trends        │
│  │   ├── supplier_analysis: How to analyze suppliers             │
│  │   ├── roj_schedule_analysis: How to interpret schedule changes│
│  │   └── exclusion_rules: What NOT to count as changes           │
│  │                                                                │
│  └── RESPONSE_GUIDELINES (How to structure responses)            │
│      ├── Structure: Greeting, Answer, Metrics, Explanation, etc. │
│      ├── Tone: Conversational, not robotic                       │
│      └── Constraints: Never compute, never hallucinate, etc.     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 2: Business Rules Formatted into System Prompt             │
│                                                                   │
│  planning_intelligence/llm_service.py                            │
│  _build_system_prompt()                                          │
│  ├── Imports business rules from business_rules.py               │
│  ├── Calls get_business_rules_context()                          │
│  ├── Calls get_field_definitions_context()                       │
│  ├── Calls get_response_guidelines_context()                     │
│  └── Combines into single system prompt (~2,500 tokens)          │
│                                                                   │
│  System Prompt Content:                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ You are a Planning Intelligence Copilot...              │    │
│  │                                                          │    │
│  │ BUSINESS RULES & DOMAIN KNOWLEDGE:                      │    │
│  │ 1. COMPOSITE KEY (Unique Record Identifier):            │    │
│  │    - LOCID + GSCEQUIPCAT + PRDID = unique record        │    │
│  │                                                          │    │
│  │ 2. DESIGN CHANGE DETECTION:                             │    │
│  │    - Design Change = TRUE if (ZCOIBODVER changed) OR    │    │
│  │      (ZCOIFORMFACT changed)                             │    │
│  │    - EXCLUDE: Is_New Demand = TRUE, Is_cancelled = TRUE │    │
│  │                                                          │    │
│  │ 3. FORECAST TREND ANALYSIS:                             │    │
│  │    - Formula: Trend = GSCFSCTQTY - GSCPREVFCSTQTY       │    │
│  │    - Positive → Forecast increased                      │    │
│  │    - Negative → Forecast decreased                      │    │
│  │                                                          │    │
│  │ 4. SUPPLIER ANALYSIS:                                   │    │
│  │    - Group records by LOCFR (Supplier)                  │    │
│  │    - Risk indicators: GSCSUPLDATE changes, etc.         │    │
│  │                                                          │    │
│  │ 5. ROJ / SCHEDULE ANALYSIS:                             │    │
│  │    - NBD_DeltaDays = days between ROJ dates             │    │
│  │    - Positive → Schedule delayed                        │    │
│  │    - Negative → Schedule accelerated                    │    │
│  │                                                          │    │
│  │ SAP FIELD DEFINITIONS:                                  │    │
│  │ LOCID (Location ID):                                    │    │
│  │   Description: Unique identifier for a facility         │    │
│  │   Type: string                                          │    │
│  │   Business Context: Used to group records by location   │    │
│  │                                                          │    │
│  │ ZCOIBODVER (BOD Version):                               │    │
│  │   Description: Bill of Design version number            │    │
│  │   Type: string                                          │    │
│  │   Business Context: Tracks design version. Change       │    │
│  │   indicates design modification.                        │    │
│  │                                                          │    │
│  │ ... (28 more field definitions)                         │    │
│  │                                                          │    │
│  │ RESPONSE GENERATION GUIDELINES:                         │    │
│  │ - Explain WHY changes happened (business context)       │    │
│  │ - Connect forecast, supplier, design, schedule impacts  │    │
│  │ - Use natural, conversational tone                      │    │
│  │ - Never compute values - use provided metrics           │    │
│  │ - Never hallucinate data or logic                       │    │
│  │ - Always use MCP context and blob data                  │    │
│  │ - Always respect SAP field definitions                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 3: System Prompt Sent to ChatGPT                           │
│                                                                   │
│  OpenAI API Call:                                                │
│  client.chat.completions.create(                                │
│    model="gpt-4",                                                │
│    messages=[                                                    │
│      {                                                           │
│        "role": "system",                                         │
│        "content": system_prompt  ← Business rules here           │
│      },                                                          │
│      {                                                           │
│        "role": "user",                                           │
│        "content": "What are the top risks?"                      │
│      }                                                           │
│    ]                                                             │
│  )                                                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 4: ChatGPT Processes with Business Rules                   │
│                                                                   │
│  ChatGPT reads:                                                  │
│  1. System prompt (business rules, field definitions, guidelines)│
│  2. User message (question + data)                               │
│                                                                   │
│  ChatGPT understands:                                            │
│  ✅ Composite key structure (LOCID + GSCEQUIPCAT + PRDID)        │
│  ✅ Design change detection (ZCOIBODVER or ZCOIFORMFACT changed) │
│  ✅ Forecast trends (GSCFSCTQTY - GSCPREVFCSTQTY)                │
│  ✅ Supplier analysis (group by LOCFR)                           │
│  ✅ ROJ schedule analysis (NBD_DeltaDays)                        │
│  ✅ Exclusion rules (Is_New Demand, Is_cancelled)                │
│  ✅ Field meanings (30+ fields with business context)            │
│  ✅ Response guidelines (structure, tone, constraints)           │
│                                                                   │
│  ChatGPT applies business rules to data:                         │
│  - Identifies design changes using detection rule                │
│  - Calculates forecast trends using formula                      │
│  - Groups suppliers using grouping rule                          │
│  - Interprets schedule changes using ROJ rule                    │
│  - Excludes new demands and cancellations                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 5: ChatGPT Generates Strong Insights                       │
│                                                                   │
│  Response:                                                       │
│  "We're seeing CRITICAL risk levels affecting 24.4% of your     │
│   records (3,208 out of 13,148). The primary concern is Design  │
│   + Supplier Change Risk - materials experiencing both design   │
│   modifications AND supplier transitions simultaneously.         │
│                                                                   │
│   This combination creates supply chain complexity because:      │
│   1. Design changes require engineering review and may impact    │
│      supplier capacity                                           │
│   2. Supplier transitions introduce new relationships and        │
│      potential delays                                            │
│   3. Combined, they create uncertainty in delivery timelines     │
│                                                                   │
│   I recommend prioritizing these 1,500 records for supplier      │
│   coordination and engineering review to mitigate delivery       │
│   risks. Specifically:                                           │
│   - Reach out to affected suppliers to confirm they can          │
│     accommodate design changes                                   │
│   - Coordinate engineering reviews to ensure supplier capacity   │
│   - Establish clear delivery timelines for the transition period"│
│                                                                   │
│  Why this is a strong insight:                                   │
│  ✅ Uses business rules (understands design + supplier impact)   │
│  ✅ Explains WHY (business context, not just numbers)            │
│  ✅ Provides context (why combination is risky)                  │
│  ✅ Actionable (specific recommendations)                        │
│  ✅ Professional (uses business terminology)                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Business Rules Categories

### 1. Composite Key Rules

```
┌─────────────────────────────────────────┐
│ COMPOSITE KEY RULES                     │
├─────────────────────────────────────────┤
│ Unique Record = LOCID + GSCEQUIPCAT +   │
│                 PRDID                   │
│                                         │
│ Example:                                │
│ CYS20_F01C01 + UPS + ACC = unique       │
│                                         │
│ WHY: ChatGPT needs to understand how    │
│ records are uniquely identified         │
│                                         │
│ IMPACT: ChatGPT can group and analyze   │
│ records correctly                       │
└─────────────────────────────────────────┘
```

### 2. Design Change Detection Rules

```
┌─────────────────────────────────────────┐
│ DESIGN CHANGE DETECTION RULES           │
├─────────────────────────────────────────┤
│ Design Change = TRUE if:                │
│ - ZCOIBODVER changed OR                 │
│ - ZCOIFORMFACT changed                  │
│                                         │
│ EXCLUDE if:                             │
│ - Is_New Demand = TRUE                  │
│ - Is_cancelled = TRUE                   │
│                                         │
│ WHY: ChatGPT needs to know what         │
│ constitutes a design change             │
│                                         │
│ IMPACT: ChatGPT can identify and        │
│ explain design changes correctly        │
└─────────────────────────────────────────┘
```

### 3. Forecast Trend Analysis Rules

```
┌─────────────────────────────────────────┐
│ FORECAST TREND ANALYSIS RULES           │
├─────────────────────────────────────────┤
│ Trend = GSCFSCTQTY - GSCPREVFCSTQTY     │
│                                         │
│ Positive → Forecast increased           │
│ Negative → Forecast decreased           │
│ Zero → Forecast stable                  │
│                                         │
│ WHY: ChatGPT needs to understand        │
│ forecast calculations                   │
│                                         │
│ IMPACT: ChatGPT can explain forecast    │
│ changes and business impact             │
└─────────────────────────────────────────┘
```

### 4. Supplier Analysis Rules

```
┌─────────────────────────────────────────┐
│ SUPPLIER ANALYSIS RULES                 │
├─────────────────────────────────────────┤
│ Group records by LOCFR (Supplier)       │
│                                         │
│ Risk indicators:                        │
│ - GSCSUPLDATE changes                   │
│ - Is_SupplierDateMissing = TRUE         │
│ - Multiple design changes               │
│ - Multiple forecast changes             │
│                                         │
│ WHY: ChatGPT needs to understand        │
│ supplier grouping and risk              │
│                                         │
│ IMPACT: ChatGPT can identify supplier   │
│ issues and risks                        │
└─────────────────────────────────────────┘
```

### 5. ROJ Schedule Analysis Rules

```
┌─────────────────────────────────────────┐
│ ROJ SCHEDULE ANALYSIS RULES             │
├─────────────────────────────────────────┤
│ NBD_DeltaDays = days between:           │
│ GSCCONROJDATE - GSCPREVROJNBD           │
│                                         │
│ Positive → Schedule delayed             │
│ Negative → Schedule accelerated         │
│ Zero → Schedule unchanged               │
│                                         │
│ WHY: ChatGPT needs to understand        │
│ schedule changes                        │
│                                         │
│ IMPACT: ChatGPT can explain schedule    │
│ impacts on supply chain                 │
└─────────────────────────────────────────┘
```

### 6. Exclusion Rules

```
┌─────────────────────────────────────────┐
│ EXCLUSION RULES                         │
├─────────────────────────────────────────┤
│ EXCLUDE if:                             │
│ - Is_New Demand = TRUE                  │
│ - Is_cancelled = TRUE                   │
│                                         │
│ Reason: New demands and cancellations   │
│ are not considered 'changes' to         │
│ existing plans                          │
│                                         │
│ WHY: ChatGPT needs to know what NOT     │
│ to count as changes                     │
│                                         │
│ IMPACT: ChatGPT avoids false positives  │
│ in change detection                     │
└─────────────────────────────────────────┘
```

---

## Field Definitions Example

```
┌─────────────────────────────────────────────────────────────┐
│ FIELD DEFINITION EXAMPLE                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ZCOIBODVER (BOD Version)                                    │
│ ├── Name: BOD Version                                       │
│ ├── Description: Bill of Design (BOD) version number        │
│ ├── Type: string                                            │
│ ├── Example: "1.0"                                          │
│ └── Business Context:                                       │
│     "Tracks design version. Change indicates design         │
│      modification. Used to detect design changes."          │
│                                                              │
│ WHY: ChatGPT needs to understand what each field means      │
│                                                              │
│ IMPACT: ChatGPT can explain field meanings and their        │
│ business context                                            │
│                                                              │
│ × 30 more fields with same structure                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Response Guidelines Example

```
┌─────────────────────────────────────────────────────────────┐
│ RESPONSE GUIDELINES                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ STRUCTURE:                                                  │
│ 1. Greeting (optional): "Hi! Here's what I found..."        │
│ 2. Direct Answer: Answer the question                       │
│ 3. Key Metrics: Specific numbers and percentages            │
│ 4. Explanation: WHY changes happened                        │
│ 5. Business Impact: What it means for business              │
│ 6. Suggested Actions: What to do about it                   │
│                                                              │
│ TONE:                                                       │
│ - Quick queries: Concise and direct                         │
│ - Analysis queries: Detailed and explanatory                │
│ - Always: Conversational, not robotic                       │
│                                                              │
│ CONSTRAINTS:                                                │
│ - NEVER compute values - use provided metrics               │
│ - NEVER hallucinate data or logic                           │
│ - ALWAYS use MCP context and blob data                      │
│ - ALWAYS respect SAP field definitions                      │
│                                                              │
│ WHY: ChatGPT needs to know how to structure responses       │
│                                                              │
│ IMPACT: ChatGPT generates professional, actionable insights  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Without vs With Business Rules

### Without Business Rules

```
User: "What are the top risks?"

ChatGPT Response (Generic):
"Risk level is CRITICAL. Highest risk type: Design + Supplier 
Change Risk. 3,208 high-risk records out of 13,148 total (24.4%)."

Problems:
❌ No business context
❌ No explanation of WHY
❌ No actionable insights
❌ Sounds robotic
❌ Doesn't explain what the combination means
```

### With Business Rules

```
User: "What are the top risks?"

ChatGPT Response (Intelligent):
"We're seeing CRITICAL risk levels affecting 24.4% of your records 
(3,208 out of 13,148). The primary concern is Design + Supplier 
Change Risk - materials experiencing both design modifications AND 
supplier transitions simultaneously.

This combination creates supply chain complexity because:
1. Design changes require engineering review and may impact supplier 
   capacity
2. Supplier transitions introduce new relationships and potential delays
3. Combined, they create uncertainty in delivery timelines

I recommend prioritizing these 1,500 records for supplier coordination 
and engineering review to mitigate delivery risks."

Strengths:
✅ Uses business rules (understands design + supplier impact)
✅ Explains WHY (business context, not just numbers)
✅ Provides context (why combination is risky)
✅ Actionable (specific recommendations)
✅ Professional (uses business terminology)
```

---

## Summary

### How ChatGPT Gets Business Rules

1. **Backend loads** business rules from `business_rules.py`
2. **Business rules are formatted** into system prompt
3. **System prompt is sent to ChatGPT** before user question
4. **ChatGPT reads system prompt** and understands business rules
5. **ChatGPT applies business rules** to interpret data
6. **ChatGPT generates intelligent responses** with business context

### Business Rules Included

- ✅ Composite key rules
- ✅ Design change detection
- ✅ Forecast trend analysis
- ✅ Supplier analysis
- ✅ ROJ schedule analysis
- ✅ Exclusion rules
- ✅ 30+ field definitions
- ✅ Response guidelines

### Result

ChatGPT generates professional, business-aware, actionable insights instead of generic data summaries.

---

**Status**: ✅ COMPLETE
**Business Rules**: 8 categories
**Field Definitions**: 30+ fields
**System Prompt Size**: ~2,500 tokens
**Result**: Strong, intelligent insights
