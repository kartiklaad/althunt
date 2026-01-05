# Altitude Huntsville Party Booking Assistant

A friendly AI-powered party booking system for Altitude Trampoline Park in Huntsville, built with FastAPI, LangChain, Streamlit, and powered by **xAI's Grok API**! 🚀

## Features

- 🤖 Conversational AI agent powered by Grok that guides users through party booking
- 🎤 Voice mode support (WebSocket-based, Grok Voice Agent API compatible)
- 📄 Document upload & search - upload waivers, park rules, FAQs for AI to reference
- 📅 Real-time availability checking via Roller API
- 💳 Secure payment processing through Roller checkout
- 📧 Email confirmations
- 💬 Multi-turn conversation memory
- 🎉 Support for all party packages (Rookie, All-Star, MVP, Glo Party)
- ✨ Super friendly and enthusiastic AI personality

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
# REQUIRED: XAI_API_KEY (get from https://console.x.ai - it's pay-as-you-go and very affordable!)
```

3. **Run the application:**

   **Option A: Streamlit (Recommended for local testing)**
   ```bash
   streamlit run app.py
   ```
   Then open http://localhost:8501

   **Option B: FastAPI backend only**
   ```bash
   uvicorn backend.main:app --reload
   ```
   Then open http://localhost:8000/docs for API docs

## Project Structure

```
.
├── app.py                 # Streamlit frontend
├── backend/
│   ├── main.py           # FastAPI server
│   ├── agent.py          # LangChain agent setup
│   ├── roller_client.py  # Roller API integration
│   └── packages.py       # Party package definitions
├── .env.example          # Environment variables template
└── requirements.txt      # Python dependencies
```

## Party Packages (Updated Jan 2026)

- **Rookie**: $25/jumper (min 10) - Jump time, table time, party host, setup/cleanup, basic supplies, grip socks. No pizza/soda/arcade/gift/pass.
- **All-Star**: $30/jumper (min 10) - Everything in Rookie + large pizza per 5 jumpers
- **MVP**: $35/jumper (min 10) - Everything in All-Star + arcade card per jumper
- **Glo Party**: $40/jumper (min 10) - Everything in MVP + gift for birthday child, 3 hours total, **Friday/Saturday nights ONLY**
- **Private Room**: +$5 per jumper for ALL packages

## xAI Grok Integration

The system uses xAI's Grok API for:
- **Text Chat**: OpenAI-compatible client with `base_url="https://api.x.ai/v1"`
- **Model**: `grok-2-1212` (latest) - excellent tool calling and reasoning
- **Voice Mode**: WebSocket-based Grok Voice Agent API (OpenAI Realtime compatible)
- **File Handling**: xAI Files API for document upload and search
- **Voices**: "Ara" (friendly female) or "Rex" (energetic male) for voice interactions

Get your API key at https://console.x.ai - it's pay-as-you-go and very affordable!

## Roller API Integration

The system integrates with Roller API for:
- Authentication (OAuth2 client credentials)
- Availability checking
- Booking creation
- Payment checkout generation

## New Features

### Document Upload & Search
Upload waivers, park rules, or FAQs through the Streamlit UI. The AI can search through these documents to answer questions about policies, requirements, etc.

### Voice Mode
Toggle voice mode in the sidebar. The system is ready for WebSocket integration with Grok Voice Agent API for real-time voice conversations.

## License

Private project for Altitude Trampoline Park Huntsville

