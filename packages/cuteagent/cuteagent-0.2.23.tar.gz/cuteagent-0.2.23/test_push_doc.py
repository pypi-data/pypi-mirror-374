#!/usr/bin/env python3
"""
Test script for DocumentAgent push_doc method
Tests document submission workflow with DocRepo extraction and TaskDoc integration.
"""

from cuteagent.cuteagent import DocumentAgent
import json

def test_push_doc():
    """Test the push_doc method for document submission"""
    print("=" * 80)
    print("📤 TESTING DOCUMENT AGENT - push_doc METHOD")
    print("=" * 80)
    
    # Initialize DocumentAgent
    agent = DocumentAgent()
    
    # Test parameters
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
    print(f"   Submission Type: {test_params['submission_type']}")
    print(f"   Auto Lock: {test_params['auto_lock']}")
    print(f"   ESFuse Token: {'***masked***' if test_params['token'] else 'None'}")
    print(f"   TaskDoc API Token: {'***masked***' if test_params['taskdoc_api_token'] else 'None'}")
    print(f"   TaskDoc Auth Token: {'***masked***' if test_params['taskdoc_auth_token'] else 'None'}")
    print()
    
    print("🚀 Calling push_doc method...")
    print("   Step 1: Extract DocRepo data from API")
    print("   Step 2: Get task details using TaskDoc API (if taskId found)")
    print("   Step 3: Create submission using extracted document IDs")
    print()
    
    try:
        # Call the push_doc method
        result = agent.ESFuse.push_doc(
            submission_type=test_params['submission_type'],
            auto_lock=test_params['auto_lock'],
            client_id=test_params['client_id'],
            doc_id=test_params['doc_id'],
            token=test_params['token'],
            api_base=test_params['api_base'],
            taskdoc_api_token=test_params['taskdoc_api_token'],
            taskdoc_auth_token=test_params['taskdoc_auth_token']
        )
        
        # Display results
        print("📊 PUSH_DOC RESULTS:")
        print("-" * 50)
        
        if result.get("success"):
            print("✅ push_doc successful!")
            print(f"   Message: {result.get('message')}")
            print()
            
            # Show DocRepo fields
            docrepo_fields = result.get("docrepo_fields", {})
            if docrepo_fields:
                print("📋 DOCREPO EXTRACTION RESULTS:")
                print("-" * 40)
                
                # Basic DocRepo fields
                print(f"   Task ID: {docrepo_fields.get('taskId', 'N/A')}")
                print(f"   Loan ID: {docrepo_fields.get('loanId', 'N/A')}")
                print(f"   Client ID: {docrepo_fields.get('clientId', 'N/A')}")
                print(f"   Doc ID: {docrepo_fields.get('docId', 'N/A')}")
                print(f"   Has Task ID: {docrepo_fields.get('hasTaskId', 'N/A')}")
                print(f"   Has Loan ID: {docrepo_fields.get('hasLoanId', 'N/A')}")
                print(f"   Has Data Object: {docrepo_fields.get('hasDataObject', 'N/A')}")
                print(f"   URL: {docrepo_fields.get('url', 'N/A')}")
                print()
                
                # TaskDoc integration results
                if 'task_details' in docrepo_fields:
                    print("📋 TASKDOC INTEGRATION RESULTS:")
                    print("-" * 40)
                    task_details = docrepo_fields['task_details']
                    print(f"   Task Status: {task_details.get('status', 'N/A')}")
                    print(f"   Fallback Used: {task_details.get('fallback_used', 'N/A')}")
                    
                    # Show extracted TaskDoc fields
                    if 'taskdoc_document_ids' in docrepo_fields:
                        doc_ids = docrepo_fields['taskdoc_document_ids']
                        print(f"   Document IDs: {len(doc_ids)} documents")
                        if doc_ids:
                            print(f"      IDs: {doc_ids[:5]}{'...' if len(doc_ids) > 5 else ''}")
                    
                    if 'taskdoc_loan_id' in docrepo_fields:
                        print(f"   TaskDoc Loan ID: {docrepo_fields['taskdoc_loan_id']}")
                    
                    if 'taskdoc_root_url' in docrepo_fields:
                        print(f"   TaskDoc Root URL: {docrepo_fields['taskdoc_root_url']}")
                    
                    if 'taskdoc_workflow_state' in docrepo_fields:
                        print(f"   Workflow State: {docrepo_fields['taskdoc_workflow_state']}")
                    
                    if 'taskdoc_assignee' in docrepo_fields:
                        assignee = docrepo_fields['taskdoc_assignee']
                        print(f"   Assignee: {assignee.get('first_name')} {assignee.get('last_name')} ({assignee.get('username')})")
                    print()
                
                # Submission results
                if 'submission_result' in docrepo_fields:
                    print("📤 SUBMISSION RESULTS:")
                    print("-" * 40)
                    submission = docrepo_fields['submission_result']
                    print(f"   Success: {submission.get('success')}")
                    print(f"   Status Code: {submission.get('status_code', 'N/A')}")
                    
                    if submission.get('success'):
                        print("   ✅ Submission created successfully!")
                        if 'response' in submission:
                            response = submission['response']
                            if isinstance(response, dict) and 'details' in response:
                                details = response['details'].get('submission', {})
                                if details:
                                    print(f"      Submission ID: {details.get('id', 'N/A')}")
                                    print(f"      Submission Name: {details.get('name', 'N/A')}")
                                    print(f"      Locked: {details.get('locked', 'N/A')}")
                    else:
                        print(f"   ❌ Submission failed: {submission.get('error', 'Unknown error')}")
                        
                        # Print response text if available
                        if 'response_text' in submission:
                            print(f"\n📄 SUBMISSION RESPONSE TEXT:")
                            print(f"   {submission['response_text']}")
                    
                    # Show submission URL and body for debugging
                    if 'submission_url' in submission:
                        print(f"   Submission URL: {submission['submission_url']}")
                    if 'submission_body' in submission:
                        body = submission['submission_body']
                        print(f"   Document Count in Body: {len(body.get('document_ids', []))}")
                        
                        # Print the complete submission body
                        print(f"\n📋 COMPLETE SUBMISSION BODY:")
                        submission_body_json = json.dumps(body, indent=2)
                        print(submission_body_json)
                    print()
                
                # Show full DocRepo fields (truncated)
                print("📄 FULL DOCREPO FIELDS (JSON - first 1000 chars):")
                docrepo_json = json.dumps(docrepo_fields, indent=2, default=str)
                print(docrepo_json[:1000] + "..." if len(docrepo_json) > 1000 else docrepo_json)
        else:
            print("❌ push_doc failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print("💥 EXCEPTION OCCURRED:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print("   Full traceback:")
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("🏁 PUSH_DOC TEST COMPLETED")
    print("=" * 80)
    print()
    print("📝 NOTES:")
    print("   - This method performs a complex 3-step workflow:")
    print("     1. DocRepo data extraction from ESFuse API")
    print("     2. TaskDoc integration to get task details and document IDs")
    print("     3. Submission creation using extracted document IDs")
    print("   - Requires valid tokens for both ESFuse and TaskDoc APIs")
    print("   - Returns comprehensive results including submission status")
    print("   - Replace test parameters with real values for actual testing")
    print("   - auto_lock parameter controls whether submission is locked after creation")

if __name__ == "__main__":
    test_push_doc()
