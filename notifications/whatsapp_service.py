"""WhatsApp notification service using Twilio"""
import os
from typing import Optional
from twilio.rest import Client
from dotenv import load_dotenv
import streamlit as st

# Load .env first
load_dotenv()

# Initialize credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Use st.write for debugging (will show in app)
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    print("✓ Twilio credentials loaded from environment")
else:
    print("⚠️ WARNING: Twilio credentials NOT found in environment!")
    print(f"  TWILIO_ACCOUNT_SID: {TWILIO_ACCOUNT_SID[:10] if TWILIO_ACCOUNT_SID else 'MISSING'}...")
    print(f"  TWILIO_AUTH_TOKEN: {'SET' if TWILIO_AUTH_TOKEN else 'MISSING'}")


class WhatsAppService:
    """Send WhatsApp notifications via Twilio"""
    
    def __init__(self):
        self.client = None
        self.from_number = TWILIO_WHATSAPP_NUMBER
        
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            try:
                print(f"🔧 Initializing Twilio with Account SID: {TWILIO_ACCOUNT_SID[:10]}...")
                self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                print("✓ WhatsApp service initialized successfully")
            except Exception as e:
                print(f"⚠️ WhatsApp service initialization failed: {e}")
                print(f"   Account SID: {TWILIO_ACCOUNT_SID[:10] if TWILIO_ACCOUNT_SID else 'None'}...")
                print(f"   Auth Token: {'Set' if TWILIO_AUTH_TOKEN else 'None'}")
        else:
            print("⚠️ WhatsApp credentials not found.")
            print(f"   TWILIO_ACCOUNT_SID: {'Set' if TWILIO_ACCOUNT_SID else 'Missing'}")
            print(f"   TWILIO_AUTH_TOKEN: {'Set' if TWILIO_AUTH_TOKEN else 'Missing'}")
            print("   Set credentials in Streamlit secrets or .env file")
    
    def send_message(self, to_number: str, message: str) -> bool:
        """
        Send WhatsApp message
        
        Args:
            to_number: Recipient's WhatsApp number (format: whatsapp:+1234567890)
            message: Message text to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.client:
            print("⚠️ WhatsApp service not available")
            return False
        
        try:
            # Ensure number has whatsapp: prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            message_obj = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=to_number
            )
            
            print(f"✓ WhatsApp message sent: {message_obj.sid}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send WhatsApp message: {e}")
            return False
    
    def send_order_confirmation(self, to_number: str, order_id: str, items: list, total: float) -> bool:
        """Send order confirmation message"""
        items_text = "\n".join([f"• {item['name']} - ${item['price']}" for item in items])
        
        message = f"""✅ *Order Confirmed!*

Order #: {order_id}
Total: ${total}

Items:
{items_text}

We'll notify you when your order ships!

Track your order: jashanmal.com/orders/{order_id}"""
        
        return self.send_message(to_number, message)
    
    def send_shipping_update(self, to_number: str, order_id: str, tracking_number: str, carrier: str = "DHL") -> bool:
        """Send shipping notification"""
        message = f"""📦 *Your Order Has Shipped!*

Order #: {order_id}
Carrier: {carrier}
Tracking: {tracking_number}

Expected delivery: 2-3 business days

Track: https://track.{carrier.lower()}.com/{tracking_number}"""
        
        return self.send_message(to_number, message)
    
    def send_delivery_update(self, to_number: str, order_id: str, delivery_time: str = "Today by 6 PM") -> bool:
        """Send out for delivery notification"""
        message = f"""🚚 *Out for Delivery!*

Order #: {order_id}

Your package is on its way and will arrive {delivery_time}.

Please ensure someone is available to receive the package."""
        
        return self.send_message(to_number, message)
    
    def send_delivered_notification(self, to_number: str, order_id: str) -> bool:
        """Send delivery confirmation"""
        message = f"""✅ *Delivered Successfully!*

Order #: {order_id}

Your package has been delivered!

Enjoy your purchase! If you have any issues, contact us at support@jashanmal.com"""
        
        return self.send_message(to_number, message)
    
    def send_return_approved(self, to_number: str, return_id: str, order_id: str, refund_amount: float) -> bool:
        """Send return approval notification"""
        message = f"""✅ *Return Approved*

Return ID: {return_id}
Order #: {order_id}
Refund Amount: ${refund_amount}

Your return shipping label has been sent to your email.

Drop off at any UPS location. Refund will be processed once we receive the item."""
        
        return self.send_message(to_number, message)
    
    def send_refund_processing(self, to_number: str, return_id: str, refund_amount: float) -> bool:
        """Send refund processing notification"""
        message = f"""💰 *Refund Processing*

Return ID: {return_id}
Amount: ${refund_amount}

We've received your returned item and your refund is being processed.

Expected in your account: 3-5 business days"""
        
        return self.send_message(to_number, message)
    
    def send_refund_completed(self, to_number: str, refund_amount: float, order_id: str) -> bool:
        """Send refund completion notification"""
        message = f"""🎉 *Refund Completed!*

Order #: {order_id}
Amount: ${refund_amount}

Your refund has been processed and should appear in your account within 24 hours.

Thank you for shopping with us!"""
        
        return self.send_message(to_number, message)
    
    def send_booking_confirmation(self, to_number: str, meeting_time: str, meeting_link: str) -> bool:
        """Send meeting booking confirmation"""
        message = f"""📅 *Meeting Booked!*

Time: {meeting_time}

Your customer support meeting has been confirmed.

Join meeting: {meeting_link}

A calendar invitation has been sent to your email."""
        
        return self.send_message(to_number, message)


# Singleton instance
_whatsapp_service = None

def get_whatsapp_service() -> WhatsAppService:
    """Get or create WhatsApp service instance"""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service
