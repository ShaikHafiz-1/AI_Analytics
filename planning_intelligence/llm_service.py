"""
LLM Service for Planning Intelligence Copilot.

Provides ChatGPT integration with fallback to template-based responses.
Handles API calls, error handling, and response formatting.
Uses SAP schema for proper data interpretation from blob files.
"""

import os
import logging
from typing import Dict, Optional, List
from datetime import datetime
from functools import wraps
import time

logger = logging.getLogger(__name__)

# Import SAP schema for field interpretation
try:
    from sap_schema import SAPSchema
    SCHEMA = SAPSchema()
    FIELD_DICT = SCHEMA.get_field_dictionary()
except ImportError:
    logger.warning("SAP schema not available. Using basic field names.")
    FIELD_DICT = {}


class LLMService:
    """Service for generating responses using OpenAI's ChatGPT API."""
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize LLM service.
        
        Args:
            use_mock: If True, uses mock responses instead of real API calls.
                     Useful for testing without API key.
        """
        self.use_mock = use_mock
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
        self.timeout = int(os.getenv("OPENAI_TIMEOUT", "30"))
        
        # Initialize OpenAI client only if API key is available and not using mock
        self.client = None
        if self.api_key and not self.use_mock:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"LLM Service initialized with model: {self.model}")
            except ImportError:
                logger.warning("OpenAI library not installed. Install with: pip install openai")
                self.use_mock = True
        else:
            if not self.api_key:
                logger.info("OPENAI_API_KEY not set. Using mock responses for testing.")
            self.use_mock = True
    
    def generate_response(self, prompt: str, context: Dict, detail_records: List[Dict] = None) -> str:
        """
        Generate a natural language response using ChatGPT with retry logic.
        
        Args:
            prompt: The user's question/prompt
            context: Dictionary of metrics and data context
            detail_records: Optional list of actual blob records for full context
            
        Returns:
            Natural language response string
        """
        if self.use_mock:
            return self._generate_mock_response(prompt, context)
        
        # Retry logic: try up to 3 times with exponential backoff
        max_retries = 3
        retry_delay = 1  # Start with 1 second
        
        for attempt in range(max_retries):
            try:
                system_message = self._build_system_prompt()
                user_message = self._build_user_prompt(prompt, context, detail_records)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=self.max_tokens,
                    timeout=self.timeout
                )
                
                result = response.choices[0].message.content
                logger.info(f"LLM response generated for prompt: {prompt[:50]}...")
                return result
                
            except Exception as e:
                logger.warning(f"LLM API error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                
                if attempt < max_retries - 1:
                    # Wait before retrying (exponential backoff)
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Double the delay for next retry
                else:
                    # Last attempt failed, raise error
                    logger.error(f"LLM API failed after {max_retries} attempts: {str(e)}")
                    raise
    
    def _build_system_prompt(self, include_full_context: bool = True) -> str:
        """Build the system prompt for ChatGPT with optional business rules and field definitions.
        
        Args:
            include_full_context: If True, include full business rules and field definitions.
                                 If False, use minimal prompt for faster responses.
        """
        if include_full_context:
            try:
                from business_rules import (
                    get_business_rules_context,
                    get_field_definitions_context,
                    get_response_guidelines_context
                )
                business_rules = get_business_rules_context()
                field_definitions = get_field_definitions_context()
                response_guidelines = get_response_guidelines_context()
            except ImportError:
                logger.warning("Business rules module not available. Using basic schema info.")
                business_rules = ""
                field_definitions = self._get_schema_info()
                response_guidelines = ""
            
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
- When explaining fields, reference their business context
- Provide actionable insights and recommendations

Response format:
- Start with natural greeting or direct answer
- Provide specific metrics and numbers
- Explain business impact and WHY it matters
- End with suggested actions or recommendations"""
        else:
            # Minimal prompt for fast responses
            return """You are a Planning Intelligence Copilot for supply chain analytics.
Provide clear, concise, business-focused insights about planning data.
Use natural, conversational tone. Never compute values - use provided metrics.
Always respect data definitions and business rules."""
    
    def _get_schema_info(self) -> str:
        """Get schema information for the system prompt."""
        if not FIELD_DICT:
            return "No schema information available."
        
        # Group fields by category
        categories = {}
        for field_key, field_info in FIELD_DICT.items():
            # Extract category from description or use generic
            category = "Other"
            if "location" in field_info.get("description", "").lower():
                category = "Location & Facility"
            elif "material" in field_info.get("description", "").lower():
                category = "Material & Product"
            elif "forecast" in field_info.get("description", "").lower():
                category = "Forecast & Quantity"
            elif "supplier" in field_info.get("description", "").lower():
                category = "Supplier"
            elif "schedule" in field_info.get("description", "").lower() or "roj" in field_key.lower():
                category = "Schedule & ROJ"
            elif "design" in field_info.get("description", "").lower() or "bod" in field_key.lower():
                category = "Design & BOD"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(f"{field_info.get('name', field_key)}: {field_info.get('description', '')}")
        
        # Format schema info
        lines = []
        for category, fields in sorted(categories.items()):
            lines.append(f"\n{category}:")
            for field in fields[:3]:  # Limit to 3 per category for brevity
                lines.append(f"  • {field}")
            if len(fields) > 3:
                lines.append(f"  • ... and {len(fields) - 3} more fields")
        
        return "\n".join(lines)
    
    def _build_user_prompt(self, prompt: str, context: Dict, detail_records: List[Dict] = None) -> str:
        """Build the user prompt with context and optional blob records."""
        formatted_context = self._format_context(context)
        
        # Add sample records if available
        records_context = ""
        if detail_records:
            records_context = self._format_sample_records(detail_records)
        
        return f"""User Question: {prompt}

Data Context:
{formatted_context}

{records_context}

Please provide a natural language response based on this data. Be specific and actionable."""
    
    def _format_context(self, context: Dict) -> str:
        """Format metrics context for ChatGPT using SAP schema."""
        if not context:
            return "No context data available."
        
        lines = []
        for key, value in context.items():
            # Get field name from SAP schema
            field_info = FIELD_DICT.get(key, {})
            field_name = field_info.get("name", key.replace("_", " ").title())
            field_description = field_info.get("description", "")
            
            # Format the value
            if isinstance(value, (int, float)):
                formatted_value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
            elif isinstance(value, list):
                formatted_value = ", ".join(str(v) for v in value[:5])
                if len(value) > 5:
                    formatted_value += f", ... ({len(value)} total)"
            else:
                formatted_value = str(value)
            
            # Build line with field name and description
            if field_description:
                lines.append(f"- {field_name} ({key}): {formatted_value}\n  Description: {field_description}")
            else:
                lines.append(f"- {field_name}: {formatted_value}")
        
        return "\n".join(lines) if lines else "No context data available."
    
    def _format_sample_records(self, detail_records: List[Dict], sample_size: int = 10) -> str:
        """Format sample records from blob data with field definitions for context."""
        if not detail_records:
            return ""
        
        try:
            from business_rules import SAP_FIELD_DICTIONARY
        except ImportError:
            SAP_FIELD_DICTIONARY = {}
        
        # Take sample of records
        sample_records = detail_records[:sample_size]
        
        lines = ["\nSample Records from Blob Data:"]
        for i, record in enumerate(sample_records, 1):
            lines.append(f"\nRecord {i}:")
            for key, value in record.items():
                field_info = SAP_FIELD_DICTIONARY.get(key, {})
                field_name = field_info.get("name", key.replace("_", " ").title())
                
                # Format value based on type
                if isinstance(value, bool):
                    formatted_value = "Yes" if value else "No"
                elif isinstance(value, (int, float)):
                    formatted_value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                else:
                    formatted_value = str(value)
                
                lines.append(f"  {field_name} ({key}): {formatted_value}")
        
        if len(detail_records) > sample_size:
            lines.append(f"\n... and {len(detail_records) - sample_size} more records")
        
        return "\n".join(lines)
    
    def _generate_mock_response(self, prompt: str, context: Dict) -> str:
        """
        Generate a mock response for testing without API key.
        
        Args:
            prompt: The user's question
            context: Dictionary of metrics
            
        Returns:
            Mock response string
        """
        # Extract key metrics from context
        health = context.get("planningHealth", 75)
        changed_count = context.get("changedRecordCount", 0)
        total_count = context.get("totalRecords", 100)
        design_changes = context.get("designChanges", 0)
        supplier_changes = context.get("supplierChanges", 0)
        qty_changes = context.get("qtyChanges", 0)
        
        # Generate contextual mock response based on prompt
        prompt_lower = prompt.lower()
        
        if "health" in prompt_lower:
            change_rate = (changed_count / total_count * 100) if total_count > 0 else 0
            return f"Planning health is currently at {health}/100 (Moderate). {changed_count} of {total_count} records ({change_rate:.1f}%) have recent changes. Primary drivers include {design_changes} design changes, {supplier_changes} supplier changes, and {qty_changes} quantity adjustments. Recommend reviewing high-risk items."
        
        elif "risk" in prompt_lower:
            high_risk_count = changed_count
            risk_level = "CRITICAL" if high_risk_count > 5 else "HIGH" if high_risk_count > 2 else "NORMAL"
            return f"Risk level is {risk_level}. {high_risk_count} records show changes indicating potential supply chain disruptions. Key risks: {design_changes} design modifications, {supplier_changes} supplier transitions. Recommend immediate attention to supplier changes."
        
        elif "forecast" in prompt_lower or "trend" in prompt_lower:
            return f"Forecast analysis shows {qty_changes} records with quantity changes. Total forecast adjustments detected across {changed_count} records. Trend indicates {('increasing' if qty_changes > 0 else 'stable')} demand patterns. Monitor supplier capacity for upcoming changes."
        
        elif "change" in prompt_lower:
            return f"Total changes detected: {changed_count} records affected. Breakdown: {design_changes} design changes, {supplier_changes} supplier changes, {qty_changes} quantity changes. Change rate: {(changed_count/total_count*100):.1f}% of total records."
        
        elif "compare" in prompt_lower or "difference" in prompt_lower:
            loc1_changes = context.get("location1Changes", changed_count // 2)
            loc2_changes = context.get("location2Changes", changed_count // 2)
            return f"Location comparison: Location 1 shows {loc1_changes} changes, Location 2 shows {loc2_changes} changes. Location 1 has higher activity. Recommend reviewing Location 1 for potential supply chain impacts."
        
        elif "supplier" in prompt_lower or "impact" in prompt_lower:
            return f"Supplier analysis: {supplier_changes} supplier changes detected. {design_changes} design-related impacts. Affected suppliers represent significant portion of supply chain. Recommend supplier communication and contingency planning."
        
        else:
            # Generic response
            return f"Based on current planning data: {changed_count} records show changes out of {total_count} total ({(changed_count/total_count*100):.1f}%). Planning health score: {health}/100. Key metrics: {design_changes} design changes, {supplier_changes} supplier changes, {qty_changes} quantity adjustments."
    
    def interpret_blob_record(self, record: Dict) -> str:
        """
        Interpret a blob record using SAP schema.
        
        Args:
            record: A single record from blob data
            
        Returns:
            Human-readable interpretation of the record
        """
        if not record:
            return "No record data available."
        
        interpretations = []
        for field_key, field_value in record.items():
            field_info = FIELD_DICT.get(field_key, {})
            field_name = field_info.get("name", field_key)
            field_type = field_info.get("type", "unknown")
            
            # Format value based on type
            if field_type == "number":
                if isinstance(field_value, (int, float)):
                    formatted_value = f"{field_value:,}" if isinstance(field_value, int) else f"{field_value:.2f}"
                else:
                    formatted_value = str(field_value)
            elif field_type == "boolean":
                formatted_value = "Yes" if field_value else "No"
            else:
                formatted_value = str(field_value)
            
            interpretations.append(f"{field_name}: {formatted_value}")
        
        return "\n".join(interpretations)
    
    def get_field_description(self, field_key: str) -> str:
        """Get human-readable description of a field."""
        field_info = FIELD_DICT.get(field_key, {})
        return field_info.get("description", f"Field: {field_key}")
    
    def get_field_name(self, field_key: str) -> str:
        """Get human-readable name of a field."""
        field_info = FIELD_DICT.get(field_key, {})
        return field_info.get("name", field_key.replace("_", " ").title())
    
    def is_available(self) -> bool:
        """Check if LLM service is available (has API key)."""
        return self.api_key is not None and not self.use_mock
    
    def has_schema(self) -> bool:
        """Check if SAP schema is available for data interpretation."""
        return len(FIELD_DICT) > 0
    
    def get_status(self) -> Dict:
        """Get LLM service status."""
        return {
            "available": self.is_available(),
            "model": self.model,
            "use_mock": self.use_mock,
            "api_key_set": self.api_key is not None,
            "schema_available": self.has_schema(),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


# Global LLM service instance
_llm_service = None


def get_llm_service(use_mock: bool = False) -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService(use_mock=use_mock)
    return _llm_service


def reset_llm_service():
    """Reset the global LLM service instance (useful for testing)."""
    global _llm_service
    _llm_service = None
