# ✅ Streamlit Cloud Deployment Checklist

## Before You Deploy

### 1. Files Ready ✅
- [x] `runtime.txt` created (Python 3.11.9)
- [x] `.python-version` created
- [x] `.streamlit/config.toml` created
- [x] `requirements.txt` exists
- [x] `.gitignore` protects sensitive files

### 2. Environment Variables ✅
You said you already pasted `.env` in Streamlit Cloud advanced settings.

**Make sure it includes:**
```
GOOGLE_API_KEY=your_actual_gemini_api_key
```

### 3. Git Repository
```bash
# If not already initialized
git init
git add .
git commit -m "Initial commit for Streamlit Cloud"

# Push to GitHub
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

## Deployment Steps

### Step 1: Go to Streamlit Cloud
Visit: https://share.streamlit.io

### Step 2: Create New App
1. Click **"New app"** button
2. Choose **"From existing repo"**

### Step 3: Configure App
Fill in these fields:

**Repository:**
- Your GitHub username/repo-name

**Branch:**
- `main` (or your default branch)

**Main file path:**
- `app.py`

**App URL (optional):**
- Choose a custom subdomain or use auto-generated

### Step 4: Advanced Settings
Click **"Advanced settings"** and:

1. **Python version:** 
   - Will automatically use `runtime.txt` (3.11.9) ✅

2. **Secrets:**
   - Paste your environment variables:
   ```
   GOOGLE_API_KEY="your_actual_key_here"
   ```
   - Use quotes around the value
   - No spaces around `=`

### Step 5: Deploy!
Click **"Deploy"** button

## What Happens Next

### ⏱️ Deployment Timeline
1. **0-2 min:** Cloning repository
2. **2-5 min:** Installing dependencies
3. **5-8 min:** Building FAISS index
4. **8-10 min:** Starting app

### 📊 Watch the Logs
You'll see:
```
Cloning repository...
Installing requirements...
Building FAISS index...
App is live!
```

### ✅ Success Indicators
- App URL becomes clickable
- Status shows "Running"
- You can access the app

## Testing Your Deployed App

### Test These Features:

1. **Basic Query:**
   - "What's your return policy?"
   - Should search knowledge base and respond

2. **Greeting:**
   - "hi"
   - Should respond naturally

3. **Contact:**
   - "How do I contact support?"
   - Should show contact information

4. **Booking:**
   - "I want to book a meeting"
   - Will show contact info (calendar won't work on cloud)

5. **Streaming:**
   - Watch responses appear word-by-word ✨

## Common Issues & Solutions

### ❌ "Module not found"
**Solution:** Check `requirements.txt` has all packages

### ❌ "API Key Error"
**Solution:** 
- Go to app settings → Secrets
- Verify `GOOGLE_API_KEY` is set correctly
- No extra spaces or quotes issues

### ❌ "FAISS Index Error"
**Solution:** 
- Make sure `data/processed/faiss_index/` is in repo
- Check `.gitignore` doesn't exclude it

### ❌ "Booking Not Working"
**Expected:** Calendar booking won't work on cloud (OAuth issue)
- Users see contact info instead
- This is normal and handled gracefully

## After Deployment

### 🔄 Auto-Deploy on Push
Every time you push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```
Streamlit Cloud automatically redeploys!

### 📊 Monitor Your App
- Check app logs in Streamlit Cloud dashboard
- Monitor resource usage
- View error reports

### 🔒 Security Check
Verify these are NOT in your GitHub repo:
- `.env` file
- `booking/credentials.json`
- `booking/token.pickle`
- Any API keys in code

## Quick Reference

### Your Configuration
- **Python Version:** 3.11.9
- **Main File:** app.py
- **Required Secret:** GOOGLE_API_KEY

### Important URLs
- Streamlit Cloud: https://share.streamlit.io
- Your App: `https://[your-app-name].streamlit.app`
- Logs: Streamlit Cloud Dashboard → Your App → Logs

### Support
- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community Forum: https://discuss.streamlit.io

---

## 🎉 You're Ready!

Your app is configured and ready to deploy. Just:
1. Push to GitHub
2. Connect on Streamlit Cloud
3. Add your `GOOGLE_API_KEY` in secrets
4. Click Deploy!

Good luck! 🚀
