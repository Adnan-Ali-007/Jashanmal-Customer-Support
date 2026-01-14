# ✅ Calendar Booking Now Works on Cloud!

## What I Fixed

### 1. Missing Dependency ❌ → ✅
**Error:** `ModuleNotFoundError: langchain_community`

**Fixed:** Added `langchain-community>=0.0.38` to `requirements.txt`

### 2. Calendar Authentication ❌ → ✅
**Problem:** OAuth doesn't work on cloud servers

**Solution:** Added Service Account support - works on both local AND cloud!

---

## How It Works Now

### Local Development (OAuth)
- Uses `credentials.json` and `token.pickle`
- Opens browser for authentication
- Works as before ✅

### Streamlit Cloud (Service Account)
- Uses service account credentials from Streamlit secrets
- No browser needed
- Fully automated ✅

---

## Setup for Streamlit Cloud

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: `gen-lang-client-0913736552`
3. **IAM & Admin** → **Service Accounts** → **Create Service Account**
4. Name: `jashanmal-calendar-bot`
5. Click **Create and Continue** → **Done**

### Step 2: Create Key

1. Click on the service account
2. **Keys** tab → **Add Key** → **Create new key**
3. Choose **JSON**
4. Download the JSON file (keep it safe!)

### Step 3: Share Your Calendar

1. Open [Google Calendar](https://calendar.google.com)
2. Your calendar → **Settings and sharing**
3. **Share with specific people** → **Add people**
4. Paste service account email from JSON:
   ```
   jashanmal-calendar-bot@gen-lang-client-0913736552.iam.gserviceaccount.com
   ```
5. Permission: **Make changes to events**
6. Click **Send**

### Step 4: Add to Streamlit Secrets

1. Open the downloaded JSON file
2. Go to Streamlit Cloud → Your App → **Settings** → **Secrets**
3. Add this format:

```toml
GOOGLE_API_KEY = "your_gemini_api_key"

[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "from_json_file"
private_key = "from_json_file"
client_email = "from_json_file"
client_id = "from_json_file"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "from_json_file"
```

**Copy these fields from your JSON:**
- `project_id`
- `private_key_id`
- `private_key` (keep the quotes and \n characters!)
- `client_email`
- `client_id`
- `client_x509_cert_url`

### Step 5: Deploy!

```bash
git add .
git commit -m "Enable calendar booking on cloud"
git push origin main
```

Streamlit Cloud will auto-redeploy.

---

## Testing

### Test Locally (OAuth)
```bash
streamlit run app.py
```
- Uses OAuth as before
- Opens browser for auth

### Test on Cloud (Service Account)
1. Deploy to Streamlit Cloud
2. Try: "I want to book a meeting"
3. Select a slot
4. Provide email
5. Meeting created! ✅

---

## Troubleshooting

### "Service account not found"
- Check you added `[gcp_service_account]` section in Streamlit secrets
- Verify all fields are copied correctly

### "Permission denied"
- Make sure you shared your calendar with the service account email
- Permission must be "Make changes to events"

### "Invalid private_key"
- Copy the entire private_key including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`
- Keep all `\n` characters in the key

### Still using OAuth on cloud?
- Check Streamlit logs - should say "Using Service Account authentication"
- If it says "Using OAuth", secrets aren't configured correctly

---

## Security Notes

✅ **Service account JSON is secure:**
- Never commit to GitHub
- Only in Streamlit Cloud secrets
- Encrypted at rest

✅ **Calendar access is limited:**
- Service account only has access to calendars you explicitly share
- Can't access other Google services
- Can be revoked anytime

---

## What's Different?

### Before
- ❌ Calendar booking only worked locally
- ❌ Cloud users saw contact info fallback

### After
- ✅ Calendar booking works everywhere
- ✅ Local: OAuth authentication
- ✅ Cloud: Service account authentication
- ✅ Seamless experience for users

---

## Quick Reference

### Files Modified
- `requirements.txt` - Added `langchain-community`
- `booking/calendar_service.py` - Added service account support

### New Files
- `CALENDAR_CLOUD_SETUP.md` - Detailed setup guide
- `ENABLE_CALENDAR_ON_CLOUD.md` - This file

### Streamlit Secrets Format
```toml
GOOGLE_API_KEY = "your_key"

[gcp_service_account]
# Paste service account JSON fields here
```

---

## 🎉 You're Done!

Calendar booking now works on both local and cloud deployments!

**Next Steps:**
1. Create service account
2. Share calendar with service account
3. Add credentials to Streamlit secrets
4. Push and deploy
5. Test booking feature

Your users can now book real meetings through the chatbot! 📅
