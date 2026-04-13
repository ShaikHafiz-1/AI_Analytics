#!/usr/bin/env python3
"""
Test script to verify blob connection and load real data.
"""
import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Load local.settings.json
settings_path = os.path.join(os.path.dirname(__file__), "local.settings.json")
if os.path.exists(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)
        for key, value in settings.get("Values", {}).items():
            os.environ[key] = value
    logger.info(f"Loaded environment variables from {settings_path}")

# Test blob connection
try:
    from blob_loader import load_current_previous_from_blob
    logger.info("Loading data from Azure Blob Storage...")
    current, previous = load_current_previous_from_blob()
    logger.info(f"✅ SUCCESS: Loaded {len(current)} current rows and {len(previous)} previous rows")
    
    # Show sample
    if current:
        logger.info(f"Sample current record: {current[0]}")
    if previous:
        logger.info(f"Sample previous record: {previous[0]}")
        
except Exception as e:
    logger.error(f"❌ FAILED: {e}")
    sys.exit(1)
