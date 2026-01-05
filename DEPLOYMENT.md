# Deployment Guide for Altitude Huntsville Party Booking Assistant

This guide covers multiple hosting options for deploying your Streamlit + FastAPI application.

## 🚀 Quick Options

### Option 1: Railway (Recommended - Easiest)

**Pros:** Very easy setup, good free tier, handles both services well
**Cons:** Free tier has usage limits

#### Steps:

1. **Sign up at [railway.app](https://railway.app)**

2. **Create a new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (connect your GitHub)
   - Or use "Empty Project" and deploy via CLI

3. **Deploy Backend:**
   - Add a new service → "GitHub Repo" → Select your repo
   - Set **Root Directory** to: `/` (root)
   - Set **Start Command** to: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables:
     - `XAI_API_KEY` = your xAI API key
     - `XAI_MODEL` = `grok-3`
     - `PORT` = `8000` (Railway sets this automatically)

4. **Deploy Frontend:**
   - Add another service → "GitHub Repo" → Same repo
   - Set **Root Directory** to: `/` (root)
   - Set **Start Command** to: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - Add environment variables:
     - `BACKEND_URL` = `https://your-backend-service.railway.app` (get from backend service)
     - `PORT` = `8501` (or let Railway set it)

5. **Get your URLs:**
   - Backend: `https://your-backend.railway.app`
   - Frontend: `https://your-frontend.railway.app`

---

### Option 2: Render (Good Free Tier)

**Pros:** Free tier available, simple setup
**Cons:** Free tier services sleep after inactivity

#### Steps:

1. **Sign up at [render.com](https://render.com)**

2. **Deploy Backend:**
   - New → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - **Name:** `altitude-backend`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables:
     - `XAI_API_KEY` = your xAI API key
     - `XAI_MODEL` = `grok-3`

3. **Deploy Frontend:**
   - New → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - **Name:** `altitude-frontend`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - Add environment variables:
     - `BACKEND_URL` = `https://altitude-backend.onrender.com` (your backend URL)

4. **Or use render.yaml (easier):**
   - Push `render.yaml` to your repo
   - Render will detect it and create both services automatically
   - Just add environment variables in the dashboard

---

### Option 3: Streamlit Cloud (Frontend) + Railway/Render (Backend)

**Pros:** Streamlit Cloud is optimized for Streamlit apps
**Cons:** Need to manage two separate platforms

#### Steps:

1. **Deploy Backend** (Railway or Render - follow Option 1 or 2)

2. **Deploy Frontend on Streamlit Cloud:**
   - Sign up at [streamlit.io/cloud](https://streamlit.io/cloud)
   - Click "New app"
   - Connect GitHub repo
   - Set:
     - **Main file:** `app.py`
     - **Python version:** `3.11`
   - Add secrets (Settings → Secrets):
     ```
     BACKEND_URL=https://your-backend-url.com
     ```

---

### Option 4: Fly.io (Good for Full-Stack)

**Pros:** Good free tier, fast, global
**Cons:** Requires CLI setup

#### Steps:

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Create apps:**
   ```bash
   # Backend
   fly launch --name altitude-backend
   # Follow prompts, select Python
   
   # Frontend (in separate directory or use fly.toml)
   fly launch --name altitude-frontend
   ```

4. **Set environment variables:**
   ```bash
   fly secrets set XAI_API_KEY=your_key -a altitude-backend
   fly secrets set BACKEND_URL=https://altitude-backend.fly.dev -a altitude-frontend
   ```

---

## 🔧 Important Configuration

### Environment Variables Needed:

**Backend:**
- `XAI_API_KEY` - Your xAI API key (required)
- `XAI_MODEL` - Model name (default: `grok-3`)
- `PORT` - Port number (usually set by platform)

**Frontend:**
- `BACKEND_URL` - Full URL of your backend (e.g., `https://your-backend.railway.app`)

### Update app.py for Production:

Make sure `BACKEND_URL` is read from environment:

```python
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
```

This is already set up in your code! ✅

---

## 🧪 Testing After Deployment

1. **Test Backend:**
   ```bash
   curl https://your-backend-url.com/
   # Should return: {"status": "online", ...}
   ```

2. **Test Frontend:**
   - Visit your frontend URL
   - Try sending a message
   - Check browser console (F12) for errors

3. **Test Voice Mode:**
   - Enable voice mode
   - Grant microphone permissions
   - Test speech recognition

---

## 🐛 Troubleshooting

### Backend not responding:
- Check environment variables are set
- Check logs in hosting platform dashboard
- Verify `XAI_API_KEY` is correct

### Frontend can't connect to backend:
- Verify `BACKEND_URL` is correct (include `https://`)
- Check CORS settings (already configured in `backend/main.py`)
- Check backend is running (visit backend URL directly)

### Voice mode not working:
- Requires HTTPS (most hosting platforms provide this)
- Check browser console for microphone permission errors
- Verify Web Speech API is supported (Chrome/Edge work best)

---

## 📝 Quick Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] Environment variables configured
- [ ] Backend deployed and accessible
- [ ] Frontend `BACKEND_URL` points to backend
- [ ] Tested basic chat functionality
- [ ] Tested voice mode (if needed)

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Starts At |
|----------|-----------|----------------|
| Railway  | $5 credit/month | $5/month |
| Render   | Free (sleeps) | $7/month |
| Streamlit Cloud | Free | Free |
| Fly.io   | 3 VMs free | $1.94/month |

**Recommendation:** Start with Railway or Render for easiest setup!

