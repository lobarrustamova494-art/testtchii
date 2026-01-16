# Render.com Deployment Guide

## Prerequisites

- GitHub account
- Render.com account (free tier available)
- Git installed locally

## Step 1: Prepare Repository

### 1.1 Initialize Git (if not already)

```bash
git init
git add .
git commit -m "Initial commit - EvalBee OMR System"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com/new
2. Create new repository: `evalbee-omr-system`
3. Don't initialize with README (we already have files)

### 1.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/evalbee-omr-system.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy Backend on Render

### 2.1 Create Web Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `evalbee-backend`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `./render-build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### 2.2 Environment Variables

Add these in Render dashboard:

```
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
```

### 2.3 Advanced Settings

- **Auto-Deploy**: Yes
- **Health Check Path**: `/`

## Step 3: Deploy Frontend on Render

### 3.1 Create Static Site

1. Click "New +" → "Static Site"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `evalbee-frontend`
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### 3.2 Environment Variables

```
NODE_VERSION=18
VITE_API_URL=https://evalbee-backend.onrender.com
```

### 3.3 Rewrite Rules

Add in Render dashboard:

```
Source: /*
Destination: /index.html
Action: Rewrite
```

## Step 4: Update Frontend API URL

Update `src/services/backendApi.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

## Step 5: Test Deployment

### Backend Health Check

```bash
curl https://evalbee-backend.onrender.com/
```

Should return: `{"message": "EvalBee OMR Backend API"}`

### Frontend

Visit: `https://evalbee-frontend.onrender.com`

## Step 6: Configure CORS (Backend)

Update `backend/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://evalbee-frontend.onrender.com",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Build Fails

- Check build logs in Render dashboard
- Verify all dependencies in `requirements.txt` and `package.json`
- Ensure Python version is 3.11

### Backend Crashes

- Check logs: `render logs evalbee-backend`
- Verify environment variables are set
- Check system dependencies (tesseract, libzbar)

### Frontend Can't Connect to Backend

- Verify CORS settings
- Check API_BASE_URL in frontend
- Ensure backend is running

### Camera Not Working

- HTTPS required for camera access
- Render provides HTTPS by default
- Check browser permissions

## Free Tier Limitations

### Render Free Tier:

- **Backend**:
  - 750 hours/month
  - Spins down after 15 min inactivity
  - First request after spin-down takes ~30s
- **Frontend**:
  - 100 GB bandwidth/month
  - Global CDN

### Workarounds:

1. Use cron job to ping backend every 14 minutes
2. Show "Waking up server..." message on first load
3. Upgrade to paid plan ($7/month) for always-on

## Production Checklist

- [ ] Environment variables set
- [ ] CORS configured
- [ ] HTTPS enabled (automatic on Render)
- [ ] Health checks passing
- [ ] Error logging configured
- [ ] Database backup (if using)
- [ ] API rate limiting
- [ ] Security headers
- [ ] Performance monitoring

## Monitoring

### Render Dashboard

- View logs
- Monitor CPU/Memory
- Check deploy history
- View metrics

### Custom Monitoring

Add to backend:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Updating Deployment

### Automatic (Recommended)

Push to GitHub main branch:

```bash
git add .
git commit -m "Update: description"
git push origin main
```

Render auto-deploys on push.

### Manual

In Render dashboard:

1. Go to service
2. Click "Manual Deploy"
3. Select branch
4. Deploy

## Cost Optimization

### Free Tier Strategy:

1. Use free backend (with spin-down)
2. Use free frontend (static)
3. Total cost: $0/month

### Paid Strategy ($7/month):

1. Upgrade backend to Starter ($7)
2. Always-on, no spin-down
3. Better performance

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: Create issue in your repo

## Next Steps

1. Set up custom domain
2. Configure SSL certificate
3. Add monitoring/analytics
4. Set up CI/CD pipeline
5. Add automated tests

## URLs After Deployment

- **Frontend**: https://evalbee-frontend.onrender.com
- **Backend**: https://evalbee-backend.onrender.com
- **API Docs**: https://evalbee-backend.onrender.com/docs

---

**Deployment Date**: $(date)
**Version**: 1.0.0
**Status**: Production Ready ✅
