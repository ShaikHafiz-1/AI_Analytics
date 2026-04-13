# LLM Schema Integration - ChatGPT Data Interpretation

## Overview

The LLM service now uses `get_field_dictionary()` from `sap_schema.py` to properly interpret and explain blob data fields to ChatGPT. This ensures accurate, contextual responses based on the actual SAP data schema.

---

## How It Works

### 1. Schema Loading

```python
from sap_schema import SAPSchema

SCHEMA = SAPSchema()
FIELD_DICT = SCHEMA.get_field_dictionary()
```

**Result**: Dictionary of 100+ SAP fields with:
- Field name (human-readable)
- Field type (string, number, boolean, date)
- Description (business meaning)
- Example values

### 2. System Prompt Enhancement

When ChatGPT is initialized, the system prompt includes schema information:

```
DATA SCHEMA REFERENCE:

Location & Facility:
  • Location ID: Unique identifier for location/facility
  • Supplier From: Source supplier identifier
  • Form Factor: Facility form factor
  • ... and 5 more fields

Material & Product:
  • Material ID: Unique product/material identifier
  • Equipment Category: Material group (UPS, PUMP, VALVE)
  • Component ID: Component identifier
  • ... and 2 more fields

Forecast & Quantity:
  • Previous Forecast Quantity: Forecast from previous cycle
  • Current Forecast Quantity: Current forecast quantity
  • ... and 3 more fields
```

This helps ChatGPT understand what each field means and provide accurate interpretations.

### 3. Context Formatting

When sending data to ChatGPT, fields are formatted with their schema information:

```python
def _format_context(self, context: Dict) -> str:
    """Format metrics context for ChatGPT using SAP schema."""
    lines = []
    for key, value in context.items():
        # Get field name from SAP schema
        field_info = FIELD_DICT.get(key, {})
        field_name = field_info.get("name", key.replace("_", " ").title())
        field_description = field_info.get("description", "")
        
        # Format the value
        if isinstance(value, (int, float)):
            formatted_value = f"{value:,}"  # Add commas for readability
        
        # Build line with field name and description
        if field_description:
            lines.append(f"- {field_name} ({key}): {formatted_value}\n  Description: {field_description}")
```

**Example Output:**
```
- Location ID (ZCOILLEPLANINDZCO): LOC001
  Description: Unique identifier for location/facility

- Current Forecast Quantity (GSCFSCTQTY): 1,000
  Description: Current forecast quantity

- BOD Version (ZCOIBODVERZ): 1.0
  Description: Bill of Distribution version
```

### 4. Record Interpretation

Individual blob records can be interpreted using the schema:

```python
def interpret_blob_record(self, record: Dict) -> str:
    """Interpret a blob record using SAP schema."""
    interpretations = []
    for field_key, field_value in record.items():
        field_info = FIELD_DICT.get(field_key, {})
        field_name = field_info.get("name", field_key)
        field_type = field_info.get("type", "unknown")
        
        # Format value based on type
        if field_type == "number":
            formatted_value = f"{field_value:,}"
        elif field_type == "boolean":
            formatted_value = "Yes" if field_value else "No"
        else:
            formatted_value = str(field_value)
        
        interpretations.append(f"{field_name}: {formatted_value}")
    
    return "\n".join(interpretations)
```

---

## Field Categories

The schema organizes fields into logical categories:

### Location & Facility
- Location ID
- Supplier From
- Supplier Description
- Form Factor
- BOD Version
- Metro ID
- Country

### Material & Product
- Material ID
- Equipment Category
- Component ID

### Forecast & Quantity
- Previous Forecast Quantity
- Current Forecast Quantity
- Quantity Delta
- Quantity Changed Flag

### Supplier
- Supplier ID
- Supplier Previous
- Supplier Changed Flag

### Schedule & ROJ
- ROJ Current (Release Order Date)
- ROJ Previous
- ROJ Delta
- ROJ Changed Flag

### Design & BOD
- BOD Current (Bill of Distribution)
- BOD Previous
- Design Changed Flag

### Other
- Changed Flag (overall)
- Data Mode
- Last Refreshed

---

## Usage Examples

### Example 1: Health Status Query

**User Question:** "What's the planning health?"

**Backend Processing:**
1. Classify question → "health"
2. Compute metrics from blob data
3. Format context using schema:
   ```
   - Planning Health: 65/100
     Description: Overall planning health score
   
   - Changed Records: 5
     Description: Number of records with changes
   
   - Total Records: 20
     Description: Total planning records
   ```
4. Send to ChatGPT with schema context
5. ChatGPT generates response:
   ```
   "Planning health is currently at 65/100 (Acceptable). 
    5 of 20 records (25%) have recent changes. 
    Primary drivers include 2 design changes, 2 supplier changes, 
    and 1 quantity adjustment. Recommend reviewing high-risk items."
   ```

### Example 2: Supplier Impact Query

**User Question:** "Which supplier has the most impact?"

**Backend Processing:**
1. Classify question → "impact"
2. Compute supplier metrics
3. Format context:
   ```
   - Top Suppliers: Supplier_A (3 records), Supplier_B (2 records)
     Description: Suppliers with most changes
   
   - Supplier Changes: 2
     Description: Number of supplier transitions
   
   - Affected Suppliers: 5
     Description: Total unique suppliers involved
   ```
4. ChatGPT interprets and responds:
   ```
   "Supplier_A has the most impact with 3 affected records. 
    2 supplier transitions detected. These represent significant 
    portions of your supply chain. Recommend supplier communication 
    and contingency planning."
   ```

### Example 3: Design Changes Query

**User Question:** "What design changes have been detected?"

**Backend Processing:**
1. Classify question → "design"
2. Compute design metrics
3. Format context:
   ```
   - Design Changes: 2
     Description: Number of BOD/Form Factor changes
   
   - Affected Materials: Material_X, Material_Y, Material_Z
     Description: Materials with design modifications
   
   - BOD Version: 1.0
     Description: Bill of Distribution version
   ```
4. ChatGPT responds:
   ```
   "2 records show design modifications (BOD or Form Factor changes). 
    Affected materials include Material_X and Material_Y. 
    These design changes may impact supplier capacity and 
    production schedules. Review with design and supply teams."
   ```

---

## Schema Methods Available

### LLMService Methods

```python
# Get field name from schema
field_name = llm_service.get_field_name("GSCFSCTQTY")
# Returns: "Current Forecast Quantity"

# Get field description
description = llm_service.get_field_description("GSCFSCTQTY")
# Returns: "Current forecast quantity"

# Interpret a blob record
record = {"PRDID": "MAT001", "GSCFSCTQTY": 1000}
interpretation = llm_service.interpret_blob_record(record)
# Returns formatted interpretation with field names and descriptions

# Check schema availability
has_schema = llm_service.has_schema()
# Returns: True if schema loaded successfully

# Get service status
status = llm_service.get_status()
# Returns: {
#   "available": True,
#   "model": "gpt-3.5-turbo",
#   "schema_available": True,
#   "api_key_set": True,
#   ...
# }
```

---

## Data Flow with Schema

```
User Question
    ↓
Backend Classify
    ↓
Compute Metrics from Blob Data
    ↓
Format Context Using Schema
    ├─ Get field names from FIELD_DICT
    ├─ Get field descriptions
    ├─ Format values based on field type
    └─ Build human-readable context
    ↓
Send to ChatGPT with Schema Info
    ├─ System prompt includes schema categories
    ├─ Context includes field descriptions
    └─ ChatGPT understands data meaning
    ↓
ChatGPT Generates Response
    ├─ Uses schema context for accuracy
    ├─ References field names correctly
    └─ Provides business-focused insights
    ↓
Return Response to Frontend
```

---

## Error Handling

### Schema Not Available

If `sap_schema.py` is not available:

```python
try:
    from sap_schema import SAPSchema
    SCHEMA = SAPSchema()
    FIELD_DICT = SCHEMA.get_field_dictionary()
except ImportError:
    logger.warning("SAP schema not available. Using basic field names.")
    FIELD_DICT = {}
```

**Fallback Behavior:**
- Field names are formatted as: `key.replace("_", " ").title()`
- No descriptions available
- System prompt doesn't include schema categories
- ChatGPT still works but with less context

### Missing Field in Schema

If a field is not in the schema:

```python
field_info = FIELD_DICT.get(key, {})
field_name = field_info.get("name", key.replace("_", " ").title())
# Falls back to formatted key name
```

---

## Testing Schema Integration

### Test 1: Schema Loading

```python
from llm_service import get_llm_service

llm = get_llm_service(use_mock=True)
status = llm.get_status()

assert status["schema_available"] == True
assert llm.has_schema() == True
```

### Test 2: Field Interpretation

```python
field_name = llm.get_field_name("GSCFSCTQTY")
assert field_name == "Current Forecast Quantity"

description = llm.get_field_description("GSCFSCTQTY")
assert "forecast" in description.lower()
```

### Test 3: Record Interpretation

```python
record = {
    "PRDID": "MAT001",
    "GSCFSCTQTY": 1000,
    "GSCPREVFCSTQTY": 900
}

interpretation = llm.interpret_blob_record(record)
assert "Material ID" in interpretation
assert "Current Forecast Quantity" in interpretation
assert "1,000" in interpretation  # Formatted with comma
```

### Test 4: Context Formatting

```python
context = {
    "GSCFSCTQTY": 1000,
    "GSCPREVFCSTQTY": 900,
    "planningHealth": 65
}

formatted = llm._format_context(context)
assert "Current Forecast Quantity" in formatted
assert "1,000" in formatted
assert "Description:" in formatted
```

---

## Benefits

✅ **Accurate Interpretation**: ChatGPT understands exact meaning of each field
✅ **Consistent Naming**: Uses official SAP field names and descriptions
✅ **Type-Aware Formatting**: Numbers formatted with commas, booleans as Yes/No
✅ **Business Context**: Descriptions help ChatGPT provide relevant insights
✅ **Fallback Support**: Works even if schema is unavailable
✅ **Extensible**: Easy to add new fields to schema

---

## Next Steps

1. **Deploy with API Key**: Add OpenAI API key to Azure Function App settings
2. **Monitor Responses**: Track ChatGPT response quality and accuracy
3. **Refine Schema**: Add more fields or descriptions as needed
4. **Optimize Prompts**: Adjust system prompt based on response patterns
5. **Add Caching**: Cache schema info to reduce processing time

---

## Configuration

**Environment Variables:**
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500
```

**Schema Location:**
```
planning_intelligence/sap_schema.py
```

**LLM Service Location:**
```
planning_intelligence/llm_service.py
```
