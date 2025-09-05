#!/usr/bin/env python3
"""
Test script to run only up to get_task and show raw response
"""

from cuteagent.cuteagent import DocumentAgent
import json
import requests

def test_get_task_only():
    """Test up to get_task and show raw response"""
    print("=" * 80)
    print("📋 TESTING DOCUMENT AGENT - UP TO get_task ONLY")
    print("=" * 80)
    
    # Initialize DocumentAgent
    agent = DocumentAgent()
    
    # Test parameters (same as your original)
    test_params = {
        "submission_type": "Initial Submission",
        "auto_lock": False,
        "client_id": "137",
        "doc_id": "935",
        "token": "esfuse-token",
        "api_base": "https://m49lxh6q5d.execute-api.us-west-1.amazonaws.com/prod",
        "taskdoc_api_token": "N-rAFD-TGYhnlh-sp6AGlbPzn1XOaumloj-K0WrXBFk",
        "taskdoc_auth_token": "nLTVa7pStD9yBVhSTgZ7"
    }
    
    print("🔧 Test Parameters:")
    print(f"   Client ID: {test_params['client_id']}")
    print(f"   Document ID: {test_params['doc_id']}")
    print(f"   API Base: {test_params['api_base']}")
    print(f"   ESFuse Token: {'***masked***' if test_params['token'] else 'None'}")
    print(f"   TaskDoc API Token: {'***masked***' if test_params['taskdoc_api_token'] else 'None'}")
    print(f"   TaskDoc Auth Token: {'***masked***' if test_params['taskdoc_auth_token'] else 'None'}")
    print()
    
    try:
        # STEP 1: Extract DocRepo data first (mirroring push_doc logic)
        print("🔍 STEP 1: Extracting DocRepo data...")
        docrepo_url = f"{test_params['api_base']}/doc?clientId={test_params['client_id']}&docId={test_params['doc_id']}"
        docrepo_headers = {
            "Authorization": f"Bearer {test_params['token']}",
            "Content-Type": "application/json"
        }
        
        print(f"   URL: {docrepo_url}")
        print(f"   Headers: {{'Authorization': '***masked***', 'Content-Type': 'application/json'}}")
        print()
        
        docrepo_response = requests.get(docrepo_url, headers=docrepo_headers, timeout=30)
        
        print(f"📊 DocRepo Response:")
        print(f"   Status Code: {docrepo_response.status_code}")
        print(f"   Headers: {dict(docrepo_response.headers)}")
        print()
        
        if docrepo_response.status_code == 200:
            docrepo_data = docrepo_response.json()
            
            print("📄 RAW DOCREPO RESPONSE:")
            print("-" * 50)
            print(json.dumps(docrepo_data, indent=2))
            print("-" * 50)
            print()
            
            # Extract taskId
            task_id = docrepo_data.get("taskId")
            print(f"✅ DocRepo extraction successful. Found TaskId: {task_id}")
            print()
            
            # STEP 2: Call get_task if taskId exists (this is where we stop)
            if task_id and test_params['taskdoc_api_token'] and test_params['taskdoc_auth_token']:
                print(f"📋 STEP 2: Calling get_task for TaskId: {task_id}")
                print(f"   TaskDoc Root URL: {agent.TASKDOC_ROOT_URL}")
                print(f"   API Token: {'***masked***'}")
                print(f"   Auth Token: {'***masked***'}")
                print()
                
                # Call get_task and show raw response
                task_details = agent.get_task(task_id, test_params['taskdoc_api_token'], test_params['taskdoc_auth_token'])
                
                print("🎯 RAW get_task RESPONSE:")
                print("=" * 60)
                print(json.dumps(task_details, indent=2, default=str))
                print("=" * 60)
                print()
                
                # Also show if there's a response field with more data
                if 'response' in task_details:
                    print("📋 DETAILED get_task RESPONSE DATA:")
                    print("=" * 60)
                    print(json.dumps(task_details['response'], indent=2, default=str))
                    print("=" * 60)
                
            elif task_id and (not test_params['taskdoc_api_token'] or not test_params['taskdoc_auth_token']):
                print(f"⚠️ TaskId found ({task_id}) but TASKDOC tokens not provided - cannot call get_task")
            else:
                print(f"⚠️ No TaskId found in DocRepo response - cannot call get_task")
                
        else:
            print(f"❌ DocRepo API failed with status {docrepo_response.status_code}")
            print(f"   Response text: {docrepo_response.text}")
        
    except Exception as e:
        print("💥 EXCEPTION OCCURRED:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print("   Full traceback:")
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("🏁 TEST COMPLETED - STOPPED AT get_task")
    print("=" * 80)
    print()
    print("📝 NOTES:")
    print("   - This script replicates steps 1-2 of push_doc method:")
    print("     1. ✅ DocRepo data extraction from ESFuse API")
    print("     2. ✅ get_task call to TaskDoc API (RAW RESPONSE SHOWN)")
    print("     3. ❌ SKIPPED: Submission creation (not executed)")
    print("   - Raw responses are displayed in full JSON format")
    print("   - Replace test parameters with real values for actual testing")

if __name__ == "__main__":
    test_get_task_only()
