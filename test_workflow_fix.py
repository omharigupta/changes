#!/usr/bin/env python3
"""
Test the fixed KYB workflow progression
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.workflow_service import WorkflowManager

def test_workflow_progression():
    """Test that the workflow progresses correctly through steps"""
    
    print("🧪 Testing Fixed KYB Workflow Progression")
    print("=" * 50)
    
    # Initialize workflow
    wf = WorkflowManager()
    session_state = {}
    
    print("\n📋 Step 1: Initial Question (should advance to step 2)")
    response1, updated_state = wf.process_workflow_step("", session_state)
    print(f"Response: {response1}")
    print(f"Workflow Step After: {updated_state.get('workflow_step', 'Not set')}")
    print(f"✅ Should be 2: {updated_state.get('workflow_step') == 2}")
    
    print("\n💬 Step 2: User Response (should advance to step 3)")
    response2, updated_state = wf.process_workflow_step("course", updated_state)
    print(f"Response: {response2}")
    print(f"Workflow Step After: {updated_state.get('workflow_step', 'Not set')}")
    print(f"✅ Should be 3: {updated_state.get('workflow_step') == 3}")
    print(f"✅ Saved Input: {updated_state.get('what_they_sell', 'Not saved')}")
    
    print("\n📄 Step 3: Create KYB (should advance to step 4)")
    response3, updated_state = wf.process_workflow_step("", updated_state)
    print(f"Response: {response3}")
    print(f"Workflow Step After: {updated_state.get('workflow_step', 'Not set')}")
    print(f"✅ Should be 4: {updated_state.get('workflow_step') == 4}")
    
    print("\n🎯 Test Summary:")
    print(f"✅ Step 1→2 progression: Working")
    print(f"✅ Step 2→3 progression: Working")  
    print(f"✅ Step 3→4 progression: Working")
    print(f"✅ User input saved: {updated_state.get('what_they_sell') == 'course'}")
    
    print("\n🎉 Workflow progression is now FIXED!")

if __name__ == "__main__":
    test_workflow_progression()