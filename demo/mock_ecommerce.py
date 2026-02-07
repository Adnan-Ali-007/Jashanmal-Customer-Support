"""Mock E-commerce Backend for Demo Purposes"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import random

class MockEcommerceBackend:
    """Simulates an e-commerce backend with orders, returns, and refunds"""
    
    def __init__(self):
        self.orders = self._generate_mock_orders()
        self.returns = {}
        self.refunds = {}
        self.return_counter = 1
        self.refund_counter = 1
    
    def _generate_mock_orders(self) -> Dict:
        """Generate realistic mock orders"""
        today = datetime.now()
        
        return {
            "ORD-12345": {
                "order_id": "ORD-12345",
                "customer_name": "John Smith",
                "customer_email": "john@example.com",
                "order_date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "status": "delivered",
                "items": [
                    {
                        "name": "iPhone 15 Pro",
                        "quantity": 1,
                        "price": 999.00,
                        "category": "electronics"
                    }
                ],
                "total": 999.00,
                "shipping_address": "123 Main St, Dubai, UAE",
                "tracking_number": "1Z999AA10123456784",
                "carrier": "DHL",
                "delivery_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "estimated_delivery": None
            },
            "ORD-12346": {
                "order_id": "ORD-12346",
                "customer_name": "Sarah Johnson",
                "customer_email": "sarah@example.com",
                "order_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
                "status": "shipped",
                "items": [
                    {
                        "name": "Samsung Galaxy S24",
                        "quantity": 1,
                        "price": 899.00,
                        "category": "electronics"
                    }
                ],
                "total": 899.00,
                "shipping_address": "456 Oak Ave, Abu Dhabi, UAE",
                "tracking_number": "1Z999AA10123456785",
                "carrier": "FedEx",
                "delivery_date": None,
                "estimated_delivery": (today + timedelta(days=2)).strftime("%Y-%m-%d")
            },
            "ORD-12347": {
                "order_id": "ORD-12347",
                "customer_name": "Mike Chen",
                "customer_email": "mike@example.com",
                "order_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "status": "processing",
                "items": [
                    {
                        "name": "MacBook Pro 16-inch",
                        "quantity": 1,
                        "price": 2499.00,
                        "category": "electronics"
                    }
                ],
                "total": 2499.00,
                "shipping_address": "789 Palm St, Sharjah, UAE",
                "tracking_number": None,
                "carrier": None,
                "delivery_date": None,
                "estimated_delivery": (today + timedelta(days=5)).strftime("%Y-%m-%d")
            },
            "ORD-12348": {
                "order_id": "ORD-12348",
                "customer_name": "Emma Wilson",
                "customer_email": "emma@example.com",
                "order_date": (today - timedelta(days=15)).strftime("%Y-%m-%d"),
                "status": "delivered",
                "items": [
                    {
                        "name": "Sony WH-1000XM5 Headphones",
                        "quantity": 1,
                        "price": 399.00,
                        "category": "electronics"
                    }
                ],
                "total": 399.00,
                "shipping_address": "321 Beach Rd, Dubai, UAE",
                "tracking_number": "1Z999AA10123456786",
                "carrier": "DHL",
                "delivery_date": (today - timedelta(days=12)).strftime("%Y-%m-%d"),
                "estimated_delivery": None
            }
        }
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order details by order ID"""
        return self.orders.get(order_id)
    
    def track_order(self, order_id: str) -> Optional[Dict]:
        """Get tracking information for an order"""
        order = self.get_order(order_id)
        if not order:
            return None
        
        tracking_info = {
            "order_id": order_id,
            "status": order["status"],
            "tracking_number": order.get("tracking_number"),
            "carrier": order.get("carrier"),
            "estimated_delivery": order.get("estimated_delivery"),
            "delivery_date": order.get("delivery_date")
        }
        
        # Add status timeline
        if order["status"] == "delivered":
            tracking_info["timeline"] = [
                {"status": "Order Placed", "date": order["order_date"]},
                {"status": "Processing", "date": order["order_date"]},
                {"status": "Shipped", "date": (datetime.fromisoformat(order["order_date"]) + timedelta(days=1)).strftime("%Y-%m-%d")},
                {"status": "Out for Delivery", "date": order["delivery_date"]},
                {"status": "Delivered", "date": order["delivery_date"]}
            ]
        elif order["status"] == "shipped":
            tracking_info["timeline"] = [
                {"status": "Order Placed", "date": order["order_date"]},
                {"status": "Processing", "date": order["order_date"]},
                {"status": "Shipped", "date": (datetime.fromisoformat(order["order_date"]) + timedelta(days=1)).strftime("%Y-%m-%d")}
            ]
        else:
            tracking_info["timeline"] = [
                {"status": "Order Placed", "date": order["order_date"]},
                {"status": "Processing", "date": order["order_date"]}
            ]
        
        return tracking_info
    
    def check_return_eligibility(self, order_id: str) -> Dict:
        """Check if order is eligible for return"""
        order = self.get_order(order_id)
        
        if not order:
            return {
                "eligible": False,
                "reason": "Order not found"
            }
        
        if order["status"] != "delivered":
            return {
                "eligible": False,
                "reason": "Order must be delivered before initiating return"
            }
        
        # Check return window (30 days for electronics)
        order_date = datetime.fromisoformat(order["order_date"])
        days_since_order = (datetime.now() - order_date).days
        
        if days_since_order > 30:
            return {
                "eligible": False,
                "reason": "Return window has expired (30 days for electronics)"
            }
        
        return {
            "eligible": True,
            "return_window_days": 30 - days_since_order,
            "items": order["items"]
        }
    
    def create_return(self, order_id: str, items: List[str], reason: str) -> Dict:
        """Create a return request"""
        eligibility = self.check_return_eligibility(order_id)
        
        if not eligibility["eligible"]:
            return {
                "success": False,
                "reason": eligibility["reason"]
            }
        
        order = self.get_order(order_id)
        return_id = f"RET-{self.return_counter:05d}"
        self.return_counter += 1
        
        # Create return record
        self.returns[return_id] = {
            "return_id": return_id,
            "order_id": order_id,
            "items": items,
            "reason": reason,
            "status": "approved",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "return_label": f"https://shipping.example.com/label/{return_id}",
            "tracking_number": f"RET{random.randint(100000000, 999999999)}",
            "refund_amount": order["total"]
        }
        
        return {
            "success": True,
            "return_id": return_id,
            "return_label": self.returns[return_id]["return_label"],
            "tracking_number": self.returns[return_id]["tracking_number"],
            "refund_amount": order["total"],
            "instructions": "Print the label and drop off at any DHL location"
        }
    
    def get_return_status(self, return_id: str) -> Optional[Dict]:
        """Get return status"""
        return self.returns.get(return_id)
    
    def create_refund(self, return_id: str) -> Dict:
        """Process refund for a return"""
        return_info = self.get_return_status(return_id)
        
        if not return_info:
            return {
                "success": False,
                "reason": "Return not found"
            }
        
        refund_id = f"REF-{self.refund_counter:05d}"
        self.refund_counter += 1
        
        self.refunds[refund_id] = {
            "refund_id": refund_id,
            "return_id": return_id,
            "order_id": return_info["order_id"],
            "amount": return_info["refund_amount"],
            "status": "processing",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estimated_completion": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        }
        
        return {
            "success": True,
            "refund_id": refund_id,
            "amount": return_info["refund_amount"],
            "status": "processing",
            "estimated_days": 3
        }
    
    def get_refund_status(self, order_id: str) -> Optional[Dict]:
        """Get refund status for an order"""
        # Find refund by order_id
        for refund_id, refund in self.refunds.items():
            if refund["order_id"] == order_id:
                return refund
        
        return None
    
    def simulate_status_update(self, order_id: str, new_status: str):
        """Simulate order status update (for demo purposes)"""
        if order_id in self.orders:
            self.orders[order_id]["status"] = new_status
            
            if new_status == "shipped" and not self.orders[order_id].get("tracking_number"):
                self.orders[order_id]["tracking_number"] = f"1Z999AA{random.randint(10000000, 99999999)}"
                self.orders[order_id]["carrier"] = random.choice(["DHL", "FedEx", "UPS"])


# Singleton instance
_mock_backend = None

def get_mock_backend() -> MockEcommerceBackend:
    """Get or create mock backend instance"""
    global _mock_backend
    if _mock_backend is None:
        _mock_backend = MockEcommerceBackend()
    return _mock_backend
