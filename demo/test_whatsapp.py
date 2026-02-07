"""Test WhatsApp notifications"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from notifications.whatsapp_service import get_whatsapp_service
import os
from dotenv import load_dotenv

load_dotenv()

def test_whatsapp_notifications():
    """Test WhatsApp notification service"""
    
    print("🧪 Testing WhatsApp Notifications")
    print("=" * 50)
    
    # Get your WhatsApp number from .env
    your_number = os.getenv("YOUR_WHATSAPP_NUMBER", "whatsapp:+917780879882")
    
    print(f"\n📱 Sending test messages to: {your_number}")
    print("\nMake sure you:")
    print("1. Created Twilio account")
    print("2. Added credentials to .env file")
    print("3. Joined Twilio WhatsApp sandbox")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    whatsapp = get_whatsapp_service()
    
    if not whatsapp.client:
        print("\n❌ WhatsApp service not configured!")
        print("\nPlease:")
        print("1. Sign up at https://www.twilio.com/try-twilio")
        print("2. Get your Account SID and Auth Token")
        print("3. Add them to .env file:")
        print("   TWILIO_ACCOUNT_SID=ACxxxxx")
        print("   TWILIO_AUTH_TOKEN=xxxxx")
        print("4. Join WhatsApp sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
        return
    
    print("\n" + "=" * 50)
    print("Sending test messages...")
    print("=" * 50)
    
    # Test 1: Simple message
    print("\n1️⃣ Sending welcome message...")
    success = whatsapp.send_message(
        your_number,
        "🤖 Hello! This is a test message from your Jashanmal chatbot. WhatsApp integration is working!"
    )
    print(f"   {'✅ Sent!' if success else '❌ Failed'}")
    
    # Test 2: Order confirmation
    print("\n2️⃣ Sending order confirmation...")
    success = whatsapp.send_order_confirmation(
        your_number,
        "ORD-12345",
        [
            {"name": "iPhone 15 Pro", "price": 999.00},
            {"name": "AirPods Pro", "price": 249.00}
        ],
        1248.00
    )
    print(f"   {'✅ Sent!' if success else '❌ Failed'}")
    
    # Test 3: Shipping update
    print("\n3️⃣ Sending shipping update...")
    success = whatsapp.send_shipping_update(
        your_number,
        "ORD-12345",
        "1Z999AA10123456784",
        "DHL"
    )
    print(f"   {'✅ Sent!' if success else '❌ Failed'}")
    
    # Test 4: Delivery notification
    print("\n4️⃣ Sending delivery notification...")
    success = whatsapp.send_delivery_update(
        your_number,
        "ORD-12345",
        "Today by 6 PM"
    )
    print(f"   {'✅ Sent!' if success else '❌ Failed'}")
    
    # Test 5: Return approval
    print("\n5️⃣ Sending return approval...")
    success = whatsapp.send_return_approved(
        your_number,
        "RET-00001",
        "ORD-12345",
        999.00
    )
    print(f"   {'✅ Sent!' if success else '❌ Failed'}")
    
    # Test 6: Refund completion
    print("\n6️⃣ Sending refund completion...")
    success = whatsapp.send_refund_completed(
        your_number,
        999.00,
        "ORD-12345"
    )
    print(f"   {'✅ Sent!' if success else '❌ Failed'}")
    
    # Test 7: Booking confirmation
    print("\n7️⃣ Sending booking confirmation...")
    success = whatsapp.send_booking_confirmation(
        your_number,
        "Tomorrow at 2:00 PM",
        "https://meet.google.com/abc-defg-hij"
    )
    print(f"   {'✅ Sent!' if success else '❌ Failed'}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("\n📱 Check your WhatsApp for messages!")
    print(f"   Number: {your_number}")
    print("\nIf you didn't receive messages:")
    print("1. Verify you joined Twilio sandbox")
    print("2. Check your Twilio console for errors")
    print("3. Ensure phone number format is correct")


if __name__ == "__main__":
    test_whatsapp_notifications()
