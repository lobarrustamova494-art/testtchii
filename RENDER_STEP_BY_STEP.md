# Render.com - Bosqichma-Bosqich Deploy Qo'llanmasi

## Umumiy Ma'lumot

Render.com'da **2 ta alohida service** yaratamiz:

1. **Backend** - Python Web Service
2. **Frontend** - Static Site

## Boshlashdan Oldin

### Kerakli Narsalar:

- ✅ GitHub repository: https://github.com/lobarrustamova494-art/testtchii
- ✅ Render.com account (https://render.com - bepul)
- ✅ Groq API key (agar AI kerak bo'lsa)

---

## QISM 1: BACKEND DEPLOY QILISH

### Bosqich 1.1: Render Dashboard'ga Kirish

1. https://dashboard.render.com ga kiring
2. "New +" tugmasini bosing
3. "Web Service" ni tanlang

### Bosqich 1.2: GitHub Repository Ulash

1. "Connect a repository" bo'limida GitHub'ni tanlang
2. Agar birinchi marta bo'lsa, GitHub'ga ruxsat bering
3. Repository'ni toping: `lobarrustamova494-art/testtchii`
4. "Connect" tugmasini bosing

### Bosqich 1.3: Backend Sozlamalari

**Name (Nom):**

```
evalbee-backend
```

**Region (Hudud):**

```
Oregon (US West) - yoki eng yaqin hudud
```

**Branch:**

```
main
```

**Root Directory (Asosiy papka):**

```
backend
```

⚠️ **MUHIM**: `backend` papkasini ko'rsating!

**Runtime:**

```
Python 3
```

**Build Command:**

```
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**

```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Plan:**

```
Free (bepul)
```

### Bosqich 1.4: Environment Variables (Muhit O'zgaruvchilari)

"Environment" bo'limida quyidagilarni qo'shing:

**1. GROQ_API_KEY** (agar AI kerak bo'lsa)

```
Key: GROQ_API_KEY
Value: your_groq_api_key_here
```

**2. ENVIRONMENT**

```
Key: ENVIRONMENT
Value: production
```

**3. PYTHON_VERSION**

```
Key: PYTHON_VERSION
Value: 3.11.0
```

**4. CORS_ORIGINS** (keyinroq frontend URL qo'shamiz)

```
Key: CORS_ORIGINS
Value: http://localhost:5173,https://evalbee-frontend.onrender.com
```

### Bosqich 1.5: Advanced Settings (Qo'shimcha Sozlamalar)

**Auto-Deploy:**

```
✅ Yes (GitHub'ga push qilganda avtomatik deploy)
```

**Health Check Path:**

```
/
```

### Bosqich 1.6: Deploy Qilish

1. "Create Web Service" tugmasini bosing
2. Deploy jarayoni boshlanadi (5-10 daqiqa)
3. Logs'ni kuzatib turing

### Bosqich 1.7: Backend URL Olish

Deploy tugagach:

```
https://evalbee-backend.onrender.com
```

Bu URL'ni eslab qoling - frontend uchun kerak bo'ladi!

### Bosqich 1.8: Backend Test Qilish

Browser'da oching:

```
https://evalbee-backend.onrender.com
```

Ko'rinishi kerak:

```json
{
	"message": "EvalBee OMR Backend API",
	"version": "3.0.0",
	"status": "healthy"
}
```

API docs:

```
https://evalbee-backend.onrender.com/docs
```

---

## QISM 2: FRONTEND DEPLOY QILISH

### Bosqich 2.1: Yangi Static Site Yaratish

1. Render dashboard'ga qayting
2. "New +" tugmasini bosing
3. "Static Site" ni tanlang

### Bosqich 2.2: GitHub Repository Ulash

1. Xuddi backend kabi repository'ni ulang
2. `lobarrustamova494-art/testtchii` ni tanlang
3. "Connect" tugmasini bosing

### Bosqich 2.3: Frontend Sozlamalari

**Name (Nom):**

```
evalbee-frontend
```

**Branch:**

```
main
```

**Root Directory:**

```
(bo'sh qoldiring - root papka)
```

**Build Command:**

```
npm install && npm run build
```

**Publish Directory:**

```
dist
```

### Bosqich 2.4: Environment Variables

"Environment" bo'limida:

**1. NODE_VERSION**

```
Key: NODE_VERSION
Value: 18
```

**2. VITE_BACKEND_URL** (Backend URL'ni qo'ying)

```
Key: VITE_BACKEND_URL
Value: https://evalbee-backend.onrender.com
```

⚠️ **MUHIM**: Backend URL'ni to'g'ri kiriting!

### Bosqich 2.5: Rewrite Rules (URL Qayta Yozish)

"Redirects/Rewrites" bo'limida:

**Source:**

```
/*
```

**Destination:**

```
/index.html
```

**Action:**

```
Rewrite
```

Bu React Router uchun kerak!

### Bosqich 2.6: Deploy Qilish

1. "Create Static Site" tugmasini bosing
2. Deploy jarayoni boshlanadi (3-5 daqiqa)
3. Logs'ni kuzatib turing

### Bosqich 2.7: Frontend URL Olish

Deploy tugagach:

```
https://evalbee-frontend.onrender.com
```

---

## QISM 3: CORS SOZLASH (MUHIM!)

### Bosqich 3.1: Backend CORS Yangilash

1. Backend service'ga o'ting
2. "Environment" bo'limini oching
3. `CORS_ORIGINS` ni yangilang:

```
Key: CORS_ORIGINS
Value: http://localhost:5173,https://evalbee-frontend.onrender.com
```

4. "Save Changes" bosing
5. Backend avtomatik qayta deploy bo'ladi

---

## QISM 4: TEST QILISH

### Test 1: Backend Health Check

Browser'da:

```
https://evalbee-backend.onrender.com/
```

Natija:

```json
{ "message": "EvalBee OMR Backend API", "status": "healthy" }
```

### Test 2: Frontend Ochilishi

Browser'da:

```
https://evalbee-frontend.onrender.com
```

Login sahifasi ochilishi kerak.

### Test 3: Backend Connection

Frontend'da:

1. Login qiling
2. Exam yarating
3. Kamera ochib ko'ring
4. Rasm yuklang

Agar xatolik bo'lsa, browser console'ni tekshiring (F12).

---

## MUAMMOLARNI HAL QILISH

### Muammo 1: Backend 503 Error

**Sabab:** Free tier - 15 daqiqa ishlamasdan spin down bo'ladi

**Yechim:**

- Birinchi request 30 sekund kutadi
- Keyingi requestlar tez ishlaydi
- Yoki paid plan ($7/month) oling

### Muammo 2: Frontend Backend'ga Ulanmayapti

**Tekshirish:**

1. Browser console (F12) ni oching
2. CORS xatosi bormi?
3. Backend URL to'g'rimi?

**Yechim:**

1. Backend CORS_ORIGINS'ni tekshiring
2. Frontend VITE_BACKEND_URL'ni tekshiring
3. Ikkalasini ham qayta deploy qiling

### Muammo 3: Build Failed

**Backend:**

- Logs'ni o'qing
- Python version 3.11 ekanligini tekshiring
- requirements.txt to'g'ri ekanligini tekshiring

**Frontend:**

- Logs'ni o'qing
- Node version 18 ekanligini tekshiring
- package.json to'g'ri ekanligini tekshiring

### Muammo 4: Kamera Ishlamayapti

**Sabab:** HTTP'da kamera ishlamaydi

**Yechim:**

- Render avtomatik HTTPS beradi
- Browser'da HTTPS ekanligini tekshiring
- Camera permission bering

---

## QISM 5: MONITORING VA LOGS

### Backend Logs Ko'rish

1. Backend service'ga o'ting
2. "Logs" tab'ini oching
3. Real-time logs ko'rinadi

### Frontend Logs Ko'rish

1. Frontend service'ga o'ting
2. "Logs" tab'ini oching
3. Build logs ko'rinadi

### Metrics Ko'rish

1. Service'ga o'ting
2. "Metrics" tab'ini oching
3. CPU, Memory, Request count ko'rinadi

---

## QISM 6: YANGILASH (UPDATE)

### Kod O'zgarganda

1. GitHub'ga push qiling:

```bash
git add .
git commit -m "Update: description"
git push origin main
```

2. Render avtomatik deploy qiladi
3. Logs'da jarayonni kuzating

### Manual Deploy

Agar avtomatik ishlamasa:

1. Service'ga o'ting
2. "Manual Deploy" tugmasini bosing
3. "Deploy latest commit" ni tanlang

---

## QISM 7: CUSTOM DOMAIN (Ixtiyoriy)

### O'z Domeningizni Ulash

**Backend:**

1. Backend service → Settings → Custom Domain
2. Domain qo'shing: `api.yourdomain.com`
3. DNS'da CNAME record qo'shing

**Frontend:**

1. Frontend service → Settings → Custom Domain
2. Domain qo'shing: `yourdomain.com`
3. DNS'da CNAME record qo'shing

---

## XULOSA

### Tayyor URL'lar:

**Backend:**

```
https://evalbee-backend.onrender.com
https://evalbee-backend.onrender.com/docs (API docs)
```

**Frontend:**

```
https://evalbee-frontend.onrender.com
```

### Xarajatlar:

**Free Tier:**

- Backend: $0/month (750 hours, spin down after 15 min)
- Frontend: $0/month (100 GB bandwidth)
- **Jami: $0/month** ✅

**Paid Tier (tavsiya):**

- Backend: $7/month (always-on, no spin down)
- Frontend: $0/month
- **Jami: $7/month**

### Keyingi Qadamlar:

1. ✅ Backend deploy qilish
2. ✅ Frontend deploy qilish
3. ✅ CORS sozlash
4. ✅ Test qilish
5. ✅ Custom domain (ixtiyoriy)
6. ✅ Monitoring sozlash

---

## YORDAM

**Render Docs:**
https://render.com/docs

**Render Community:**
https://community.render.com

**GitHub Issues:**
https://github.com/lobarrustamova494-art/testtchii/issues

---

**Omad! Savollar bo'lsa so'rang!** 🚀
