from typing import TypedDict, List
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Add ingestion folder to path for imports
sys.path.append(str(Path(__file__).parent.parent / "ingestion"))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from gemini_embeddings import GeminiEmbeddings

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

embeddings = GeminiEmbeddings(model="models/embedding-001")

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
- greeting : hi, hello, hey, thanks, thank you, goodbye, bye, ok, okay, yes, no (simple greetings/acknowledgments)
- fallback : anything else not related to customer support

Return ONLY one word.
"""

def router_node(state: AgentState) -> AgentState:
    res = llm.invoke(
        ROUTER_PROMPT + f"\n\nQuery: {state['query']}"
    )

    route = res.content.strip().lower()
    if route not in {"rag", "contact", "booking", "greeting", "fallback"}:
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
# LANGGRAPH
# --------------------------------------------------
graph = StateGraph(AgentState)

graph.add_node("router", router_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("answer", answer_node)
graph.add_node("contact", contact_node)
graph.add_node("booking", booking_node)
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
        "greeting": "greeting",
        "fallback": "fallback",
    },
)

graph.add_edge("retrieve", "answer")
graph.add_edge("answer", END)
graph.add_edge("contact", END)
graph.add_edge("booking", END)
graph.add_edge("greeting", END)
graph.add_edge("fallback", END)

# --------------------------------------------------
# CHECKPOINTER (SESSION MEMORY READY)
# --------------------------------------------------
checkpointer = MemorySaver()

agent = graph.compile(checkpointer=checkpointer)
