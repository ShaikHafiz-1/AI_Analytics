"""
Ollama LLM Service
Provides ChatGPT-like functionality using local Ollama models
Replaces Azure OpenAI with open-source models (Llama 2, Mistral, etc.)

Features:
- Local model execution (no API costs)
- Full data privacy (data stays local)
- Offline capability
- Customizable business rules
- Fallback to template responses if needed
"""

import requests
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# SAP Field Mappings (camelCase to actual SAP codes from data)
SAP_FIELD_CODES = {
    'locationId': 'LOCID',
    'materialId': 'PRDID',
    'materialGroup': 'GSCEQUIPCAT',
    'supplier': 'LOCFR',
    'supplierDescription': 'LOCFRDESCR',
    'forecastQty': 'GSCFSCTQTY',
    'forecastQtyPrevious': 'GSCPREVFCSTQTY',
    'rojCurrent': 'GSCCONROJDATE',
    'rojPrevious': 'GSCPREVROJNBD',
    'bodCurrent': 'ZCOIBODVERZ',
    'bodPrevious': 'ZCOIBODVERZ (previous)',
    'ffCurrent': 'ZCOIFORMFACTZ',
    'ffPrevious': 'ZCOIFORMFACTZ (previous)',
    'supplierDate': 'GSCSUPLDATE',
    'supplierDatePrevious': 'GSCPREVSUPLDATE',
    'dcSite': 'ZCOICIDZ',
    'metro': 'ZCOIMETROIDZ',
    'country': 'ZCOICOUNTRY',
    'sendForecastToSCP': 'GSCFCSTTOSCPZ',
    'forecastApproval': 'GSCFCSTAPPROVALSCP',
    'scpRojDate': 'GSCSCPROJDATEZ',
    'scpRojIndicator': 'GSCSCPROJINDZ',
    'scpSupplierComment': 'GSCSCPSUPCMT',
    'msftComment': 'GSCMSFTCMTZ',
    'automationReason': 'GSCAUTOMATIONREASONZ',
    'planningException': 'GSCPLANNINGEXCEPTIONZ',
    'rojDateReasonCode': 'GSCROJDATEREASONCODEZ',
    'datastewardNotes': 'GSCDATASTEWARDNOTESZ',
    'plannerReviewNotes': 'GSCPLNRVWNOTESZ',
    'rojLastChangedDate': 'GSCROJNBDLASTCHANGEDDATE',
    'rojCreationDate': 'GSCROJNBDCREATIONDATE',
    'scpBodVersion': 'GSCSCPBODVERSIONZ',
    'sendForecastFirstPublishDate': 'GSCSENDFCSTSCPFIRSTPUBLISHDATEZ',
    'lastPublishDate': 'GSCTRACKLASTPUBLISHDATEZ',
    'sendForecastLastRemovedDate': 'GSCSENDFCSTSCPLASTREMOVEDDATEZ',
    'scpFormFactor': 'GSCSCPFORMFACTORZ',
    'sendForecastLastChangedDate': 'GSCSENDFCSTSCPLASTCHANGEDDATEZ',
    'cmApprovalFirstDate': 'GSCCMAPPROVALFIRSTDATEZ',
    'cmApprovalLastChangedDate': 'GSCCMAPPROVALLASTCHANGEDDATEZ',
    'cmApprovalLastChangedValue': 'GSCCMAPPROVALLASTCHANGEDVALUEZ',
    'invalid': 'TINVALID',
    'lastModifiedBy': 'LASTMODIFIEDBY',
    'lastModifiedDate': 'LASTMODIFIEDDATE',
    'createdBy': 'CREATEDBY',
    'createdDate': 'CREATEDDATE',
    'version': '#Version',
    'rocRegion': 'ROC',
    'changeType': 'NBD_Change Type',
    'rojDelta': 'NBD_DeltaDays',
    'forecastDelta': 'FCST_Delta Qty',
    'isNewDemand': 'Is_New Demand',
    'isCancelled': 'Is_cancelled',
    'isSupplierDateMissing': 'Is_SupplierDateMissing',
    'riskFlag': 'Risk_Flag',
    'qtyChanged': 'Qty Changed Flag',
    'designChanged': 'Design Changed Flag',
    'rojChanged': 'ROJ Changed Flag',
    'supplierChanged': 'Supplier Changed Flag'
}

# Business rules for supply chain planning (from business_rules.py)
BUSINESS_RULES = """
COMPOSITE KEY (Unique Record Identifier):
- LOCID (Location ID) + GSCEQUIPCAT (Equipment Category) + PRDID (Material ID)
- Example: CYS20_F01C01 + UPS + ACC = unique record

DESIGN CHANGE DETECTION:
- Design Change = TRUE if (ZCOIBODVER changed) OR (ZCOIFORMFACT changed)
- EXCLUDE: Is_New Demand = TRUE, Is_cancelled = TRUE
- Business Impact: Design changes require engineering review and may impact supplier capacity

FORECAST TREND ANALYSIS:
- Formula: Trend = GSCFSCTQTY - GSCPREVFCSTQTY
- Positive → Forecast increased (higher procurement requirements)
- Negative → Forecast decreased (lower procurement requirements)
- Business Impact: Affects supplier capacity, inventory, and delivery timelines

SUPPLIER ANALYSIS:
- Group records by LOCFR (Supplier)
- Risk indicators: GSCSUPLDATE changes, Is_SupplierDateMissing, multiple design/forecast changes
- Business Impact: Supplier issues can disrupt supply chain

ROJ / SCHEDULE ANALYSIS:
- NBD_DeltaDays = days between GSCCONROJDATE and GSCPREVROJNBD
- Positive → Schedule delayed (material needed later)
- Negative → Schedule accelerated (material needed sooner)
- Business Impact: Affects procurement timing and supplier coordination

EXCLUSION RULES:
- EXCLUDE if Is_New Demand = TRUE (new demands are not changes)
- EXCLUDE if Is_cancelled = TRUE (cancellations are not changes)

PLANNING HEALTH RULES:
- Green (80-100): All metrics optimal, no action needed
- Yellow (60-79): Some metrics need attention, monitor closely
- Red (0-59): Critical issues require immediate action

RISK ASSESSMENT RULES:
- Critical: Immediate action required, escalate to management
- High: Address within 1 week, assign resources
- Medium: Address within 2 weeks, plan mitigation
- Low: Monitor and plan accordingly, no urgent action
"""

# SAP Field Definitions (key fields for reference with actual SAP codes)
SAP_FIELD_DEFINITIONS = """
KEY SAP FIELDS (with actual SAP codes):

LOCATION & FACILITY:
- LOCID: Location ID (unique facility identifier)
- ZCOICIDZ: Facility/DC/Site Name
- ZCOIMETROIDZ: Planning Metro (metropolitan area)
- ZCOICOUNTRY: Country code
- ROC: ROC Region

MATERIAL & PRODUCT:
- PRDID: Material ID (unique product identifier)
- GSCEQUIPCAT: Equipment Category (UPS, Mechanical, Hydraulic, etc.)
- ZCOIFORMFACTZ: Form Factor (physical characteristics)

SUPPLIER:
- LOCFR: Supplier (supplier code/identifier)
- LOCFRDESCR: Supplier Description
- GSCSUPLDATE: Supplier Date (data freshness indicator)
- GSCPREVSUPLDATE: Previous Supplier Date
- GSCSCPSUPCMT: SCP Supplier Comment

FORECAST QUANTITY:
- GSCFSCTQTY: Current Forecast Quantity
- GSCPREVFCSTQTY: Previous Forecast Quantity
- FCST_Delta Qty: Forecast Delta (current - previous)
- GSCFCSTTOSCPZ: Send Forecast to SCP flag

SCHEDULE & ROJ (Required On-hand):
- GSCCONROJDATE: Current ROJ Need-By Date
- GSCPREVROJNBD: Previous ROJ Need-By Date
- NBD_DeltaDays: ROJ Shift in days (positive = delayed, negative = accelerated)
- GSCROJDATEREASONCODEZ: ROJ Date Reason Code
- GSCROJNBDLASTCHANGEDDATE: ROJ Last Changed Date
- GSCROJNBDCREATIONDATE: ROJ Creation Date
- GSCSCPROJDATEZ: SCP ROJ Need-By Date
- GSCSCPROJINDZ: SCP ROJ Indicator

DESIGN & BOD:
- ZCOIBODVERZ: BOD (Bill of Design) Version
- GSCSCPBODVERSIONZ: SCP BOD Version
- GSCSCPFORMFACTORZ: SCP Form Factor

APPROVAL & WORKFLOW:
- GSCFCSTAPPROVALSCP: Forecast Approval status
- GSCCMAPPROVALFIRSTDATEZ: CM Approval First Date
- GSCCMAPPROVALLASTCHANGEDDATEZ: CM Approval Last Changed Date
- GSCCMAPPROVALLASTCHANGEDVALUEZ: CM Approval Last Changed Value

PLANNING & EXCEPTIONS:
- GSCPLANNINGEXCEPTIONZ: Planning Exception code
- GSCLLEPLANNING: LLE Planning Needed flag
- GSCCONSUMEINVFLG: Consume Inventory Flag

DATA QUALITY & TRACKING:
- Is_SupplierDateMissing: Supplier Date Missing flag (data quality issue)
- TINVALID: Invalid Flag
- LASTMODIFIEDBY: Last Modified By (user)
- LASTMODIFIEDDATE: Last Modified Date
- CREATEDBY: Created By (user)
- CREATEDDATE: Created Date
- #Version: Record Version

CHANGE TRACKING:
- Is_New Demand: New Demand flag (exclude from change analysis)
- Is_cancelled: Cancelled Demand flag (exclude from change analysis)
- NBD_Change Type: Type of ROJ change
- Risk_Flag: Risk indicator flag

COMPUTED/DERIVED FIELDS:
- Qty Changed Flag: Quantity changed indicator
- Design Changed Flag: Design changed indicator
- ROJ Changed Flag: Schedule changed indicator
- Supplier Changed Flag: Supplier changed indicator
"""


class OllamaLLMService:
    """
    LLM Service using local Ollama models
    Provides ChatGPT-like functionality without cloud dependency
    """
    
    def __init__(
        self,
        model: str = "llama2",
        base_url: str = "http://localhost:11434",
        timeout: int = 120
    ):
        """
        Initialize Ollama LLM Service
        
        Args:
            model: Model name (llama2, mistral, neural-chat, etc.)
            base_url: Ollama server URL
            timeout: Request timeout in seconds
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.api_endpoint = f"{base_url}/api/generate"
        
        logger.info(f"Initialized OllamaLLMService with model: {model}")
    
    def generate_response(
        self,
        prompt: str,
        context: Dict,
        detail_records: List[Dict] = None,
        system_prompt: str = None
    ) -> str:
        """
        Generate response using Ollama
        
        Args:
            prompt: User question
            context: Context information (metrics, filters, etc.)
            detail_records: Planning data records
            system_prompt: Optional custom system prompt (overrides default)
        
        Returns:
            Generated response string
        
        Raises:
            Exception: If Ollama is unavailable or request fails
        """
        
        try:
            # Use provided system prompt or build default
            if system_prompt is None:
                system_prompt = self._build_system_prompt()
            
            # Build user prompt with context
            user_prompt = self._build_user_prompt(prompt, context, detail_records)
            
            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            logger.info(f"Calling Ollama with model: {self.model}")
            
            # Call Ollama API
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 500
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                logger.info(f"Ollama response received ({len(generated_text)} chars)")
                return generated_text
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Cannot connect to Ollama at {self.base_url}. Is it running?"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except requests.exceptions.Timeout:
            error_msg = f"Ollama request timeout ({self.timeout}s)"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Error calling Ollama: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt with business rules and SAP field definitions
        
        Returns:
            System prompt string
        """
        
        system_prompt = f"""You are an expert supply chain planning analyst with deep knowledge of SAP planning data.

Your role is to analyze planning data and provide actionable insights based on business rules and SAP field definitions.

{BUSINESS_RULES}

{SAP_FIELD_DEFINITIONS}

RESPONSE GUIDELINES:
1. Be concise and professional
2. Provide specific, actionable insights
3. Reference data when available
4. Suggest next steps
5. Use business rule terminology
6. Highlight critical issues
7. Provide recommendations
8. Respect SAP field definitions and exclusion rules
9. Never compute values - use provided metrics
10. Never hallucinate data or logic

Always apply the business rules above when analyzing data. When referencing fields, use both the SAP code and the field name for clarity."""
        
        return system_prompt
    
    def _build_user_prompt(
        self,
        prompt: str,
        context: Dict,
        detail_records: List[Dict] = None
    ) -> str:
        """
        Build user prompt with context
        
        Args:
            prompt: User question
            context: Context information
            detail_records: Planning data records
        
        Returns:
            User prompt string
        """
        
        user_prompt = f"""Question: {prompt}

Context Information:
{self._format_context(context)}"""
        
        if detail_records:
            user_prompt += f"\n\nPlanning Data (sample records):\n{self._format_sample_records(detail_records)}"
        
        user_prompt += "\n\nProvide a clear, actionable response based on the data and business rules above."
        
        return user_prompt
    
    def _format_context(self, context: Dict) -> str:
        """
        Format context information (OPTIMIZED for speed)
        
        Args:
            context: Context dictionary
        
        Returns:
            Formatted context string
        """
        
        if not context:
            return "No context available"
        
        lines = []
        for key, value in context.items():
            # Skip large nested structures to reduce token count
            if isinstance(value, (list, dict)):
                # Only show summary for large structures
                if isinstance(value, list):
                    lines.append(f"- {key}: {len(value)} items")
                elif isinstance(value, dict):
                    # Only show top-level keys, not full JSON
                    keys = list(value.keys())[:5]  # Limit to 5 keys
                    lines.append(f"- {key}: {', '.join(keys)}")
            else:
                lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)
    
    def _format_sample_records(
        self,
        detail_records: List[Dict],
        sample_size: int = 3  # Reduced from 10 to 3 for faster processing
    ) -> str:
        """
        Format sample records for context (OPTIMIZED for speed)
        Includes SAP code mappings for clarity
        
        Args:
            detail_records: List of planning records
            sample_size: Number of records to include (reduced for performance)
        
        Returns:
            Formatted records string with SAP code references
        """
        
        if not detail_records:
            return "No records available"
        
        # Map camelCase fields to actual SAP codes
        field_mapping = {
            'locationId': 'LOCID',
            'materialId': 'PRDID',
            'materialGroup': 'GSCEQUIPCAT',
            'supplier': 'LOCFR',
            'forecastQty': 'GSCFSCTQTY',
            'forecastQtyPrevious': 'GSCPREVFCSTQTY',
            'rojCurrent': 'GSCCONROJDATE',
            'rojPrevious': 'GSCPREVROJNBD',
            'bodCurrent': 'ZCOIBODVERZ',
            'bodPrevious': 'ZCOIBODVERZ (previous)',
            'ffCurrent': 'ZCOIFORMFACTZ',
            'ffPrevious': 'ZCOIFORMFACTZ (previous)',
            'qtyChanged': 'Qty Changed Flag',
            'designChanged': 'Design Changed Flag',
            'rojChanged': 'ROJ Changed Flag',
            'supplierChanged': 'Supplier Changed Flag'
        }
        
        # Only include most relevant fields to reduce token count
        relevant_fields = [
            'locationId', 'materialId', 'materialGroup', 'supplier',
            'forecastQty', 'forecastQtyPrevious', 'qtyChanged', 
            'designChanged', 'rojChanged', 'supplierChanged'
        ]
        
        lines = []
        # Sample from beginning, middle, and end for diversity
        indices = [0, len(detail_records)//2, len(detail_records)-1]
        
        for idx, i in enumerate(indices[:sample_size]):
            if i >= len(detail_records):
                continue
            record = detail_records[i]
            record_lines = []
            for key in relevant_fields:
                if key in record:
                    sap_code = field_mapping.get(key, key)
                    value = record[key]
                    record_lines.append(f"  {key} ({sap_code}): {value}")
            
            lines.append(f"Record {idx+1}:")
            lines.extend(record_lines)
        
        if len(detail_records) > sample_size:
            lines.append(f"... and {len(detail_records) - sample_size} more records")
        
        return "\n".join(lines)
    
    def is_available(self) -> bool:
        """
        Check if Ollama is available
        
        Returns:
            True if Ollama is running, False otherwise
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama availability check failed: {e}")
            return False
    
    def has_model(self, model_name: str) -> bool:
        """
        Check if a specific model is available
        
        Args:
            model_name: Model name to check
        
        Returns:
            True if model is available, False otherwise
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
                return model_name in models
        except Exception as e:
            logger.warning(f"Model check failed: {e}")
        
        return False
    
    def get_status(self) -> Dict:
        """
        Get Ollama status and available models
        
        Returns:
            Status dictionary with available models
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name") for m in data.get("models", [])]
                
                return {
                    "status": "available",
                    "models": models,
                    "current_model": self.model,
                    "base_url": self.base_url
                }
        except Exception as e:
            logger.warning(f"Status check failed: {e}")
        
        return {
            "status": "unavailable",
            "error": f"Cannot connect to Ollama at {self.base_url}",
            "current_model": self.model
        }
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry
        
        Args:
            model_name: Model name to pull
        
        Returns:
            True if successful, False otherwise
        """
        
        try:
            logger.info(f"Pulling model: {model_name}")
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minute timeout for pulling
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_name}")
                return True
            else:
                logger.error(f"Failed to pull model: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False


# Singleton instance
_ollama_service: Optional[OllamaLLMService] = None


def get_ollama_service(
    model: str = "llama2",
    base_url: str = "http://localhost:11434",
    timeout: int = 120
) -> OllamaLLMService:
    """
    Get or create Ollama LLM service instance
    
    Args:
        model: Model name
        base_url: Ollama server URL
        timeout: Request timeout in seconds (default 120s)
    
    Returns:
        OllamaLLMService instance
    """
    
    global _ollama_service
    
    if _ollama_service is None:
        _ollama_service = OllamaLLMService(model=model, base_url=base_url, timeout=timeout)
    
    return _ollama_service


def reset_ollama_service():
    """Reset the Ollama service instance"""
    
    global _ollama_service
    _ollama_service = None
