# 🚀 EvalBee - To'liq Deployment Qo'llanmasi

## 📋 Umumiy Ma'lumot

**Loyiha:** EvalBee OMR (Optical Mark Recognition) System  
**Texnologiya:** React + TypeScript (Frontend), Python FastAPI (Backend)  
**Deployment:** Render.com (2 ta alohida service)  
**GitHub:** https://github.com/lobarrustamova494-art/testtchii

---

## 🎯 Deployment Arxitekturasi

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Frontend (Static Site)                        │
│  https://evalbee-frontend.onrender.com         │
│  - React + TypeScript + Vite                   │
│  - Tailwind CSS                                │
│  - Camera System (EvalBee Style)               │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 │ API Calls
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│                                                 │
│  Backend (Docker Container)                    │
│  https://evalbee-backend.onrender.com          │
│  - Python 3.11 + FastAPI                       │
│  - OpenCV + Tesseract OCR                      │
│  - OMR Detection Engine                        │
│  - QR Code Reader                              │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔴 BACKEND DEPLOYMENT (Docker)

### Nima Uchun Docker?

**Muammo:** Native build'da system dependencies (tesseract-ocr, libzbar0) to'g'ri install bo'lmaydi.

**Yechim:** Docker container ishlatish - barcha dependencies kafolatlangan.

### Bosqich 1: Render'da Backend Service Yaratish

1. **Render Dashboard:** https://dashboard.render.com
2. **New +** → **Web Service**
3. **Connect GitHub Repository:**
   - Repository: `lobarrustamova494-art/testtchii`
   - Branch: `main`

### Bosqich 2: Service Sozlamalari

```yaml
Name: evalbee-backend
Region: Oregon (US West)
Branch: main
Root Directory: backend
Runtime: Docker
```

### Bosqich 3: Docker Sozlamalari

**MUHIM:** Docker'ni yoqish kerak!

1. **Settings** → **Docker** bo'limiga o'ting
2. **"Docker Command"** ni yoqing (Enable)
3. Quyidagi sozlamalarni kiriting:

```
Docker Build Context: backend
Dockerfile Path: Dockerfile
```

4. **Build Command:** bo'sh qoldiring (Docker'da kerak emas)
5. **Start Command:** bo'sh qoldiring (Dockerfile'da bor)

### Bosqich 4: Environment Variables

```bash
PYTHON_VERSION=3.11.0
GROQ_API_KEY=your_groq_api_key_here  # Ixtiyoriy
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:5173,https://evalbee-frontend.onrender.com
```

**CORS_ORIGINS:** Frontend URL'ni to'g'ri kiriting!

### Bosqich 5: Deploy

1. **"Save Changes"** tugmasini bosing
2. Render avtomatik build va deploy qiladi
3. **Logs'ni kuzating** (5-10 daqiqa)

### Kutilgan Build Logs

```
==> Building with Dockerfile
Step 1/10 : FROM python:3.11-slim
 ---> Pulling image...
Step 2/10 : WORKDIR /app
 ---> Running in...
Step 3/10 : RUN apt-get update && apt-get install -y...
 ---> Installing tesseract-ocr... ✅
 ---> Installing libzbar0... ✅
 ---> Installing libgl1-mesa-glx... ✅
Step 4/10 : COPY requirements.txt .
 ---> Copying...
Step 5/10 : RUN pip install...
 ---> Installing Python packages... ✅
Step 6/10 : COPY . .
 ---> Copying application code...
Step 7/10 : EXPOSE 8000
Step 8/10 : HEALTHCHECK...
Step 9/10 : CMD ["uvicorn"...]
 ---> Build complete! ✅
==> Deploying...
==> Your service is live! 🎉
```

### Bosqich 6: Test Qilish

**Health Check:**

```bash
curl https://evalbee-backend.onrender.com/
```

**Kutilgan Javob:**

```json
{
	"message": "EvalBee OMR Backend API",
	"version": "3.0.0",
	"status": "healthy"
}
```

**API Documentation:**

```
https://evalbee-backend.onrender.com/docs
```

---

## 🔵 FRONTEND DEPLOYMENT (Static Site)

### Bosqich 1: Render'da Static Site Yaratish

1. **Render Dashboard:** https://dashboard.render.com
2. **New +** → **Static Site**
3. **Connect GitHub Repository:**
   - Repository: `lobarrustamova494-art/testtchii`
   - Branch: `main`

### Bosqich 2: Build Sozlamalari

```yaml
Name: evalbee-frontend
Branch: main
Root Directory: (bo'sh qoldiring!)
Build Command: npm install && npm run build
Publish Directory: dist
```

### Bosqich 3: Environment Variables

```bash
NODE_VERSION=18
VITE_BACKEND_URL=https://evalbee-backend.onrender.com
```

**MUHIM:** Backend URL'ni to'g'ri kiriting!

### Bosqich 4: Rewrite Rules (SPA uchun)

```
Source: /*
Destination: /index.html
Action: Rewrite
```

Bu React Router'ning ishlashi uchun kerak.

### Bosqich 5: Deploy

1. **"Create Static Site"** tugmasini bosing
2. Build jarayoni boshlanadi (3-5 daqiqa)
3. **Logs'ni kuzating**

### Kutilgan Build Logs

```
==> Cloning from GitHub...
==> Installing dependencies...
npm install
 ---> Installing packages... ✅
==> Building...
npm run build
 ---> Building with Vite...
 ---> Optimizing assets...
 ---> Build complete! ✅
==> Publishing to CDN...
==> Your site is live! 🎉
```

### Bosqich 6: Test Qilish

Browser'da oching:

```
https://evalbee-frontend.onrender.com
```

**Tekshirish:**

- ✅ Login sahifasi ochiladi
- ✅ Exam yaratish ishlaydi
- ✅ Kamera ochiladi
- ✅ Backend bilan bog'lanadi

---

## 🔧 MUAMMOLARNI HAL QILISH

### Backend 503 Service Unavailable

**Sabab:** Free tier - 15 daqiqa ishlamasdan uxlab qoladi.

**Yechim:**

- Birinchi request 30-60 sekund kutadi
- Keyin tez ishlaydi
- Paid plan ($7/month) - always-on

### Frontend Backend'ga Ulanmayapti

**Tekshirish:**

1. Browser Console (F12) → Network tab
2. CORS error ko'rinsa:

**Yechim:**

1. Backend `CORS_ORIGINS` environment variable'ni tekshiring
2. Frontend URL to'g'ri kiritilganligini tekshiring
3. Backend'ni qayta deploy qiling

### Docker Build Failed

**Umumiy Xatolar:**

1. **"Cannot find Dockerfile"**

   - Docker Build Context: `backend` ekanligini tekshiring
   - Dockerfile Path: `Dockerfile` ekanligini tekshiring

2. **"Out of memory"**

   - Free tier'da ba'zan bo'ladi
   - Qayta deploy qiling

3. **"Build timeout"**
   - Birinchi build uzoq davom etadi (10 daqiqa)
   - Sabr qiling yoki qayta boshlang

### Frontend Build Failed

**Umumiy Xatolar:**

1. **"Cannot find module"**

   - `package.json` to'g'ri ekanligini tekshiring
   - `npm install` local'da ishlashini tekshiring

2. **"PostCSS error"**

   - `package.json` da `"type": "module"` borligini tekshiring

3. **"Vite build failed"**
   - `vite.config.ts` to'g'ri ekanligini tekshiring

---

## 📊 DEPLOYMENT STATUS

### Backend Status

```bash
# Health check
curl https://evalbee-backend.onrender.com/

# API endpoints
GET  /                    # Health check
POST /api/process         # Process exam image
POST /api/camera/preview  # Camera preview
POST /api/camera/quick-analysis  # Quick analysis
GET  /docs                # API documentation
```

### Frontend Status

```bash
# Pages
/                         # Login
/dashboard                # Dashboard
/create-exam              # Create exam
/grade-exam               # Grade exam
/camera-capture           # Camera capture
```

---

## 💰 XARAJATLAR

### Free Tier (Tavsiya Boshlovchilar Uchun)

**Backend:**

- ✅ $0/month
- ✅ 750 hours/month
- ⚠️ 15 daqiqa spin down
- ⚠️ 30-60 sekund cold start

**Frontend:**

- ✅ $0/month
- ✅ 100 GB bandwidth
- ✅ Global CDN
- ✅ Always-on

**Jami: $0/month**

### Paid Tier (Professional)

**Backend:**

- 💰 $7/month
- ✅ Always-on (no spin down)
- ✅ Instant response
- ✅ 400 hours included

**Frontend:**

- ✅ $0/month (static site)

**Jami: $7/month**

---

## 🔐 XAVFSIZLIK

### Environment Variables

**Backend:**

```bash
GROQ_API_KEY=***  # Maxfiy! Ko'rsatmang!
```

**Frontend:**

```bash
VITE_BACKEND_URL=https://evalbee-backend.onrender.com  # Public
```

### CORS

Backend faqat ruxsat berilgan origin'lardan request qabul qiladi:

```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Local development
    "https://evalbee-frontend.onrender.com"  # Production
]
```

---

## 📈 MONITORING

### Render Dashboard

1. **Logs:** Real-time logs ko'rish
2. **Metrics:** CPU, Memory, Bandwidth
3. **Events:** Deploy history
4. **Settings:** Configuration

### Health Checks

**Backend:**

```bash
# Har 30 sekundda
curl https://evalbee-backend.onrender.com/
```

**Frontend:**

```bash
# Browser'da
https://evalbee-frontend.onrender.com
```

---

## 🔄 YANGILANISHLAR

### Code O'zgarganda

1. **Git'ga push qiling:**

```bash
git add .
git commit -m "Update: description"
git push origin main
```

2. **Render avtomatik deploy qiladi:**

   - Backend: 5-10 daqiqa
   - Frontend: 3-5 daqiqa

3. **Logs'ni kuzating:**
   - Render Dashboard → Service → Logs

### Manual Deploy

Agar avtomatik deploy ishlamasa:

1. Render Dashboard → Service
2. **"Manual Deploy"** → **"Deploy latest commit"**

---

## 📚 QOSHIMCHA HUJJATLAR

- **RENDER_DOCKER_DEPLOY.md** - Docker deployment detallari
- **QUICK_DEPLOY_GUIDE.md** - Tezkor qo'llanma
- **RENDER_STEP_BY_STEP.md** - Bosqichma-bosqich
- **backend/README.md** - Backend hujjati
- **EVALBE_CAMERA_SYSTEM.md** - Kamera tizimi

---

## ✅ DEPLOYMENT CHECKLIST

### Backend

- [ ] GitHub repository ulangan
- [ ] Docker yoqilgan
- [ ] Docker Build Context: `backend`
- [ ] Dockerfile Path: `Dockerfile`
- [ ] Environment variables to'g'ri
- [ ] CORS_ORIGINS frontend URL'ni o'z ichiga oladi
- [ ] Build muvaffaqiyatli
- [ ] Health check ishlayapti
- [ ] API docs ochiladi

### Frontend

- [ ] GitHub repository ulangan
- [ ] Build command to'g'ri
- [ ] Publish directory: `dist`
- [ ] VITE_BACKEND_URL to'g'ri
- [ ] Rewrite rules sozlangan
- [ ] Build muvaffaqiyatli
- [ ] Login sahifasi ochiladi
- [ ] Backend bilan bog'lanadi

---

## 🎉 TAYYOR!

Endi sizda professional OMR tizimi ishlayapti:

**🌐 URLs:**

- Backend: https://evalbee-backend.onrender.com
- Frontend: https://evalbee-frontend.onrender.com
- API Docs: https://evalbee-backend.onrender.com/docs

**📱 Foydalanish:**

1. Frontend'ga kiring
2. Login qiling (demo: admin/admin)
3. Exam yarating
4. Kamera bilan rasm oling
5. Natijalarni ko'ring

**🚀 Omad!**

---

**Sana:** 2026-01-16  
**Versiya:** 3.0.0  
**Status:** ✅ Production Ready
