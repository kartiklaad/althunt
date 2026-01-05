# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:
- `XAI_API_KEY` - **REQUIRED** - Get from https://console.x.ai (pay-as-you-go, very affordable!)
- `ROLLER_CLIENT_ID` - Already included (from your blueprint)
- `ROLLER_CLIENT_SECRET` - Already included (from your blueprint)
- `SENDGRID_API_KEY` - Optional (for email confirmations)
- `TWILIO_*` - Optional (for SMS notifications)
- `XAI_MODEL` - Optional (defaults to "grok-beta", can use "grok-2-1212" for specific version)

## 3. Run the Application

### Option A: Using the Run Script (Easiest)

```bash
./run.sh
```

This will start both the FastAPI backend and Streamlit frontend automatically.

### Option B: Manual Start

**Terminal 1 - Start FastAPI backend:**
```bash
uvicorn backend.main:app --reload
```

**Terminal 2 - Start Streamlit frontend:**
```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## 4. Test the System

1. Open the Streamlit app at http://localhost:8501
2. Start a conversation: "Hi, I'd like to book a party"
3. The AI will guide you through:
   - Package selection
   - Date/time selection
   - Availability checking
   - Price calculation
   - Booking creation

## Features Implemented

✅ **Conversational AI Agent** - Powered by xAI Grok, super friendly and enthusiastic!  
✅ **Package Information** - All 4 packages with updated Jan 2026 details  
✅ **Availability Checking** - Real-time slot checking via Roller API  
✅ **Price Calculation** - Automatic price breakdowns (private room: $5/jumper for all)  
✅ **Booking Creation** - Creates bookings and generates checkout links  
✅ **Glo Party Restrictions** - Strictly enforces Friday/Saturday only  
✅ **Conversation Memory** - Remembers context across turns  
✅ **Document Upload & Search** - Upload waivers, rules, FAQs for AI to reference  
✅ **Voice Mode** - Toggle for voice interactions (WebSocket ready)  
✅ **Email Service** - Ready for confirmation emails (needs SendGrid key)  

## Testing Without Roller API

The system includes mock responses for local testing. If the Roller API is unavailable, it will:
- Return mock availability data
- Create mock bookings with test checkout URLs
- Log warnings instead of failing

## Next Steps

1. **Test with real Roller API**: Update the `ROLLER_BASE_URL` in `.env` if needed
2. **Configure SendGrid**: Add your SendGrid API key for email confirmations
3. **Customize prompts**: Edit `backend/agent.py` to adjust the AI's personality
4. **Add webhook handling**: Implement payment confirmation webhooks in `backend/main.py`

## Troubleshooting

**"Module not found" errors:**
- Make sure you're in the project root directory
- Run `pip install -r requirements.txt` again

**"XAI_API_KEY not found":**
- Check your `.env` file has `XAI_API_KEY` set
- Get your API key from https://console.x.ai (sign up, it's free to start!)
- Make sure you're using `python-dotenv` to load it

**Backend not connecting:**
- Check that FastAPI is running on port 8000
- Verify `BACKEND_URL` in Streamlit matches your backend URL

**Agent not remembering conversation:**
- The memory is maintained through conversation history passed to the API
- Make sure the Streamlit app is sending the full message history

