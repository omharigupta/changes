import streamlit as st
from services.chat_service import process_user_input, get_workflow_status
try:
    from services.chroma_service import init_chroma
except ImportError:
    def init_chroma(): pass

st.set_page_config(page_title="Datasynth KYB Chat", layout="wide", initial_sidebar_state="expanded")

# Initialize ChromaDB
try:
    init_chroma()
except:
    pass

# Initialize session state for KYB workflow
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'workflow_session_state' not in st.session_state:
    st.session_state.workflow_session_state = {}
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
    
    # Workflow Status
    if st.session_state.workflow_session_state:
        workflow_status = get_workflow_status(st.session_state.workflow_session_state)
        st.markdown("### 📋 Workflow Status")
        st.markdown(f"**Step:** {workflow_status.get('current_step', 1)}/8")
        
        step_names = {
            1: "Greeting", 2: "Business Info", 3: "Create KYB", 4: "Update KYB",
            5: "Continue Chat", 6: "Update KYB 2", 7: "Continue Chat 2", 8: "Check Complete"
        }
        current_step_name = step_names.get(workflow_status.get('current_step', 1), "Ongoing")
        st.markdown(f"**Current:** {current_step_name}")
        
        if workflow_status.get('business_info'):
            business = workflow_status['business_info'].get('what_they_sell', 'Not specified')
            st.markdown(f"**Business:** {business}")
    
    view = st.radio("Navigation", ["KYB Chat", "Analytics", "Export"], label_visibility="collapsed")
    
    # Reset conversation button
    if st.button("🔄 Start New KYB Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.workflow_session_state = {}
        st.session_state.knowledge_data = {
            'business_understanding': [],
            'objectives': [],
            'constraints': [],
            'summary': ''
        }
        st.rerun()

# Main layout
col1, col2 = st.columns([2, 1])

# Chat area
with col1:
    st.markdown("### 💬 KYB Conversation")
    
    # Messages container
    chat_container = st.container()
    with chat_container:
        if len(st.session_state.messages) == 0:
            # Show initial workflow message
            st.info("👋 Welcome to KYB (Know Your Business) Chat!\n\nI'll guide you through understanding your business needs step by step.")
            
            # Auto-start the workflow
            if not st.session_state.workflow_session_state:
                from services.workflow_service import WorkflowManager
                workflow_manager = WorkflowManager()
                initial_message = workflow_manager.get_initial_message()
                st.session_state.messages.append({'role': 'assistant', 'content': initial_message})
        
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                st.write(msg['content'])
    
    # Input area
    user_input = st.chat_input("Type your response here...")
    
    if user_input:
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        
        with st.spinner('Processing through KYB workflow...'):
            response = process_user_input(
                user_input, 
                st.session_state.messages, 
                st.session_state.workflow_session_state
            )
            
        st.session_state.messages.append({'role': 'assistant', 'content': response['message']})
        
        # Update workflow session state
        if 'session_state' in response:
            st.session_state.workflow_session_state = response['session_state']
        
        # Update knowledge data if available
        if response.get('knowledge_update'):
            for key, value in response['knowledge_update'].items():
                if value:
                    st.session_state.knowledge_data[key] = value
        
        st.rerun()

# Knowledge Base panel  
with col2:
    st.markdown("### 📚 KYB Profile")
    
    with st.container():
        # Show workflow progress
        if st.session_state.workflow_session_state:
            current_step = st.session_state.workflow_session_state.get('workflow_step', 1)
            progress = min(current_step / 8.0, 1.0)
            st.progress(progress, text=f"KYB Progress: {progress:.0%}")
        
        st.markdown("#### Business Understanding:")
        if st.session_state.knowledge_data['business_understanding']:
            for item in st.session_state.knowledge_data['business_understanding']:
                st.markdown(f"• {item}")
        else:
            st.markdown("• *Information will appear as we chat*")
            st.markdown("• *Business details and context*")
            st.markdown("• *Key insights about your business*")
        
        st.markdown("#### Objectives:")
        if st.session_state.knowledge_data['objectives']:
            for item in st.session_state.knowledge_data['objectives']:
                st.markdown(f"• {item}")
        else:
            st.markdown("• *Your goals and desired outcomes*")
            st.markdown("• *What you want to achieve*")
            st.markdown("• *Success metrics and targets*")
        
        st.markdown("#### Constraints:")
        if st.session_state.knowledge_data['constraints']:
            for item in st.session_state.knowledge_data['constraints']:
                st.markdown(f"• {item}")
        else:
            st.markdown("• *Challenges and limitations*")
            st.markdown("• *Resource constraints*")
            st.markdown("• *Technical or business barriers*")
        
        st.markdown("#### KYB Summary:")
        summary = st.session_state.knowledge_data['summary'] or \
                  "Your business profile will be built as we progress through the KYB workflow. I'll gather information about what you sell, your goals, and challenges to provide targeted insights."
        st.info(summary)
        
        # KYB File info
        if st.session_state.workflow_session_state.get('kyb_filepath'):
            st.markdown("#### 📁 KYB File:")
            kyb_file = st.session_state.workflow_session_state['kyb_filepath'].split('\\')[-1]
            st.code(kyb_file, language=None)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📊 View Details", use_container_width=True):
                if st.session_state.workflow_session_state:
                    status = get_workflow_status(st.session_state.workflow_session_state)
                    st.json(status)
        with col_b:
            if st.button("💾 Export KYB", use_container_width=True):
                st.toast("KYB export feature coming soon!")

# Custom CSS for KYB theme
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
    }
    .stChatMessage {
        background-color: #2a2a2a;
        border-radius: 12px;
    }
    [data-testid="stSidebar"] {
        background-color: #2a2a2a;
    }
    .stProgress .stProgressBar {
        background-color: #4CAF50;
    }
    .kyb-step {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        padding: 8px;
        border-radius: 8px;
        color: white;
        margin: 4px 0;
    }
</style>
""", unsafe_allow_html=True)
