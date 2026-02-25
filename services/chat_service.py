import re
from services.gemini_service import analyze_with_gemini
from services.scraper_service import scrape_url
from services.workflow_service import WorkflowManager

# Initialize workflow manager
workflow_manager = WorkflowManager()

def process_user_input(user_input, conversation_history, session_state=None):
    """Process user input using hardcoded KYB workflow"""
    
    # Initialize session_state if not provided
    if session_state is None:
        session_state = {}
    
    # Check if this is the first message
    if not conversation_history or len(conversation_history) == 0:
        return {
            'message': workflow_manager.get_initial_message(),
            'session_state': session_state,
            'knowledge_update': extract_knowledge_for_display(session_state)
        }
    
    # Process through hardcoded workflow (handles URLs internally)
    response_message, updated_session_state = workflow_manager.process_workflow_step(
        user_input, session_state
    )
    
    return {
        'message': response_message,
        'session_state': updated_session_state,
        'knowledge_update': extract_knowledge_for_display(updated_session_state)
    }

def extract_knowledge_for_display(session_state):
    """Extract knowledge data for display in the sidebar"""
    if not session_state or 'kyb_data' not in session_state:
        return {
            'business_understanding': [],
            'objectives': [],
            'constraints': [],
            'summary': ''
        }
    
    kyb_data = session_state['kyb_data']
    
    return {
        'business_understanding': kyb_data.get('business_understanding', []),
        'objectives': kyb_data.get('objectives', []),
        'constraints': kyb_data.get('constraints', []),
        'summary': kyb_data.get('summary', f"Progress: Step {session_state.get('workflow_step', 1)}/8")
    }

def get_workflow_status(session_state):
    """Get current workflow status for debugging"""
    return {
        'current_step': session_state.get('workflow_step', 1),
        'session_id': session_state.get('session_id', 'Not set'),
        'kyb_file': session_state.get('kyb_filepath', 'Not created'),
        'business_info': session_state.get('what_they_sell', 'Not specified')
    }
