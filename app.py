import streamlit as st
from dotenv import load_dotenv
from agents.agents import agent
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()


st.set_page_config(
    page_title="Jashanmal customer Support Assistant",
    page_icon="💬",
    layout="centered",
)

st.title("💬 Jashanmal Customer Support")
st.caption("Ask anything about orders, payments, shipping, returns & more.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    # for future persistence / checkpoints
    st.session_state.thread_id = "demo-thread-1"

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