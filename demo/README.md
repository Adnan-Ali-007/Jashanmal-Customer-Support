# 🎬 E-commerce Demo Backend

## Overview
This module provides a mock e-commerce backend for demonstrating chatbot capabilities without requiring access to a real e-commerce system.

## Features

### ✅ Order Management
- 4 pre-configured demo orders
- Multiple order statuses (delivered, shipped, processing)
- Realistic tracking information
- Carrier details (DHL, FedEx, UPS)

### ✅ Return Processing
- Automatic eligibility checking
- 30-day return window validation
- Return label generation
- Refund amount calculation

### ✅ Refund Tracking
- Real-time refund status
- Processing timelines
- Estimated completion dates

## Quick Start

### Test the Mock Backend
```bash
cd demo
python test_demo.py
```

This will show you all available orders and test the functionality.

### Use in Chatbot
The demo is already integrated into your chatbot. Just ask:
- "Track order 12345"
- "I want to return order 12345"
- "Where is my refund?"

## Available Demo Orders

### ORD-12345 - Delivered iPhone
- **Status**: Delivered 3 days ago
- **Item**: iPhone 15 Pro ($999)
- **Best for**: Return request demos
- **Tracking**: 1Z999AA10123456784

### ORD-12346 - Shipped Samsung
- **Status**: Currently in transit
- **Item**: Samsung Galaxy S24 ($899)
- **Best for**: Order tracking demos
- **Tracking**: 1Z999AA10123456785

### ORD-12347 - Processing MacBook
- **Status**: Being prepared for shipment
- **Item**: MacBook Pro 16-inch ($2,499)
- **Best for**: Early-stage tracking
- **Tracking**: Not yet assigned

### ORD-12348 - Delivered Headphones
- **Status**: Delivered 15 days ago
- **Item**: Sony WH-1000XM5 ($399)
- **Best for**: Return eligibility testing
- **Tracking**: 1Z999AA10123456786

## Architecture

### MockEcommerceBackend Class
```python
from demo.mock_ecommerce import get_mock_backend

backend = get_mock_backend()

# Track order
tracking = backend.track_order("ORD-12345")

# Check return eligibility
eligibility = backend.check_return_eligibility("ORD-12345")

# Create return
result = backend.create_return("ORD-12345", ["all"], "Defective")

# Check refund status
refund = backend.get_refund_status("ORD-12345")
```

## Integration with Agent

The demo backend is integrated into your LangGraph agent through three new nodes:

1. **order_tracking_node** - Handles order tracking queries
2. **return_request_node** - Processes return requests
3. **refund_status_node** - Checks refund status

The router automatically directs queries to the appropriate node.

## Customization

### Adding New Orders
Edit `mock_ecommerce.py` and add to `_generate_mock_orders()`:

```python
"ORD-12349": {
    "order_id": "ORD-12349",
    "customer_name": "Your Name",
    "status": "delivered",
    "items": [{"name": "Product Name", "price": 99.00}],
    # ... other fields
}
```

### Changing Return Window
Modify the return window in `check_return_eligibility()`:

```python
if days_since_order > 30:  # Change 30 to your desired days
```

### Simulating Status Changes
```python
backend = get_mock_backend()
backend.simulate_status_update("ORD-12347", "shipped")
```

## Client Presentation

### What to Say
*"This demo uses a mock backend with realistic data. The chatbot makes the same API calls it would make to your real system - we just swap the endpoint URLs during integration."*

### What to Show
1. Order tracking with real-time status
2. Automated return processing
3. Refund status checking
4. End-to-end customer journey

### What to Emphasize
- **Speed**: Instant responses vs 5-10 minute phone calls
- **Availability**: 24/7 automated service
- **Consistency**: Same quality every time
- **Scalability**: Handles unlimited concurrent users

## Production Migration

When moving to production with a real e-commerce system:

1. **Keep the node structure** - Same order_tracking_node, return_request_node, etc.
2. **Replace backend calls** - Change from `get_mock_backend()` to real API calls
3. **Update data models** - Adjust to match client's data structure
4. **Add error handling** - Handle real-world API failures
5. **Implement authentication** - Add proper API keys and security

### Example Migration
```python
# Demo version
backend = get_mock_backend()
order = backend.get_order(order_id)

# Production version
import httpx
response = await httpx.get(
    f"{CLIENT_API_URL}/orders/{order_id}",
    headers={"Authorization": f"Bearer {API_KEY}"}
)
order = response.json()
```

## Testing

### Manual Testing
1. Start the chatbot: `streamlit run app.py`
2. Try each demo order
3. Test all three features (tracking, returns, refunds)
4. Verify error handling with invalid order IDs

### Automated Testing
```bash
python demo/test_demo.py
```

## Troubleshooting

### Order Not Found
- Make sure you're using the correct format: "ORD-12345" or just "12345"
- Check that the order exists in `_generate_mock_orders()`

### Return Not Working
- Verify order status is "delivered"
- Check that order is within 30-day window
- Ensure order exists in the system

### Refund Not Showing
- Create a return first before checking refund status
- Verify you're using the correct order ID

## Future Enhancements

Possible additions for more impressive demos:
- [ ] Real-time status updates (simulate shipping progress)
- [ ] Multiple items per order
- [ ] Partial returns
- [ ] Exchange requests
- [ ] Gift card refunds
- [ ] International shipping
- [ ] Multiple warehouses
- [ ] Inventory checking

## Support

For questions or issues with the demo:
1. Check the DEMO_GUIDE.md for usage instructions
2. Review DEMO_QUICK_REFERENCE.md for common scenarios
3. Run test_demo.py to verify functionality

---

**This demo backend makes your chatbot look production-ready for client presentations!** 🚀
