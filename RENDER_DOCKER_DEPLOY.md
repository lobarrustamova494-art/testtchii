# Render Docker Deployment - Backend

## Muammo

Build script bilan deploy qilishda system dependencies (tesseract, libzbar) to'g'ri install bo'lmayapti.

## Yechim: Docker Ishlatish

Docker ishlatish eng ishonchli usul, chunki:

- ✅ Barcha dependencies to'g'ri install bo'ladi
- ✅ Local va production bir xil environment
- ✅ Reproducible builds
- ✅ Kamroq xatolar

## Render'da Docker'ni Yoqish

### Bosqich 1: Backend Service'ga O'tish

1. Render dashboard: https://dashboard.render.com
2. Backend service'ni oching (evalbee-backend)

### Bosqich 2: Settings'ni Ochish

1. "Settings" tab'ini bosing
2. Pastga scroll qiling

### Bosqich 3: Docker'ni Yoqish

1. "Docker" bo'limini toping
2. **"Docker Command"** ni yoqing (Enable)
3. Quyidagi sozlamalarni kiriting:

**Docker Build Context:**

```
backend
```

**Dockerfile Path:**

```
Dockerfile
```

(yoki `backend/Dockerfile` agar root'dan build qilsa)

### Bosqich 4: Build Command'ni O'chirish

Docker ishlatganda build command kerak emas:

**Build Command:**

```
(bo'sh qoldiring yoki o'chiring)
```

### Bosqich 5: Start Command'ni O'chirish

Docker'da CMD allaqachon Dockerfile'da:

**Start Command:**

```
(bo'sh qoldiring yoki o'chiring)
```

### Bosqich 6: Environment Variables

Qoldiriladi (o'zgarishsiz):

```
PYTHON_VERSION=3.11.0
GROQ_API_KEY=your_key_here
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:5173,https://evalbee-frontend.onrender.com
```

### Bosqich 7: Save va Deploy

1. "Save Changes" tugmasini bosing
2. Render avtomatik qayta deploy qiladi
3. Logs'ni kuzating

## Kutilgan Natija

Build logs'da Docker build jarayoni ko'rinadi:

```
==> Building with Dockerfile
Step 1/10 : FROM python:3.11-slim
Step 2/10 : WORKDIR /app
Step 3/10 : RUN apt-get update && apt-get install -y...
✅ tesseract-ocr installed
✅ libzbar0 installed
✅ libgl1-mesa-glx installed
Step 4/10 : COPY requirements.txt .
Step 5/10 : RUN pip install...
✅ All Python packages installed
Step 6/10 : COPY . .
Step 7/10 : EXPOSE 8000
Step 8/10 : HEALTHCHECK...
Step 9/10 : CMD ["uvicorn"...]
✅ Build complete!
==> Deploying...
✅ Deploy successful!
```

## Test Qilish

### Health Check

```bash
curl https://evalbee-backend.onrender.com/
```

Natija:

```json
{
	"message": "EvalBee OMR Backend API",
	"version": "3.0.0",
	"status": "healthy"
}
```

### API Docs

```
https://evalbee-backend.onrender.com/docs
```

## Dockerfile Tuzilishi

Bizning `backend/Dockerfile`:

```dockerfile
# Python 3.11 slim image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libzbar0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Afzalliklari

### Docker vs Build Script

**Build Script (muammoli):**

- ❌ System dependencies ba'zan install bo'lmaydi
- ❌ Environment farqlari
- ❌ Debug qilish qiyin

**Docker (ishonchli):**

- ✅ Barcha dependencies kafolatlangan
- ✅ Local va production bir xil
- ✅ Reproducible
- ✅ Health check built-in

## Troubleshooting

### Build Failed

1. Logs'ni o'qing
2. Dockerfile syntax'ini tekshiring
3. Docker Build Context to'g'ri ekanligini tekshiring

### Container Crashes

1. Logs'da error'ni toping
2. Health check ishlayaptimi tekshiring
3. Port 8000 ochiq ekanligini tekshiring

### Slow Build

- Birinchi build 5-10 daqiqa oladi
- Keyingi build'lar tezroq (cache)

## Alternative: Native Build

Agar Docker ishlamasa, native build'ga qaytish:

1. Docker'ni o'chiring
2. Build Command:

```bash
bash render-build.sh
```

3. Start Command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Lekin Docker tavsiya etiladi!

## Xulosa

Docker ishlatish:

- ✅ Eng ishonchli usul
- ✅ Production-ready
- ✅ Kamroq muammolar
- ✅ Oson debug

**Render'da Docker'ni yoqing va qayta deploy qiling!**

---

**Status:** ✅ Dockerfile tayyor  
**Commit:** ec387ed  
**Next:** Render'da Docker'ni yoqish
