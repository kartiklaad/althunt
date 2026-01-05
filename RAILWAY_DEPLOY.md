# Deploying to Railway.app - Step by Step Guide

## 🚀 Quick Deploy Steps

### Step 1: Sign up / Login to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with GitHub (recommended - easiest way)

### Step 2: Create New Project

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
   - If not connected, click "Configure GitHub App"
   - Authorize Railway to access your repositories
   - Select repository: `kartiklaad/althunt`
   - Click "Deploy Now"

### Step 3: Deploy Backend Service

Railway will automatically detect your project. You need to configure it:

1. **Click on the service** (or "New" → "Service" if needed)

2. **Configure Service:**
   - **Name:** `altitude-backend` (or keep default)
   - Railway will auto-detect it's a Python project

3. **Set Start Command:**
   - Click on the service
   - Go to "Settings" tab
   - Under "Deploy", set **Start Command:**
     ```
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```

4. **Add Environment Variables:**
   - Click "Variables" tab
   - Click "New Variable"
   - Add:
     - `XAI_API_KEY` = `your_actual_xai_api_key_here`
     - `XAI_MODEL` = `grok-3`
     - `PORT` = `8000` (Railway sets this automatically, but you can set it)

5. **Get Backend URL:**
   - Click "Settings" tab
   - Under "Domains", Railway will generate a URL
   - Copy the URL (e.g., `https://altitude-backend-production.up.railway.app`)

### Step 4: Deploy Frontend Service

1. **Add another service:**
   - In your project, click "New" → "Service"
   - Select "GitHub Repo"
   - Choose: `kartiklaad/althunt` (same repo)

2. **Configure Service:**
   - **Name:** `altitude-frontend`

3. **Set Start Command:**
   - Go to "Settings" → "Deploy"
   - Set **Start Command:**
     ```
     streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
     ```

4. **Add Environment Variables:**
   - Click "Variables" tab
   - Add:
     - `BACKEND_URL` = `https://altitude-backend-production.up.railway.app` (use your actual backend URL from Step 3)

5. **Get Frontend URL:**
   - Click "Settings" → "Domains"
   - Railway will generate a URL
   - Or click "Generate Domain" to get a custom URL

### Step 5: Test Your Deployment

1. **Test Backend:**
   ```bash
   curl https://your-backend-url.railway.app/
   ```
   Should return: `{"status": "online", ...}`

2. **Test Frontend:**
   - Visit your frontend URL
   - Try sending a message
   - Test voice mode (requires HTTPS - Railway provides this ✅)

## 🔧 Alternative: Using Railway CLI

If you prefer command line:

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Link project:**
   ```bash
   railway link
   ```

4. **Set variables:**
   ```bash
   railway variables set XAI_API_KEY=your_key
   railway variables set XAI_MODEL=grok-3
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

## ⚙️ Important Notes

### Railway Free Tier:
- **$5 credit/month** (enough for testing)
- Services run continuously (no sleep)
- Fast deployments
- Auto-deploys on git push

### Environment Variables:
- **Backend needs:**
  - `XAI_API_KEY` (required)
  - `XAI_MODEL` (optional, defaults to grok-3)

- **Frontend needs:**
  - `BACKEND_URL` (required - must be full URL with https://)

### Custom Domains:
- Railway provides free `.railway.app` domains
- You can add custom domains in "Settings" → "Domains"

### Updating Your App:
- Push changes to GitHub
- Railway automatically redeploys
- Or click "Redeploy" in dashboard

### Viewing Logs:
- Click on your service
- Go to "Deployments" tab
- Click on a deployment to see logs
- Or use "Logs" tab for real-time logs

## 🐛 Troubleshooting

### Backend not starting:
- Check logs in Railway dashboard
- Verify `XAI_API_KEY` is set correctly
- Check "Deployments" tab for build errors
- Verify start command is correct

### Frontend can't connect to backend:
- Verify `BACKEND_URL` is set correctly (include `https://`)
- Check backend is running (visit backend URL directly)
- Check CORS settings (already configured ✅)
- Make sure backend URL doesn't have trailing slash

### Build fails:
- Check Python version (Railway uses Python 3.11 by default)
- Check `requirements.txt` for any issues
- Review build logs in "Deployments" tab

### Port issues:
- Railway sets `$PORT` automatically
- Don't hardcode port numbers
- Use `$PORT` in start commands

### Voice mode not working:
- Requires HTTPS (Railway provides this ✅)
- Check browser console (F12) for errors
- Verify microphone permissions
- Check that `BACKEND_URL` uses `https://`

## 📝 Quick Checklist

- [ ] Railway account created and GitHub connected
- [ ] Backend service created and deployed
- [ ] `XAI_API_KEY` environment variable set in backend
- [ ] Backend URL copied
- [ ] Frontend service created and deployed
- [ ] `BACKEND_URL` environment variable set in frontend (pointing to backend)
- [ ] Frontend accessible and can send messages
- [ ] Voice mode tested (if needed)

## 🎉 You're Done!

Your app should now be live at:
- **Backend:** `https://your-backend.railway.app`
- **Frontend:** `https://your-frontend.railway.app`

Share the frontend URL with others to test!

## 💡 Pro Tips

1. **Use Railway's GitHub integration** - Auto-deploys on every push
2. **Check the "Metrics" tab** - See CPU, memory usage
3. **Use "Settings" → "Healthcheck"** - Set health check path: `/`
4. **Enable "Auto Deploy"** - Deploys automatically on git push
5. **Use "Preview Deployments"** - Test PRs before merging

