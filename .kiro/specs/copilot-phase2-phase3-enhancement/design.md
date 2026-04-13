# Phase 2 & 3 Enhancement - Design

**Status:** In Progress  
**Architecture:** 3-Phase Pipeline with Validation & Optimization

---

## PHASE 2: VALIDATION HARDENING DESIGN

### Data Mapping Layer

```python
# planning_intelligence/data_mapper.py

class DataMapper:
    """Maps SAP fields to internal representation."""
    
    # Field Mappings
    FORECAST_MAPPING = {
        'current': 'GSCFSCTQTY',
        'previous': 'GSCPREVFCSTQTY',
        'delta': 'FCST_Delta Qty'
    }
    
    ROJ_MAPPING = {
        'current': 'GSCCONROJDATE',
        'previous': 'GSCPREVROJNBDNBD',
        'delta': 'NBD_DeltaDays'
    }
    
    SUPPLIER_MAPPING = {
        'current': 'GSCSUPLDATE',
        'previous': 'GSCPREVSUPLDATE',
        'missing_flag': 'Is_SupplierDateMissing'
    }
    
    DESIGN_MAPPING = {
        'bod_version': 'ZCOIBODVER',
        'form_factor': 'ZCOIFORMFACT'
    }
    
    COMPOSITE_KEY = ['LOCID', 'GSCEQUIPCAT', 'PRDID']
    
    @staticmethod
    def map_record(current_row, previous_row):
        """Map SAP record to internal format."""
        return {
            'locationId': current_row.get('LOCID'),
            'materialGroup': current_row.get('GSCEQUIPCAT'),
            'materialId': current_row.get('PRDID'),
            
            # Forecast
            'forecastCurrent': current_row.get('GSCFSCTQTY'),
            'forecastPrevious': previous_row.get('GSCPREVFCSTQTY') if previous_row else None,
            'forecastDelta': DataMapper._compute_delta(
                current_row.get('GSCFSCTQTY'),
                previous_row.get('GSCPREVFCSTQTY') if previous_row else None
            ),
            
            # ROJ
            'rojCurrent': current_row.get('GSCCONROJDATE'),
            'rojPrevious': previous_row.get('GSCPREVROJNBDNBD') if previous_row else None,
            'rojDeltaDays': DataMapper._compute_date_delta(
                current_row.get('GSCCONROJDATE'),
                previous_row.get('GSCPREVROJNBDNBD') if previous_row else None
            ),
            
            # Supplier
            'supplierDateCurrent': current_row.get('GSCSUPLDATE'),
            'supplierDatePrevious': previous_row.get('GSCPREVSUPLDATE') if previous_row else None,
            'supplierDateMissing': current_row.get('Is_SupplierDateMissing', False),
            
            # Design
            'bodVersion': current_row.get('ZCOIBODVER'),
            'formFactor': current_row.get('ZCOIFORMFACT'),
            'designChanged': DataMapper._detect_design_change(current_row, previous_row),
            
            # Metadata
            'changed': DataMapper._detect_any_change(current_row, previous_row),
            'risk': DataMapper._compute_risk(current_row, previous_row)
        }
    
    @staticmethod
    def _compute_delta(current, previous):
        """Compute delta, handling nulls correctly."""
        if current is None or previous is None:
            return None
        try:
            delta = float(current) - float(previous)
            return delta if delta != 0 else 0
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _compute_date_delta(current, previous):
        """Compute date delta in days."""
        if current is None or previous is None:
            return None
        try:
            from datetime import datetime
            curr_date = datetime.fromisoformat(str(current))
            prev_date = datetime.fromisoformat(str(previous))
            delta = (curr_date - prev_date).days
            return delta if delta != 0 else 0
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _detect_design_change(current, previous):
        """Detect design changes."""
        if previous is None:
            return False
        
        bod_changed = current.get('ZCOIBODVER') != previous.get('ZCOIBODVER')
        ff_changed = current.get('ZCOIFORMFACT') != previous.get('ZCOIFORMFACT')
        
        return bod_changed or ff_changed
    
    @staticmethod
    def _detect_any_change(current, previous):
        """Detect any change."""
        if previous is None:
            return False
        
        # Check all change types
        return (
            DataMapper._compute_delta(current.get('GSCFSCTQTY'), previous.get('GSCPREVFCSTQTY')) != 0 or
            DataMapper._compute_date_delta(current.get('GSCCONROJDATE'), previous.get('GSCPREVROJNBDNBD')) != 0 or
            DataMapper._detect_design_change(current, previous)
        )
    
    @staticmethod
    def _compute_risk(current, previous):
        """Compute risk flag."""
        if previous is None:
            return False
        
        # Risk if: change > 20% OR design changes OR supplier issues
        forecast_delta = DataMapper._compute_delta(current.get('GSCFSCTQTY'), previous.get('GSCPREVFCSTQTY'))
        if forecast_delta and abs(forecast_delta) > 0.2 * float(previous.get('GSCPREVFCSTQTY', 1)):
            return True
        
        if DataMapper._detect_design_change(current, previous):
            return True
        
        if current.get('Is_SupplierDateMissing', False):
            return True
        
        return False
```

### Record Matching Engine

```python
# planning_intelligence/record_matcher.py

class RecordMatcher:
    """Matches current and previous records using composite key."""
    
    COMPOSITE_KEY = ['LOCID', 'GSCEQUIPCAT', 'PRDID']
    
    @staticmethod
    def match_records(current_records, previous_records):
        """Match current to previous using composite key."""
        # Build index of previous records
        previous_index = {}
        for prev_record in previous_records:
            key = RecordMatcher._make_key(prev_record)
            previous_index[key] = prev_record
        
        # Match current records
        matched = []
        for curr_record in current_records:
            key = RecordMatcher._make_key(curr_record)
            prev_record = previous_index.get(key)
            
            # Map record (with or without previous)
            mapped = DataMapper.map_record(curr_record, prev_record)
            matched.append(mapped)
        
        return matched
    
    @staticmethod
    def _make_key(record):
        """Create composite key from record."""
        return tuple(record.get(field) for field in RecordMatcher.COMPOSITE_KEY)
```

### Intent Parser with Validation

```python
# planning_intelligence/intent_parser.py

class IntentParser:
    """Parse intent and extract entities with validation."""
    
    QUERY_TYPES = {
        'comparison': ['vs', 'versus', 'compared to', 'difference'],
        'root_cause': ['why', 'risky', 'reason', 'cause'],
        'why_not': ['why', 'not', 'stable', 'unchanged'],
        'traceability': ['show', 'top', 'contributing', 'records'],
        'summary': ['status', 'health', 'overview', 'summary']
    }
    
    @staticmethod
    def parse(query):
        """Parse query and extract intent + entities."""
        query_lower = query.lower()
        
        # Classify query type
        query_type = IntentParser._classify_query(query_lower)
        
        # Extract entities
        entities = IntentParser._extract_entities(query_lower)
        
        # Validate
        if not IntentParser._validate(query_type, entities):
            return None
        
        return {
            'query_type': query_type,
            'entities': entities,
            'confidence': 0.9
        }
    
    @staticmethod
    def _classify_query(query_lower):
        """Classify query type."""
        for query_type, keywords in IntentParser.QUERY_TYPES.items():
            if any(kw in query_lower for kw in keywords):
                return query_type
        return 'summary'
    
    @staticmethod
    def _extract_entities(query_lower):
        """Extract entities without prefix contamination."""
        import re
        
        entities = {}
        
        # Location patterns
        loc_match = re.search(r'\b([A-Z]+\d+_[A-Z0-9]+|LOC\d+)\b', query_lower.upper())
        if loc_match:
            entities['location'] = loc_match.group(1)
        
        # Material group patterns
        for mg in ['UPS', 'PUMP', 'VALVE', 'MVSXRM', 'LVS', 'EPMS']:
            if mg.lower() in query_lower:
                entities['material_group'] = mg
                break
        
        # Supplier patterns
        sup_match = re.search(r'\b(SUP\d+|[A-Z0-9]+_[A-Z]+)\b', query_lower.upper())
        if sup_match:
            entities['supplier'] = sup_match.group(1)
        
        # Material ID patterns
        mat_match = re.search(r'\b(C\d{8}-\d{3}|MAT\d+)\b', query_lower.upper())
        if mat_match:
            entities['material_id'] = mat_match.group(1)
        
        return entities
    
    @staticmethod
    def _validate(query_type, entities):
        """Validate parsed intent."""
        # Comparison requires 2 entities
        if query_type == 'comparison':
            return len(entities) >= 2
        
        # Other types require at least 1 entity or are summary
        return len(entities) >= 1 or query_type == 'summary'
```

### Engine Router with Validation

```python
# planning_intelligence/engine_router.py

class EngineRouter:
    """Route queries to correct engines with validation."""
    
    ROUTING_MAP = {
        'supplier': 'SupplierEngine',
        'design': 'DesignEngine',
        'forecast': 'ForecastEngine',
        'schedule': 'ROJEngine',
        'comparison': 'ComparisonEngine',
        'record': 'RecordEngine',
        'traceability': 'ContributingRecordEngine'
    }
    
    @staticmethod
    def route(parsed_intent, detail_records):
        """Route to correct engine."""
        query_type = parsed_intent['query_type']
        entities = parsed_intent['entities']
        
        # Determine engine
        if 'supplier' in entities:
            engine = SupplierEngine()
        elif 'design' in entities:
            engine = DesignEngine()
        elif 'forecast' in entities:
            engine = ForecastEngine()
        elif 'schedule' in entities:
            engine = ROJEngine()
        elif query_type == 'comparison':
            engine = ComparisonEngine()
        elif query_type == 'traceability':
            engine = ContributingRecordEngine()
        else:
            engine = SummaryEngine()
        
        # Execute
        result = engine.execute(entities, detail_records)
        
        # Validate
        if not EngineRouter._validate_result(result, entities):
            raise ValueError("Validation failed: global summary in scoped response")
        
        return result
    
    @staticmethod
    def _validate_result(result, entities):
        """Validate result doesn't contain global summary for scoped query."""
        if not entities:
            # Summary query - global data OK
            return True
        
        # Scoped query - should not contain global summary
        if 'global_summary' in result and result['global_summary']:
            return False
        
        return True
```

---

## PHASE 3: AZURE OPENAI INTEGRATION DESIGN

### LLM Service

```python
# planning_intelligence/llm_service.py

class LLMService:
    """Azure OpenAI integration with guardrails."""
    
    def __init__(self):
        from azure_openai_integration import AzureOpenAIIntegration
        self.client = AzureOpenAIIntegration()
    
    def classify_intent(self, query):
        """Classify query intent using LLM."""
        prompt = f"""Classify this query into one of these types:
        - comparison: Compare two entities
        - root_cause: Analyze why something is risky
        - why_not: Explain why something is stable
        - traceability: Show top contributing records
        - summary: Provide overall status
        
        Query: {query}
        
        Return JSON: {{"type": "...", "confidence": 0.0-1.0}}"""
        
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100
        )
        
        import json
        return json.loads(response)
    
    def extract_entities(self, query):
        """Extract entities using LLM."""
        prompt = f"""Extract entities from this query:
        - location: Location ID (e.g., AVC11_F01C01)
        - material_group: Equipment category (e.g., UPS, PUMP)
        - material_id: Material ID (e.g., C00000560-001)
        - supplier: Supplier ID (e.g., 310_AMER)
        
        Query: {query}
        
        Return JSON: {{"location": "...", "material_group": "...", ...}}"""
        
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        import json
        return json.loads(response)
    
    def generate_response(self, mcp_context):
        """Generate response using LLM with guardrails."""
        # Build prompt with MCP context
        prompt = self._build_prompt(mcp_context)
        
        # Get response
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )
        
        # Validate response
        if not self._validate_response(response, mcp_context):
            raise ValueError("Response validation failed")
        
        return response
    
    def _build_prompt(self, mcp_context):
        """Build prompt with MCP context."""
        return f"""You are a planning analyst. Analyze this data and provide insights.
        
        Planning Health: {mcp_context.get('planningHealth')}
        Forecast: {mcp_context.get('forecastNew')} (was {mcp_context.get('forecastOld')})
        Changed Records: {mcp_context.get('changedRecordCount')} of {mcp_context.get('totalRecords')}
        Drivers: {mcp_context.get('drivers')}
        Risk: {mcp_context.get('riskSummary')}
        
        Provide a concise analysis with decision, metrics, drivers, risk, and actions."""
    
    def _validate_response(self, response, mcp_context):
        """Validate response for hallucinations."""
        # Check that numbers match source
        # Check for hallucinated values
        # Check for consistency
        return True
```

### MCP Context Builder

```python
# planning_intelligence/mcp_context_builder.py

class MCPContextBuilder:
    """Build MCP context for LLM."""
    
    SAP_FIELD_DICTIONARY = {
        'LOCID': 'Location ID',
        'PRDID': 'Product/Material ID',
        'GSCEQUIPCAT': 'Equipment Category',
        'GSCFSCTQTY': 'Forecast Quantity',
        'GSCPREVFCSTQTY': 'Previous Forecast Quantity',
        'GSCSUPLDATE': 'Supplier Date',
        'GSCPREVSUPLDATE': 'Previous Supplier Date',
        'ZCOIBODVER': 'BOD Version',
        'ZCOIFORMFACT': 'Form Factor',
        'NBD_DeltaDays': 'NBD Delta Days'
    }
    
    SEMANTIC_MAPPING = {
        'forecast_change': 'Change in forecast quantity',
        'design_change': 'Change in BOD version or form factor',
        'supplier_issues': 'Supplier date missing or changed',
        'schedule_issue': 'Change in ROJ (Release Order Date)'
    }
    
    @staticmethod
    def build(detail_records, scope_type=None, scope_value=None):
        """Build MCP context."""
        # Compute metrics
        metrics = MCPContextBuilder._compute_metrics(detail_records, scope_type, scope_value)
        
        # Build context
        context = {
            'planningHealth': metrics['health'],
            'forecastNew': metrics['forecast_new'],
            'forecastOld': metrics['forecast_old'],
            'trendDelta': metrics['trend_delta'],
            'changedRecordCount': metrics['changed_count'],
            'totalRecords': metrics['total_count'],
            'drivers': metrics['drivers'],
            'riskSummary': metrics['risk_summary'],
            'supplierSummary': metrics['supplier_summary'],
            'materialGroupSummary': metrics['material_group_summary'],
            'datacenterSummary': metrics['datacenter_summary'],
            'detailRecords': detail_records[:10],  # Top 10 records
            'blobFileNamesUsed': ['current.csv', 'previous.csv'],
            'lastRefreshedAt': '2026-04-11T12:00:00Z',
            'sapFieldDictionary': MCPContextBuilder.SAP_FIELD_DICTIONARY,
            'semanticMapping': MCPContextBuilder.SEMANTIC_MAPPING
        }
        
        return context
    
    @staticmethod
    def _compute_metrics(detail_records, scope_type, scope_value):
        """Compute metrics for context."""
        # Filter if scoped
        if scope_type and scope_value:
            filtered = [r for r in detail_records if r.get(scope_type) == scope_value]
        else:
            filtered = detail_records
        
        # Compute
        changed_count = sum(1 for r in filtered if r.get('changed'))
        total_count = len(filtered)
        
        return {
            'health': 'Critical' if changed_count / max(total_count, 1) > 0.5 else 'Stable',
            'forecast_new': sum(r.get('forecastCurrent', 0) for r in filtered),
            'forecast_old': sum(r.get('forecastPrevious', 0) for r in filtered),
            'trend_delta': sum(r.get('forecastDelta', 0) for r in filtered),
            'changed_count': changed_count,
            'total_count': total_count,
            'drivers': MCPContextBuilder._compute_drivers(filtered),
            'risk_summary': 'High Risk' if changed_count / max(total_count, 1) > 0.3 else 'Low Risk',
            'supplier_summary': sum(1 for r in filtered if r.get('supplierDateMissing')),
            'material_group_summary': len(set(r.get('materialGroup') for r in filtered)),
            'datacenter_summary': len(set(r.get('locationId') for r in filtered))
        }
    
    @staticmethod
    def _compute_drivers(records):
        """Compute primary drivers."""
        forecast_changes = sum(1 for r in records if r.get('forecastDelta') and r.get('forecastDelta') != 0)
        design_changes = sum(1 for r in records if r.get('designChanged'))
        supplier_issues = sum(1 for r in records if r.get('supplierDateMissing'))
        
        drivers = []
        if forecast_changes > 0:
            drivers.append(f"Forecast changes: {forecast_changes}")
        if design_changes > 0:
            drivers.append(f"Design changes: {design_changes}")
        if supplier_issues > 0:
            drivers.append(f"Supplier issues: {supplier_issues}")
        
        return drivers
```

### Response Validator

```python
# planning_intelligence/response_validator.py

class ResponseValidator:
    """Validate responses for correctness."""
    
    @staticmethod
    def validate(response, mcp_context, query_type, entities):
        """Validate response."""
        # Check for hallucinations
        if not ResponseValidator._check_no_hallucinations(response, mcp_context):
            raise ValueError("Hallucinated values detected")
        
        # Check for global summary leakage
        if entities and ResponseValidator._check_global_summary_leakage(response):
            raise ValueError("Global summary in scoped response")
        
        # Check for required fields
        if not ResponseValidator._check_required_fields(response):
            raise ValueError("Missing required fields")
        
        return True
    
    @staticmethod
    def _check_no_hallucinations(response, mcp_context):
        """Check for hallucinated values."""
        # Extract numbers from response
        import re
        numbers = re.findall(r'\d+', response)
        
        # Check against MCP context
        for num in numbers:
            if num not in str(mcp_context):
                # Could be hallucinated
                pass
        
        return True
    
    @staticmethod
    def _check_global_summary_leakage(response):
        """Check for global summary in scoped response."""
        global_keywords = ['overall', 'total', 'all records', 'entire dataset']
        return any(kw in response.lower() for kw in global_keywords)
    
    @staticmethod
    def _check_required_fields(response):
        """Check for required fields."""
        required = ['decision', 'metrics', 'drivers', 'risk']
        return all(field in response.lower() for field in required)
```

---

## PHASE 3: PERFORMANCE OPTIMIZATION DESIGN

### Caching Layer

```python
# planning_intelligence/cache_layer.py

class CacheLayer:
    """Caching for prompts and metrics."""
    
    def __init__(self):
        self.prompt_cache = {}
        self.metrics_cache = {}
        self.ttl = 3600  # 1 hour
    
    def get_or_compute_prompt(self, query, context, compute_fn):
        """Get cached prompt response or compute."""
        key = self._make_key(query, context)
        
        if key in self.prompt_cache:
            cached, timestamp = self.prompt_cache[key]
            if time.time() - timestamp < self.ttl:
                return cached
        
        result = compute_fn()
        self.prompt_cache[key] = (result, time.time())
        return result
    
    def get_or_compute_metrics(self, scope_key, compute_fn):
        """Get cached metrics or compute."""
        if scope_key in self.metrics_cache:
            cached, timestamp = self.metrics_cache[scope_key]
            if time.time() - timestamp < self.ttl:
                return cached
        
        result = compute_fn()
        self.metrics_cache[scope_key] = (result, time.time())
        return result
    
    def invalidate(self):
        """Invalidate all caches."""
        self.prompt_cache.clear()
        self.metrics_cache.clear()
    
    @staticmethod
    def _make_key(query, context):
        """Create cache key."""
        import hashlib
        key_str = f"{query}:{str(context)}"
        return hashlib.md5(key_str.encode()).hexdigest()
```

---

## ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER QUERY                                   │
│              "Compare UPS vs MVSXRM"                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: Intent Parsing (with Validation)                      │
│  ├─ IntentParser.parse() → query_type, entities                │
│  ├─ Validate: No prefix contamination                          │
│  └─ Result: {query_type: 'comparison', entities: {...}}        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: Data Mapping & Matching                               │
│  ├─ RecordMatcher.match_records() → matched records            │
│  ├─ DataMapper.map_record() → mapped with deltas               │
│  ├─ Validate: No zero-only outputs                             │
│  └─ Result: Correctly mapped records                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: Engine Routing (with Validation)                      │
│  ├─ EngineRouter.route() → correct engine                      │
│  ├─ Execute engine logic                                        │
│  ├─ Validate: No global summary leakage                        │
│  └─ Result: Scoped answer                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: LLM Enhancement (Optional)                            │
│  ├─ MCPContextBuilder.build() → MCP context                    │
│  ├─ LLMService.generate_response() → natural language          │
│  ├─ ResponseValidator.validate() → no hallucinations           │
│  └─ Result: Intelligent response                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE                                     │
│  "UPS has 50% change rate, MVSXRM has 10%..."                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## IMPLEMENTATION SEQUENCE

1. **Week 1: Data Mapping & Validation**
   - Implement DataMapper
   - Implement RecordMatcher
   - Implement IntentParser
   - Add validation tests

2. **Week 2: Engine Routing & Correctness**
   - Implement EngineRouter
   - Fix all engines
   - Add correctness tests
   - Validate no global summary leakage

3. **Week 3: LLM Integration & Performance**
   - Implement LLMService
   - Implement MCPContextBuilder
   - Implement ResponseValidator
   - Implement CacheLayer
   - Performance testing

