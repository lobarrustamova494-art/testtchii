# ⚡ Tezkor Deploy Qo'llanmasi

## 🎯 Maqsad

Render.com'da 2 ta alohida service deploy qilish:

1. **Backend** (Python)
2. **Frontend** (React)

---

## 📋 Tayyor Bo'lish

✅ GitHub: https://github.com/lobarrustamova494-art/testtchii  
✅ Render account: https://render.com (bepul)  
✅ Groq API key (ixtiyoriy, AI uchun)

---

## 🔴 BACKEND DEPLOY (5 daqiqa)

### 1. Render'da Yangi Service

- Dashboard → "New +" → "Web Service"
- GitHub repository ulang
- `lobarrustamova494-art/testtchii` ni tanlang

### 2. Sozlamalar

```
Name: evalbee-backend
Region: Oregon (US West)
Branch: main
Root Directory: backend          ⚠️ MUHIM!
Runtime: Python 3
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

### 3. Environment Variables

```
GROQ_API_KEY = your_key_here (ixtiyoriy)
ENVIRONMENT = production
PYTHON_VERSION = 3.11.0
CORS_ORIGINS = http://localhost:5173,https://evalbee-frontend.onrender.com
```

### 4. Deploy

- "Create Web Service" bosing
- 5-10 daqiqa kuting
- URL oling: `https://evalbee-backend.onrender.com`

### 5. Test

Browser'da: `https://evalbee-backend.onrender.com`

Ko'rinishi kerak:

```json
{ "message": "EvalBee OMR Backend API", "status": "healthy" }
```

---

## 🔵 FRONTEND DEPLOY (3 daqiqa)

### 1. Render'da Yangi Static Site

- Dashboard → "New +" → "Static Site"
- Xuddi shu repository'ni ulang

### 2. Sozlamalar

```
Name: evalbee-frontend
Branch: main
Root Directory: (bo'sh)          ⚠️ Bo'sh qoldiring!
Build Command: npm install && npm run build
Publish Directory: dist
```

### 3. Environment Variables

```
NODE_VERSION = 18
VITE_BACKEND_URL = https://evalbee-backend.onrender.com
```

⚠️ Backend URL'ni to'g'ri kiriting!

### 4. Rewrite Rules

```
Source: /*
Destination: /index.html
Action: Rewrite
```

### 5. Deploy

- "Create Static Site" bosing
- 3-5 daqiqa kuting
- URL oling: `https://evalbee-frontend.onrender.com`

### 6. Test

Browser'da: `https://evalbee-frontend.onrender.com`

Login sahifasi ochilishi kerak!

---

## ✅ YAKUNIY TEKSHIRISH

### Backend

```bash
curl https://evalbee-backend.onrender.com/
```

### Frontend

Browser'da ochib ko'ring va:

- Login qiling
- Exam yarating
- Kamera ochib ko'ring

---

## 🔧 MUAMMOLAR

### Backend 503 Error

**Sabab:** Free tier - 15 daqiqa ishlamasdan uxlaydi  
**Yechim:** Birinchi request 30 sekund kutadi, keyin tez ishlaydi

### Frontend Backend'ga Ulanmayapti

**Tekshirish:** Browser console (F12) → CORS xatosi?  
**Yechim:**

1. Backend CORS_ORIGINS'ni tekshiring
2. Frontend VITE_BACKEND_URL'ni tekshiring

### Build Failed

**Backend:** Logs'ni o'qing, Python 3.11 ekanligini tekshiring  
**Frontend:** Logs'ni o'qing, Node 18 ekanligini tekshiring

---

## 💰 XARAJATLAR

**Free Tier (tavsiya boshlovchilar uchun):**

- Backend: $0/month (750 hours, 15 min spin down)
- Frontend: $0/month (100 GB bandwidth)
- **Jami: $0/month** ✅

**Paid Tier (professional):**

- Backend: $7/month (always-on, no spin down)
- Frontend: $0/month
- **Jami: $7/month**

---

## 📚 BATAFSIL QOLLANMA

Ko'proq ma'lumot uchun:

- **RENDER_STEP_BY_STEP.md** - Bosqichma-bosqich qo'llanma
- **RENDER_DEPLOYMENT.md** - Texnik detallari
- **backend/README.md** - Backend hujjati

---

## 🎉 TAYYOR!

Endi sizda professional OMR tizimi ishlayapti:

**Backend:** https://evalbee-backend.onrender.com  
**Frontend:** https://evalbee-frontend.onrender.com  
**API Docs:** https://evalbee-backend.onrender.com/docs

**Omad!** 🚀
