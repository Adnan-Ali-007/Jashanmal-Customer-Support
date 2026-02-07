# 📝 How to Update FAQs

## Quick Steps

### 1. Edit the FAQs
Edit `data/processed/faqs.json` with your updated information.

### 2. Rebuild the Index
Run this command to update the vector database:
```bash
venv\Scripts\python.exe ingestion\build_index.py
```

### 3. Test Locally
```bash
streamlit run app.py
```

### 4. Deploy to Cloud
```bash
git add data/processed/faqs.json data/processed/faiss_index/
git commit -m "Update FAQs"
git push origin main
```

---

## What I Just Updated

### Payment Methods - Before:
```
"We offer flexible and secure payment options. Accepted payment methods 
include Mastercard credit or debit cards. Payments must be made in the 
currency shown on your order."
```

### Payment Methods - After:
```
"We offer flexible and secure payment options for a smooth checkout experience.

Accepted payment methods:
• VISA credit/debit
• MASTERCARD credit/debit
• Apple Pay
• Tabby
• Tamara
• Cash on Delivery

Payment must be made in the currency as indicated on your order before you 
submit it. Your products will be supplied after your payment is cleared."
```

---

## FAQ Structure

Each FAQ entry has:
```json
{
  "category": "payment",
  "question": "Accepted payment methods",
  "answer": "Your detailed answer here...",
  "source": "https://www.jashanmal.com/pages/payment"
}
```

### Categories:
- `orders` - Order placement, confirmation, changes
- `payment` - Payment methods, issues, verification
- `shipping` - Delivery, timelines, tracking
- `returns` - Return policy, refunds, exchanges
- `gift_card` - Gift card usage and terms
- `about` - Company information

---

## Tips for Better Answers

### ✅ Do:
- Be specific and detailed
- Use bullet points for lists
- Include all relevant information
- Keep a friendly, helpful tone

### ❌ Don't:
- Be too brief or vague
- Leave out important details
- Use overly technical language
- Forget to rebuild the index!

---

## Testing Your Changes

### Test Query Examples:
```python
# Test payment methods
"What payment methods do you accept?"
"Can I use Apple Pay?"
"Do you accept Tabby?"

# Test shipping
"How long does delivery take?"
"Do you deliver to Abu Dhabi?"

# Test returns
"What's your return policy?"
"Can I return perfume?"
```

---

## Troubleshooting

### Bot gives old answer?
- Make sure you ran `build_index.py`
- Check that `faqs.json` was saved correctly
- Restart Streamlit app

### Bot doesn't find the answer?
- Check the question phrasing in `faqs.json`
- Make sure the category is correct
- Try adding more keywords to the answer

### Changes not showing on cloud?
- Make sure you committed the FAISS index files
- Check that both `faqs.json` and `faiss_index/` are pushed
- Wait for Streamlit Cloud to redeploy

---

## File Locations

```
data/
└── processed/
    ├── faqs.json              # Edit this file
    └── faiss_index/           # Auto-generated, commit to git
        ├── index.faiss
        └── index.pkl
```

---

## Quick Commands Reference

```bash
# Rebuild index after editing FAQs
venv\Scripts\python.exe ingestion\build_index.py

# Test locally
streamlit run app.py

# Deploy to cloud
git add data/processed/
git commit -m "Update FAQs"
git push origin main
```

---

## Result

Now when users ask about payment methods, they get the complete, detailed answer with all 6 payment options! 🎉
