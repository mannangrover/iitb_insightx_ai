# Railway Deployment Guide for InsightX

## Quick Start

### Option 1: Deploy via Railway CLI (Recommended)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy the app**
   ```bash
   railway up
   ```

   This will:
   - Build the Docker image
   - Deploy both FastAPI and Streamlit services
   - Assign public URLs automatically

### Option 2: Deploy via GitHub (Push-to-Deploy)

1. **Push your code to GitHub** (already done)
   ```bash
   git push origin main
   ```

2. **Go to Railway.app**
   - Sign in or create an account at https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account and select `iitb_insightx_ai`

3. **Configure Environment Variables**
   - In the Railway dashboard, go to your project's "Variables"
   - Set any required variables (e.g., `OPENAI_API_KEY` if using LLM features)
   - `DATABASE_URL` defaults to SQLite locally; if you need persistent storage, you can add a PostgreSQL service

4. **View Deployment**
   - Railway automatically detects Dockerfile and builds
   - Services will be assigned URLs like `https://your-app-*.railway.app`

---

## What Gets Deployed

The `Dockerfile` in the repo:
- Installs all Python dependencies from `requirements.txt`
- Pulls Git LFS files (for `insightx_db.db`)
- Starts **FastAPI** on port 8000
- Starts **Streamlit** on port 8501
- Exposes both via Railway's public domain

**Access Points:**
- **Streamlit UI**: `https://your-app-*.railway.up.railway.app:8501`
- **FastAPI API**: `https://your-app-*.railway.up.railway.app:8000`
- **API Docs**: `https://your-app-*.railway.up.railway.app:8000/docs`

---

## Environment Variables

Set these in Railway's Variables section:

| Variable | Value | Required |
|----------|-------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | No (falls back to template responses) |
| `DATABASE_URL` | SQLite path or PostgreSQL URL | No (defaults to `sqlite:///./insightx_db.db`) |
| `API_URL` | For local Streamlit dev pointing to remote API | No |

---

## Monitoring & Logs

After deployment:
1. Go to Railway dashboard → your project
2. Click the **Logs** tab to see real-time output
3. Click **Deployments** to see build history
4. Use **Variables** tab to update env vars (auto-redeploys)

---

## Scaling & Persistence

- **Multiple Replicas**: Railway's "Scale" tab lets you run multiple instances (auto load-balanced)
- **Database Persistence**: SQLite is ephemeral on Railway; for production, add a PostgreSQL service:
  - Click "Add Service" → PostgreSQL
  - Railway auto-injects `DATABASE_URL` to your app
  - Update your app's SQLAlchemy config to use it

---

## Troubleshooting

### Port conflicts
Railway assigns a dynamic `PORT` variable; the Dockerfile uses fixed ports 8000 & 8501. If needed, modify:
```dockerfile
# In Dockerfile entrypoint:
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} &
streamlit run app.py --server.port=${STREAMLIT_PORT:-8501} --server.address=0.0.0.0
```

### Database not found
The SQLite file is created on first run. Ensure Git LFS objects are pulled:
```dockerfile
RUN git lfs pull || true
```

### Streamlit config issues
If Streamlit UI doesn't load, try disabling analytics in `railway.json`:
Add to deploy section:
```json
"env": {
  "STREAMLIT_CONFIG_SERVER_HEADLESS": "true",
  "STREAMLIT_CONFIG_CLIENT_SHOWERRORDETAILS": "true"
}
```

---

## Next Steps

1. **Commit & Push**:
   ```bash
   git add Dockerfile railway.json RAILWAY_DEPLOYMENT.md
   git commit -m "Add Railway deployment config"
   git push origin main
   ```

2. **Deploy**:
   - Use `railway up` (CLI) or connect GitHub in Railway dashboard

3. **Update Streamlit Config**  
   Once you have the Railway URL, update the Streamlit app:
   - In Railway's Variables, set `API_URL=https://your-railway-domain.com:8000`
   - Streamlit will pick it up automatically

---

## Cost
- **Free tier**: 1 project, unlimited deployments, 100 compute hours/month (enough for demos)
- **Paid**: Per-usage pricing, very affordable for side projects

---

For more info: https://docs.railway.app/
