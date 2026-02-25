import streamlit as st
from services.chat_service import process_user_input, get_workflow_status

st.set_page_config(page_title="Datasynth KYB Chat", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_state' not in st.session_state:
    st.session_state.session_state = {}
if 'knowledge_data' not in st.session_state:
    st.session_state.knowledge_data = {
        'business_understanding': [],
        'objectives': [],
        'constraints': [],
        'summary': ''
    }

# Sidebar
with st.sidebar:
    st.title("🔷 Datasynth KYB")
    st.info("Know Your Business Chat")
    st.markdown("---")
    
    # Show workflow progress
    workflow_status = get_workflow_status(st.session_state.session_state)
    st.markdown("**Workflow Progress:**")
    st.write(f"Step: {workflow_status['current_step']}/8")
    st.write(f"Business: {workflow_status['business_info']}")
    
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("• Answer the guided questions")
    st.markdown("• Or paste a URL to scrape business data")
    st.markdown("• View your business profile build in real-time")

# Main layout
col1, col2 = st.columns([2, 1])

# Chat area
with col1:
    st.markdown("### KYB Chat")
    
    # Initialize with greeting if no messages
    if len(st.session_state.messages) == 0:
        initial_msg = {"role": "assistant", "content": "Hi! 👋 What do you sell? (You can also paste a URL to scrape your business website)"}
        st.session_state.messages.append(initial_msg)
    
    # Display all messages
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.write(msg['content'])
    
    # Input area
    user_input = st.chat_input("Your response (or paste a URL)...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        
        with st.spinner('Processing...'):
            # Process through KYB workflow
            result = process_user_input(
                user_input, 
                st.session_state.messages,
                st.session_state.session_state
            )
            
            # Update session state
            st.session_state.session_state = result['session_state']
            
            # Update knowledge data if available
            if result.get('knowledge_update'):
                st.session_state.knowledge_data = result['knowledge_update']
            
            # Add assistant response
            st.session_state.messages.append({
                'role': 'assistant', 
                'content': result['message']
            })
            
            st.rerun()

# Knowledge Base area
with col2:
    st.markdown("### Your Business Profile")
    
    if st.session_state.knowledge_data['summary']:
        st.markdown("**Summary:**")
        st.info(st.session_state.knowledge_data['summary'])
    else:
        st.info("💡 Your business insights will appear here as we chat")
    
    if st.session_state.knowledge_data['business_understanding']:
        st.markdown("**Business Understanding:**")
        for i, item in enumerate(st.session_state.knowledge_data['business_understanding']):
            st.write(f"{i+1}. {item}")
    
    if st.session_state.knowledge_data['objectives']:
        st.markdown("**Objectives:**")
        for i, item in enumerate(st.session_state.knowledge_data['objectives']):
            st.write(f"🎯 {item}")
    
    if st.session_state.knowledge_data['constraints']:
        st.markdown("**Challenges:**")
        for i, item in enumerate(st.session_state.knowledge_data['constraints']):
            st.write(f"⚠️ {item}")
    
    # Show KYB file info if created
    if st.session_state.session_state.get('kyb_filepath'):
        st.markdown("---")
        st.success(f"✅ KYB File: `{st.session_state.session_state['kyb_filepath']}`")

# Debug info (can be removed in production)
if st.checkbox("Show Debug Info"):
    st.json({
        "workflow_status": workflow_status,
        "session_state_keys": list(st.session_state.session_state.keys()),
        "message_count": len(st.session_state.messages)
    })