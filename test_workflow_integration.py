#!/usr/bin/env python3
"""
Test the integrated KYB workflow with URL scraping
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.workflow_service import WorkflowManager

def test_workflow():
    """Test the 8-step KYB workflow"""
    
    print("🧪 Testing KYB Workflow Integration")
    print("=" * 50)
    
    # Initialize workflow
    wf = WorkflowManager()
    session_state = {'current_step': 1, 'kyb_data': {}}
    
    # Test Step 1
    print("\n📋 Step 1: Initial Question")
    response1, updated_state = wf.process_workflow_step("", session_state)
    print(f"Response: {response1}")
    print(f"Expected to contain: Hi, what do you sell?")
    print(f"✅ Match: {'what do you sell' in response1.lower()}")
    
    # Test user response
    print("\n💬 User Response to Step 1:")
    session_state['current_step'] = 2
    response2, updated_state = wf.process_workflow_step("I make ai os", session_state)
    print(f"Bot Response: {response2}")
    print(f"Current Step: {updated_state.get('current_step', 'Unknown')}")
    
    # Test URL input (Step 4 should handle URL input well)
    print("\n🌐 Testing URL Input at Step 4:")
    session_state['current_step'] = 4
    response3, updated_state = wf.process_workflow_step("Check out https://nfsu.ac.in for more info", session_state)
    print(f"Response: {response3[:200]}...")
    print(f"URL Processing: {'URL' in str(response3) or 'website' in str(response3) or 'scraped' in str(response3)}")
    
    # Test workflow progression
    print(f"\n📊 Workflow Status:")
    print(f"Initial Step: 1")
    print(f"Current Step: {updated_state.get('current_step', 'Unknown')}")
    print(f"Total Steps: 8")
    print(f"Has KYB Data: {'kyb_data' in updated_state}")
    
    print("\n✅ Test Complete!")

if __name__ == "__main__":
    test_workflow()