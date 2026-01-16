# ✅ Render Deployment Checklist

## 🎯 Tezkor Qo'llanma - 15 Daqiqa

---

## 🔴 BACKEND (10 daqiqa)

### Bosqich 1: Service Yaratish (2 min)

1. https://dashboard.render.com ga kiring
2. **"New +"** → **"Web Service"**
3. **"Connect GitHub"** → Repository tanlang
4. Repository: `lobarrustamova494-art/testtchii`

### Bosqich 2: Asosiy Sozlamalar (2 min)

```
Name: evalbee-backend
Region: Oregon (US West)
Branch: main
Root Directory: backend          ⚠️ MUHIM!
```

### Bosqich 3: Docker Yoqish (2 min)

1. **Settings** → **Docker** bo'limiga o'ting
2. **"Docker Command"** ni yoqing ✅
3. Sozlamalar:

```
Docker Build Context: backend
Dockerfile Path: Dockerfile
```

4. **Build Command:** bo'sh qoldiring
5. **Start Command:** bo'sh qoldiring

### Bosqich 4: Environment Variables (2 min)

**Add Environment Variable** tugmasini bosing:

```bash
PYTHON_VERSION=3.11.0
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:5173,https://evalbee-frontend.onrender.com
```

**Ixtiyoriy (AI uchun):**

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Bosqich 5: Deploy (2 min)

1. **"Create Web Service"** tugmasini bosing
2. Build jarayoni boshlanadi (5-10 daqiqa)
3. **Logs'ni kuzating**

### Kutilgan Natija

```
✅ Building with Dockerfile
✅ Installing system dependencies
✅ Installing Python packages
✅ Build complete
✅ Container started
✅ Health check passing
🎉 Your service is live!
```

### Test

```bash
curl https://evalbee-backend.onrender.com/
```

**Javob:**

```json
{
	"message": "EvalBee OMR Backend API",
	"version": "3.0.0",
	"status": "healthy"
}
```

---

## 🔵 FRONTEND (5 daqiqa)

### Bosqich 1: Static Site Yaratish (1 min)

1. https://dashboard.render.com ga kiring
2. **"New +"** → **"Static Site"**
3. **"Connect GitHub"** → Xuddi shu repository
4. Repository: `lobarrustamova494-art/testtchii`

### Bosqich 2: Build Sozlamalar (2 min)

```
Name: evalbee-frontend
Branch: main
Root Directory: (bo'sh qoldiring!)    ⚠️ Bo'sh!
Build Command: npm install && npm run build
Publish Directory: dist
```

### Bosqich 3: Environment Variables (1 min)

```bash
NODE_VERSION=18
VITE_BACKEND_URL=https://evalbee-backend.onrender.com
```

⚠️ **Backend URL'ni to'g'ri kiriting!**

### Bosqich 4: Rewrite Rules (1 min)

**Add Rewrite Rule:**

```
Source: /*
Destination: /index.html
Action: Rewrite
```

### Bosqich 5: Deploy (1 min)

1. **"Create Static Site"** tugmasini bosing
2. Build jarayoni boshlanadi (3-5 daqiqa)
3. **Logs'ni kuzating**

### Kutilgan Natija

```
✅ Cloning repository
✅ Installing dependencies
✅ Building with Vite
✅ Optimizing assets
✅ Publishing to CDN
🎉 Your site is live!
```

### Test

Browser'da oching:

```
https://evalbee-frontend.onrender.com
```

**Ko'rinishi kerak:**

- ✅ Login sahifasi
- ✅ EvalBee logo
- ✅ Login form

---

## 🧪 INTEGRATION TEST

### 1. Login (30 sekund)

```
Username: admin
Password: admin
```

### 2. Exam Yaratish (1 daqiqa)

1. **"Create Exam"** tugmasini bosing
2. Exam ma'lumotlarini kiriting
3. **"Create"** bosing

### 3. Kamera Test (1 daqiqa)

1. **"Grade Exam"** → **"Camera Capture"**
2. Kamera ochiladi
3. A4 qog'ozni ko'rsating
4. 4 ta corner marker ko'rinadi
5. **"Capture"** tugmasini bosing

### 4. Backend Test (30 sekund)

```bash
# Health check
curl https://evalbee-backend.onrender.com/

# API docs
https://evalbee-backend.onrender.com/docs
```

---

## ⚠️ UMUMIY MUAMMOLAR

### Backend 503 Error

**Sabab:** Cold start (free tier - 15 min spin down)  
**Yechim:** 30-60 sekund kuting, keyin qayta urinib ko'ring

### CORS Error

**Sabab:** Frontend URL CORS_ORIGINS'da yo'q  
**Yechim:**

1. Backend Settings → Environment Variables
2. CORS_ORIGINS tekshiring
3. Frontend URL qo'shing
4. Redeploy qiling

### Docker Build Failed

**Sabab:** Docker sozlamalari noto'g'ri  
**Yechim:**

1. Settings → Docker
2. Build Context: `backend` ✅
3. Dockerfile Path: `Dockerfile` ✅
4. Redeploy qiling

### Frontend Build Failed

**Sabab:** Dependencies yoki config xatosi  
**Yechim:**

1. Logs'ni o'qing
2. Local'da test qiling: `npm run build`
3. GitHub'ga push qiling
4. Redeploy qiling

---

## 📊 DEPLOYMENT STATUS

### Backend

```
Service: evalbee-backend
Type: Web Service (Docker)
Status: [ ] Not Started  [ ] Building  [ ] Live
URL: https://evalbee-backend.onrender.com
```

### Frontend

```
Service: evalbee-frontend
Type: Static Site
Status: [ ] Not Started  [ ] Building  [ ] Live
URL: https://evalbee-frontend.onrender.com
```

---

## 💰 XARAJATLAR

### Free Tier (Hozir)

```
Backend:  $0/month
Frontend: $0/month
Total:    $0/month ✅
```

**Cheklovlar:**

- Backend: 15 min spin down
- Backend: 750 hours/month
- Frontend: 100 GB bandwidth

### Paid Tier (Tavsiya)

```
Backend:  $7/month (always-on)
Frontend: $0/month
Total:    $7/month
```

**Afzalliklari:**

- ✅ No spin down
- ✅ Instant response
- ✅ Better performance

---

## 📚 BATAFSIL HUJJATLAR

Agar muammo bo'lsa:

1. **DEPLOYMENT_COMPLETE_GUIDE.md** - To'liq qo'llanma
2. **DOCKER_TROUBLESHOOTING.md** - Docker muammolari
3. **RENDER_DOCKER_DEPLOY.md** - Docker deployment
4. **QUICK_DEPLOY_GUIDE.md** - Tezkor qo'llanma

---

## ✅ FINAL CHECKLIST

### Pre-Deployment

- [x] GitHub repository tayyor
- [x] Dockerfile tayyor
- [x] Environment variables ma'lum
- [x] Hujjatlar o'qilgan

### Backend Deployment

- [ ] Service yaratildi
- [ ] Docker yoqildi
- [ ] Docker Build Context: `backend`
- [ ] Dockerfile Path: `Dockerfile`
- [ ] Environment variables kiritildi
- [ ] Build muvaffaqiyatli
- [ ] Health check ishlayapti
- [ ] API endpoint test qilindi

### Frontend Deployment

- [ ] Static site yaratildi
- [ ] Build command to'g'ri
- [ ] Publish directory: `dist`
- [ ] VITE_BACKEND_URL to'g'ri
- [ ] Rewrite rules sozlangan
- [ ] Build muvaffaqiyatli
- [ ] Site ochiladi
- [ ] Backend bilan bog'lanadi

### Integration Test

- [ ] Login ishlaydi
- [ ] Exam yaratish ishlaydi
- [ ] Kamera ochiladi
- [ ] Backend API ishlaydi
- [ ] Natijalar ko'rinadi

---

## 🎉 TAYYOR!

Endi sizda professional OMR tizimi ishlayapti!

**URLs:**

- Backend: https://evalbee-backend.onrender.com
- Frontend: https://evalbee-frontend.onrender.com
- API Docs: https://evalbee-backend.onrender.com/docs

**Omad!** 🚀

---

**Sana:** 2026-01-16  
**Versiya:** 3.0.0  
**GitHub:** https://github.com/lobarrustamova494-art/testtchii
