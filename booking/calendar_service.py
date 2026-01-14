"""Google Calendar booking service"""
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Paths
TOKEN_PATH = Path("booking/token.pickle")
CREDENTIALS_PATH = Path("booking/credentials.json")

# Configure your timezone here (e.g., 'Asia/Dubai', 'Asia/Kolkata', 'America/New_York')
LOCAL_TIMEZONE = 'Asia/Dubai'  # Change this to your timezone


class CalendarService:
    """Google Calendar service for booking meetings"""
    
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if TOKEN_PATH.exists():
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_PATH.exists():
                    raise FileNotFoundError(
                        f"Please download OAuth credentials to {CREDENTIALS_PATH}\n"
                        "Get them from: https://console.cloud.google.com/apis/credentials"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_PATH), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            TOKEN_PATH.parent.mkdir(exist_ok=True)
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_available_slots(
        self, 
        days_ahead: int = 7,
        start_hour: int = 9,
        end_hour: int = 18,
        slot_duration: int = 30
    ) -> List[Dict]:
        """Get available time slots"""
        
        if not self.service:
            return []
        
        # Get busy times (use local timezone)
        try:
            local_tz = ZoneInfo(LOCAL_TIMEZONE)
        except:
            # Fallback to UTC if timezone not found
            from datetime import timezone
            local_tz = timezone.utc
            
        now_local = datetime.now(local_tz)
        now_utc = datetime.now(ZoneInfo('UTC'))
        
        time_min = now_utc.isoformat()
        time_max = (now_utc + timedelta(days=days_ahead)).isoformat()
        
        try:
            body = {
                "timeMin": time_min,
                "timeMax": time_max,
                "items": [{"id": "primary"}]
            }
            
            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars']['primary']['busy']
            
            # Generate available slots
            available_slots = []
            
            # Start checking from the next 2 hours
            next_slot_time = now_local + timedelta(hours=2)
            
            for day in range(days_ahead + 1):
                check_date = (now_local + timedelta(days=day)).date()
                
                # Skip weekends
                if check_date.weekday() >= 5:
                    continue
                
                # Check each slot
                for hour in range(start_hour, end_hour):
                    slot_start_local = datetime.combine(check_date, datetime.min.time()).replace(hour=hour, tzinfo=local_tz)
                    slot_end_local = slot_start_local + timedelta(minutes=slot_duration)
                    
                    # Skip slots that are in the past or too soon
                    if slot_start_local <= next_slot_time:
                        continue
                    
                    # Convert to UTC for comparison with busy times
                    slot_start_utc = slot_start_local.astimezone(ZoneInfo('UTC'))
                    slot_end_utc = slot_end_local.astimezone(ZoneInfo('UTC'))
                    
                    # Check if slot is free
                    is_free = True
                    for busy in busy_times:
                        busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                        busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                        
                        if not (slot_end_utc <= busy_start or slot_start_utc >= busy_end):
                            is_free = False
                            break
                    
                    if is_free:
                        available_slots.append({
                            'start': slot_start_utc.isoformat(),
                            'end': slot_end_utc.isoformat(),
                            'display': slot_start_local.strftime('%A, %B %d at %I:%M %p')
                        })
            
            return available_slots[:10]  # Return first 10 slots
            
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []
    
    def create_meeting(
        self,
        summary: str,
        start_time: str,
        duration_minutes: int = 30,
        description: str = "",
        attendee_email: Optional[str] = None
    ) -> Optional[str]:
        """Create a calendar event"""
        
        if not self.service:
            return None
        
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            
            return event.get('htmlLink')
            
        except Exception as e:
            print(f"Error creating meeting: {e}")
            return None


# Singleton instance
_calendar_service = None

def get_calendar_service() -> CalendarService:
    """Get or create calendar service instance"""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = CalendarService()
    return _calendar_service
