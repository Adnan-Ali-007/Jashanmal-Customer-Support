# 🚀 Streamlit Cloud Deployment Guide

## Python Version
**Your app uses: Python 3.11.9** ✅

This is specified in:
- `runtime.txt` - For Streamlit Cloud
- `.python-version` - For version managers

## Pre-Deployment Checklist

### ✅ Files Created
- [x] `runtime.txt` - Specifies Python 3.11.9
- [x] `.streamlit/config.toml` - Streamlit configuration
- [x] `requirements.txt` - All dependencies listed
- [x] `.gitignore` - Sensitive files excluded

### ⚠️ Important: Environment Variables

You mentioned you pasted your `.env` in Streamlit Cloud's advanced settings. Make sure you have:

**Required Environment Variables:**
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Optional (if using booking):**
- Google Calendar credentials will need special handling (see below)

## Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set:
   - **Main file path:** `app.py`
   - **Python version:** Will use `runtime.txt` (3.11.9)
5. Click "Advanced settings"
6. Paste your environment variables:
   ```
   GOOGLE_API_KEY=your_actual_key_here
   ```
7. Click "Deploy"

### 3. Wait for Deployment

- Initial deployment: 5-10 minutes
- Streamlit will install all dependencies from `requirements.txt`
- Watch the logs for any errors

## Important Notes

### 🔒 Security

**Already Protected (in .gitignore):**
- `.env` - Your API keys
- `booking/credentials.json` - OAuth credentials
- `booking/token.pickle` - OAuth token
- `storage/*.db` - Database files

**Never commit these files to GitHub!**

### 📅 Google Calendar Booking

**Important:** Calendar booking won't work on Streamlit Cloud by default because:
- OAuth requires local browser authentication
- `credentials.json` and `token.pickle` are not in the repo

**Options:**

**Option 1: Disable Booking for Cloud** (Recommended)
- Booking works locally
- On cloud, users see contact info instead
- No code changes needed - it already has fallback

**Option 2: Use Service Account** (Advanced)
- Create a Google Service Account
- Share your calendar with the service account email
- Use service account credentials instead of OAuth
- Requires code modifications

**Option 3: Pre-authenticate Locally**
- Not recommended - tokens expire
- Security risk

### 📊 Database

Your SQLite database (`storage/chat.db`) will be:
- Created fresh on deployment
- Reset on each redeploy
- Not persistent across restarts

For production, consider:
- PostgreSQL (via Streamlit Cloud secrets)
- External database service

## Troubleshooting

### "Module not found" Error
- Check `requirements.txt` has all dependencies
- Verify package names are correct
- Check Python version compatibility

### "API Key Error"
- Verify `GOOGLE_API_KEY` is in Streamlit secrets
- Check for typos in variable name
- Ensure key is valid and has Gemini API enabled

### "Booking Not Working"
- Expected behavior on cloud (see Calendar section above)
- Users will see contact info fallback
- Works fine locally

### App Crashes on Startup
- Check logs in Streamlit Cloud dashboard
- Verify all imports are in `requirements.txt`
- Check for file path issues (use relative paths)

## Post-Deployment

### Test Your App
1. Visit your app URL (e.g., `yourapp.streamlit.app`)
2. Test basic queries: "What's your return policy?"
3. Test greetings: "hi", "thanks"
4. Test contact: "How do I contact support?"
5. Booking will show contact info (expected)

### Monitor Usage
- Check Streamlit Cloud dashboard for:
  - App uptime
  - Error logs
  - Resource usage

### Update Your App
```bash
git add .
git commit -m "Update app"
git push origin main
```
Streamlit Cloud auto-deploys on push!

## Files Structure for Deployment

```
your-repo/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Dependencies
├── runtime.txt                     # Python version (3.11.9)
├── .python-version                 # Python version backup
├── .streamlit/
│   └── config.toml                 # Streamlit config
├── .gitignore                      # Excludes sensitive files
├── agents/
│   ├── agents.py                   # Agent logic
│   └── __init__.py
├── booking/                        # Booking module (works locally)
│   ├── calendar_service.py
│   ├── test_calendar.py
│   └── __init__.py
├── ingestion/                      # Data processing
│   ├── build_index.py
│   ├── gemini_embeddings.py
│   └── scrape_faq.py
├── data/
│   └── processed/
│       ├── faqs.json
│       └── faiss_index/
└── db/
    ├── database.py
    └── schema.sql
```

## Environment Variables Reference

### Required
```bash
GOOGLE_API_KEY=your_gemini_api_key
```

### Optional (for local development)
```bash
# Add any other API keys or configs here
```

## Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all environment variables
3. Test locally first: `streamlit run app.py`
4. Check [Streamlit Community Forum](https://discuss.streamlit.io)

## Quick Commands

```bash
# Test locally
streamlit run app.py

# Check Python version
python --version

# Verify requirements
pip list

# Push to GitHub
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main
```

---

**Your app is ready to deploy!** 🎉

Just push to GitHub and connect it to Streamlit Cloud.
