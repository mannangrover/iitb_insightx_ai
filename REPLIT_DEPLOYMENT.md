# Replit Deployment Guide

## 1. Create New Replit Project

### Option A: From GitHub (Recommended - Easiest)
1. Go to https://replit.com/~
2. Click **"Create"** → **"Import from GitHub"**
3. Paste your repo URL: `https://github.com/mannangrover/iitb_insightx_ai`
4. Click **"Import"** — Replit auto-detects everything
5. Wait for dependencies to install, then click **"Run"**

### Option B: Manual
1. Create a new Python 3.12 Replit
2. Copy-paste your code into the editor
3. Click **"Run"**

---

## 2. What Happens When You Run

The `.replit` config tells Replit to:
- Use Python 3.12 + Node.js 20
- Run `honcho start` (which reads your `Procfile`)
- Start **FastAPI** on :8000
- Start **Streamlit** on :8501

Both services run in the same Replit container.

---

## 3. Access Your App

Once running, Replit gives you a **live URL**:

```
https://your-replit-name.replit.dev
```

- **Streamlit UI**: `https://your-replit-name.replit.dev:8501`  
  *(Replit auto-proxies ports)*
- **FastAPI API**: `https://your-replit-name.replit.dev:8000`
- **API Docs**: `https://your-replit-name.replit.dev:8000/docs`

---

## 4. Environment Variables

If you need `OPENAI_API_KEY` or other vars:

1. Click the **🔒 Secrets** icon (lock) in the left sidebar
2. Add new secret:
   - Key: `OPENAI_API_KEY`
   - Value: `sk-...your-key...`
3. Save — Replit injects them automatically

---

## 5. Enable Always-On (Keep Running 24/7)

Free Replit stops after 1 hour of inactivity. To keep it running:

1. Click your profile → **Account**
2. Upgrade to **Replit Core** ($7/mo) or use **Always-On** tier
3. Enable "Always-On"

*Alternative*: Use a free service like [UptimeRobot](https://uptimerobot.com) to ping your Replit URL every 5 min (keeps it warm).

---

## 6. Update Configuration

If you change `Procfile` or add new packages:

1. Update `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```
2. Commit & push to GitHub (if using GitHub import)
3. Click **"Pull"** in Replit to sync latest
4. Click **"Run"** again

Or directly in Replit's editor → **"Run"** (reinstalls deps automatically).

---

## 7. Logs & Debugging

Click the **"Logs"** tab to see:
- FastAPI startup messages
- Streamlit logs
- Any errors from your app

If something breaks, check:
1. Port conflicts (8000 & 8501 must be free)
2. Missing `.env` file (use `.env.example`)
3. Database file permissions

---

## 8. Scale with Cloud Database (Optional)

SQLite on Replit is ephemeral (resets on restart). For persistence:

1. Create a free PostgreSQL at [neon.tech](https://neon.tech)
2. Copy connection string: `postgresql://...`
3. In Replit, go to **🔒 Secrets** → add:
   - Key: `DATABASE_URL`
   - Value: `postgresql://...`
4. Your app auto-uses PostgreSQL

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Port 8000 already in use" | Replit runs old process; click **Stop** then **Run** |
| Streamlit not showing | Check port 8501 in Replit's proxy settings |
| Database file missing | Run once to auto-create, or upload CSV via data loader |
| Dependencies not installed | Delete `.upm/replit_nix/tmp` folder and **Run** again |

---

## Quick Summary

✅ **One-click deploy**: GitHub → Replit  
✅ **Both services run**: FastAPI + Streamlit in one place  
✅ **Live URL**: `https://your-replit.replit.dev`  
✅ **Free tier**: 0.5 vCPU, 500MB RAM, 1-hour timeout  
✅ **Paid Always-On**: $7/mo to keep running 24/7  

Enjoy! 🚀
