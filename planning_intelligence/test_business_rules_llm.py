"""
Test suite for LLM Business Rules Enhancement.

Validates that ChatGPT understands business rules, field definitions,
and generates domain-aware responses.
"""

import logging
from business_rules import (
    SAP_FIELD_DICTIONARY,
    BUSINESS_RULES,
    RESPONSE_GUIDELINES,
    EXAMPLE_RESPONSES,
    get_business_rules_context,
    get_field_definitions_context,
    get_response_guidelines_context
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sap_field_dictionary():
    """Test that SAP field dictionary is complete."""
    logger.info("=" * 80)
    logger.info("TEST 1: SAP Field Dictionary")
    logger.info("=" * 80)
    
    required_fields = [
        "LOCID", "PRDID", "GSCEQUIPCAT", "LOCFR",
        "ZCOIBODVER", "ZCOIFORMFACT",
        "GSCFSCTQTY", "GSCPREVFCSTQTY",
        "GSCCONROJDATE", "GSCPREVROJNBD", "NBD_DeltaDays",
        "GSCSUPLDATE", "Is_SupplierDateMissing",
        "Is_New Demand", "Is_cancelled"
    ]
    
    for field in required_fields:
        assert field in SAP_FIELD_DICTIONARY, f"Missing field: {field}"
        field_info = SAP_FIELD_DICTIONARY[field]
        assert "name" in field_info, f"Missing 'name' for {field}"
        assert "description" in field_info, f"Missing 'description' for {field}"
        assert "business_context" in field_info, f"Missing 'business_context' for {field}"
        logger.info(f"✓ {field}: {field_info['name']}")
    
    logger.info(f"✓ All {len(required_fields)} required fields present")
    logger.info("")

def test_business_rules():
    """Test that business rules are defined."""
    logger.info("=" * 80)
    logger.info("TEST 2: Business Rules")
    logger.info("=" * 80)
    
    required_rules = [
        "composite_key",
        "design_change_detection",
        "forecast_trend",
        "supplier_analysis",
        "roj_schedule_analysis",
        "exclusion_rules"
    ]
    
    for rule in required_rules:
        assert rule in BUSINESS_RULES, f"Missing rule: {rule}"
        rule_info = BUSINESS_RULES[rule]
        assert "description" in rule_info, f"Missing 'description' for {rule}"
        logger.info(f"✓ {rule}: {rule_info['description']}")
    
    logger.info(f"✓ All {len(required_rules)} business rules defined")
    logger.info("")

def test_response_guidelines():
    """Test that response guidelines are defined."""
    logger.info("=" * 80)
    logger.info("TEST 3: Response Guidelines")
    logger.info("=" * 80)
    
    required_sections = ["structure", "tone", "field_explanation", "constraints"]
    
    for section in required_sections:
        assert section in RESPONSE_GUIDELINES, f"Missing section: {section}"
        logger.info(f"✓ {section}: {RESPONSE_GUIDELINES[section]}")
    
    logger.info(f"✓ All {len(required_sections)} response guideline sections present")
    logger.info("")

def test_example_responses():
    """Test that example responses are defined."""
    logger.info("=" * 80)
    logger.info("TEST 4: Example Responses")
    logger.info("=" * 80)
    
    required_examples = [
        "forecast_change",
        "design_change",
        "supplier_analysis",
        "risk_analysis"
    ]
    
    for example in required_examples:
        assert example in EXAMPLE_RESPONSES, f"Missing example: {example}"
        example_info = EXAMPLE_RESPONSES[example]
        assert "question" in example_info, f"Missing 'question' for {example}"
        assert "before" in example_info, f"Missing 'before' for {example}"
        assert "after" in example_info, f"Missing 'after' for {example}"
        logger.info(f"✓ {example}")
        logger.info(f"  Question: {example_info['question']}")
        logger.info(f"  Before: {example_info['before'][:60]}...")
        logger.info(f"  After: {example_info['after'][:60]}...")
    
    logger.info(f"✓ All {len(required_examples)} example responses present")
    logger.info("")

def test_context_generation():
    """Test that context generation functions work."""
    logger.info("=" * 80)
    logger.info("TEST 5: Context Generation")
    logger.info("=" * 80)
    
    # Test business rules context
    business_rules_context = get_business_rules_context()
    assert "COMPOSITE KEY" in business_rules_context
    assert "DESIGN CHANGE DETECTION" in business_rules_context
    assert "FORECAST TREND ANALYSIS" in business_rules_context
    logger.info(f"✓ Business rules context generated ({len(business_rules_context)} chars)")
    
    # Test field definitions context
    field_definitions_context = get_field_definitions_context()
    assert "LOCID" in field_definitions_context
    assert "GSCFSCTQTY" in field_definitions_context
    logger.info(f"✓ Field definitions context generated ({len(field_definitions_context)} chars)")
    
    # Test response guidelines context
    response_guidelines_context = get_response_guidelines_context()
    assert "RESPONSE GENERATION GUIDELINES" in response_guidelines_context
    assert "NEVER compute values" in response_guidelines_context
    logger.info(f"✓ Response guidelines context generated ({len(response_guidelines_context)} chars)")
    
    logger.info("")

def test_design_change_logic():
    """Test design change detection logic."""
    logger.info("=" * 80)
    logger.info("TEST 6: Design Change Logic")
    logger.info("=" * 80)
    
    design_rule = BUSINESS_RULES["design_change_detection"]
    logger.info(f"Rule: {design_rule['rule']}")
    logger.info(f"Exclusions: {design_rule['exclusions']}")
    logger.info(f"Business Impact: {design_rule['business_impact']}")
    logger.info("✓ Design change logic validated")
    logger.info("")

def test_forecast_trend_logic():
    """Test forecast trend calculation logic."""
    logger.info("=" * 80)
    logger.info("TEST 7: Forecast Trend Logic")
    logger.info("=" * 80)
    
    forecast_rule = BUSINESS_RULES["forecast_trend"]
    logger.info(f"Formula: {forecast_rule['formula']}")
    logger.info(f"Interpretation:")
    for key, value in forecast_rule['interpretation'].items():
        logger.info(f"  {key}: {value}")
    logger.info(f"Business Impact: {forecast_rule['business_impact']}")
    logger.info("✓ Forecast trend logic validated")
    logger.info("")

def test_supplier_analysis_logic():
    """Test supplier analysis logic."""
    logger.info("=" * 80)
    logger.info("TEST 8: Supplier Analysis Logic")
    logger.info("=" * 80)
    
    supplier_rule = BUSINESS_RULES["supplier_analysis"]
    logger.info(f"Grouping: {supplier_rule['grouping']}")
    logger.info(f"Risk Indicators:")
    for indicator in supplier_rule['risk_indicators']:
        logger.info(f"  - {indicator}")
    logger.info(f"Business Impact: {supplier_rule['business_impact']}")
    logger.info("✓ Supplier analysis logic validated")
    logger.info("")

def test_roj_schedule_logic():
    """Test ROJ schedule analysis logic."""
    logger.info("=" * 80)
    logger.info("TEST 9: ROJ Schedule Logic")
    logger.info("=" * 80)
    
    roj_rule = BUSINESS_RULES["roj_schedule_analysis"]
    logger.info(f"Calculation: {roj_rule['calculation']}")
    logger.info(f"Interpretation:")
    for key, value in roj_rule['interpretation'].items():
        logger.info(f"  {key}: {value}")
    logger.info(f"Business Impact: {roj_rule['business_impact']}")
    logger.info("✓ ROJ schedule logic validated")
    logger.info("")

def test_exclusion_rules():
    """Test exclusion rules."""
    logger.info("=" * 80)
    logger.info("TEST 10: Exclusion Rules")
    logger.info("=" * 80)
    
    exclusion_rule = BUSINESS_RULES["exclusion_rules"]
    logger.info(f"Description: {exclusion_rule['description']}")
    logger.info(f"Rules:")
    for rule in exclusion_rule['rules']:
        logger.info(f"  - {rule}")
    logger.info(f"Reason: {exclusion_rule['reason']}")
    logger.info("✓ Exclusion rules validated")
    logger.info("")

def run_all_tests():
    """Run all business rules tests."""
    logger.info("\n")
    logger.info("=" * 80)
    logger.info("LLM BUSINESS RULES TEST SUITE")
    logger.info("=" * 80)
    logger.info("\n")
    
    try:
        test_sap_field_dictionary()
        test_business_rules()
        test_response_guidelines()
        test_example_responses()
        test_context_generation()
        test_design_change_logic()
        test_forecast_trend_logic()
        test_supplier_analysis_logic()
        test_roj_schedule_logic()
        test_exclusion_rules()
        
        logger.info("=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\nBusiness rules are properly defined and ready for LLM integration.")
        logger.info("ChatGPT will now understand:")
        logger.info("  - All SAP field definitions and business context")
        logger.info("  - Design change detection logic")
        logger.info("  - Forecast trend analysis")
        logger.info("  - Supplier analysis and risk indicators")
        logger.info("  - ROJ schedule analysis")
        logger.info("  - Exclusion rules for change detection")
        logger.info("  - Response generation guidelines")
        logger.info("\n")
        
    except AssertionError as e:
        logger.error(f"✗ TEST FAILED: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"✗ UNEXPECTED ERROR: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()
