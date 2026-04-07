#!/usr/bin/env python3
"""
Test Blob Storage Connection
Run this to verify your Blob Storage connection string is valid
"""
import os
import sys

def test_connection():
    connection_string = os.environ.get('BLOB_CONNECTION_STRING')
    container_name = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')

    if not connection_string:
        print("❌ ERROR: BLOB_CONNECTION_STRING not set")
        print("\nSet it in:")
        print("  - planning_intelligence/local.settings.json")
        print("  - planning_intelligence/.env")
        return False

    print(f"Connection String: {connection_string[:50]}...")
    print(f"Container: {container_name}")

    try:
        from azure.storage.blob import BlobServiceClient
        
        # Create client
        client = BlobServiceClient.from_connection_string(connection_string)
        print("✅ Connected to Blob Storage")
        
        # List containers
        containers = list(client.list_containers())
        print(f"\n✅ Available containers ({len(containers)}):")
        for container in containers:
            print(f"  - {container.name}")
        
        # Check if our container exists
        container_client = client.get_container_client(container_name)
        if container_client.exists():
            print(f"\n✅ Container '{container_name}' exists")
            
            # List blobs
            blobs = list(container_client.list_blobs())
            print(f"\n✅ Blobs in '{container_name}' ({len(blobs)}):")
            for blob in blobs:
                print(f"  - {blob.name} ({blob.size} bytes)")
            
            if not blobs:
                print("\n⚠️  WARNING: Container is empty!")
                print("   Upload current.csv and previous.csv to the container")
            
            return True
        else:
            print(f"\n❌ Container '{container_name}' does NOT exist")
            print(f"\nCreate it in Azure Portal:")
            print(f"  1. Go to Storage Account")
            print(f"  2. Click 'Containers'")
            print(f"  3. Click '+ Container'")
            print(f"  4. Name: {container_name}")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"\nError type: {type(e).__name__}")
        
        # Provide specific guidance
        error_str = str(e)
        if "AuthenticationFailed" in error_str or "403" in error_str:
            print("\n💡 Hint: Check your AccountKey in the connection string")
            print("   Get fresh connection string from Azure Portal:")
            print("   Storage Account → Access keys → Connection string")
        elif "BlobNotFound" in error_str or "404" in error_str:
            print("\n💡 Hint: Container or blob not found")
        elif "InvalidConnectionString" in error_str:
            print("\n💡 Hint: Connection string format is invalid")
            print("   Should be: DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net")
        elif "No module named" in error_str:
            print("\n💡 Hint: azure-storage-blob not installed")
            print("   Run: pip install -r requirements.txt")
        
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
