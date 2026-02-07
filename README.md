# 🤖 Jashanmal AI Customer Support Chatbot

An intelligent, agentic AI chatbot for e-commerce customer support with real-time order tracking, returns management, and WhatsApp notifications.

## ✨ Features

### 🎯 Core Capabilities
- **Intelligent FAQ System** - RAG-based question answering using FAISS vector store
- **Order Tracking** - Real-time order status with tracking information
- **Return Management** - Automated return request processing
- **Refund Status** - Live refund tracking and updates
- **Meeting Booking** - Google Calendar integration for support appointments
- **WhatsApp Notifications** - Proactive customer updates via Twilio

### 🧠 AI Architecture
- **LangGraph Agent System** - Multi-node agentic workflow
- **Google Gemini 2.5 Flash** - Advanced language model
- **Context-Aware Routing** - Intelligent intent classification
- **Conversation Memory** - Persistent chat history with SQLite
- **Streaming Responses** - Real-time token-by-token generation

### 🎨 User Experience
- **Dark Mode UI** - Professional, modern interface
- **Conversation History** - Sidebar with past chats
- **Multi-turn Conversations** - Context retention across messages
- **Real-time Status Updates** - Live processing indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google API Key (for Gemini)
- Twilio Account (for WhatsApp, optional)
- Google Calendar API (for booking, optional)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd chatbot_demo
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Run the chatbot**
```bash
streamlit run app.py
```

## 🔧 Configuration

### Required Environment Variables

Create a `.env` file with:

```env
# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# WhatsApp (Optional - for notifications)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+your_number

# Google Calendar (Optional - for booking)
# Place credentials.json in booking/ folder
```

## 📦 Project Structure

```
chatbot_demo/
├── agents/                 # LangGraph agent nodes
│   ├── agents.py          # Main agent logic
│   └── __init__.py
├── booking/               # Google Calendar integration
│   ├── calendar_service.py
│   └── test_calendar.py
├── data/                  # Vector store and FAQs
│   └── processed/
│       ├── faiss_index/
│       └── faqs.json
├── db/                    # Database utilities
│   └── database.py        # SQLite conversation storage
├── demo/                  # Mock e-commerce backend
│   ├── mock_ecommerce.py  # Demo order system
│   ├── test_demo.py
│   └── test_whatsapp.py
├── ingestion/             # Data processing
│   ├── scrape_faq.py      # Web scraping
│   ├── build_index.py     # Vector index creation
│   └── gemini_embeddings.py
├── notifications/         # WhatsApp service
│   └── whatsapp_service.py
├── storage/               # SQLite database
│   └── chat.db
├── .streamlit/            # Streamlit config
│   └── config.toml
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
└── README.md
```

## 🎯 Demo Features

### Order Tracking
```
User: "Track order 12346"
Bot: Shows shipping status with tracking number
WhatsApp: Sends notification to customer
```

### Return Requests
```
User: "I want to return order 12345"
Bot: Processes return, generates label
WhatsApp: Sends return approval notification
```

### Refund Status
```
User: "Where is my refund?"
Bot: Shows refund processing status
WhatsApp: Sends refund update
```

## 📚 Documentation

- [Demo Guide](DEMO_GUIDE.md) - Complete demo walkthrough
- [Demo Quick Reference](DEMO_QUICK_REFERENCE.md) - Quick tips
- [WhatsApp Setup](WHATSAPP_SETUP.md) - WhatsApp integration guide
- [Booking Flow](BOOKING_FLOW.md) - Calendar booking documentation
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment

## 🛠️ Tech Stack

- **Framework**: Streamlit
- **AI/ML**: LangChain, LangGraph, Google Gemini
- **Vector Store**: FAISS
- **Database**: SQLite
- **Notifications**: Twilio WhatsApp API
- **Calendar**: Google Calendar API
- **Web Scraping**: BeautifulSoup, Requests

## 🎬 Demo Orders

For testing, use these demo order IDs:
- **ORD-12345** - Delivered iPhone ($999)
- **ORD-12346** - Shipped Samsung ($899)
- **ORD-12347** - Processing MacBook ($2,499)
- **ORD-12348** - Delivered Headphones ($399)

## 🔒 Security

- Environment variables for sensitive data
- `.gitignore` configured to exclude credentials
- No API keys in code
- Secure token storage for Google Calendar

## 📈 Performance

- Sub-second response times
- Streaming for better UX
- Efficient vector search with FAISS
- Indexed database queries

## 🤝 Contributing

This is a demo project. For production use:
1. Replace mock backend with real e-commerce API
2. Implement proper authentication
3. Add rate limiting
4. Set up monitoring and logging
5. Deploy with proper CI/CD

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Built for Jashanmal customer support automation

## 🙏 Acknowledgments

- Google Gemini for LLM capabilities
- LangChain/LangGraph for agent framework
- Twilio for WhatsApp integration
- Streamlit for rapid UI development

---

**Note**: This is a demo/prototype. For production deployment, additional security, scalability, and integration work is required.
