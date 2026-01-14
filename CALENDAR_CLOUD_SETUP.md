# 📅 Enable Calendar Booking on Streamlit Cloud

## The Problem
OAuth requires local browser authentication, which doesn't work on cloud servers.

## The Solution
Use a **Google Service Account** - a special account for server-to-server authentication.

---

## Step-by-Step Setup

### 1. Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `gen-lang-client-0913736552`
3. Go to **"IAM & Admin"** → **"Service Accounts"**
4. Click **"Create Service Account"**
5. Fill in:
   - **Name:** `jashanmal-calendar-bot`
   - **Description:** `Service account for calendar booking`
6. Click **"Create and Continue"**
7. Skip role assignment (click "Continue")
8. Click **"Done"**

### 2. Create Service Account Key

1. Click on the service account you just created
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Choose **"JSON"**
5. Click **"Create"**
6. A JSON file will download - **save it securely!**

### 3. Enable Calendar API

1. Go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Calendar API"**
3. Click **"Enable"** (if not already enabled)

### 4. Share Your Calendar

1. Open [Google Calendar](https://calendar.google.com)
2. Find your calendar in the left sidebar
3. Click the **three dots** → **"Settings and sharing"**
4. Scroll to **"Share with specific people"**
5. Click **"Add people"**
6. Paste the service account email (from the JSON file):
   - Format: `jashanmal-calendar-bot@gen-lang-client-0913736552.iam.gserviceaccount.com`
7. Set permission: **"Make changes to events"**
8. Click **"Send"**

### 5. Add Service Account Credentials to Streamlit Cloud

1. Open the downloaded JSON file
2. Copy the ENTIRE contents
3. Go to your Streamlit Cloud app
4. Click **"Settings"** → **"Secrets"**
5. Add this:

```toml
GOOGLE_API_KEY = "your_gemini_api_key"

# Service Account Credentials (paste the entire JSON)
[gcp_service_account]
type = "service_account"
project_id = "gen-lang-client-0913736552"
private_key_id = "paste_from_json"
private_key = "paste_from_json"
client_email = "paste_from_json"
client_id = "paste_from_json"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "paste_from_json"
```

**Important:** Keep the exact structure with `[gcp_service_account]` section!

---

## Code Changes Needed

I'll create a new version of `calendar_service.py` that works with both OAuth (local) and Service Account (cloud).
