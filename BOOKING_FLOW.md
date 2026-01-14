# 📅 Complete Booking Flow

## User Journey

### Step 1: User Requests Booking
```
User: "I want to book a meeting"
```

### Step 2: Bot Shows Available Slots
```
Bot: "I'd be happy to help you book a meeting! 📅

Here are the next available time slots:

**1.** Thursday, January 15 at 09:00 AM
**2.** Thursday, January 15 at 10:00 AM
**3.** Thursday, January 15 at 11:00 AM
**4.** Thursday, January 15 at 12:00 PM
**5.** Thursday, January 15 at 01:00 PM

**Please reply with the number (1-5) of your preferred slot**, 
and I'll schedule the meeting for you."
```

### Step 3: User Selects a Slot
```
User: "2"
```

### Step 4: Bot Asks for Email
```
Bot: "Great choice! You've selected **Thursday, January 15 at 10:00 AM**.

📧 Please provide your email address so I can send you the calendar invitation."
```

### Step 5: User Provides Email
```
User: "john.doe@example.com"
```

### Step 6: Bot Creates Meeting & Confirms
```
Bot: "✅ Perfect! Your meeting has been booked for **Thursday, January 15 at 10:00 AM**.

📅 [View in Google Calendar](link)

📧 A calendar invitation has been sent to **john.doe@example.com**.

Is there anything else I can help you with?"
```

## Features

✅ **Email Validation** - Checks for valid email format
✅ **Calendar Invitation** - Sends invite to user's email
✅ **Attendee Tracking** - Meeting includes attendee information
✅ **Error Handling** - Handles invalid emails gracefully
✅ **State Management** - Tracks booking flow across messages

## Technical Details

- **Session State Variables:**
  - `booking_slots` - Available time slots
  - `awaiting_booking_confirmation` - Waiting for slot selection
  - `awaiting_user_email` - Waiting for email address
  - `selected_booking_slot` - User's chosen slot

- **Email Validation:** Uses regex pattern to validate email format
- **Calendar API:** Uses `attendee_email` parameter to send invitations
- **Meeting Details:** Includes attendee email in description

## Error Handling

**Invalid Email:**
```
User: "notanemail"
Bot: "⚠️ That doesn't look like a valid email address. 
Please provide a valid email (e.g., yourname@example.com) 
so I can send you the calendar invitation."
```

**Calendar API Error:**
```
Bot: "I'm sorry, there was an issue creating the meeting. 
Please try again or contact us directly at:

📧 Email: support@jashanmal.com
📞 Call: 800 562 63"
```
