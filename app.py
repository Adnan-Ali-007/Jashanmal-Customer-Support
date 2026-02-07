import streamlit as st
from dotenv import load_dotenv
from agents.agents import agent
from langchain_core.messages import HumanMessage, AIMessage
from db.database import get_db
import uuid
from datetime import datetime

# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()

# Initialize database
db = get_db()

st.set_page_config(
    page_title="Jashanmal Customer Support Assistant",
    page_icon="💬",
    layout="wide",
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Dark mode enhancements */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1d24;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #262730;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* User message */
    [data-testid="stChatMessageContent"] {
        color: #FAFAFA;
    }
    
    /* Conversation button styling */
    .stButton button {
        text-align: left;
        color: #FAFAFA !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0.75rem !important;
        transition: background-color 0.2s;
    }
    
    .stButton button:hover {
        background-color: #2d3139 !important;
    }
    
    /* Active conversation */
    .stButton button[kind="primary"] {
        background-color: #2d3139 !important;
        font-weight: 500;
        border-left: 3px solid #FF6B6B !important;
    }
    
    /* Delete button styling */
    .delete-btn button {
        color: #9ca3af !important;
        font-size: 1.2rem !important;
        padding: 0.5rem !important;
    }
    
    .delete-btn button:hover {
        color: #ef4444 !important;
        background-color: #3d1f1f !important;
    }
    
    /* Input box */
    .stChatInputContainer {
        background-color: #262730;
        border-radius: 10px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1d24;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4a4d57;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5a5d67;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FAFAFA !important;
    }
    
    /* Captions */
    .stCaption {
        color: #9ca3af !important;
    }
    
    /* Divider */
    hr {
        border-color: #2d3139 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for conversation history
with st.sidebar:
    st.markdown("### 💬 Chat History")
    
    # New conversation button
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        st.session_state.thread_id = f"thread-{uuid.uuid4()}"
        st.session_state.messages = []
        st.session_state.booking_slots = []
        st.session_state.awaiting_booking_confirmation = False
        st.session_state.awaiting_user_email = False
        st.session_state.selected_booking_slot = None
        db.create_conversation(st.session_state.thread_id, "New Conversation")
        st.rerun()
    
    st.divider()
    
    # Load all conversations
    conversations = db.get_all_conversations()
    
    if conversations:
        for conv in conversations:
            # Format timestamp
            updated = datetime.fromisoformat(conv['updated_at'])
            time_str = updated.strftime("%b %d")
            
            # Create container for each conversation
            col1, col2 = st.columns([5, 1])
            
            with col1:
                # Conversation title (truncate if too long)
                title = conv['title'][:40] + "..." if len(conv['title']) > 40 else conv['title']
                
                if st.button(
                    f"{title}",
                    key=f"conv_{conv['thread_id']}",
                    use_container_width=True,
                    help=f"Last updated: {time_str}",
                    type="primary" if conv['thread_id'] == st.session_state.get('thread_id') else "secondary"
                ):
                    # Load this conversation
                    st.session_state.thread_id = conv['thread_id']
                    
                    # Load messages from database
                    messages_data = db.get_messages(conv['thread_id'])
                    st.session_state.messages = []
                    
                    for msg in messages_data:
                        if msg['role'] == 'user':
                            st.session_state.messages.append(HumanMessage(content=msg['content']))
                        else:
                            st.session_state.messages.append(AIMessage(content=msg['content']))
                    
                    st.rerun()
            
            with col2:
                # Use × symbol like OpenAI
                if st.button("×", key=f"del_{conv['thread_id']}", help="Delete chat"):
                    db.delete_conversation(conv['thread_id'])
                    if conv['thread_id'] == st.session_state.get('thread_id'):
                        st.session_state.thread_id = f"thread-{uuid.uuid4()}"
                        st.session_state.messages = []
                    st.rerun()
    else:
        st.caption("No previous chats")

# Main chat area
st.title("💬 Jashanmal Customer Support")
st.caption("Ask anything about orders, payments, shipping, returns & more.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"thread-{uuid.uuid4()}"
    db.create_conversation(st.session_state.thread_id, "New Conversation")

if "booking_slots" not in st.session_state:
    st.session_state.booking_slots = []
    
if "awaiting_booking_confirmation" not in st.session_state:
    st.session_state.awaiting_booking_confirmation = False

if "awaiting_user_email" not in st.session_state:
    st.session_state.awaiting_user_email = False
    
if "selected_booking_slot" not in st.session_state:
    st.session_state.selected_booking_slot = None
    
    
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)
            
            
user_input = st.chat_input("How can I help you today?")

if user_input:
    # Save user message to database
    db.save_message(st.session_state.thread_id, "user", user_input)
    
    # Update conversation title if this is the first message
    if len(st.session_state.messages) == 0:
        title = db.generate_title_from_first_message(st.session_state.thread_id)
        db.update_conversation_title(st.session_state.thread_id, title)
    
    # Check if user is providing their email for booking
    if st.session_state.awaiting_user_email and st.session_state.selected_booking_slot:
        # Validate email format (basic check)
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, user_input.strip()):
            user_email = user_input.strip()
            selected_slot = st.session_state.selected_booking_slot
            
            human_msg = HumanMessage(content=user_input)
            st.session_state.messages.append(human_msg)
            
            with st.chat_message("user"):
                st.markdown(user_input)
            
            with st.chat_message("assistant"):
                status_placeholder = st.empty()
                status_placeholder.markdown("📅 *Creating your meeting...*")
                
                # Create the meeting with attendee email
                from booking.calendar_service import get_calendar_service
                calendar = get_calendar_service()
                
                meeting_link = calendar.create_meeting(
                    summary="Customer Support Meeting",
                    start_time=selected_slot['start'],
                    duration_minutes=30,
                    description=f"Meeting booked through Jashanmal Support Assistant\nAttendee: {user_email}",
                    attendee_email=user_email
                )
                
                status_placeholder.empty()
                
                if meeting_link:
                    response = f"✅ Perfect! Your meeting has been booked for **{selected_slot['display']}**.\n\n📅 [View in Google Calendar]({meeting_link})\n\n📧 A calendar invitation has been sent to **{user_email}**.\n\nIs there anything else I can help you with?"
                else:
                    response = "I'm sorry, there was an issue creating the meeting. Please try again or contact us directly at:\n\n📧 Email: support@jashanmal.com\n📞 Call: 800 562 63"
                
                st.markdown(response)
                ai_msg = AIMessage(content=response)
                st.session_state.messages.append(ai_msg)
                
                # Save AI response to database
                db.save_message(st.session_state.thread_id, "assistant", response)
                
                # Reset booking state
                st.session_state.awaiting_user_email = False
                st.session_state.awaiting_booking_confirmation = False
                st.session_state.selected_booking_slot = None
                st.session_state.booking_slots = []
                st.stop()
        else:
            # Invalid email format
            human_msg = HumanMessage(content=user_input)
            st.session_state.messages.append(human_msg)
            
            with st.chat_message("user"):
                st.markdown(user_input)
            
            with st.chat_message("assistant"):
                response = "⚠️ That doesn't look like a valid email address. Please provide a valid email (e.g., yourname@example.com) so I can send you the calendar invitation."
                st.markdown(response)
                ai_msg = AIMessage(content=response)
                st.session_state.messages.append(ai_msg)
                
                # Save to database
                db.save_message(st.session_state.thread_id, "assistant", response)
                st.stop()
    
    # Check if user is selecting a booking slot
    if st.session_state.awaiting_booking_confirmation and st.session_state.booking_slots:
        try:
            slot_number = int(user_input.strip())
            if 1 <= slot_number <= len(st.session_state.booking_slots):
                # User selected a valid slot - now ask for email
                selected_slot = st.session_state.booking_slots[slot_number - 1]
                
                human_msg = HumanMessage(content=user_input)
                st.session_state.messages.append(human_msg)
                
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    response = f"Great choice! You've selected **{selected_slot['display']}**.\n\n📧 Please provide your email address so I can send you the calendar invitation."
                    st.markdown(response)
                    ai_msg = AIMessage(content=response)
                    st.session_state.messages.append(ai_msg)
                    
                    # Save to database
                    db.save_message(st.session_state.thread_id, "assistant", response)
                    
                    # Update state to await email
                    st.session_state.selected_booking_slot = selected_slot
                    st.session_state.awaiting_user_email = True
                    st.session_state.awaiting_booking_confirmation = False
                    st.stop()
        except ValueError:
            # Not a number, continue with normal flow
            pass
    
    human_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(human_msg)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        status_placeholder = st.empty()
        
        full_response = ""
        streaming_response = ""
        is_answer_node = False
        
        # Stream through agent nodes
        for chunk in agent.stream(
            {"query": user_input},
            config={
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            },
            stream_mode="updates"
        ):
            # Show which node is processing
            node_name = list(chunk.keys())[0] if chunk else ""
            
            if node_name == "router":
                status_placeholder.markdown("🔍 *Analyzing your question...*")
            elif node_name == "retrieve":
                status_placeholder.markdown("📚 *Searching knowledge base...*")
            elif node_name == "answer":
                is_answer_node = True
                status_placeholder.markdown("✍️ *Generating response...*")
                
                if "answer" in chunk.get(node_name, {}):
                    full_response = chunk[node_name]["answer"]
                    
            elif node_name == "contact":
                if "answer" in chunk.get(node_name, {}):
                    full_response = chunk[node_name]["answer"]
            elif node_name == "booking":
                if "answer" in chunk.get(node_name, {}):
                    full_response = chunk[node_name]["answer"]
                # Store booking slots if available
                if "booking_slots" in chunk.get(node_name, {}):
                    st.session_state.booking_slots = chunk[node_name]["booking_slots"]
                    st.session_state.awaiting_booking_confirmation = True
            elif node_name == "order_tracking":
                status_placeholder.markdown("📦 *Checking order status...*")
                if "answer" in chunk.get(node_name, {}):
                    full_response = chunk[node_name]["answer"]
            elif node_name == "return_request":
                status_placeholder.markdown("🔄 *Processing return request...*")
                if "answer" in chunk.get(node_name, {}):
                    full_response = chunk[node_name]["answer"]
            elif node_name == "refund_status":
                status_placeholder.markdown("💰 *Checking refund status...*")
                if "answer" in chunk.get(node_name, {}):
                    full_response = chunk[node_name]["answer"]
            elif node_name == "greeting":
                if "answer" in chunk.get(node_name, {}):
                    full_response = chunk[node_name]["answer"]
            elif node_name == "fallback":
                if "answer" in chunk.get(node_name, {}):
                    full_response = chunk[node_name]["answer"]
        
        # Clear status
        status_placeholder.empty()
        
        if not full_response:
            full_response = "Sorry, something went wrong."
        
        # Stream the response word by word for better UX
        if full_response:
            import time
            words = full_response.split()
            streaming_response = ""
            
            for word in words:
                streaming_response += word + " "
                response_placeholder.markdown(streaming_response + "▌")
                time.sleep(0.02)  # Adjust speed (0.02 = 50 words/sec)
            
            # Show final response without cursor
            response_placeholder.markdown(full_response)
        
        ai_msg = AIMessage(content=full_response)
        st.session_state.messages.append(ai_msg)
        
        # Save AI response to database
        db.save_message(st.session_state.thread_id, "assistant", full_response)