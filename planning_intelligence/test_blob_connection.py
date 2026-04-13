#!/usr/bin/env python3
"""
Test Blob Storage Connection
Diagnoses blob loading issues
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_connection_string():
    """Test if connection string is valid"""
    print("\n" + "="*60)
    print("TEST 1: Connection String Validation")
    print("="*60)
    
    conn_str = os.environ.get('BLOB_CONNECTION_STRING')
    if not conn_str:
        print("❌ BLOB_CONNECTION_STRING not set in environment")
        return False
    
    print("✅ BLOB_CONNECTION_STRING is set")
    
    # Parse connection string
    parts = conn_str.split(';')
    for part in parts:
        if part.startswith('AccountName='):
            account_name = part.split('=')[1]
            print(f"   Account: {account_name}")
        elif part.startswith('AccountKey='):
            key = part.split('=')[1]
            print(f"   Key: {key[:20]}...{key[-10:]}")
    
    return True


def test_blob_client():
    """Test if BlobServiceClient can be created"""
    print("\n" + "="*60)
    print("TEST 2: BlobServiceClient Creation")
    print("="*60)
    
    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        print("❌ azure-storage-blob not installed")
        print("   Run: pip install azure-storage-blob")
        return False
    
    conn_str = os.environ.get('BLOB_CONNECTION_STRING')
    if not conn_str:
        print("❌ BLOB_CONNECTION_STRING not set")
        return False
    
    try:
        client = BlobServiceClient.from_connection_string(conn_str)
        print(f"✅ BlobServiceClient created successfully")
        print(f"   Account: {client.account_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to create BlobServiceClient: {e}")
        return False


def test_container_access():
    """Test if container is accessible"""
    print("\n" + "="*60)
    print("TEST 3: Container Access")
    print("="*60)
    
    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        print("❌ azure-storage-blob not installed")
        return False
    
    conn_str = os.environ.get('BLOB_CONNECTION_STRING')
    container = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')
    
    if not conn_str:
        print("❌ BLOB_CONNECTION_STRING not set")
        return False
    
    try:
        client = BlobServiceClient.from_connection_string(conn_str)
        container_client = client.get_container_client(container)
        
        # Try to list blobs
        blobs = list(container_client.list_blobs())
        print(f"✅ Container '{container}' is accessible")
        print(f"   Found {len(blobs)} blobs:")
        for blob in blobs:
            print(f"     - {blob.name} ({blob.size} bytes)")
        return True
    except Exception as e:
        print(f"❌ Failed to access container '{container}': {e}")
        return False


def test_blob_files():
    """Test if required blob files exist"""
    print("\n" + "="*60)
    print("TEST 4: Required Blob Files")
    print("="*60)
    
    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        print("❌ azure-storage-blob not installed")
        return False
    
    conn_str = os.environ.get('BLOB_CONNECTION_STRING')
    container = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')
    current_file = os.environ.get('BLOB_CURRENT_FILE', 'current.csv')
    previous_file = os.environ.get('BLOB_PREVIOUS_FILE', 'previous.csv')
    
    if not conn_str:
        print("❌ BLOB_CONNECTION_STRING not set")
        return False
    
    try:
        client = BlobServiceClient.from_connection_string(conn_str)
        container_client = client.get_container_client(container)
        
        blobs = {blob.name: blob for blob in container_client.list_blobs()}
        
        all_exist = True
        for filename in [current_file, previous_file]:
            if filename in blobs:
                size = blobs[filename].size
                print(f"✅ {filename} exists ({size} bytes)")
            else:
                print(f"❌ {filename} NOT FOUND")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"❌ Failed to check blob files: {e}")
        return False


def test_blob_loading():
    """Test if blob loading works"""
    print("\n" + "="*60)
    print("TEST 5: Blob Loading")
    print("="*60)
    
    try:
        from blob_loader import load_current_previous_from_blob
    except ImportError:
        print("❌ blob_loader module not found")
        return False
    
    try:
        current_rows, previous_rows = load_current_previous_from_blob()
        print(f"✅ Blob loading successful")
        print(f"   Current records: {len(current_rows)}")
        print(f"   Previous records: {len(previous_rows)}")
        
        if current_rows:
            print(f"   Current columns: {list(current_rows[0].keys())}")
        if previous_rows:
            print(f"   Previous columns: {list(previous_rows[0].keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Blob loading failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("BLOB STORAGE CONNECTION TEST")
    print("="*60)
    
    results = {
        "Connection String": test_connection_string(),
        "BlobServiceClient": test_blob_client(),
        "Container Access": test_container_access(),
        "Blob Files": test_blob_files(),
        "Blob Loading": test_blob_loading(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Blob storage is working correctly")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
