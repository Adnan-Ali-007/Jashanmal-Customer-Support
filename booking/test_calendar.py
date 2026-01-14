"""Test Google Calendar integration"""
from calendar_service import get_calendar_service

print("Testing Google Calendar integration...\n")

try:
    # Initialize service (will trigger OAuth flow if needed)
    calendar = get_calendar_service()
    print("✓ Authentication successful!\n")
    
    # Get available slots
    print("Fetching available time slots...")
    slots = calendar.get_available_slots(days_ahead=7)
    
    if slots:
        print(f"\n✓ Found {len(slots)} available slots:\n")
        for i, slot in enumerate(slots[:5], 1):
            print(f"{i}. {slot['display']}")
    else:
        print("\n⚠ No available slots found (calendar might be full)")
    
    print("\n✓ Calendar integration is working!")
    print("\nYou can now use the booking feature in your chatbot.")
    
except FileNotFoundError as e:
    print(f"\n✗ Error: {e}")
    print("\nPlease follow the setup instructions in SETUP.md")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nCheck the error message above and refer to SETUP.md")
