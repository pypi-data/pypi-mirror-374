#!/usr/bin/env python3
"""
Test script for the new org() function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eloq_sdk import EloqAPI

def test_org_function():
    """Test the org() function"""
    
    # Use a valid token from the example
    token = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIzMCwiZXhwIjoxNzU2Mjc3MjAzfQ.LKsO4liXITseCWNzDW4tsssbsRDQohru-JhHUbDkQhZProCqncM157s8S3No2htPKgegCWlJDEzM2zM5SstJtQ"
    
    try:
        # Initialize client
        client = EloqAPI.from_token(token)
        print("✅ Client initialized successfully")
        
        # Test org() function
        print("\n🔍 Testing org() function...")
        org_data = client.org()
        
        print("📋 Organization Information:")
        print(f"  - Organization Name: {org_data.org_name}")
        print(f"  - Organization ID: {org_data.org_id}")
        print(f"  - Created At: {org_data.org_create_at}")
        
        # Verify the structure
        expected_keys = ['org_name', 'org_id', 'org_create_at']
        actual_keys = list(org_data.__dict__.keys())
        
        if set(expected_keys) == set(actual_keys):
            print("✅ org() function returned correct structure")
        else:
            print("❌ org() function returned unexpected structure")
            print(f"Expected keys: {expected_keys}")
            print(f"Actual keys: {actual_keys}")
        
        # Compare with org_info() to verify data consistency
        print("\n🔍 Comparing with org_info() for data consistency...")
        org_info = client.org_info()
        
        if (org_data.org_name == org_info.org_info.org_name and
            org_data.org_id == org_info.org_info.org_id and
            org_data.org_create_at == org_info.org_info.org_create_at):
            print("✅ Data consistency verified with org_info()")
        else:
            print("❌ Data inconsistency detected")
            print(f"org() org_name: {org_data['org_name']}")
            print(f"org_info() org_name: {org_info.org_info.org_name}")
            print(f"org() org_id: {org_data['org_id']}")
            print(f"org_info() org_id: {org_info.org_info.org_id}")
            print(f"org() org_create_at: {org_data['org_create_at']}")
            print(f"org_info() org_create_at: {org_info.org_info.org_create_at}")
        
        print("\n🎉 org() function test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_org_function()
