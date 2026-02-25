import streamlit as st
from services.chat_service import process_user_input
from services.chroma_service import init_chroma

st.set_page_config(page_title="Datasynth", layout="wide", initial_sidebar_state="expanded")

# Initialize ChromaDB
init_chroma()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'knowledge_data' not in st.session_state:
    st.session_state.knowledge_data = {
        'business_understanding': [],
        'objectives': [],
        'constraints': [],
        'summary': ''
    }

# Sidebar
with st.sidebar:
    st.title("🔷 Datasynth")
    view = st.radio("Navigation", ["Chat", "Plan", "Visualization"], label_visibility="collapsed")

# Main layout
col1, col2 = st.columns([2, 1])

# Chat area
with col1:
    st.markdown("### Chat")
    
    # Messages container
    chat_container = st.container()
    with chat_container:
        if len(st.session_state.messages) == 0:
            st.info("👋 Hi there! Tell me about your business.\n\nYou can paste a URL to scrape business data, or just start chatting.")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                st.write(msg['content'])
    
    # Input area
    user_input = st.chat_input("What would you like to know?")
    
    if user_input:
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        
        with st.spinner('Thinking...'):
            response = process_user_input(user_input, st.session_state.messages)
            
        st.session_state.messages.append({'role': 'assistant', 'content': response['message']})
        
        if response.get('knowledge_update'):
            for key, value in response['knowledge_update'].items():
                if value:
                    st.session_state.knowledge_data[key] = value
        
        st.rerun()

# Knowledge Base panel
with col2:
    st.markdown("### 📚 Knowledge Base")
    
    with st.container():
        st.markdown("#### Business Understanding:")
        if st.session_state.knowledge_data['business_understanding']:
            for item in st.session_state.knowledge_data['business_understanding']:
                st.markdown(f"• {item}")
        else:
            st.markdown("• Information extracted from conversation")
            st.markdown("• Important details and context")
            st.markdown("• Another point")
        
        st.markdown("#### Objectives:")
        if st.session_state.knowledge_data['objectives']:
            for item in st.session_state.knowledge_data['objectives']:
                st.markdown(f"• {item}")
        else:
            st.markdown("• Outcome desired by user")
            st.markdown("• Another thing that the user wants to know")
            st.markdown("• Another point")
        
        st.markdown("#### Constraints:")
        if st.session_state.knowledge_data['constraints']:
            for item in st.session_state.knowledge_data['constraints']:
                st.markdown(f"• {item}")
        else:
            st.markdown("• Constraint 1")
            st.markdown("• Constraint 2")
        
        st.markdown("#### Summary:")
        summary = st.session_state.knowledge_data['summary'] or \
                  "A short summary that clearly shows the agent's understanding of the user problem statement and requirements."
        st.info(summary)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✏️ Edit", use_container_width=True):
                st.toast("Edit mode coming soon!")
        with col_b:
            if st.button("💾 Save", use_container_width=True):
                st.toast("Saved to ChromaDB!")

# Custom CSS
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
</style>
""", unsafe_allow_html=True)
