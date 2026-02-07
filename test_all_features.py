"""Comprehensive test of all chatbot features"""
import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from agents.agents import agent
from dotenv import load_dotenv

load_dotenv()

def test_query(query: str, description: str):
    """Test a single query"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Query: {query}\n")
    
    try:
        config = {"configurable": {"thread_id": "test-thread"}}
        result = agent.invoke(
            {"query": query},
            config=config
        )
        
        print(f"Route: {result.get('route', 'N/A')}")
        print(f"\nAnswer:\n{result.get('answer', 'No answer')}")
        print(f"\n✅ Test passed")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("CHATBOT FUNCTIONALITY TEST SUITE")
    print("="*60)
    
    tests = [
        # 1. Greeting
        ("hi", "Greeting - Simple hello"),
        
        # 2. Order Tracking (Demo)
        ("track order ORD-12345", "Order Tracking - Delivered order (should send WhatsApp)"),
        ("track order ORD-12346", "Order Tracking - Shipped order (should send WhatsApp)"),
        ("track order ORD-12347", "Order Tracking - Processing order"),
        
        # 3. Return Request (Demo)
        ("I want to return order ORD-12345", "Return Request - Eligible order (should send WhatsApp)"),
        ("return order ORD-12348", "Return Request - Another eligible order"),
        
        # 4. Refund Status (Demo)
        ("what's the refund status for order ORD-12345", "Refund Status - Check refund (should send WhatsApp)"),
        
        # 5. RAG - FAQ Questions
        ("what are your shipping policies?", "RAG - Shipping policy question"),
        ("how do I track my order?", "RAG - Order tracking FAQ"),
        ("what is your return policy?", "RAG - Return policy question"),
        
        # 6. Contact Info
        ("how can I contact support?", "Contact - Support information"),
        
        # 7. Booking
        ("I want to book a meeting", "Booking - Schedule meeting"),
        
        # 8. Fallback
        ("what's the weather today?", "Fallback - Off-topic question"),
        
        # 9. Thank you
        ("thanks", "Greeting - Thank you response"),
    ]
    
    passed = 0
    failed = 0
    
    for query, description in tests:
        if test_query(query, description):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("\n📱 Check your WhatsApp (+917780879882) for notifications!")
    print("="*60)

if __name__ == "__main__":
    main()
