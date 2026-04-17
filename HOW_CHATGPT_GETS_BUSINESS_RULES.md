# How ChatGPT Gets Business Rules to Interpret Data & Generate Strong Insights

## Your Question
**"How does ChatGPT get the business rules to interpret the data and have strong insights?"**

---

## The Answer (Simple Version)

```
1. Backend loads business rules from business_rules.py
   ↓
2. Business rules are injected into ChatGPT's SYSTEM PROMPT
   ↓
3. ChatGPT reads the system prompt before processing user question
   ↓
4. ChatGPT uses business rules to interpret the data
   ↓
5. ChatGPT generates intelligent, business-aware responses
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│                    BACKEND (explain endpoint)                     │
│                                                                   │
│  1. User asks: "What are the top risks?"                         │
│     ↓                                                              │
│  2. Backend receives question + context + detailRecords          │
│     ↓                                                              │
│  3. Backend calls LLMService.generate_response()                 │
│     ↓                                                              │
│  4. LLMService._build_system_prompt() is called                  │
│     ↓                                                              │
│  5. System prompt imports business rules:                        │
│     from business_rules import (                                 │
│       get_business_rules_context,                                │
│       get_field_definitions_context,                             │
│       get_response_guidelines_context                            │
│     )                                                             │
│     ↓                                                              │
│  6. Business rules are formatted into system prompt:             │
│     - Composite key rules                                        │
│     - Design change detection rules                              │
│     - Forecast trend analysis rules                              │
│     - Supplier analysis rules                                    │
│     - ROJ schedule analysis rules                                │
│     - Exclusion rules                                            │
│     - Field definitions (30+ fields)                             │
│     - Response guidelines                                        │
│     ↓                                                              │
│  7. System prompt sent to ChatGPT:                               │
│     {                                                             │
│       "role": "system",                                          │
│       "content": "You are a Planning Intelligence Copilot...     │
│                   BUSINESS RULES & DOMAIN KNOWLEDGE:             │
│                   1. COMPOSITE KEY...                            │
│                   2. DESIGN CHANGE DETECTION...                  │
│                   3. FORECAST TREND ANALYSIS...                  │
│                   ... (all business rules) ..."                  │
│     }                                                             │
│     ↓                                                              │
│  8. User message sent to ChatGPT:                                │
│     {                                                             │
│       "role": "user",                                            │
│       "content": "What are the top risks?                        │
│                   Context: 13,148 records, 24.4% high risk...   │
│                   Data: [record1, record2, ...]"                 │
│     }                                                             │
│     ↓                                                              │
│  9. ChatGPT processes:                                           │
│     - Reads system prompt (business rules)                       │
│     - Understands composite key structure                        │
│     - Understands design change detection                        │
│     - Understands forecast trends                                │
│     - Understands supplier analysis                              │
│     - Understands ROJ schedule analysis                          │
│     - Reads user message (question + data)                       │
│     - Applies business rules to data                             │
│     - Generates intelligent response                             │
│     ↓                                                              │
│  10. ChatGPT response:                                           │
│      "We're seeing CRITICAL risk levels affecting 24.4% of      │
│       your records (3,208 out of 13,148). The primary concern   │
│       is Design + Supplier Change Risk - materials experiencing  │
│       both design modifications AND supplier transitions          │
│       simultaneously. This combination creates supply chain      │
│       complexity. I recommend prioritizing these records for     │
│       supplier coordination and engineering review to mitigate   │
│       delivery risks."                                           │
│     ↓                                                              │
│  11. Response sent to frontend                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Business Rules Included in System Prompt

### 1. Composite Key Rules

```
COMPOSITE KEY (Unique Record Identifier):
- LOCID (Location ID) + GSCEQUIPCAT (Equipment Category) + PRDID (Material ID)
- Example: CYS20_F01C01 + UPS + ACC = unique record

WHY: ChatGPT needs to understand how records are uniquely identified
IMPACT: Helps ChatGPT group and analyze records correctly
```

### 2. Design Change Detection Rules

```
DESIGN CHANGE DETECTION:
- Design Change = TRUE if (ZCOIBODVER changed) OR (ZCOIFORMFACT changed)
- EXCLUDE: Is_New Demand = TRUE, Is_cancelled = TRUE
- Business Impact: Design changes require engineering review and may impact supplier capacity

WHY: ChatGPT needs to know what constitutes a design change
IMPACT: ChatGPT can identify and explain design changes correctly
```

### 3. Forecast Trend Analysis Rules

```
FORECAST TREND ANALYSIS:
- Formula: Trend = GSCFSCTQTY - GSCPREVFCSTQTY
- Positive → Forecast increased (higher procurement requirements)
- Negative → Forecast decreased (lower procurement requirements)
- Business Impact: Affects supplier capacity, inventory, and delivery timelines

WHY: ChatGPT needs to understand forecast calculations
IMPACT: ChatGPT can explain forecast changes and their business impact
```

### 4. Supplier Analysis Rules

```
SUPPLIER ANALYSIS:
- Group records by LOCFR (Supplier)
- Risk indicators: GSCSUPLDATE changes, Is_SupplierDateMissing, multiple design/forecast changes
- Business Impact: Supplier issues can disrupt supply chain

WHY: ChatGPT needs to understand supplier grouping and risk
IMPACT: ChatGPT can identify supplier issues and risks
```

### 5. ROJ Schedule Analysis Rules

```
ROJ / SCHEDULE ANALYSIS:
- NBD_DeltaDays = days between GSCCONROJDATE and GSCPREVROJNBD
- Positive → Schedule delayed (material needed later)
- Negative → Schedule accelerated (material needed sooner)
- Business Impact: Affects procurement timing and supplier coordination

WHY: ChatGPT needs to understand schedule changes
IMPACT: ChatGPT can explain schedule impacts on supply chain
```

### 6. Exclusion Rules

```
EXCLUSION RULES:
- EXCLUDE if Is_New Demand = TRUE (new demands are not changes)
- EXCLUDE if Is_cancelled = TRUE (cancellations are not changes)

WHY: ChatGPT needs to know what NOT to count as changes
IMPACT: ChatGPT avoids false positives in change detection
```

### 7. Field Definitions (30+ Fields)

```
Each field has:
- Name: Human-readable name
- Description: What the field means
- Type: Data type (string, number, date, boolean)
- Example: Sample value
- Business Context: Why it matters

Example:
ZCOIBODVER (BOD Version):
- Description: Bill of Design (BOD) version number
- Type: string
- Example: "1.0"
- Business Context: Tracks design version. Change indicates design modification.

WHY: ChatGPT needs to understand what each field means
IMPACT: ChatGPT can explain field meanings and their business context
```

### 8. Response Guidelines

```
RESPONSE GENERATION GUIDELINES:

Structure:
1. Greeting (optional): Natural greeting
2. Direct Answer: Answer the question
3. Key Metrics: Specific numbers and percentages
4. Explanation: WHY changes happened
5. Business Impact: What it means for business
6. Suggested Actions: What to do about it

Tone:
- Quick queries: Concise and direct
- Analysis queries: Detailed and explanatory
- Always: Conversational, not robotic

Constraints:
- NEVER compute values - use provided metrics
- NEVER hallucinate data or logic
- ALWAYS use MCP context and blob data
- ALWAYS respect SAP field definitions

WHY: ChatGPT needs to know how to structure responses
IMPACT: ChatGPT generates professional, actionable insights
```

---

## Code Implementation

### Step 1: Business Rules Defined

**File**: `planning_intelligence/business_rules.py`

```python
SAP_FIELD_DICTIONARY = {
    "LOCID": {
        "name": "Location ID",
        "description": "Unique identifier for a facility/location",
        "business_context": "Used to group records by physical location. Part of composite key."
    },
    "ZCOIBODVER": {
        "name": "BOD Version",
        "description": "Bill of Design (BOD) version number",
        "business_context": "Tracks design version. Change indicates design modification."
    },
    # ... 30+ more fields
}

BUSINESS_RULES = {
    "composite_key": {
        "description": "Unique record identifier",
        "fields": ["LOCID", "GSCEQUIPCAT", "PRDID"],
    },
    "design_change_detection": {
        "rule": "Design Change = TRUE if (ZCOIBODVER changed) OR (ZCOIFORMFACT changed)",
    },
    # ... more rules
}

def get_business_rules_context() -> str:
    """Generate business rules context for LLM system prompt."""
    # Returns formatted business rules as string
```

### Step 2: System Prompt Built with Business Rules

**File**: `planning_intelligence/llm_service.py`

```python
def _build_system_prompt(self, include_full_context: bool = True) -> str:
    """Build the system prompt for ChatGPT with business rules."""
    
    # Import business rules
    from business_rules import (
        get_business_rules_context,
        get_field_definitions_context,
        get_response_guidelines_context
    )
    
    # Get formatted business rules
    business_rules = get_business_rules_context()
    field_definitions = get_field_definitions_context()
    response_guidelines = get_response_guidelines_context()
    
    # Build system prompt with business rules
    return f"""You are a Planning Intelligence Copilot assistant for supply chain and planning analytics.

Your role is to provide clear, concise, business-focused insights about planning data.
You understand SAP schema, business rules, and supply chain domain knowledge.

{business_rules}

{field_definitions}

{response_guidelines}

CRITICAL REQUIREMENTS:
- Explain WHY changes happened (business context, not just numbers)
- Connect forecast, supplier, design, and schedule impacts
- Use natural, conversational tone (not robotic or templated)
- Never compute values - use provided metrics
- Never hallucinate data or logic
- Always use MCP context and blob data
- Always respect SAP field definitions and business rules
"""
```

### Step 3: System Prompt Sent to ChatGPT

**File**: `planning_intelligence/llm_service.py`

```python
def generate_response(self, prompt: str, context: Dict, detail_records: List[Dict] = None) -> str:
    """Generate response using ChatGPT with business rules."""
    
    # Build system prompt with business rules
    system_prompt = self._build_system_prompt(include_full_context=True)
    
    # Build user prompt with data
    user_prompt = self._build_user_prompt(prompt, context, detail_records)
    
    # Send to ChatGPT
    response = self.client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": system_prompt  # ← Business rules injected here
            },
            {
                "role": "user",
                "content": user_prompt  # ← User question + data
            }
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content
```

---

## Example: How Business Rules Generate Strong Insights

### User Question
```
"What are the top risks?"
```

### Data Provided
```
13,148 total records
3,208 high-risk records (24.4%)
Risk breakdown:
- Design + Supplier Change Risk: 1,500 records
- Forecast Change Risk: 1,200 records
- Schedule Change Risk: 508 records
```

### Without Business Rules (Generic Response)
```
"Risk level is CRITICAL. Highest risk type: Design + Supplier Change Risk. 
3,208 high-risk records out of 13,148 total (24.4%)."
```

### With Business Rules (Strong Insight)
```
"We're seeing CRITICAL risk levels affecting 24.4% of your records (3,208 out of 13,148). 

The primary concern is Design + Supplier Change Risk - materials experiencing both 
design modifications AND supplier transitions simultaneously. This combination creates 
supply chain complexity because:

1. Design changes require engineering review and may impact supplier capacity
2. Supplier transitions introduce new relationships and potential delays
3. Combined, they create uncertainty in delivery timelines

I recommend prioritizing these 1,500 records for supplier coordination and engineering 
review to mitigate delivery risks. Specifically:
- Reach out to affected suppliers to confirm they can accommodate design changes
- Coordinate engineering reviews to ensure supplier capacity
- Establish clear delivery timelines for the transition period"
```

### Why the Second Response is Better

✅ **Uses business rules**: Understands design change detection and supplier analysis
✅ **Explains WHY**: Connects business impact to data
✅ **Provides context**: Explains what the combination means
✅ **Actionable**: Gives specific recommendations
✅ **Professional**: Uses business terminology correctly

---

## Business Rules Content

### What's Included

```
1. Composite Key Rules (How records are uniquely identified)
2. Design Change Detection (How to identify design changes)
3. Forecast Trend Analysis (How to calculate and interpret forecast changes)
4. Supplier Analysis (How to group and analyze suppliers)
5. ROJ Schedule Analysis (How to interpret schedule changes)
6. Exclusion Rules (What NOT to count as changes)
7. Field Definitions (30+ SAP fields with business context)
8. Response Guidelines (How to structure responses)
```

### Size

```
Business Rules: ~500 lines of Python
System Prompt: ~2,000 tokens (when formatted)
Field Definitions: ~30 fields × 5 properties = ~150 lines
Response Guidelines: ~50 lines
Total: ~2,500 tokens sent to ChatGPT
```

---

## How ChatGPT Uses Business Rules

### 1. Understanding the Data

ChatGPT reads the business rules and understands:
- What each field means
- How records are uniquely identified
- What constitutes a change
- What business impact each change has

### 2. Interpreting the Data

ChatGPT applies business rules to the data:
- Groups records by supplier (supplier analysis)
- Identifies design changes (design change detection)
- Calculates forecast trends (forecast trend analysis)
- Interprets schedule changes (ROJ schedule analysis)

### 3. Generating Insights

ChatGPT uses business rules to generate insights:
- Explains WHY changes happened
- Connects forecast, supplier, design, and schedule impacts
- Provides business context
- Recommends actions

### 4. Ensuring Quality

ChatGPT follows business rules to ensure quality:
- Never computes values (uses provided metrics)
- Never halluccinates data (uses provided data)
- Always respects field definitions
- Always uses business context

---

## Example Business Rules in Action

### Rule: Design Change Detection

```
Rule: Design Change = TRUE if (ZCOIBODVER changed) OR (ZCOIFORMFACT changed)
Exclusions: Is_New Demand = TRUE, Is_cancelled = TRUE

Data:
- Record 1: ZCOIBODVER changed from "1.0" to "2.0", Is_New Demand = FALSE
  → Design Change = TRUE ✅

- Record 2: ZCOIFORMFACT changed from "Standard" to "Compact", Is_cancelled = TRUE
  → Design Change = FALSE (excluded because Is_cancelled = TRUE) ✅

- Record 3: ZCOIBODVER unchanged, ZCOIFORMFACT unchanged, Is_New Demand = TRUE
  → Design Change = FALSE (excluded because Is_New Demand = TRUE) ✅

ChatGPT Response:
"We've detected 1 design change (Record 1). The BOD version was updated from 1.0 to 2.0, 
which indicates a design modification. This requires engineering review and may impact 
supplier capacity. I recommend coordinating with the supplier to confirm they can 
accommodate the design change."
```

### Rule: Forecast Trend Analysis

```
Rule: Trend = GSCFSCTQTY - GSCPREVFCSTQTY

Data:
- Record 1: Current Forecast = 1,000, Previous Forecast = 800
  → Trend = +200 (Forecast increased)

- Record 2: Current Forecast = 500, Previous Forecast = 600
  → Trend = -100 (Forecast decreased)

ChatGPT Response:
"Forecast demand has increased by 200 units (from 800 to 1,000) for Record 1, 
indicating higher procurement requirements. This may impact supplier capacity and 
delivery timelines. For Record 2, forecast demand decreased by 100 units, reducing 
procurement requirements. I recommend coordinating with suppliers to adjust production 
plans accordingly."
```

---

## Summary

### How ChatGPT Gets Business Rules

1. **Backend loads business rules** from `business_rules.py`
2. **Business rules are formatted** into system prompt
3. **System prompt is sent to ChatGPT** before user question
4. **ChatGPT reads system prompt** and understands business rules
5. **ChatGPT applies business rules** to interpret data
6. **ChatGPT generates intelligent responses** with business context

### Why This Creates Strong Insights

✅ ChatGPT understands the domain (supply chain planning)
✅ ChatGPT understands the data (SAP fields and business rules)
✅ ChatGPT understands the business impact (why changes matter)
✅ ChatGPT can explain WHY (not just WHAT)
✅ ChatGPT can recommend actions (not just report data)

### Business Rules Included

- Composite key rules
- Design change detection
- Forecast trend analysis
- Supplier analysis
- ROJ schedule analysis
- Exclusion rules
- 30+ field definitions
- Response guidelines

### Result

ChatGPT generates professional, business-aware, actionable insights instead of generic data summaries.

---

**Status**: ✅ COMPLETE
**Business Rules**: 8 categories
**Field Definitions**: 30+ fields
**System Prompt Size**: ~2,500 tokens
**Result**: Strong, intelligent insights
