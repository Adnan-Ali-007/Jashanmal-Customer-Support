# Streamlit Cloud Deployment Checklist

## Pre-Deployment

- [ ] Push latest code to GitHub
- [ ] Verify `.gitignore` excludes sensitive files (.env, credentials.json, *.db)
- [ ] Test all features locally

## Streamlit Cloud Setup

### 1. Create New App
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repository
4. Set main file path: `app.py`
5. Click "Advanced settings"

### 2. Configure Secrets

Click "Secrets" and paste this (replace with YOUR actual values):

```toml
GOOGLE_API_KEY = "your-google-api-key-here"

TWILIO_ACCOUNT_SID = "your-twilio-account-sid-here"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token-here"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
YOUR_WHATSAPP_NUMBER = "whatsapp:+917780879882"
```

**IMPORTANT:**
- Replace placeholder values with your actual credentials from `.env`
- Use spaces around `=` (TOML format)
- Use double quotes around values
- Don't include comments (#)
- Match exact key names from .env

### 3. Deploy

Click "Deploy" and wait for build to complete

## Post-Deployment Testing

### Check Logs
1. Click "Manage app" → "Logs"
2. Look for these debug messages:
   ```
   [DEBUG] WhatsApp Service Initialization:
     TWILIO_ACCOUNT_SID: ✓ Set
     TWILIO_AUTH_TOKEN: ✓ Set
   ```

### Test Features

Test each feature and check logs:

1. **Order Tracking**
   - Query: "track order ORD-12345"
   - Expected: Delivered status + WhatsApp sent
   - Check logs for: `[DEBUG] WhatsApp delivered notification: ✓ Sent`

2. **Return Request**
   - Query: "return order ORD-12345"
   - Expected: Return approved + WhatsApp sent
   - Check logs for: `[DEBUG] WhatsApp return approval: ✓ Sent`

3. **RAG/FAQ**
   - Query: "what are your shipping policies?"
   - Expected: Policy details from FAQ

4. **Contact**
   - Query: "how can I contact support?"
   - Expected: Contact information

## Troubleshooting

### WhatsApp Not Sending

**Check Streamlit Logs for:**

1. **Missing Credentials**
   ```
   ⚠️ Twilio credentials not found in environment
   ```
   **Fix:** Add secrets in Streamlit dashboard

2. **Wrong Format**
   ```
   [ERROR] WhatsApp notification failed: ...
   ```
   **Fix:** Check secrets format (spaces, quotes)

3. **Twilio Error**
   ```
   ✗ Failed to send WhatsApp message: ...
   ```
   **Fix:** Verify Twilio credentials are correct

### How to View Logs

1. Go to your app on Streamlit Cloud
2. Click hamburger menu (☰) → "Manage app"
3. Click "Logs" tab
4. Look for `[DEBUG]` and `[ERROR]` messages

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| No WhatsApp | Secrets not configured | Add secrets in dashboard |
| Wrong credentials | Copy-paste error | Double-check Account SID/Token |
| Sandbox not joined | Twilio sandbox | Send "join <code>" to sandbox |
| Rate limit | Too many messages | Wait 1 minute between tests |

## Features That Work on Cloud

✅ Order tracking with WhatsApp
✅ Return requests with WhatsApp
✅ Refund status with WhatsApp
✅ RAG/FAQ retrieval
✅ Contact information
✅ Greetings and fallback

## Features That Need Extra Setup

❌ **Google Calendar Booking**
- Requires service account setup
- See: `ENABLE_CALENDAR_ON_CLOUD.md`

❌ **Persistent Conversation History**
- SQLite doesn't persist on Streamlit Cloud
- Would need PostgreSQL/external DB

## Success Criteria

- [ ] App loads without errors
- [ ] Order tracking shows correct status
- [ ] WhatsApp messages received on +917780879882
- [ ] FAQ questions return relevant answers
- [ ] No error messages in logs

## Quick Test Commands

After deployment, test with these queries:

```
1. "hi" → Should greet
2. "track order ORD-12345" → Should show delivered + send WhatsApp
3. "return order ORD-12345" → Should approve return + send WhatsApp
4. "what are your shipping policies?" → Should show FAQ
5. "contact support" → Should show contact info
```

Check your WhatsApp for 2 messages (tracking + return).
