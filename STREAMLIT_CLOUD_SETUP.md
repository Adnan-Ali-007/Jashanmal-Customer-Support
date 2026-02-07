# ☁️ Streamlit Cloud Deployment Guide

## 🚀 Deploy Your Chatbot to Streamlit Cloud

### **Step 1: Push to GitHub**
```bash
git add .
git commit -m "Deploy chatbot to Streamlit Cloud"
git push origin main
```

### **Step 2: Deploy on Streamlit Cloud**
1. Go to https://share.streamlit.io/
2. Click **"New app"**
3. Select your GitHub repository
4. Set main file: `app.py`
5. Click **"Deploy"**

---

## 🔒 **Step 3: Add Secrets (IMPORTANT!)**

Your app won't work without secrets! Here's how to add them:

### **3.1: Open Secrets Manager**
1. Go to your deployed app dashboard
2. Click **Settings** (⚙️ icon)
3. Click **"Secrets"** in left menu

### **3.2: Add Your Secrets**

Paste this in the secrets editor (replace with your actual values):

```toml
# Google Gemini API (Required)
GOOGLE_API_KEY = "your_actual_google_api_key"

# Twilio WhatsApp (Required for notifications)
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "your_actual_twilio_auth_token"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
YOUR_WHATSAPP_NUMBER = "whatsapp:+917780879882"
```

**Important Notes:**
- ✅ Use your ACTUAL credentials (not placeholders)
- ✅ `TWILIO_ACCOUNT_SID` must start with **AC** (not SK)
- ✅ Get Auth Token from https://console.twilio.com/
- ✅ No quotes around values in TOML format
- ✅ Save the secrets

### **3.3: Restart Your App**
1. Click **"Reboot app"** button
2. Wait for app to restart
3. Test WhatsApp notifications

---

## ✅ **Verify Deployment**

### **Test These Features:**

1. **Basic Chat**
   - Ask: "What are your shipping options?"
   - Should get FAQ response

2. **Order Tracking**
   - Ask: "Track order 12346"
   - Should show order status
   - **Should send WhatsApp notification** 📱

3. **Return Request**
   - Ask: "I want to return order 12345"
   - Should process return
   - **Should send WhatsApp notification** 📱

4. **Refund Status**
   - Ask: "Where is my refund?"
   - Should show refund status
   - **Should send WhatsApp notification** 📱

---

## 🐛 **Troubleshooting**

### **WhatsApp Not Working on Cloud**

**Problem:** Works locally but not on Streamlit Cloud

**Solution:**
1. ✅ Check secrets are added correctly
2. ✅ Verify `TWILIO_ACCOUNT_SID` starts with AC
3. ✅ Ensure Auth Token is correct
4. ✅ Reboot app after adding secrets
5. ✅ Check app logs for errors

**View Logs:**
- Click **"Manage app"** → **"Logs"**
- Look for "WhatsApp notification failed" errors

### **Common Errors:**

**Error: "Authentication Error - invalid username"**
- ❌ Wrong Account SID (should start with AC)
- ❌ Wrong Auth Token
- ✅ Fix: Update secrets with correct credentials

**Error: "No module named 'twilio'"**
- ❌ Missing dependency
- ✅ Fix: Ensure `twilio>=8.10.0` is in requirements.txt
- ✅ Reboot app

**Error: "WhatsApp service not available"**
- ❌ Secrets not configured
- ✅ Fix: Add secrets in Streamlit Cloud dashboard

---

## 📊 **Check Secrets Are Loaded**

Add this temporarily to your app to debug:

```python
import streamlit as st

# Debug: Check if secrets are loaded
if st.secrets:
    st.write("✅ Secrets loaded")
    st.write("TWILIO_ACCOUNT_SID:", st.secrets.get("TWILIO_ACCOUNT_SID", "NOT FOUND")[:10] + "...")
else:
    st.write("❌ No secrets found")
```

Remove this after confirming secrets work!

---

## 🔐 **Security Best Practices**

### **DO:**
- ✅ Use Streamlit secrets for all credentials
- ✅ Keep `.env` in `.gitignore`
- ✅ Never commit API keys to GitHub
- ✅ Rotate credentials regularly

### **DON'T:**
- ❌ Put credentials in code
- ❌ Commit `.env` file
- ❌ Share secrets publicly
- ❌ Use production keys for testing

---

## 🎯 **Production Checklist**

Before going live:
- [ ] All secrets added to Streamlit Cloud
- [ ] WhatsApp notifications tested
- [ ] Order tracking working
- [ ] Return requests functional
- [ ] Refund status operational
- [ ] Dark mode enabled
- [ ] Conversation history working
- [ ] No errors in logs

---

## 📱 **WhatsApp Sandbox Limitations**

**Twilio Sandbox (Free):**
- ✅ Good for demos
- ✅ Free testing
- ❌ "Sent from Twilio Sandbox" prefix
- ❌ Limited to sandbox numbers

**Production WhatsApp:**
- ✅ Your own number
- ✅ No sandbox prefix
- ✅ Unlimited recipients
- 💰 $0.005 per message

**Upgrade to Production:**
1. Apply for WhatsApp Business API
2. Get approved by Meta
3. Buy Twilio phone number
4. Enable WhatsApp on number
5. Update `TWILIO_WHATSAPP_NUMBER` in secrets

---

## 🚀 **Performance Tips**

### **Optimize for Cloud:**
1. Use caching for vector store
2. Minimize API calls
3. Implement rate limiting
4. Monitor usage

### **Cost Optimization:**
- Gemini API: ~$0.001 per request
- Twilio WhatsApp: $0.005 per message
- Streamlit Cloud: Free tier available

---

## 📞 **Support**

**Streamlit Cloud Issues:**
- Docs: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io/

**Twilio Issues:**
- Docs: https://www.twilio.com/docs/whatsapp
- Support: https://support.twilio.com/

---

## ✅ **Success!**

Once deployed and secrets configured:
- ✅ Your chatbot is live 24/7
- ✅ WhatsApp notifications work
- ✅ Accessible from anywhere
- ✅ Auto-updates from GitHub
- ✅ Free hosting (Streamlit tier)

**Your deployed URL:**
`https://your-app-name.streamlit.app`

Share this with clients for demos! 🎉
