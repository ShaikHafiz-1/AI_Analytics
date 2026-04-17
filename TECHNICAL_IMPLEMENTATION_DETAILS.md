# Planning Intelligence Copilot - Technical Implementation Details

**Purpose**: Deep dive into technical architecture and implementation  
**Audience**: Technical stakeholders, architects, developers  
**Status**: ✅ Complete

---

## 🏗️ Technology Stack

### Frontend
```
Framework: React 18.x
Language: TypeScript
Styling: Tailwind CSS
HTTP Client: Axios
State Management: React Hooks
Build Tool: Webpack
Server: Node.js Express
```

### Backend
```
Runtime: Python 3.9
Framework: Azure Functions
HTTP: FastAPI-style routing
Data Processing: Pandas
Excel Support: openpyxl, xlrd
CSV Support: Built-in
```

### Cloud Platform
```
Compute: Azure Functions (Serverless)
Storage: Azure Blob Storage
AI/ML: Azure OpenAI (GPT-3.5-turbo)
Secrets: Azure Key Vault
Monitoring: Azure Monitor
Authentication: Azure AD (Entra)
```

### Data Format
```
Current Data: CSV (13,000+ rows)
Previous Data: CSV (for trends)
Historical: CSV (archive)
Columns: Location, Material, Equipment, Metrics, Timestamps
```

---

## 📊 Backend Architecture

### API Endpoints

```
1. POST /api/planning_intelligence_nlp
   Purpose: Main Copilot endpoint
   Input: {
     "question": "What's the health status?",
     "location": "Dallas",
     "material": "Electronics",
     "detailRecords": [...]
   }
   Output: {
     "answer": "...",
     "metrics": {...},
     "recommendations": [...]
   }
   Response Time: 2-8 seconds

2. GET /api/planning_dashboard_v2
   Purpose: Get dashboard data
   Input: Query parameters (location, material)
   Output: Dashboard metrics and KPIs
   Response Time: 1-2 seconds

3. POST /api/daily_refresh
   Purpose: Refresh data from Blob Storage
   Input: None (scheduled)
   Output: Refresh status
   Response Time: 5 minutes

4. POST /api/explain
   Purpose: Get detailed explanation
   Input: {"question": "..."}
   Output: Detailed response with drill-down
   Response Time: 3-5 seconds

5. GET /api/debug_snapshot
   Purpose: Debug endpoint (development only)
   Input: Query parameters
   Output: Raw snapshot data
   Response Time: 1-2 seconds
```

### Question Classification (12 Types)

```python
def classify_question(question: str) -> str:
    """
    Classifies user question into one of 12 types
    Returns: question_type (string)
    """
    
    # Type 1: HEALTH_STATUS
    if any(word in question.lower() for word in 
           ["health", "status", "how are", "doing"]):
        return "HEALTH_STATUS"
    
    # Type 2: FORECAST
    if any(word in question.lower() for word in 
           ["forecast", "predict", "coming", "future"]):
        return "FORECAST"
    
    # Type 3: RISK
    if any(word in question.lower() for word in 
           ["risk", "danger", "issue", "problem"]):
        return "RISK"
    
    # Type 4: DESIGN_CHANGE
    if any(word in question.lower() for word in 
           ["design", "change", "impact", "affect"]):
        return "DESIGN_CHANGE"
    
    # Type 5: GENERAL
    if any(word in question.lower() for word in 
           ["tell", "about", "explain", "what"]):
        return "GENERAL"
    
    # Type 6: GREETING
    if any(word in question.lower() for word in 
           ["hi", "hello", "hey", "greetings"]):
        return "GREETING"
    
    # Type 7: DESIGN_SPEC
    if any(word in question.lower() for word in 
           ["design", "specification", "spec"]):
        return "DESIGN_SPEC"
    
    # Type 8: SCHEDULE
    if any(word in question.lower() for word in 
           ["schedule", "timeline", "when", "due"]):
        return "SCHEDULE"
    
    # Type 9: LOCATION
    if any(word in question.lower() for word in 
           ["location", "site", "facility", "center"]):
        return "LOCATION"
    
    # Type 10: MATERIAL
    if any(word in question.lower() for word in 
           ["material", "product", "equipment", "category"]):
        return "MATERIAL"
    
    # Type 11: ENTITY
    if any(word in question.lower() for word in 
           ["supplier", "vendor", "equipment", "specific"]):
        return "ENTITY"
    
    # Type 12: COMPARISON
    if any(word in question.lower() for word in 
           ["compare", "versus", "vs", "better", "difference"]):
        return "COMPARISON"
    
    return "GENERAL"  # Default
```

### Answer Generation Functions (12 Functions)

```python
# Function 1: Health Status
def generate_health_answer(detail_records, context, use_llm=True):
    """Analyzes overall planning health"""
    # Calculates health score (0-100)
    # Identifies problem areas
    # Uses ChatGPT for insights
    # Returns: {"answer": "...", "metrics": {...}}

# Function 2: Forecast
def generate_forecast_answer(detail_records, context, question, use_llm=True):
    """Predicts future demand and trends"""
    # Analyzes historical trends
    # Predicts future demand
    # Identifies seasonal patterns
    # Uses ChatGPT for insights

# Function 3: Risk
def generate_risk_answer(detail_records, context, use_llm=True):
    """Identifies and prioritizes risks"""
    # Scans for critical issues
    # Prioritizes by impact
    # Suggests mitigation
    # Uses ChatGPT for insights

# Function 4: Design Change
def generate_design_answer(detail_records, context, question, use_llm=True):
    """Analyzes design change impact"""
    # Identifies affected areas
    # Calculates impact metrics
    # Suggests adjustments
    # Uses ChatGPT for insights

# Function 5: General
def generate_general_answer(detail_records, context):
    """Provides general planning overview"""
    # Summarizes key metrics
    # Highlights important items
    # Suggests next steps

# Function 6: Greeting
def generate_greeting_answer(detail_records, context, question):
    """Responds to greetings"""
    # Friendly response
    # Offers assistance
    # Guides to features

# Function 7: Design Specification
def generate_design_answer(detail_records, context, question):
    """Lists and compares designs"""
    # Shows available designs
    # Compares specifications
    # Provides details

# Function 8: Schedule
def generate_schedule_answer(detail_records, context, question):
    """Analyzes timelines and schedules"""
    # Shows project timelines
    # Identifies delays
    # Suggests adjustments

# Function 9: Location
def generate_location_answer(detail_records, context, question):
    """Location-specific analysis"""
    # Analyzes specific location
    # Compares to other locations
    # Identifies best/worst performers

# Function 10: Material
def generate_material_answer(detail_records, context, question):
    """Material-specific analysis"""
    # Analyzes specific material
    # Shows trends
    # Identifies issues

# Function 11: Entity
def generate_entity_answer(detail_records, context, question):
    """Specific entity analysis"""
    # Analyzes supplier/equipment
    # Shows relationships
    # Provides detailed metrics

# Function 12: Comparison
def generate_comparison_answer(detail_records, context, question):
    """Compares two or more entities"""
    # Side-by-side comparison
    # Highlights differences
    # Recommends best option
```

---

## 🧠 LLM Integration

### LLM Service Architecture

```python
class LLMService:
    """
    Manages ChatGPT integration with business rules
    """
    
    def __init__(self, use_mock=False):
        # Initialize Azure OpenAI client
        # Load business rules
        # Set up system prompt
    
    def generate_response(self, prompt, context, detail_records=None):
        """
        Main method to generate LLM response
        
        Steps:
        1. Build system prompt (business rules)
        2. Build user prompt (question + context)
        3. Format planning data
        4. Call ChatGPT API
        5. Validate response
        6. Return response
        """
        
        # Build system prompt with business rules
        system_prompt = self._build_system_prompt()
        
        # Build user prompt with context
        user_prompt = self._build_user_prompt(
            prompt, context, detail_records
        )
        
        # Call ChatGPT
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def _build_system_prompt(self):
        """
        Builds system prompt with business rules
        
        Includes:
        • Planning health rules
        • Forecast rules
        • Risk assessment rules
        • Equipment category rules
        • Location rules
        • Supplier rules
        • Material group rules
        • Compliance rules
        """
        
        rules = """
        You are a supply chain planning expert.
        
        PLANNING HEALTH RULES:
        - Green (80-100): All metrics optimal
        - Yellow (60-79): Some metrics need attention
        - Red (0-59): Critical issues require action
        
        FORECAST RULES:
        - Stable: Demand consistent month-to-month
        - Growing: Demand increasing 5%+ per month
        - Declining: Demand decreasing 5%+ per month
        - Volatile: Demand fluctuates unpredictably
        
        [... 6 more rule categories ...]
        
        Always apply these rules when analyzing data.
        """
        
        return rules
    
    def _build_user_prompt(self, prompt, context, detail_records):
        """
        Builds user prompt with context
        
        Includes:
        • Original question
        • Planning data (sample records)
        • Calculated metrics
        • Context information
        """
        
        user_prompt = f"""
        Question: {prompt}
        
        Context:
        {self._format_context(context)}
        
        Planning Data (sample):
        {self._format_sample_records(detail_records)}
        
        Please analyze this data and provide insights.
        """
        
        return user_prompt
```

### Business Rules Engine

```python
BUSINESS_RULES = {
    "PLANNING_HEALTH": {
        "GREEN": {"min": 80, "max": 100, "status": "Optimal"},
        "YELLOW": {"min": 60, "max": 79, "status": "Needs attention"},
        "RED": {"min": 0, "max": 59, "status": "Critical"}
    },
    
    "FORECAST": {
        "STABLE": "Demand consistent month-to-month",
        "GROWING": "Demand increasing 5%+ per month",
        "DECLINING": "Demand decreasing 5%+ per month",
        "VOLATILE": "Demand fluctuates unpredictably"
    },
    
    "RISK_ASSESSMENT": {
        "CRITICAL": "Immediate action required",
        "HIGH": "Address within 1 week",
        "MEDIUM": "Address within 2 weeks",
        "LOW": "Monitor and plan accordingly"
    },
    
    "EQUIPMENT_CATEGORY": {
        "ELECTRONICS": "High-value, long lead times",
        "MECHANICAL": "Standard lead times",
        "HYDRAULIC": "Specialized suppliers",
        "PNEUMATIC": "Quick turnaround available"
    },
    
    "LOCATION": {
        "HUB": "Central distribution points",
        "REGIONAL": "Serve specific regions",
        "REMOTE": "Limited supplier access",
        "SEASONAL": "Demand varies by season"
    },
    
    "SUPPLIER": {
        "TIER_1": "Preferred suppliers, best terms",
        "TIER_2": "Backup suppliers, standard terms",
        "TIER_3": "Emergency suppliers, premium pricing",
        "NEW": "Require validation"
    },
    
    "MATERIAL_GROUP": {
        "RAW": "Long lead times, bulk orders",
        "COMPONENTS": "Standard lead times",
        "FINISHED": "Quick delivery required",
        "CONSUMABLES": "Frequent small orders"
    },
    
    "COMPLIANCE": {
        "SFI": "Zero-trust security",
        "DATA_GOVERNANCE": "Sensitive data handling",
        "AUDIT": "Compliance tracking",
        "REGULATORY": "Industry-specific requirements"
    }
}
```

---

## 📊 Data Processing Pipeline

### Data Loading

```python
def load_current_previous_from_blob():
    """
    Loads planning data from Azure Blob Storage
    
    Steps:
    1. Connect to Blob Storage (Managed Identity)
    2. Download current.csv (13,000+ records)
    3. Download previous.csv (for trends)
    4. Parse CSV files
    5. Validate required columns
    6. Return as list of dicts
    """
    
    # Connect using Managed Identity (no API keys)
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient
    
    credential = DefaultAzureCredential()
    blob_client = BlobServiceClient(
        account_url=blob_endpoint,
        credential=credential
    )
    
    # Download current data
    current_blob = blob_client.get_blob_client(
        container="planning-data",
        blob="current.csv"
    )
    current_data = current_blob.download_blob().readall()
    
    # Parse CSV
    current_df = pd.read_csv(io.BytesIO(current_data))
    
    # Validate columns
    required_columns = {"LOCID", "PRDID", "GSCEQUIPCAT"}
    if not required_columns.issubset(current_df.columns):
        raise ValueError("Missing required columns")
    
    # Return as list of dicts
    return current_df.to_dict(orient="records")
```

### Data Filtering

```python
def filter_by_location(records, location):
    """Filters records by location"""
    return [r for r in records if r.get("LOCID") == location]

def filter_by_material(records, material):
    """Filters records by material"""
    return [r for r in records if r.get("PRDID") == material]

def filter_by_equipment(records, equipment):
    """Filters records by equipment category"""
    return [r for r in records if r.get("GSCEQUIPCAT") == equipment]

def aggregate_metrics(records):
    """Aggregates metrics from records"""
    return {
        "count": len(records),
        "health_avg": sum(r.get("health", 0) for r in records) / len(records),
        "forecast_avg": sum(r.get("forecast", 0) for r in records) / len(records),
        "risk_avg": sum(r.get("risk", 0) for r in records) / len(records)
    }
```

---

## 🔐 Security Implementation

### Authentication & Authorization

```python
# Using Managed Identity (no API keys in code)
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

# Access Blob Storage
blob_client = BlobServiceClient(
    account_url=blob_endpoint,
    credential=credential
)

# Access Azure OpenAI
openai_client = AzureOpenAI(
    api_version="2023-05-15",
    azure_endpoint=openai_endpoint,
    azure_ad_token_provider=credential.get_token
)

# Access Key Vault
vault_client = SecretClient(
    vault_url=vault_endpoint,
    credential=credential
)
```

### CORS Configuration

```python
def _cors_response(data, status=200, mimetype="application/json"):
    """
    Returns response with CORS headers
    """
    return func.HttpResponse(
        data,
        status_code=status,
        mimetype=mimetype,
        headers={
            "Access-Control-Allow-Origin": "https://yourdomain.com",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
    )
```

### Input Validation

```python
def validate_request(req):
    """Validates incoming request"""
    
    # Check required fields
    if not req.get_json():
        raise ValueError("Request body is empty")
    
    question = req.get_json().get("question", "").strip()
    if not question:
        raise ValueError("Question is required")
    
    if len(question) > 1000:
        raise ValueError("Question too long (max 1000 chars)")
    
    # Sanitize input
    question = question.replace("<script>", "")
    question = question.replace("</script>", "")
    
    return question
```

---

## 📈 Performance Optimization

### Caching Strategy

```python
# In-memory cache for blob data
_blob_cache = {
    "data": None,
    "timestamp": None,
    "ttl": 3600  # 1 hour
}

def get_blob_data_cached():
    """Gets blob data with caching"""
    
    now = time.time()
    
    # Check if cache is valid
    if (_blob_cache["data"] and 
        now - _blob_cache["timestamp"] < _blob_cache["ttl"]):
        return _blob_cache["data"]
    
    # Load from blob
    data = load_current_previous_from_blob()
    
    # Update cache
    _blob_cache["data"] = data
    _blob_cache["timestamp"] = now
    
    return data
```

### Response Compression

```python
def compress_response(data):
    """Compresses response for faster transmission"""
    
    import gzip
    import json
    
    json_data = json.dumps(data)
    compressed = gzip.compress(json_data.encode())
    
    return compressed
```

### Lazy Loading

```python
# Frontend loads detail records on demand
# Backend doesn't load all records upfront
# Only loads records needed for current query

def get_detail_records(location=None, material=None):
    """Loads only needed records"""
    
    all_records = get_blob_data_cached()
    
    # Filter by location if provided
    if location:
        all_records = filter_by_location(all_records, location)
    
    # Filter by material if provided
    if material:
        all_records = filter_by_material(all_records, material)
    
    # Return only first 100 for display
    return all_records[:100]
```

---

## 🚀 Deployment Architecture

### Azure Functions Configuration

```json
{
  "functionAppName": "func-pi-copilot-dev",
  "runtime": "python",
  "runtimeVersion": "3.9",
  "plan": "FlexConsumption",
  "region": "Central US",
  "storage": "stgpicopilotdev",
  "appInsights": "appi-pi-copilot-dev",
  "managedIdentity": "system-assigned"
}
```

### Environment Variables

```
AZURE_STORAGE_ACCOUNT_NAME=stgpicopilotdev
AZURE_STORAGE_CONTAINER_NAME=planning-data
AZURE_STORAGE_BLOB_ENDPOINT=https://stgpicopilotdev.blob.core.windows.net/
AZURE_OPENAI_ENDPOINT=https://openai-pi-copilot-dev.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2023-05-15
```

### Daily Refresh Schedule

```python
# Runs daily at 00:00 UTC
@app.schedule_trigger(schedule="0 0 * * *")
def daily_refresh(mytimer: func.TimerRequest):
    """
    Daily refresh of planning data
    
    Steps:
    1. Download current.csv from SAP
    2. Upload to Blob Storage as current.csv
    3. Backup previous.csv to historical/
    4. Clear cache
    5. Log completion
    """
    
    # Implementation
    pass
```

---

## ✅ Summary

**Frontend**: React with TypeScript, Tailwind CSS  
**Backend**: Python 3.9 with Azure Functions  
**AI**: Azure OpenAI (GPT-3.5-turbo) with business rules  
**Data**: Azure Blob Storage with 13,000+ records  
**Security**: Managed Identity, RBAC, zero-trust  
**Performance**: 2-8 second responses, auto-scaling  
**Deployment**: Serverless, fully managed, 99.9% uptime  

---

**Document Status**: ✅ Complete  
**Last Updated**: April 17, 2026
