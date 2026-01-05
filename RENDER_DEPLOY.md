# Deploying to Render.com - Step by Step Guide

## 🚀 Quick Deploy Steps

### Step 1: Sign up / Login to Render
1. Go to [render.com](https://render.com)
2. Sign up or log in (you can use GitHub to sign in)

### Step 2: Deploy Backend Service

1. **Click "New +" → "Web Service"**

2. **Connect your repository:**
   - Click "Connect account" if not already connected
   - Select your GitHub account
   - Choose repository: `kartiklaad/althunt`

3. **Configure Backend Service:**
   - **Name:** `altitude-backend`
   - **Region:** Choose closest to you (e.g., `Oregon (US West)`)
   - **Branch:** `main`
   - **Root Directory:** (leave empty - uses root)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free` (or choose paid plan)

4. **Add Environment Variables:**
   Click "Advanced" → "Add Environment Variable"
   - `XAI_API_KEY` = `your_actual_xai_api_key_here`
   - `XAI_MODEL` = `grok-3`

5. **Click "Create Web Service"**

6. **Wait for deployment** (takes 2-5 minutes)
   - You'll see build logs
   - Once deployed, you'll get a URL like: `https://altitude-backend.onrender.com`

### Step 3: Deploy Frontend Service

1. **Click "New +" → "Web Service"** (again)

2. **Connect same repository:**
   - Select: `kartiklaad/althunt`

3. **Configure Frontend Service:**
   - **Name:** `altitude-frontend`
   - **Region:** Same as backend
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - **Plan:** `Free` (or choose paid plan)

4. **Add Environment Variables:**
   - `BACKEND_URL` = `https://altitude-backend.onrender.com` (use your actual backend URL from Step 2)

5. **Click "Create Web Service"**

6. **Wait for deployment**

### Step 4: Test Your Deployment

1. **Test Backend:**
   ```bash
   curl https://altitude-backend.onrender.com/
   ```
   Should return: `{"status": "online", ...}`

2. **Test Frontend:**
   - Visit your frontend URL: `https://altitude-frontend.onrender.com`
   - Try sending a message
   - Test voice mode (requires HTTPS - which Render provides)

## 🔧 Alternative: Using render.yaml (Automatic)

If you prefer automatic setup:

1. **Push render.yaml to your repo** (already done ✅)

2. **In Render Dashboard:**
   - Click "New +" → "Blueprint"
   - Connect your repo: `kartiklaad/althunt`
   - Render will detect `render.yaml` and create both services
   - **You still need to add environment variables manually:**
     - In backend service: `XAI_API_KEY` and `XAI_MODEL`
     - In frontend service: `BACKEND_URL` (set to your backend URL)

## ⚙️ Important Notes

### Free Tier Limitations:
- Services **sleep after 15 minutes of inactivity**
- First request after sleep takes ~30 seconds to wake up
- 750 hours/month free (enough for testing)

### Environment Variables:
- **Backend needs:**
  - `XAI_API_KEY` (required)
  - `XAI_MODEL` (optional, defaults to grok-3)

- **Frontend needs:**
  - `BACKEND_URL` (required - must be full URL with https://)

### Updating Your App:
- Push changes to GitHub
- Render automatically redeploys (or click "Manual Deploy" in dashboard)

### Viewing Logs:
- Click on your service in Render dashboard
- Go to "Logs" tab
- See real-time logs and errors

## 🐛 Troubleshooting

### Backend not starting:
- Check logs in Render dashboard
- Verify `XAI_API_KEY` is set correctly
- Check build logs for dependency errors

### Frontend can't connect to backend:
- Verify `BACKEND_URL` is set correctly (include `https://`)
- Check backend is running (visit backend URL directly)
- Check CORS settings (already configured ✅)

### Build fails:
- Check Python version (Render uses Python 3.11 by default)
- Check `requirements.txt` for any issues
- Review build logs

### Voice mode not working:
- Requires HTTPS (Render provides this ✅)
- Check browser console (F12) for errors
- Verify microphone permissions

## 📝 Quick Checklist

- [ ] Backend service created and deployed
- [ ] `XAI_API_KEY` environment variable set in backend
- [ ] Backend URL working (test with curl)
- [ ] Frontend service created and deployed
- [ ] `BACKEND_URL` environment variable set in frontend (pointing to backend)
- [ ] Frontend accessible and can send messages
- [ ] Voice mode tested (if needed)

## 🎉 You're Done!

Your app should now be live at:
- **Backend:** `https://altitude-backend.onrender.com`
- **Frontend:** `https://altitude-frontend.onrender.com`

Share the frontend URL with others to test!

