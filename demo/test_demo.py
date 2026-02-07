"""Test script for demo e-commerce features"""
from mock_ecommerce import get_mock_backend

def test_order_tracking():
    """Test order tracking functionality"""
    print("\n=== Testing Order Tracking ===")
    backend = get_mock_backend()
    
    # Test delivered order
    tracking = backend.track_order("ORD-12345")
    print(f"\nOrder ORD-12345:")
    print(f"  Status: {tracking['status']}")
    print(f"  Tracking: {tracking['tracking_number']}")
    print(f"  Delivered: {tracking['delivery_date']}")
    
    # Test shipped order
    tracking = backend.track_order("ORD-12346")
    print(f"\nOrder ORD-12346:")
    print(f"  Status: {tracking['status']}")
    print(f"  Carrier: {tracking['carrier']}")
    print(f"  ETA: {tracking['estimated_delivery']}")
    
    # Test non-existent order
    tracking = backend.track_order("ORD-99999")
    print(f"\nOrder ORD-99999:")
    print(f"  Result: {tracking}")

def test_return_request():
    """Test return request functionality"""
    print("\n=== Testing Return Requests ===")
    backend = get_mock_backend()
    
    # Test eligible return
    eligibility = backend.check_return_eligibility("ORD-12345")
    print(f"\nReturn eligibility for ORD-12345:")
    print(f"  Eligible: {eligibility['eligible']}")
    
    if eligibility['eligible']:
        result = backend.create_return("ORD-12345", ["all"], "Defective")
        print(f"\nReturn created:")
        print(f"  Return ID: {result['return_id']}")
        print(f"  Refund Amount: ${result['refund_amount']}")
        print(f"  Tracking: {result['tracking_number']}")
    
    # Test ineligible return (not delivered)
    eligibility = backend.check_return_eligibility("ORD-12347")
    print(f"\nReturn eligibility for ORD-12347:")
    print(f"  Eligible: {eligibility['eligible']}")
    print(f"  Reason: {eligibility.get('reason', 'N/A')}")

def test_refund_status():
    """Test refund status functionality"""
    print("\n=== Testing Refund Status ===")
    backend = get_mock_backend()
    
    # Create a return first
    backend.create_return("ORD-12345", ["all"], "Customer request")
    
    # Create refund
    return_info = list(backend.returns.values())[0]
    refund = backend.create_refund(return_info['return_id'])
    
    print(f"\nRefund created:")
    print(f"  Refund ID: {refund['refund_id']}")
    print(f"  Amount: ${refund['amount']}")
    print(f"  Status: {refund['status']}")
    print(f"  ETA: {refund['estimated_days']} days")
    
    # Check refund status
    refund_status = backend.get_refund_status("ORD-12345")
    print(f"\nRefund status for ORD-12345:")
    print(f"  Status: {refund_status['status']}")
    print(f"  Amount: ${refund_status['amount']}")

def test_all_orders():
    """Display all available demo orders"""
    print("\n=== Available Demo Orders ===")
    backend = get_mock_backend()
    
    for order_id, order in backend.orders.items():
        print(f"\n{order_id}:")
        print(f"  Customer: {order['customer_name']}")
        print(f"  Item: {order['items'][0]['name']}")
        print(f"  Total: ${order['total']}")
        print(f"  Status: {order['status']}")
        print(f"  Order Date: {order['order_date']}")

if __name__ == "__main__":
    print("🎬 Testing Mock E-commerce Backend")
    print("=" * 50)
    
    test_all_orders()
    test_order_tracking()
    test_return_request()
    test_refund_status()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\nYou can now demo these features in the chatbot:")
    print("  - 'Track order 12345'")
    print("  - 'I want to return order 12345'")
    print("  - 'Where is my refund for order 12345?'")
