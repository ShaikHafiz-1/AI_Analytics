"""
Integration test for Blob Storage connection with Copilot Real-Time Answers.
Tests that the blob storage is properly configured and accessible.
"""

import os
import json
from azure.storage.blob import BlobServiceClient
from datetime import datetime

def test_blob_connection():
    """Test blob storage connection."""
    print("\n" + "="*80)
    print("BLOB STORAGE CONNECTION TEST")
    print("="*80)
    
    try:
        # Get connection string from environment
        connection_string = os.environ.get("BLOB_CONNECTION_STRING")
        if not connection_string:
            print("❌ BLOB_CONNECTION_STRING not found in environment")
            return False
        
        print("✓ Connection string found")
        
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        print("✓ Blob service client created")
        
        # Get container name
        container_name = os.environ.get("BLOB_CONTAINER_NAME", "planning-data")
        print(f"✓ Container name: {container_name}")
        
        # Get container client
        container_client = blob_service_client.get_container_client(container_name)
        print("✓ Container client created")
        
        # List blobs
        blobs = list(container_client.list_blobs())
        print(f"✓ Found {len(blobs)} blobs in container")
        
        for blob in blobs:
            print(f"  - {blob.name} ({blob.size} bytes)")
        
        # Get current and previous files
        current_file = os.environ.get("BLOB_CURRENT_FILE", "current.csv")
        previous_file = os.environ.get("BLOB_PREVIOUS_FILE", "previous.csv")
        
        print(f"\n✓ Looking for files:")
        print(f"  - Current: {current_file}")
        print(f"  - Previous: {previous_file}")
        
        # Check if files exist
        blob_names = [blob.name for blob in blobs]
        current_exists = current_file in blob_names
        previous_exists = previous_file in blob_names
        
        print(f"\n✓ File status:")
        print(f"  - {current_file}: {'✓ EXISTS' if current_exists else '❌ NOT FOUND'}")
        print(f"  - {previous_file}: {'✓ EXISTS' if previous_exists else '❌ NOT FOUND'}")
        
        if current_exists:
            # Download and check current file
            blob_client = container_client.get_blob_client(current_file)
            download_stream = blob_client.download_blob()
            data = download_stream.readall()
            print(f"\n✓ Downloaded {current_file} ({len(data)} bytes)")
            
            # Try to parse as CSV
            lines = data.decode('utf-8').split('\n')
            print(f"  - Lines: {len(lines)}")
            print(f"  - First line (header): {lines[0][:100]}...")
        
        print("\n" + "="*80)
        print("✓ BLOB STORAGE CONNECTION TEST PASSED")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("="*80 + "\n")
        return False


def test_copilot_with_blob_data():
    """Test Copilot Real-Time Answers with blob data."""
    print("\n" + "="*80)
    print("COPILOT REAL-TIME ANSWERS - BLOB DATA TEST")
    print("="*80)
    
    try:
        from blob_loader import load_current_previous_from_blob
        from normalizer import normalize_rows
        from filters import filter_records
        from comparator import compare_records
        from response_builder import build_response
        
        print("\n✓ Loading data from blob storage...")
        current_rows, previous_rows = load_current_previous_from_blob()
        print(f"✓ Loaded {len(current_rows)} current rows, {len(previous_rows)} previous rows")
        
        print("\n✓ Normalizing data...")
        current_records = normalize_rows(current_rows, is_current=True)
        previous_records = normalize_rows(previous_rows, is_current=False)
        print(f"✓ Normalized {len(current_records)} current records, {len(previous_records)} previous records")
        
        print("\n✓ Filtering data...")
        current_filtered = filter_records(current_records, None, None)
        previous_filtered = filter_records(previous_records, None, None)
        print(f"✓ Filtered {len(current_filtered)} current records, {len(previous_filtered)} previous records")
        
        print("\n✓ Comparing records...")
        compared = compare_records(current_filtered, previous_filtered)
        print(f"✓ Comparison complete")
        
        print("\n✓ Building response...")
        response = build_response(compared, [], None, None, data_mode="blob")
        print(f"✓ Response built")
        
        # Print summary
        print(f"\n✓ Response Summary:")
        print(f"  - Planning Health: {response.get('planningHealth', 'N/A')}")
        print(f"  - Changed Records: {response.get('changedRecordCount', 'N/A')}")
        print(f"  - Total Records: {response.get('totalRecords', 'N/A')}")
        print(f"  - Status: {response.get('status', 'N/A')}")
        
        print("\n" + "="*80)
        print("✓ COPILOT REAL-TIME ANSWERS - BLOB DATA TEST PASSED")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        return False


def test_copilot_explain_endpoint():
    """Test Copilot explain endpoint with blob data."""
    print("\n" + "="*80)
    print("COPILOT EXPLAIN ENDPOINT - BLOB DATA TEST")
    print("="*80)
    
    try:
        from blob_loader import load_current_previous_from_blob
        from normalizer import normalize_rows
        from filters import filter_records
        from comparator import compare_records
        from response_builder import build_response
        from function_app import (
            _extract_scope,
            _classify_question,
            _determine_answer_mode,
            _compute_scoped_metrics,
            _generate_answer_from_context,
        )
        
        print("\n✓ Loading data from blob storage...")
        current_rows, previous_rows = load_current_previous_from_blob()
        
        print("\n✓ Processing data...")
        current_records = normalize_rows(current_rows, is_current=True)
        previous_records = normalize_rows(previous_rows, is_current=False)
        current_filtered = filter_records(current_records, None, None)
        previous_filtered = filter_records(previous_records, None, None)
        compared = compare_records(current_filtered, previous_filtered)
        
        print("\n✓ Building context...")
        context = build_response(compared, [], None, None, data_mode="blob")
        
        # Test questions
        test_questions = [
            "What is the planning health?",
            "What changed most?",
            "Show top contributing records",
            "What should the planner do next?",
        ]
        
        print(f"\n✓ Testing {len(test_questions)} questions:")
        for question in test_questions:
            print(f"\n  Q: {question}")
            
            # Extract scope
            scope_type, scope_value = _extract_scope(question)
            
            # Classify question
            query_type = _classify_question(question)
            
            # Determine answer mode
            answer_mode = _determine_answer_mode(query_type, scope_type)
            
            # Compute scoped metrics if needed
            scoped_metrics = None
            if answer_mode == "investigate":
                scoped_metrics = _compute_scoped_metrics(
                    context.get("detailRecords", []),
                    scope_type,
                    scope_value
                )
            
            # Generate answer
            answer = _generate_answer_from_context(
                question, context, answer_mode, scope_type, scope_value, scoped_metrics
            )
            
            print(f"  Query Type: {query_type}")
            print(f"  Answer Mode: {answer_mode}")
            print(f"  Answer: {answer[:100]}...")
        
        print("\n" + "="*80)
        print("✓ COPILOT EXPLAIN ENDPOINT - BLOB DATA TEST PASSED")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COPILOT REAL-TIME ANSWERS - INTEGRATION TEST SUITE")
    print("="*80)
    
    results = []
    
    # Test 1: Blob connection
    print("\n[1/3] Testing blob storage connection...")
    results.append(("Blob Connection", test_blob_connection()))
    
    # Test 2: Copilot with blob data
    print("\n[2/3] Testing Copilot with blob data...")
    results.append(("Copilot Blob Data", test_copilot_with_blob_data()))
    
    # Test 3: Explain endpoint
    print("\n[3/3] Testing explain endpoint...")
    results.append(("Explain Endpoint", test_copilot_explain_endpoint()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("="*80 + "\n")
    
    exit(0 if passed_count == total_count else 1)
