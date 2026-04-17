"""
Business Rules and Domain Knowledge for Planning Intelligence Copilot.

Defines all business logic, field meanings, and rules that ChatGPT must understand
to provide accurate, domain-aware responses.

SAP CODES REFERENCE:
All SAP field codes used in the planning data are mapped to business meanings.
See SAP_FIELD_DICTIONARY below for complete reference.
"""

# SAP Field Dictionary with full business context and actual SAP codes
SAP_FIELD_DICTIONARY = {
    # LOCATION & FACILITY FIELDS
    "LOCID": {
        "name": "Location ID",
        "description": "Unique identifier for a facility/location",
        "type": "string",
        "example": "CYS20_F01C01",
        "business_context": "Used to group records by physical location. Part of composite key."
    },
    "ZCOICIDZ": {
        "name": "Facility/DC/Site Name",
        "description": "Name or identifier of the facility/data center",
        "type": "string",
        "example": "Dallas DC",
        "business_context": "Identifies the physical facility location"
    },
    "ZCOIMETROIDZ": {
        "name": "Planning Metro",
        "description": "Metropolitan area identifier",
        "type": "string",
        "example": "NYC",
        "business_context": "Groups locations by metropolitan region"
    },
    "ZCOICOUNTRY": {
        "name": "Country",
        "description": "Country code",
        "type": "string",
        "example": "US",
        "business_context": "Identifies country for location"
    },
    "ROC": {
        "name": "ROC Region",
        "description": "Regional Operations Center identifier",
        "type": "string",
        "example": "AMER",
        "business_context": "Groups locations by regional operations center"
    },
    
    # SUPPLIER FIELDS
    "LOCFR": {
        "name": "Supplier",
        "description": "Supplier code/identifier for this location",
        "type": "string",
        "example": "10_AMER",
        "business_context": "Identifies the supplier responsible for this location. Used in supplier analysis."
    },
    "LOCFRDESCR": {
        "name": "Supplier Description",
        "description": "Description or name of the supplier",
        "type": "string",
        "example": "Supplier A",
        "business_context": "Human-readable supplier name"
    },
    "GSCSUPLDATE": {
        "name": "Supplier Date",
        "description": "Date associated with supplier information",
        "type": "date",
        "example": "2026-04-14",
        "business_context": "Tracks supplier data freshness. Used to detect supplier issues."
    },
    "GSCPREVSUPLDATE": {
        "name": "Previous Supplier Date",
        "description": "Previous date associated with supplier information",
        "type": "date",
        "example": "2026-04-10",
        "business_context": "Previous supplier data date for comparison"
    },
    "GSCSCPSUPCMT": {
        "name": "SCP Supplier Comment",
        "description": "Supplier comment from SCP system",
        "type": "string",
        "example": "On track",
        "business_context": "Supplier feedback and status comments"
    },
    
    # MATERIAL & PRODUCT FIELDS
    "PRDID": {
        "name": "Material ID",
        "description": "Unique identifier for a material/product",
        "type": "string",
        "example": "ACC",
        "business_context": "Identifies the specific material. Part of composite key. Used for material impact analysis."
    },
    "GSCEQUIPCAT": {
        "name": "Equipment Category",
        "description": "Category/type of equipment for this material",
        "type": "string",
        "example": "UPS",
        "business_context": "Classifies materials by equipment type. Part of composite key. Used for category-based analysis."
    },
    
    # DESIGN CHANGE FIELDS
    "ZCOIBODVERZ": {
        "name": "BOD Version",
        "description": "Bill of Design (BOD) version number",
        "type": "string",
        "example": "1.0",
        "business_context": "Tracks design version. Change indicates design modification. Used to detect design changes."
    },
    "ZCOIFORMFACTZ": {
        "name": "Form Factor",
        "description": "Physical form factor/shape of the material",
        "type": "string",
        "example": "Standard",
        "business_context": "Describes physical characteristics. Change indicates design modification. Used to detect design changes."
    },
    "GSCSCPBODVERSIONZ": {
        "name": "SCP BOD Version",
        "description": "BOD version in SCP system",
        "type": "string",
        "example": "1.0",
        "business_context": "SCP system BOD version for comparison"
    },
    "GSCSCPFORMFACTORZ": {
        "name": "SCP Form Factor",
        "description": "Form factor in SCP system",
        "type": "string",
        "example": "Standard",
        "business_context": "SCP system form factor for comparison"
    },
    
    # FORECAST & QUANTITY FIELDS
    "GSCFSCTQTY": {
        "name": "Current Forecast Quantity",
        "description": "Current forecasted quantity for this material",
        "type": "number",
        "example": 1000,
        "business_context": "Latest forecast demand. Used to calculate forecast trends and deltas."
    },
    "GSCPREVFCSTQTY": {
        "name": "Previous Forecast Quantity",
        "description": "Previous forecasted quantity for this material",
        "type": "number",
        "example": 800,
        "business_context": "Previous forecast demand. Used to calculate forecast trends and deltas."
    },
    "FCST_Delta Qty": {
        "name": "Forecast Delta Quantity",
        "description": "Change in forecast quantity (current - previous)",
        "type": "number",
        "example": 200,
        "business_context": "Indicates forecast change magnitude"
    },
    "GSCFCSTTOSCPZ": {
        "name": "Send Forecast to SCP",
        "description": "Flag indicating if forecast should be sent to SCP",
        "type": "boolean",
        "example": True,
        "business_context": "Controls forecast distribution to SCP system"
    },
    "GSCFCSTAPPROVALSCP": {
        "name": "Forecast Approval",
        "description": "Approval status of forecast",
        "type": "string",
        "example": "APPROVED",
        "business_context": "Indicates if forecast has been approved"
    },
    
    # SCHEDULE & ROJ (REQUIRED ON-HAND) FIELDS
    "GSCCONROJDATE": {
        "name": "Current ROJ Date",
        "description": "Current Required On-hand date (ROJ) - when material is needed",
        "type": "date",
        "example": "2026-05-15",
        "business_context": "Target delivery date. Used for schedule analysis and ROJ trending."
    },
    "GSCPREVROJNBD": {
        "name": "Previous ROJ Date",
        "description": "Previous Required On-hand date (ROJ)",
        "type": "date",
        "example": "2026-05-10",
        "business_context": "Previous target delivery date. Used to calculate ROJ shifts."
    },
    "NBD_DeltaDays": {
        "name": "ROJ Shift (Days)",
        "description": "Number of days the ROJ has shifted (positive = delayed, negative = accelerated)",
        "type": "number",
        "example": 5,
        "business_context": "Indicates schedule changes. Positive = delay, Negative = acceleration. Critical for supply chain planning."
    },
    "GSCROJDATEREASONCODEZ": {
        "name": "ROJ Date Reason Code",
        "description": "Reason code for ROJ change",
        "type": "string",
        "example": "DEMAND_CHANGE",
        "business_context": "Explains why ROJ date changed"
    },
    "GSCROJNBDLASTCHANGEDDATE": {
        "name": "ROJ Last Changed Date",
        "description": "Date when ROJ was last modified",
        "type": "date",
        "example": "2026-04-09",
        "business_context": "Tracks ROJ modification history"
    },
    "GSCROJNBDCREATIONDATE": {
        "name": "ROJ Creation Date",
        "description": "Date when ROJ was created",
        "type": "date",
        "example": "2026-04-01",
        "business_context": "Tracks ROJ creation history"
    },
    "GSCSCPROJDATEZ": {
        "name": "SCP ROJ Date",
        "description": "ROJ date in SCP system",
        "type": "date",
        "example": "2026-05-15",
        "business_context": "SCP system ROJ for comparison"
    },
    "GSCSCPROJINDZ": {
        "name": "SCP ROJ Indicator",
        "description": "ROJ indicator in SCP system",
        "type": "string",
        "example": "Y",
        "business_context": "SCP system ROJ indicator"
    },
    "NBD_Change Type": {
        "name": "ROJ Change Type",
        "description": "Type of ROJ change (SHIFT, ACCELERATION, DELAY, etc.)",
        "type": "string",
        "example": "SHIFT",
        "business_context": "Categorizes the type of schedule change"
    },
    
    # APPROVAL & WORKFLOW FIELDS
    "GSCCMAPPROVALFIRSTDATEZ": {
        "name": "CM Approval First Date",
        "description": "First approval date from Configuration Management",
        "type": "date",
        "example": "2026-04-01",
        "business_context": "Tracks approval workflow"
    },
    "GSCCMAPPROVALLASTCHANGEDDATEZ": {
        "name": "CM Approval Last Changed Date",
        "description": "Last date CM approval was modified",
        "type": "date",
        "example": "2026-04-09",
        "business_context": "Tracks approval modification history"
    },
    "GSCCMAPPROVALLASTCHANGEDVALUEZ": {
        "name": "CM Approval Last Changed Value",
        "description": "Last approval value/status",
        "type": "string",
        "example": "APPROVED",
        "business_context": "Current approval status"
    },
    
    # PLANNING & EXCEPTION FIELDS
    "GSCPLANNINGEXCEPTIONZ": {
        "name": "Planning Exception",
        "description": "Planning exception code",
        "type": "string",
        "example": "NONE",
        "business_context": "Indicates planning issues or exceptions"
    },
    "GSCLLEPLANNING": {
        "name": "LLE Planning Needed",
        "description": "Flag indicating if Low-Level Engineering planning is needed",
        "type": "boolean",
        "example": False,
        "business_context": "Indicates need for detailed engineering planning"
    },
    "GSCCONSUMEINVFLG": {
        "name": "Consume Inventory Flag",
        "description": "Flag indicating if inventory should be consumed",
        "type": "boolean",
        "example": True,
        "business_context": "Controls inventory consumption logic"
    },
    
    # DATA QUALITY & TRACKING FIELDS
    "Is_SupplierDateMissing": {
        "name": "Supplier Date Missing",
        "description": "Flag indicating if supplier date is missing",
        "type": "boolean",
        "example": False,
        "business_context": "Indicates data quality issue with supplier information. Risk indicator."
    },
    "TINVALID": {
        "name": "Invalid Flag",
        "description": "Flag indicating if record is invalid",
        "type": "boolean",
        "example": False,
        "business_context": "Marks invalid or corrupted records"
    },
    "LASTMODIFIEDBY": {
        "name": "Last Modified By",
        "description": "User who last modified the record",
        "type": "string",
        "example": "USER001",
        "business_context": "Tracks record modification history"
    },
    "LASTMODIFIEDDATE": {
        "name": "Last Modified Date",
        "description": "Date when record was last modified",
        "type": "date",
        "example": "2026-04-09",
        "business_context": "Tracks record modification date"
    },
    "CREATEDBY": {
        "name": "Created By",
        "description": "User who created the record",
        "type": "string",
        "example": "USER001",
        "business_context": "Tracks record creation history"
    },
    "CREATEDDATE": {
        "name": "Created Date",
        "description": "Date when record was created",
        "type": "date",
        "example": "2026-04-01",
        "business_context": "Tracks record creation date"
    },
    "#Version": {
        "name": "Version",
        "description": "Record version number",
        "type": "number",
        "example": 1,
        "business_context": "Tracks record version history"
    },
    
    # DEMAND STATUS FIELDS
    "Is_New Demand": {
        "name": "New Demand",
        "description": "Flag indicating if this is a new demand",
        "type": "boolean",
        "example": False,
        "business_context": "EXCLUDE from change analysis. New demands are not considered changes."
    },
    "Is_cancelled": {
        "name": "Cancelled Demand",
        "description": "Flag indicating if this demand has been cancelled",
        "type": "boolean",
        "example": False,
        "business_context": "EXCLUDE from change analysis. Cancelled demands are not considered changes."
    },
    
    # CHANGE TRACKING FIELDS
    "Qty Changed Flag": {
        "name": "Quantity Changed",
        "description": "Flag indicating if forecast quantity has changed",
        "type": "boolean",
        "example": True,
        "business_context": "TRUE if GSCFSCTQTY != GSCPREVFCSTQTY. Used for forecast trend analysis."
    },
    "Design Changed Flag": {
        "name": "Design Changed",
        "description": "Flag indicating if design has changed",
        "type": "boolean",
        "example": True,
        "business_context": "TRUE if ZCOIBODVERZ or ZCOIFORMFACTZ changed. Used for design change analysis."
    },
    "ROJ Changed Flag": {
        "name": "ROJ Changed",
        "description": "Flag indicating if ROJ has changed",
        "type": "boolean",
        "example": True,
        "business_context": "TRUE if GSCCONROJDATE != GSCPREVROJNBD. Used for schedule change analysis."
    },
    "Supplier Changed Flag": {
        "name": "Supplier Changed",
        "description": "Flag indicating if supplier has changed",
        "type": "boolean",
        "example": False,
        "business_context": "Indicates supplier transition. Used for supplier change analysis."
    },
    "Risk_Flag": {
        "name": "Risk Flag",
        "description": "Flag indicating if record has risk",
        "type": "boolean",
        "example": True,
        "business_context": "Indicates records with supply chain risk"
    },
}
        "name": "Form Factor",
        "description": "Physical form factor/shape of the material",
        "type": "string",
        "example": "Standard",
        "business_context": "Describes physical characteristics. Change indicates design modification. Used to detect design changes."
    },
    
    # Forecast & Quantity
    "GSCFSCTQTY": {
        "name": "Current Forecast Quantity",
        "description": "Current forecasted quantity for this material",
        "type": "number",
        "example": 1000,
        "business_context": "Latest forecast demand. Used to calculate forecast trends and deltas."
    },
    "GSCPREVFCSTQTY": {
        "name": "Previous Forecast Quantity",
        "description": "Previous forecasted quantity for this material",
        "type": "number",
        "example": 800,
        "business_context": "Previous forecast demand. Used to calculate forecast trends and deltas."
    },
    
    # Schedule & ROJ
    "GSCCONROJDATE": {
        "name": "Current ROJ Date",
        "description": "Current Required On-hand date (ROJ) - when material is needed",
        "type": "date",
        "example": "2026-05-15",
        "business_context": "Target delivery date. Used for schedule analysis and ROJ trending."
    },
    "GSCPREVROJNBD": {
        "name": "Previous ROJ Date",
        "description": "Previous Required On-hand date (ROJ)",
        "type": "date",
        "example": "2026-05-10",
        "business_context": "Previous target delivery date. Used to calculate ROJ shifts."
    },
    "NBD_DeltaDays": {
        "name": "ROJ Shift (Days)",
        "description": "Number of days the ROJ has shifted (positive = delayed, negative = accelerated)",
        "type": "number",
        "example": 5,
        "business_context": "Indicates schedule changes. Positive = delay, Negative = acceleration. Critical for supply chain planning."
    },
    
    # Supplier Changes
    "GSCSUPLDATE": {
        "name": "Supplier Date",
        "description": "Date associated with supplier information",
        "type": "date",
        "example": "2026-04-14",
        "business_context": "Tracks supplier data freshness. Used to detect supplier issues."
    },
    "Is_SupplierDateMissing": {
        "name": "Supplier Date Missing",
        "description": "Flag indicating if supplier date is missing",
        "type": "boolean",
        "example": False,
        "business_context": "Indicates data quality issue with supplier information. Risk indicator."
    },
    
    # Demand Status
    "Is_New Demand": {
        "name": "New Demand",
        "description": "Flag indicating if this is a new demand",
        "type": "boolean",
        "example": False,
        "business_context": "EXCLUDE from change analysis. New demands are not considered changes."
    },
    "Is_cancelled": {
        "name": "Cancelled Demand",
        "description": "Flag indicating if this demand has been cancelled",
        "type": "boolean",
        "example": False,
        "business_context": "EXCLUDE from change analysis. Cancelled demands are not considered changes."
    },
    
    # Change Tracking
    "changed": {
        "name": "Record Changed",
        "description": "Flag indicating if this record has changed from previous period",
        "type": "boolean",
        "example": True,
        "business_context": "Indicates any change in the record. Used for change detection."
    },
    "designChanged": {
        "name": "Design Changed",
        "description": "Flag indicating if design has changed",
        "type": "boolean",
        "example": True,
        "business_context": "TRUE if ZCOIBODVER or ZCOIFORMFACT changed. Used for design change analysis."
    },
    "supplierChanged": {
        "name": "Supplier Changed",
        "description": "Flag indicating if supplier has changed",
        "type": "boolean",
        "example": False,
        "business_context": "Indicates supplier transition. Used for supplier change analysis."
    },
    "qtyChanged": {
        "name": "Quantity Changed",
        "description": "Flag indicating if forecast quantity has changed",
        "type": "boolean",
        "example": True,
        "business_context": "TRUE if GSCFSCTQTY != GSCPREVFCSTQTY. Used for forecast trend analysis."
    },
}

# Business Rules
BUSINESS_RULES = {
    "composite_key": {
        "description": "Unique record identifier",
        "fields": ["LOCID", "GSCEQUIPCAT", "PRDID"],
        "example": "CYS20_F01C01 + UPS + ACC = unique record"
    },
    
    "design_change_detection": {
        "description": "How to identify design changes",
        "rule": "Design Change = TRUE if (ZCOIBODVER changed) OR (ZCOIFORMFACT changed)",
        "exclusions": [
            "Is_New Demand = TRUE (new demands don't count as changes)",
            "Is_cancelled = TRUE (cancelled demands don't count as changes)"
        ],
        "business_impact": "Design changes require engineering review and may impact supplier capacity"
    },
    
    "forecast_trend": {
        "description": "How to calculate forecast trends",
        "formula": "Trend = GSCFSCTQTY - GSCPREVFCSTQTY",
        "interpretation": {
            "positive": "Forecast increased - higher procurement requirements",
            "negative": "Forecast decreased - lower procurement requirements",
            "zero": "Forecast stable - no change in demand"
        },
        "business_impact": "Forecast changes impact supplier capacity, inventory, and delivery timelines"
    },
    
    "supplier_analysis": {
        "description": "How to analyze suppliers",
        "grouping": "Group records by LOCFR (Supplier)",
        "risk_indicators": [
            "GSCSUPLDATE changes (supplier date updates)",
            "Is_SupplierDateMissing = TRUE (data quality issue)",
            "Multiple design changes from same supplier",
            "Multiple forecast changes from same supplier"
        ],
        "business_impact": "Supplier issues can disrupt supply chain and delay deliveries"
    },
    
    "roj_schedule_analysis": {
        "description": "How to analyze ROJ (Required On-hand) dates",
        "calculation": "NBD_DeltaDays = days between GSCCONROJDATE and GSCPREVROJNBD",
        "interpretation": {
            "positive": "Schedule delayed - material needed later than planned",
            "negative": "Schedule accelerated - material needed sooner than planned",
            "zero": "Schedule unchanged"
        },
        "business_impact": "ROJ changes affect procurement timing and supplier coordination"
    },
    
    "exclusion_rules": {
        "description": "Records to exclude from change analysis",
        "rules": [
            "EXCLUDE if Is_New Demand = TRUE",
            "EXCLUDE if Is_cancelled = TRUE"
        ],
        "reason": "New demands and cancellations are not considered 'changes' to existing plans"
    }
}

# Response Generation Guidelines
RESPONSE_GUIDELINES = {
    "structure": {
        "greeting": "Optional natural greeting (e.g., 'Hi! Here's what I found...')",
        "direct_answer": "Direct answer to the user's question",
        "key_metrics": "Specific numbers and percentages",
        "explanation": "WHY the changes happened (business context)",
        "business_impact": "What this means for the business",
        "suggested_actions": "What should be done about it"
    },
    
    "tone": {
        "quick_queries": "Concise and direct",
        "analysis_queries": "Detailed and explanatory",
        "always": "Conversational, not robotic or templated"
    },
    
    "field_explanation": {
        "when_asked": "Explain field meaning and business context",
        "example_question": "What is ZCOIBODVER?",
        "example_answer": "ZCOIBODVER represents the BOD (Bill of Design) version. When this changes, it indicates a design modification to the material. Design changes require engineering review and may impact supplier capacity and delivery timelines."
    },
    
    "constraints": {
        "never_compute": "Never calculate values - use provided metrics",
        "never_hallucinate": "Never invent data or logic",
        "always_use_context": "Always use MCP context and blob data",
        "always_respect_schema": "Always respect SAP field definitions and business rules"
    }
}

# Example Responses (Before vs After)
EXAMPLE_RESPONSES = {
    "forecast_change": {
        "question": "What's the forecast?",
        "before": "Forecast analysis shows 1 records with quantity changes. Total forecast adjustments detected across...",
        "after": "Hi! I found that forecast demand has increased by 500 units (from 800 to 1,300). This indicates higher procurement requirements, which may impact supplier capacity and delivery timelines. I recommend coordinating with suppliers to confirm they can meet the increased demand by the ROJ date."
    },
    
    "design_change": {
        "question": "What design changes have been detected?",
        "before": "2 records have design changes (BOD or Form Factor). Affected suppliers: Supplier_A, Supplier_B.",
        "after": "We've detected 2 design changes across your materials. These involve updates to either the BOD (Bill of Design) version or Form Factor. Affected suppliers are Supplier_A and Supplier_B. Design changes require engineering review and may impact supplier capacity. I recommend reaching out to these suppliers to confirm they can accommodate the design modifications."
    },
    
    "supplier_analysis": {
        "question": "List suppliers for UPS at CYS20",
        "before": "Location CYS20_F01C01: 15 records. Suppliers: 10_AMER, 130_AMER, 1690_AMER, 210_AMER, 320_AMER.",
        "after": "At location CYS20 for UPS equipment, we're working with 5 suppliers: 10_AMER, 130_AMER, 1690_AMER, 210_AMER, and 320_AMER. These suppliers manage 15 materials across this location. I recommend reviewing supplier performance and capacity to ensure they can handle current and forecasted demand."
    },
    
    "risk_analysis": {
        "question": "What are the top risks?",
        "before": "Risk level is CRITICAL. Highest risk type: Design + Supplier Change Risk. 3,208 high-risk records out of 13,148 total (24.4%).",
        "after": "We're seeing CRITICAL risk levels affecting 24.4% of your records (3,208 out of 13,148). The primary concern is Design + Supplier Change Risk - materials experiencing both design modifications AND supplier transitions simultaneously. This combination creates supply chain complexity. I recommend prioritizing these records for supplier coordination and engineering review to mitigate delivery risks."
    }
}

def get_business_rules_context() -> str:
    """Generate business rules context for LLM system prompt."""
    context = """
BUSINESS RULES & DOMAIN KNOWLEDGE:

1. COMPOSITE KEY (Unique Record Identifier):
   - LOCID (Location ID) + GSCEQUIPCAT (Equipment Category) + PRDID (Material ID)
   - Example: CYS20_F01C01 + UPS + ACC = unique record

2. DESIGN CHANGE DETECTION:
   - Design Change = TRUE if (ZCOIBODVER changed) OR (ZCOIFORMFACT changed)
   - EXCLUDE: Is_New Demand = TRUE, Is_cancelled = TRUE
   - Business Impact: Design changes require engineering review and may impact supplier capacity

3. FORECAST TREND ANALYSIS:
   - Formula: Trend = GSCFSCTQTY - GSCPREVFCSTQTY
   - Positive → Forecast increased (higher procurement requirements)
   - Negative → Forecast decreased (lower procurement requirements)
   - Business Impact: Affects supplier capacity, inventory, and delivery timelines

4. SUPPLIER ANALYSIS:
   - Group records by LOCFR (Supplier)
   - Risk indicators: GSCSUPLDATE changes, Is_SupplierDateMissing, multiple design/forecast changes
   - Business Impact: Supplier issues can disrupt supply chain

5. ROJ / SCHEDULE ANALYSIS:
   - NBD_DeltaDays = days between GSCCONROJDATE and GSCPREVROJNBD
   - Positive → Schedule delayed (material needed later)
   - Negative → Schedule accelerated (material needed sooner)
   - Business Impact: Affects procurement timing and supplier coordination

6. EXCLUSION RULES:
   - EXCLUDE if Is_New Demand = TRUE (new demands are not changes)
   - EXCLUDE if Is_cancelled = TRUE (cancellations are not changes)

RESPONSE REQUIREMENTS:
- Explain WHY changes happened (business context)
- Connect forecast, supplier, design, and schedule impacts
- Use natural, conversational tone
- Never compute values - use provided metrics
- Never hallucinate data or logic
- Always respect SAP field definitions
"""
    return context

def get_field_definitions_context() -> str:
    """Generate field definitions context for LLM system prompt."""
    lines = ["SAP FIELD DEFINITIONS:\n"]
    
    for field_key, field_info in SAP_FIELD_DICTIONARY.items():
        lines.append(f"\n{field_key} ({field_info['name']}):")
        lines.append(f"  Description: {field_info['description']}")
        lines.append(f"  Type: {field_info['type']}")
        lines.append(f"  Example: {field_info['example']}")
        lines.append(f"  Business Context: {field_info['business_context']}")
    
    return "\n".join(lines)

def get_response_guidelines_context() -> str:
    """Generate response guidelines context for LLM system prompt."""
    return """
RESPONSE GENERATION GUIDELINES:

Structure:
1. Greeting (optional): Natural greeting like "Hi! Here's what I found..."
2. Direct Answer: Answer the user's question directly
3. Key Metrics: Provide specific numbers and percentages
4. Explanation: Explain WHY changes happened (business context)
5. Business Impact: What this means for the business
6. Suggested Actions: What should be done about it

Tone:
- Quick queries: Concise and direct
- Analysis queries: Detailed and explanatory
- Always: Conversational, not robotic or templated

Field Explanations:
- When user asks about a field, explain its meaning and business context
- Example: "What is ZCOIBODVER?" → "It represents the BOD (Bill of Design) version, used to detect design changes."

Constraints:
- NEVER compute values - use provided metrics
- NEVER hallucinate data or logic
- ALWAYS use MCP context and blob data
- ALWAYS respect SAP field definitions and business rules
"""
