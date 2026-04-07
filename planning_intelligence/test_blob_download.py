#!/usr/bin/env python3
"""
Test Blob Storage Download & File Parsing
Run this to verify you can download and parse files from Blob Storage
"""
import os
import sys
import io

def test_download():
    connection_string = os.environ.get('BLOB_CONNECTION_STRING')
    container_name = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')
    current_file = os.environ.get('BLOB_CURRENT_FILE', 'current.csv')
    previous_file = os.environ.get('BLOB_PREVIOUS_FILE', 'previous.csv')

    if not connection_string:
        print("❌ ERROR: BLOB_CONNECTION_STRING not set")
        return False

    print(f"Container: {container_name}")
    print(f"Current file: {current_file}")
    print(f"Previous file: {previous_file}\n")

    try:
        from azure.storage.blob import BlobServiceClient
        import pandas as pd
        
        client = BlobServiceClient.from_connection_string(connection_string)
        
        # Test current file
        print(f"=== Testing {current_file} ===")
        try:
            blob_client = client.get_blob_client(container=container_name, blob=current_file)
            data = blob_client.download_blob().readall()
            print(f"✅ Downloaded {current_file} ({len(data)} bytes)")
            
            # Parse CSV
            df = pd.read_csv(io.BytesIO(data), dtype=str)
            print(f"✅ Parsed CSV: {len(df)} rows, {len(df.columns)} columns")
            
            # Show columns
            print(f"\nColumns ({len(df.columns)}):")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")
            
            # Check required columns
            required = {"LOCID", "PRDID", "GSCEQUIPCAT"}
            columns_upper = {c.upper() for c in df.columns}
            missing = required - columns_upper
            
            if missing:
                print(f"\n❌ Missing required columns: {missing}")
                print(f"   Found: {sorted(columns_upper)}")
                return False
            else:
                print(f"\n✅ All required columns present")
            
            # Show first row
            print(f"\nFirst row:")
            first_row = df.iloc[0].to_dict()
            for key, value in first_row.items():
                print(f"  {key}: {value}")
            
            # Show data types
            print(f"\nData types:")
            for col, dtype in df.dtypes.items():
                print(f"  {col}: {dtype}")
            
        except Exception as e:
            print(f"❌ ERROR downloading/parsing {current_file}: {e}")
            return False
        
        # Test previous file
        print(f"\n=== Testing {previous_file} ===")
        try:
            blob_client = client.get_blob_client(container=container_name, blob=previous_file)
            data = blob_client.download_blob().readall()
            print(f"✅ Downloaded {previous_file} ({len(data)} bytes)")
            
            # Parse CSV
            df = pd.read_csv(io.BytesIO(data), dtype=str)
            print(f"✅ Parsed CSV: {len(df)} rows, {len(df.columns)} columns")
            
            # Check required columns
            required = {"LOCID", "PRDID", "GSCEQUIPCAT"}
            columns_upper = {c.upper() for c in df.columns}
            missing = required - columns_upper
            
            if missing:
                print(f"\n❌ Missing required columns: {missing}")
                return False
            else:
                print(f"✅ All required columns present")
            
        except Exception as e:
            print(f"❌ ERROR downloading/parsing {previous_file}: {e}")
            return False
        
        print(f"\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_download()
    sys.exit(0 if success else 1)
