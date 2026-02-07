from typing import TypedDict, List
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import re

# Add ingestion folder to path for imports
sys.path.append(str(Path(__file__).parent.parent / "ingestion"))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from gemini_embeddings import GeminiEmbeddings

# Import mock e-commerce backend
from demo.mock_ecommerce import get_mock_backend

# --------------------------------------------------
# ENV
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# LLM — GEMINI TIER 1 (NO OPENROUTER, NO OPENAI)
# --------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Updated to available model
    temperature=0,
    streaming=True,   # Enable streaming for better UX
    google_api_key=os.environ["GOOGLE_API_KEY"],
)

# --------------------------------------------------
# VECTORSTORE (already built)
# --------------------------------------------------
VECTORSTORE_PATH = "data/processed/faiss_index"

# Use LangChain's GoogleGenerativeAIEmbeddings instead of custom wrapper
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# --------------------------------------------------
# STATE
# --------------------------------------------------
class AgentState(TypedDict):
    query: str
    route: str
    docs: List[Document]
    answer: str
    booking_slots: List[dict]  # For calendar slots

# --------------------------------------------------
# ROUTER NODE
# --------------------------------------------------
ROUTER_PROMPT = """
You are a router for a customer support assistant.

Classify the query into ONE word only:
- rag : orders, payments, shipping, returns, gift cards, company info, product questions
- contact : contact us, customer support, help, phone number, email, whatsapp, reach out, get in touch
- booking : booking calls or meetings, schedule appointment
- order_tracking : track order, where is my order, order status, delivery status, tracking number, check status, status of order
- return_request : return item, return order, want to return, initiate return
- refund_status : refund status, where is my refund, refund processing
- greeting : hi, hello, hey, thanks, thank you, goodbye, bye, ok, okay, yes, no (simple greetings/acknowledgments)
- fallback : anything else not related to customer support

IMPORTANT: If query mentions "status" with an order number (like "status ORD-12345"), classify as order_tracking.

Return ONLY one word.
"""

def router_node(state: AgentState) -> AgentState:
    res = llm.invoke(
        ROUTER_PROMPT + f"\n\nQuery: {state['query']}"
    )

    route = res.content.strip().lower()
    if route not in {"rag", "contact", "booking", "order_tracking", "return_request", "refund_status", "greeting", "fallback"}:
        route = "fallback"

    return {**state, "route": route}

# --------------------------------------------------
# RETRIEVE NODE
# --------------------------------------------------
def retrieve_node(state: AgentState) -> AgentState:
    docs = retriever.invoke(state["query"])
    return {**state, "docs": docs}

# --------------------------------------------------
# ANSWER NODE — STRICT RAG (NO HALLUCINATION)
# --------------------------------------------------
ANSWER_PROMPT = """
You are a Jashanmal customer support assistant.

Use the provided context to answer the user's question. The context contains Q&A pairs from our help documentation.

RULES:
- Answer based on the provided context
- Combine information from multiple Q&A pairs if relevant
- Be helpful and conversational while staying accurate
- If the context doesn't contain relevant information, say: "I don't have specific information about that in our help content."

Context:
{context}

User question:
{question}

Answer:
"""

def answer_node(state: AgentState) -> AgentState:
    if not state.get("docs"):
        return {
            **state,
            "answer": "This information is not available in our help content."
        }

    context = "\n\n".join(doc.page_content for doc in state["docs"])

    # Use streaming for token-by-token generation
    full_answer = ""
    for chunk in llm.stream(
        ANSWER_PROMPT.format(
            context=context,
            question=state["query"]
        )
    ):
        full_answer += chunk.content

    return {**state, "answer": full_answer.strip()}

# --------------------------------------------------
# CONTACT NODE
# --------------------------------------------------
def contact_node(state: AgentState) -> AgentState:
    return {
        **state,
        "answer": (
            "Need assistance?\n\n"
            "Our Customer Support team is available from 9am - 6pm, Monday to Friday.\n\n"
            "📱 WhatsApp us: +971 800 562 63\n"
            "📧 Email us: support@jashanmal.com\n"
            "📞 Call us: 800 562 63"
        )
    }

# --------------------------------------------------
# BOOKING NODE (WITH GOOGLE CALENDAR)
# --------------------------------------------------
def booking_node(state: AgentState) -> AgentState:
    """Handle meeting booking requests"""
    try:
        from booking.calendar_service import get_calendar_service
        
        calendar = get_calendar_service()
        slots = calendar.get_available_slots(days_ahead=7)
        
        if slots:
            slots_text = "\n".join([
                f"**{i+1}.** {slot['display']}" 
                for i, slot in enumerate(slots[:5])
            ])
            
            answer = (
                "I'd be happy to help you book a meeting! 📅\n\n"
                "Here are the next available time slots:\n\n"
                f"{slots_text}\n\n"
                "**Please reply with the number (1-5) of your preferred slot**, "
                "and I'll schedule the meeting for you."
            )
            
            return {
                **state,
                "answer": answer,
                "booking_slots": slots[:5]
            }
        else:
            return {
                **state,
                "answer": (
                    "I'd like to help you book a meeting, but I'm having trouble "
                    "accessing the calendar right now. Please contact us directly:\n\n"
                    "📧 Email: support@jashanmal.com\n"
                    "📞 Call: 800 562 63"
                )
            }
            
    except Exception as e:
        print(f"Booking error: {e}")
        return {
            **state,
            "answer": (
                "I can help with booking requests. "
                "Please share your preferred date and time, or contact us at:\n\n"
                "📧 Email: support@jashanmal.com\n"
                "📞 Call: 800 562 63"
            )
        }

# --------------------------------------------------
# GREETING NODE
# --------------------------------------------------
def greeting_node(state: AgentState) -> AgentState:
    """Handle greetings and casual messages naturally"""
    
    GREETING_PROMPT = """
You are a friendly customer support assistant for Jashanmal.

The user said: "{query}"

Respond naturally and warmly. Keep it brief (1-2 sentences).

Guidelines:
- For "hi/hello/hey": Greet warmly and ask how you can help
- For "thanks/thank you": Acknowledge warmly and offer further help
- For "ok/okay/yes/no": Respond naturally and ask if they need anything else
- For "bye/goodbye": Say goodbye warmly
- Be conversational, not robotic
- Don't list all services unless asked

Examples:
User: "hi" → "Hi there! 👋 How can I help you today?"
User: "thanks" → "You're welcome! 😊 Let me know if you need anything else."
User: "ok" → "Great! Is there anything else I can help you with?"
"""
    
    response = llm.invoke(
        GREETING_PROMPT.format(query=state['query'])
    )
    
    return {
        **state,
        "answer": response.content.strip()
    }

# --------------------------------------------------
# FALLBACK NODE
# --------------------------------------------------
def fallback_node(state: AgentState) -> AgentState:
    """Handle off-topic queries with a friendly redirect"""
    
    FALLBACK_PROMPT = """
You are a friendly customer support assistant for Jashanmal.

The user asked: "{query}"

This is outside your scope (you help with orders, payments, shipping, returns, gift cards, company info, contact details, and booking meetings).

Respond warmly but redirect them to what you CAN help with. Keep it brief and natural (2-3 sentences max).

Example:
User: "What's the weather?" → "I'm focused on helping with Jashanmal customer support, so I can't help with weather info. But I'd be happy to help with your orders, shipping questions, or booking a support call! What can I assist you with?"
"""
    
    response = llm.invoke(
        FALLBACK_PROMPT.format(query=state['query'])
    )
    
    return {
        **state,
        "answer": response.content.strip()
    }

# --------------------------------------------------
# ORDER TRACKING NODE (DEMO)
# --------------------------------------------------
def extract_order_id(query: str) -> str:
    """Extract order ID from query"""
    # Look for patterns like ORD-12345, #12345, order 12345
    patterns = [
        r'ORD-\d+',
        r'#\s*(\d+)',
        r'order\s+(\d+)',
        r'\b\d{5}\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            if 'ORD-' in match.group():
                return match.group()
            else:
                # Extract just the number and format it
                number = re.search(r'\d+', match.group()).group()
                return f"ORD-{number}"
    
    return None

def order_tracking_node(state: AgentState) -> AgentState:
    """Handle order tracking requests using mock backend"""
    
    backend = get_mock_backend()
    order_id = extract_order_id(state['query'])
    
    if not order_id:
        return {
            **state,
            "answer": (
                "I can help you track your order! 📦\n\n"
                "Please provide your order number (e.g., ORD-12345 or #12345) "
                "so I can look up the tracking information for you."
            )
        }
    
    tracking_info = backend.track_order(order_id)
    
    if not tracking_info:
        return {
            **state,
            "answer": (
                f"I couldn't find order {order_id} in our system. 🔍\n\n"
                "Please double-check your order number or contact us at:\n\n"
                "📧 Email: support@jashanmal.com\n"
                "📞 Call: 800 562 63"
            )
        }
    
    # Build response based on status
    status = tracking_info['status']
    
    if status == "delivered":
        answer = (
            f"✅ Great news! Your order {order_id} has been **delivered**!\n\n"
            f"📅 Delivered on: {tracking_info['delivery_date']}\n"
            f"📦 Tracking: {tracking_info['tracking_number']}\n"
            f"🚚 Carrier: {tracking_info['carrier']}\n\n"
            "If you have any issues with your order, I can help you initiate a return!"
        )
    elif status == "shipped":
        answer = (
            f"📦 Your order {order_id} is **on its way**!\n\n"
            f"🚚 Carrier: {tracking_info['carrier']}\n"
            f"📦 Tracking: {tracking_info['tracking_number']}\n"
            f"📅 Estimated delivery: {tracking_info['estimated_delivery']}\n\n"
            f"Track your package: https://track.example.com/{tracking_info['tracking_number']}"
        )
    else:  # processing
        answer = (
            f"⏳ Your order {order_id} is being **processed**.\n\n"
            f"📅 Estimated delivery: {tracking_info['estimated_delivery']}\n\n"
            "We'll send you tracking information once it ships!"
        )
    
    # Send WhatsApp notification
    try:
        from notifications.whatsapp_service import get_whatsapp_service
        import os
        
        whatsapp = get_whatsapp_service()
        
        # Get customer number from env
        customer_number = os.getenv("YOUR_WHATSAPP_NUMBER", "whatsapp:+917780879882")
        
        print(f"[DEBUG] Attempting WhatsApp notification to: {customer_number}")
        print(f"[DEBUG] Order status: {status}")
        
        if status == "shipped":
            success = whatsapp.send_shipping_update(
                customer_number,
                order_id,
                tracking_info['tracking_number'],
                tracking_info['carrier']
            )
            print(f"[DEBUG] WhatsApp shipped notification: {'✓ Sent' if success else '✗ Failed'}")
        elif status == "delivered":
            success = whatsapp.send_delivered_notification(
                customer_number,
                order_id
            )
            print(f"[DEBUG] WhatsApp delivered notification: {'✓ Sent' if success else '✗ Failed'}")
    except Exception as e:
        print(f"[ERROR] WhatsApp notification failed: {e}")
        import traceback
        traceback.print_exc()
    
    return {**state, "answer": answer}

# --------------------------------------------------
# RETURN REQUEST NODE (DEMO)
# --------------------------------------------------
def return_request_node(state: AgentState) -> AgentState:
    """Handle return requests using mock backend"""
    
    backend = get_mock_backend()
    order_id = extract_order_id(state['query'])
    
    if not order_id:
        return {
            **state,
            "answer": (
                "I can help you with returns! 🔄\n\n"
                "Please provide your order number (e.g., ORD-12345) "
                "so I can check if it's eligible for return."
            )
        }
    
    # Check eligibility
    eligibility = backend.check_return_eligibility(order_id)
    
    if not eligibility['eligible']:
        return {
            **state,
            "answer": (
                f"I'm sorry, order {order_id} is not eligible for return.\n\n"
                f"**Reason:** {eligibility['reason']}\n\n"
                "If you have questions, please contact us at:\n"
                "📧 Email: support@jashanmal.com\n"
                "📞 Call: 800 562 63"
            )
        }
    
    # Create return
    return_result = backend.create_return(
        order_id,
        items=["all"],
        reason="Customer request"
    )
    
    if return_result['success']:
        answer = (
            f"✅ Return approved for order {order_id}!\n\n"
            f"**Return ID:** {return_result['return_id']}\n"
            f"**Refund Amount:** ${return_result['refund_amount']:.2f}\n\n"
            f"📦 **Return Label:** [Download Label]({return_result['return_label']})\n"
            f"📍 **Tracking:** {return_result['tracking_number']}\n\n"
            f"**Instructions:**\n"
            f"{return_result['instructions']}\n\n"
            "Your refund will be processed within 3-5 business days after we receive the item."
        )
        
        # Send WhatsApp notification for return approval
        try:
            from notifications.whatsapp_service import get_whatsapp_service
            import os
            
            whatsapp = get_whatsapp_service()
            customer_number = os.getenv("YOUR_WHATSAPP_NUMBER", "whatsapp:+917780879882")
            
            print(f"[DEBUG] Sending return approval WhatsApp to: {customer_number}")
            success = whatsapp.send_return_approved(
                customer_number,
                return_result['return_id'],
                order_id,
                return_result['refund_amount']
            )
            print(f"[DEBUG] WhatsApp return approval: {'✓ Sent' if success else '✗ Failed'}")
        except Exception as e:
            print(f"[ERROR] WhatsApp notification failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        answer = (
            f"There was an issue processing your return:\n\n"
            f"{return_result['reason']}\n\n"
            "Please contact support for assistance."
        )
    
    return {**state, "answer": answer}

# --------------------------------------------------
# REFUND STATUS NODE (DEMO)
# --------------------------------------------------
def refund_status_node(state: AgentState) -> AgentState:
    """Handle refund status inquiries using mock backend"""
    
    backend = get_mock_backend()
    order_id = extract_order_id(state['query'])
    
    if not order_id:
        return {
            **state,
            "answer": (
                "I can check your refund status! 💰\n\n"
                "Please provide your order number (e.g., ORD-12345) "
                "so I can look up your refund information."
            )
        }
    
    refund_info = backend.get_refund_status(order_id)
    
    if not refund_info:
        # Check if order exists
        order = backend.get_order(order_id)
        if order:
            return {
                **state,
                "answer": (
                    f"I don't see any refund in progress for order {order_id}.\n\n"
                    "If you'd like to return this order, just let me know and I can help you start the return process!"
                )
            }
        else:
            return {
                **state,
                "answer": (
                    f"I couldn't find order {order_id} in our system.\n\n"
                    "Please check your order number or contact us at:\n"
                    "📧 Email: support@jashanmal.com"
                )
            }
    
    status = refund_info['status']
    
    if status == "completed":
        answer = (
            f"✅ Great news! Your refund has been **completed**!\n\n"
            f"💰 Amount: ${refund_info['amount']:.2f}\n"
            f"📅 Processed: {refund_info['created_at']}\n\n"
            "The refund should appear in your account within 1-2 business days."
        )
        
        # Send WhatsApp notification for completed refund
        try:
            from notifications.whatsapp_service import get_whatsapp_service
            import os
            
            whatsapp = get_whatsapp_service()
            customer_number = os.getenv("YOUR_WHATSAPP_NUMBER", "whatsapp:+917780879882")
            
            print(f"[DEBUG] Sending refund completed WhatsApp to: {customer_number}")
            success = whatsapp.send_refund_completed(
                customer_number,
                refund_info['amount'],
                order_id
            )
            print(f"[DEBUG] WhatsApp refund completed: {'✓ Sent' if success else '✗ Failed'}")
        except Exception as e:
            print(f"[ERROR] WhatsApp notification failed: {e}")
            import traceback
            traceback.print_exc()
            
    elif status == "processing":
        answer = (
            f"⏳ Your refund is being **processed**.\n\n"
            f"💰 Amount: ${refund_info['amount']:.2f}\n"
            f"📅 Estimated completion: {refund_info['estimated_completion']}\n\n"
            "We'll notify you once the refund is complete!"
        )
        
        # Send WhatsApp notification for processing refund
        try:
            from notifications.whatsapp_service import get_whatsapp_service
            import os
            
            whatsapp = get_whatsapp_service()
            customer_number = os.getenv("YOUR_WHATSAPP_NUMBER", "whatsapp:+917780879882")
            
            print(f"[DEBUG] Sending refund processing WhatsApp to: {customer_number}")
            # Get return ID from refund info
            return_id = refund_info.get('return_id', 'RET-00001')
            success = whatsapp.send_refund_processing(
                customer_number,
                return_id,
                refund_info['amount']
            )
            print(f"[DEBUG] WhatsApp refund processing: {'✓ Sent' if success else '✗ Failed'}")
        except Exception as e:
            print(f"[ERROR] WhatsApp notification failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        answer = (
            f"Your refund status: **{status}**\n\n"
            f"💰 Amount: ${refund_info['amount']:.2f}\n\n"
            "If you have questions, contact us at support@jashanmal.com"
        )
    
    return {**state, "answer": answer}

# --------------------------------------------------
# LANGGRAPH
# --------------------------------------------------
graph = StateGraph(AgentState)

graph.add_node("router", router_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("answer", answer_node)
graph.add_node("contact", contact_node)
graph.add_node("booking", booking_node)
graph.add_node("order_tracking", order_tracking_node)
graph.add_node("return_request", return_request_node)
graph.add_node("refund_status", refund_status_node)
graph.add_node("greeting", greeting_node)
graph.add_node("fallback", fallback_node)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    lambda s: s["route"],
    {
        "rag": "retrieve",
        "contact": "contact",
        "booking": "booking",
        "order_tracking": "order_tracking",
        "return_request": "return_request",
        "refund_status": "refund_status",
        "greeting": "greeting",
        "fallback": "fallback",
    },
)

graph.add_edge("retrieve", "answer")
graph.add_edge("answer", END)
graph.add_edge("contact", END)
graph.add_edge("booking", END)
graph.add_edge("order_tracking", END)
graph.add_edge("return_request", END)
graph.add_edge("refund_status", END)
graph.add_edge("greeting", END)
graph.add_edge("fallback", END)

# --------------------------------------------------
# CHECKPOINTER (SESSION MEMORY READY)
# --------------------------------------------------
checkpointer = MemorySaver()

agent = graph.compile(checkpointer=checkpointer)
