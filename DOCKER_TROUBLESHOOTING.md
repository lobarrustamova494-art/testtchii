# 🐳 Docker Deployment - Troubleshooting Guide

## 🎯 Umumiy Muammolar va Yechimlar

---

## ❌ Muammo 1: "Cannot find Dockerfile"

### Xato Matni

```
Error: Dockerfile not found at path: Dockerfile
Build failed
```

### Sabab

Docker Build Context yoki Dockerfile Path noto'g'ri sozlangan.

### Yechim

1. **Render Dashboard → Backend Service → Settings**
2. **Docker bo'limida tekshiring:**

```
Docker Build Context: backend
Dockerfile Path: Dockerfile
```

**MUHIM:**

- Build Context `backend` bo'lishi kerak
- Dockerfile Path faqat `Dockerfile` (yo'lsiz!)

3. **Save Changes** va qayta deploy qiling

---

## ❌ Muammo 2: "Docker build timeout"

### Xato Matni

```
Error: Build exceeded maximum time limit
Build failed after 15 minutes
```

### Sabab

Birinchi build uzoq davom etadi (dependencies download).

### Yechim

**Variant 1: Qayta Urinish**

1. **Manual Deploy** → **Clear build cache**
2. **Deploy latest commit**

**Variant 2: Dockerfile Optimizatsiya**

Dockerfile'da layer caching yaxshilash:

```dockerfile
# ❌ Yomon (har safar rebuild)
COPY . .
RUN pip install -r requirements.txt

# ✅ Yaxshi (cache ishlatadi)
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

Bizning Dockerfile allaqachon optimizatsiyalangan! ✅

---

## ❌ Muammo 3: "Out of memory during build"

### Xato Matni

```
Error: Container killed due to memory limit
Build failed
```

### Sabab

Free tier'da memory cheklangan (512 MB).

### Yechim

**Variant 1: Dockerfile'da Memory Optimizatsiya**

```dockerfile
# Pip cache'ni o'chirish
RUN pip install --no-cache-dir -r requirements.txt
```

Bizning Dockerfile'da bu bor! ✅

**Variant 2: Qayta Urinish**
Ba'zan ikkinchi urinishda ishlaydi (partial cache).

**Variant 3: Paid Plan**
$7/month - 2 GB memory.

---

## ❌ Muammo 4: "Port already in use"

### Xato Matni

```
Error: Address already in use: 0.0.0.0:8000
Container failed to start
```

### Sabab

Port noto'g'ri sozlangan yoki Render'ning $PORT variable ishlatilmagan.

### Yechim

**Dockerfile'da:**

```dockerfile
# ❌ Yomon (hardcoded port)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# ✅ Yaxshi (Render's $PORT)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**Bizning Dockerfile:**

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Bu ishlaydi chunki Render avtomatik port mapping qiladi! ✅

---

## ❌ Muammo 5: "Health check failed"

### Xato Matni

```
Warning: Health check failing
Container is running but unhealthy
```

### Sabab

Health check endpoint ishlamayapti yoki timeout.

### Yechim

**1. Health Check'ni Tekshirish:**

Dockerfile'da:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')"
```

**2. Agar Muammo Bo'lsa:**

Health check'ni vaqtincha o'chirish:

```dockerfile
# HEALTHCHECK'ni comment qiling
# HEALTHCHECK --interval=30s ...
```

**3. Manual Test:**

Render Logs'da:

```bash
curl http://localhost:8000/
```

---

## ❌ Muammo 6: "System dependencies not found"

### Xato Matni

```
ImportError: libtesseract.so.4: cannot open shared object file
ImportError: libzbar.so.0: cannot open shared object file
```

### Sabab

System dependencies install bo'lmagan.

### Yechim

**Dockerfile'da tekshiring:**

```dockerfile
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libzbar0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
```

Bizning Dockerfile'da bu bor! ✅

**Agar Ishlamasa:**

1. Build logs'ni diqqat bilan o'qing
2. Qaysi dependency install bo'lmayapti?
3. Package nomini tekshiring (Debian/Ubuntu)

---

## ❌ Muammo 7: "Python package installation failed"

### Xato Matni

```
ERROR: Could not find a version that satisfies the requirement opencv-python
ERROR: No matching distribution found for opencv-python
```

### Sabab

Package versiyasi noto'g'ri yoki Python versiyasi mos emas.

### Yechim

**1. requirements.txt'ni Tekshiring:**

```txt
# ❌ Yomon (juda yangi versiya)
opencv-python==4.10.0

# ✅ Yaxshi (stable versiya)
opencv-python==4.8.1.78
```

**2. Python Versiyasini Tekshiring:**

Dockerfile:

```dockerfile
FROM python:3.11-slim  # ✅ To'g'ri
```

**3. Build Tools:**

```dockerfile
RUN pip install --upgrade pip setuptools wheel
```

Bizning Dockerfile'da bu bor! ✅

---

## ❌ Muammo 8: "Container starts but crashes immediately"

### Xato Matni

```
Container started
Container exited with code 1
```

### Sabab

Application error yoki missing environment variable.

### Yechim

**1. Logs'ni O'qing:**

Render Dashboard → Logs → Oxirgi 100 qator

**2. Environment Variables:**

Tekshiring:

```bash
PYTHON_VERSION=3.11.0
GROQ_API_KEY=your_key  # Ixtiyoriy
ENVIRONMENT=production
CORS_ORIGINS=https://evalbee-frontend.onrender.com
```

**3. Local'da Test Qiling:**

```bash
cd backend
docker build -t evalbee-backend .
docker run -p 8000:8000 evalbee-backend
```

---

## ❌ Muammo 9: "CORS error in frontend"

### Xato Matni (Browser Console)

```
Access to fetch at 'https://evalbee-backend.onrender.com/api/process'
from origin 'https://evalbee-frontend.onrender.com' has been blocked by CORS policy
```

### Sabab

Backend CORS sozlamalari frontend URL'ni o'z ichiga olmaydi.

### Yechim

**1. Backend Environment Variables:**

```bash
CORS_ORIGINS=http://localhost:5173,https://evalbee-frontend.onrender.com
```

**MUHIM:** Vergul bilan ajratilgan, bo'sh joy yo'q!

**2. Backend config.py:**

```python
CORS_ORIGINS = os.getenv(
    'CORS_ORIGINS',
    'http://localhost:5173,https://evalbee-frontend.onrender.com'
).split(',')
```

**3. Backend'ni Qayta Deploy Qiling**

---

## ❌ Muammo 10: "Slow cold start (30-60 seconds)"

### Sabab

Free tier - 15 daqiqa ishlamasdan uxlab qoladi.

### Yechim

**Variant 1: Qabul Qiling**

- Bu normal (free tier)
- Birinchi request sekin
- Keyingi requestlar tez

**Variant 2: Keep-Alive Service**

Har 10 daqiqada ping qiling:

```bash
# Cron job yoki external service
curl https://evalbee-backend.onrender.com/
```

**Variant 3: Paid Plan**
$7/month - always-on, no cold start.

---

## 🔍 DEBUG QILISH

### 1. Build Logs

Render Dashboard → Service → Logs → Build

Qidiring:

- ✅ "Step X/Y" - qaysi step'da xato?
- ❌ "ERROR:" - xato matni
- ⚠️ "WARNING:" - ogohlantirish

### 2. Runtime Logs

Render Dashboard → Service → Logs → Runtime

Qidiring:

- ✅ "Application startup complete"
- ❌ "Exception:" - Python error
- ⚠️ "WARNING:" - ogohlantirish

### 3. Local Docker Test

```bash
# Build
cd backend
docker build -t evalbee-backend .

# Run
docker run -p 8000:8000 evalbee-backend

# Test
curl http://localhost:8000/
```

### 4. Dockerfile Syntax Check

```bash
# Dockerfile lint
docker run --rm -i hadolint/hadolint < backend/Dockerfile
```

---

## 📊 DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] Dockerfile syntax to'g'ri
- [ ] requirements.txt to'liq
- [ ] Local'da Docker build ishlaydi
- [ ] Local'da Docker run ishlaydi
- [ ] Environment variables tayyor

### Render Settings

- [ ] Docker yoqilgan
- [ ] Docker Build Context: `backend`
- [ ] Dockerfile Path: `Dockerfile`
- [ ] Build Command: bo'sh
- [ ] Start Command: bo'sh
- [ ] Environment variables to'g'ri

### Post-Deployment

- [ ] Build logs'da xato yo'q
- [ ] Container started
- [ ] Health check passing
- [ ] API endpoint ishlaydi
- [ ] Frontend bilan bog'lanadi

---

## 🆘 YORDAM KERAKMI?

### Render Support

- Documentation: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### Docker Documentation

- Dockerfile reference: https://docs.docker.com/engine/reference/builder/
- Best practices: https://docs.docker.com/develop/dev-best-practices/

### Bizning Hujjatlar

- **DEPLOYMENT_COMPLETE_GUIDE.md** - To'liq qo'llanma
- **RENDER_DOCKER_DEPLOY.md** - Docker deployment
- **QUICK_DEPLOY_GUIDE.md** - Tezkor qo'llanma

---

## ✅ UMUMIY YECHIMLAR

### Eng Ko'p Uchraydigan Muammolar

1. **Build Context noto'g'ri** → `backend` qiling
2. **Dockerfile Path noto'g'ri** → `Dockerfile` qiling
3. **CORS error** → Environment variable tekshiring
4. **Cold start sekin** → Normal (free tier)
5. **Memory error** → Qayta urinish yoki paid plan

### Eng Yaxshi Amaliyotlar

1. ✅ Docker ishlatish (native build emas)
2. ✅ Layer caching optimizatsiya
3. ✅ `--no-cache-dir` pip uchun
4. ✅ Health check qo'shish
5. ✅ Environment variables ishlatish

---

**Omad!** 🚀

Agar muammo hal bo'lmasa, Render logs'ni yuboring va yordam beramiz!
