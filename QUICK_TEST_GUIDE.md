# 🚀 TEZKOR TEST QO'LLANMASI

**Maqsad**: Tuzatishlarni tezda test qilish  
**Vaqt**: 5-10 daqiqa

---

## 1️⃣ BACKEND ISHGA TUSHIRISH

```bash
# Terminal 1
cd backend
python main.py
```

**Kutilgan output**:

```
============================================================
PROFESSIONAL OMR GRADING SYSTEM v3.0
============================================================
Host: 0.0.0.0
Port: 8000
AI Verification: DISABLED
============================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Tekshirish**:

- ✅ Server ishga tushdi
- ✅ Port 8000 ochiq
- ✅ Xatolik yo'q

---

## 2️⃣ FRONTEND ISHGA TUSHIRISH

```bash
# Terminal 2 (yangi terminal)
npm run dev
```

**Kutilgan output**:

```
VITE v5.0.8  ready in 1234 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Tekshirish**:

- ✅ Vite server ishga tushdi
- ✅ Port 5173 ochiq
- ✅ Xatolik yo'q

---

## 3️⃣ BACKEND STATUS TEKSHIRISH

Brauzerda: http://localhost:5173

**Ko'rinishi kerak**:

- ✅ Login sahifa
- ✅ Xatolik yo'q

**Login**:

- Username: `admin`
- Password: `admin`

---

## 4️⃣ BACKEND CONNECTION TEKSHIRISH

Dashboard'da:

1. "Yangi Imtihon" tugmasini bosing
2. Imtihon yarating (istalgan nom)
3. Imtihon yaratilgandan keyin "Tekshirish" bo'limiga o'ting

**Ko'rinishi kerak**:

```
System Status
┌─────────────────────────────────────┐
│ Backend Server                      │
│ ✓ OpenCV + Python                   │
│ Status: Available (yashil)          │
└─────────────────────────────────────┘
```

**Agar "Offline" ko'rsatsa**:

- Backend ishlamayapti
- Terminal 1'ni tekshiring
- `python main.py` qayta ishga tushiring

---

## 5️⃣ TUZATISHLARNI TEKSHIRISH

### A. Backend Ishlatilmoqda?

**Tekshirish**: System Status panelida

```
Processing Mode
Backend (99.9%)  ← Bu ko'rinishi kerak!
```

**Agar "Frontend (99%)" ko'rsatsa**:

- ❌ Backend ulanmagan
- `src/App.tsx` ni tekshiring
- `ExamGradingHybrid` import qilinganmi?

### B. Advanced Detector Ishlatilmoqda?

**Tekshirish**: Backend terminal'da

Varaq yuklanganda log'da ko'rinishi kerak:

```
INFO - STEP 4/6: OMR Detection (Advanced)...
INFO - Found 150 potential bubbles
```

**Agar "(Advanced)" yo'q bo'lsa**:

- ❌ Eski detector ishlatilmoqda
- `backend/main.py` ni tekshiring

### C. Threshold Optimal?

**Tekshirish**: Backend terminal'da

```bash
# Backend terminal'da
python -c "from config import settings; print(f'MIN_DARKNESS: {settings.MIN_DARKNESS}, MIN_DIFFERENCE: {settings.MIN_DIFFERENCE}')"
```

**Kutilgan output**:

```
MIN_DARKNESS: 25.0, MIN_DIFFERENCE: 10.0
```

### D. Offset Olib Tashlandi?

**Tekshirish**: Annotated image'da

Varaq tekshirilgandan keyin:

- To'rtburchaklar bubble'larga mos kelishi kerak
- Chapga yoki o'ngga siljimagan bo'lishi kerak

### E. Corner Detection Yaxshilandi?

**Tekshirish**: Backend log'da

```
INFO - Found 4 corner markers  ← 4/4 topildi!
```

**Yoki**:

```
WARNING - Only 2/4 corner markers found  ← Hali ham muammo
```

### F. QR Detection Ishlayapti?

**Tekshirish**: Backend log'da

```
INFO - ✅ QR Code detected! Using QR layout data
```

**Yoki**:

```
WARNING - ⚠️  No QR code found, using default layout
```

---

## 6️⃣ TO'LIQ TEST (Ixtiyoriy)

Agar real varaq bo'lsa:

1. **PDF yaratish**:

   - Imtihon yarating
   - "PDF Yuklab Olish" → To'plam A
   - PDF'ni chop eting (100% scale, A4)

2. **Varaqni to'ldirish**:

   - Qora qalam
   - Doirachalarni to'liq to'ldiring
   - Bir savolga bitta javob

3. **Skan qilish**:

   - 300+ DPI
   - Rangli yoki oq-qora
   - JPEG yoki PNG

4. **Tekshirish**:

   - "Tekshirish" bo'limiga o'ting
   - Rasmni yuklang
   - "Tekshirish" tugmasini bosing

5. **Natijalarni ko'rish**:
   - Backend log'larni kuzating
   - Frontend'da natijalarni ko'ring
   - Annotated image'ni tekshiring

---

## 7️⃣ KUTILGAN NATIJALAR

### Backend Logs

```
INFO - === NEW GRADING REQUEST ===
INFO - File: exam_sheet.jpg
INFO - File saved: temp/1234567890_exam_sheet.jpg
INFO - STEP 1/6: Image Processing...
INFO - Image loaded: 2480x3508
INFO - Detecting corner markers...
INFO - Found 4 corner markers  ← ✅ Yaxshi!
INFO - Correcting perspective...
INFO - Resizing to 1240x1754...
INFO - Converting to grayscale...
INFO - Applying adaptive thresholding...
INFO - Reducing noise...
INFO - Enhancing contrast...
INFO - Image quality: 85.3%
INFO - STEP 2/6: QR Code Detection...
INFO - Trying OpenCV QRCodeDetector...
INFO - OpenCV QR code found! Data length: 456 bytes
INFO - ✅ QR code successfully read with OpenCV  ← ✅ Yaxshi!
INFO - STEP 3/6: Coordinate Calculation...
INFO - Using layout from QR code  ← ✅ Yaxshi!
INFO - Calculated coordinates for 50 questions
INFO - STEP 4/6: OMR Detection (Advanced)...  ← ✅ Advanced!
INFO - Found 250 potential bubbles
INFO - Detection: 50/50, uncertain: 2, multiple: 0
INFO - STEP 5/6: AI Verification skipped
INFO - STEP 6/6: Grading...
INFO - Grading complete: 45/50 correct
INFO - STEP 6/6: Image Annotation...
INFO - Annotated 50 questions
INFO - === GRADING COMPLETE ===
INFO - Duration: 2.34s  ← ✅ Tez!
INFO - Score: 90/100 (90.0%)  ← ✅ Aniq!
```

### Frontend

```
System Status
✅ Backend Server: Available
✅ AI Verification: Disabled
✅ Processing Mode: Backend (99.9%)

Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ball: 90/100
Foiz: 90.0%
To'g'ri: 45
Noto'g'ri: 5
Baho: 5 (A'lo)

[Annotated Image ko'rsatiladi]
- Yashil: To'g'ri javob
- Ko'k: Student to'g'ri belgilagan
- Qizil: Student xato belgilagan
```

---

## 8️⃣ MUAMMOLARNI HAL QILISH

### Backend ulanmayapti

**Belgi**: "Backend Server: Offline"

**Yechim**:

```bash
# 1. Backend ishga tushirish
cd backend
python main.py

# 2. Port tekshirish
netstat -an | findstr "8000"

# 3. Firewall tekshirish
# Windows Firewall'da port 8000 ochiq bo'lishi kerak
```

### Corner markers topilmayapti

**Belgi**: "Only 2/4 corner markers found"

**Yechim**:

1. PDF'ni qayta chop eting (100% scale)
2. Yuqori sifatli skan qiling (300+ DPI)
3. Yorug'lik yaxshi bo'lsin
4. Qog'oz tekis bo'lsin

### QR code o'qilmayapti

**Belgi**: "No QR code found"

**Yechim**:

1. PDF'ni qayta yarating (yangi QR code)
2. QR code aniq ko'rinsin (chop sifati)
3. Skan sifati yaxshi bo'lsin
4. Default layout ishlatiladi (muammo emas)

### Aniqlik past

**Belgi**: Ko'p xato javoblar

**Yechim**:

1. Doirachalarni to'liq to'ldiring
2. Qora qalam ishlating
3. Skan sifatini oshiring (300+ DPI)
4. Yorug'lik yaxshi bo'lsin
5. Threshold'ni sozlang (config.py)

---

## 9️⃣ XULOSA

### Minimal Test (2 daqiqa)

1. ✅ Backend ishga tushirish
2. ✅ Frontend ishga tushirish
3. ✅ Backend status tekshirish
4. ✅ "Backend (99.9%)" ko'rinishi

### To'liq Test (10 daqiqa)

1. ✅ Minimal test
2. ✅ PDF yaratish
3. ✅ Varaqni to'ldirish
4. ✅ Skan qilish
5. ✅ Tekshirish
6. ✅ Natijalarni ko'rish

### Muvaffaqiyat Mezonlari

- ✅ Backend ulanadi
- ✅ Advanced detector ishlatiladi
- ✅ 4/4 corner markers topiladi (ideal)
- ✅ QR code o'qiladi (ideal)
- ✅ Aniqlik 95%+ (yuqori sifatli skan)
- ✅ Processing 2-3s
- ✅ Annotated image to'g'ri

---

**Omad!** 🎯

Agar muammolar bo'lsa, `MUAMMOLAR_HAL_QILINDI.md` va `TUZATISHLAR_SUMMARY.md` fayllarini o'qing.
