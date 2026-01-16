# 📖 TEKSHIRISH QO'LLANMASI

**Maqsad**: Varaqni to'g'ri tekshirish

---

## 🚀 BOSQICHMA-BOSQICH

### 1️⃣ BACKEND ISHGA TUSHIRISH

**MUHIM**: Backend ishlamasa, tekshirish ishlamaydi!

```bash
# Terminal 1
cd backend
python main.py
```

**Kutilgan output**:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Tekshirish**:

- Brauzerda: http://localhost:8000/health
- Ko'rinishi kerak: `{"status":"healthy"}`

---

### 2️⃣ FRONTEND ISHGA TUSHIRISH

```bash
# Terminal 2 (yangi terminal)
npm run dev
```

**Kutilgan output**:

```
➜  Local:   http://localhost:5173/
```

---

### 3️⃣ IMTIHON YARATISH

1. Login: `admin` / `admin`
2. "Yangi Imtihon" tugmasini bosing
3. Imtihon ma'lumotlarini kiriting:

   - Nomi: "4-Imtihon"
   - Mavzular va bo'limlar
   - Savol sonlari

4. "Imtihon Yaratish" tugmasini bosing

---

### 4️⃣ JAVOB KALITLARINI BELGILASH ⚠️ MUHIM!

**Bu bosqichni o'tkazib yubormang!**

1. Imtihon yaratilgandan keyin
2. "Javob Kalitlarini Boshqarish" tugmasini bosing
3. To'plam A uchun to'g'ri javoblarni belgilang:

   - Har bir savol uchun to'g'ri variantni tanlang
   - Masalan: 1-A, 2-B, 3-C, 4-D, 5-E...

4. "Saqlash" tugmasini bosing

**Agar bu bosqichni o'tkazib yuborsangiz**:

```
❌ Javob Kalitlari Topilmadi
Tekshirishni boshlash uchun avval javob kalitlarini belgilang.
```

---

### 5️⃣ PDF YARATISH

1. "PDF Yuklab Olish" tugmasini bosing
2. To'plam A'ni tanlang
3. PDF yuklab olinadi
4. PDF'ni chop eting:
   - 100% scale (kichraytirmang!)
   - A4 qog'oz
   - Yuqori sifatli printer

---

### 6️⃣ VARAQNI TO'LDIRISH

1. Qora qalam ishlating (HB yoki 2B)
2. Doirachalarni to'liq to'ldiring
3. Bir savolga faqat bitta javob
4. Tozalik bilan ishlang

**To'g'ri**:

```
1. ● ○ ○ ○ ○  ← A to'liq to'ldirilgan
```

**Noto'g'ri**:

```
1. ◐ ○ ○ ○ ○  ← Yarim to'ldirilgan
1. ● ● ○ ○ ○  ← Ikki javob
1. ○ ○ ○ ○ ○  ← Javob yo'q
```

---

### 7️⃣ SKAN QILISH

1. Varaqni skan qiling:

   - 300+ DPI (tavsiya: 300-600 DPI)
   - Rangli yoki oq-qora
   - JPEG yoki PNG format

2. Yoki telefon kamerasi bilan:
   - Yaxshi yorug'lik
   - Tekis qog'oz
   - To'liq varaq ko'rinsin
   - Qiyshiq bo'lmasin

---

### 8️⃣ TEKSHIRISH

1. "Tekshirish" bo'limiga o'ting
2. **Backend status tekshiring**:

```
System Status
┌─────────────────────────────────────┐
│ Backend Server                      │
│ ✓ OpenCV + Python                   │
│ Status: Available (YASHIL)          │  ← Bu ko'rinishi kerak!
└─────────────────────────────────────┘
```

**Agar "Offline" ko'rsatsa**:

- Backend ishlamayapti
- Terminal 1'ni tekshiring
- `python main.py` qayta ishga tushiring

3. **Rasmni yuklang**:

   - "Fayl Tanlash" tugmasini bosing
   - Yoki drag & drop qiling

4. **Tekshirish tugmasini bosing**:
   - Har bir varaq uchun "Tekshirish" tugmasi paydo bo'ladi
   - Tugmani bosing
   - Kutib turing (2-3 soniya)

---

### 9️⃣ NATIJALARNI KO'RISH

**Muvaffaqiyatli tekshirish**:

```
✅ Backend processing complete! (2.34s)

Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ball: 90/100
Foiz: 90.0%
To'g'ri: 45
Noto'g'ri: 5
Baho: 5 (A'lo)

[Annotated Image]
- Yashil: To'g'ri javob
- Ko'k: Student to'g'ri belgilagan
- Qizil: Student xato belgilagan
```

---

## ❌ MUAMMOLARNI HAL QILISH

### Muammo 1: "Javob Kalitlari Topilmadi"

**Sabab**: Answer key yaratilmagan

**Yechim**:

1. Orqaga qaytish
2. "Javob Kalitlarini Boshqarish"
3. To'g'ri javoblarni belgilash
4. Saqlash
5. Qayta tekshirish

---

### Muammo 2: "Backend mavjud emas"

**Sabab**: Backend ishlamayapti

**Yechim**:

```bash
# Terminal 1
cd backend
python main.py

# Tekshirish
curl http://localhost:8000/health
```

---

### Muammo 3: Varaq yuklangan, lekin tekshirilmayapti

**Sabab**: "Tekshirish" tugmasi bosilmagan

**Yechim**:

1. Varaq yuklangandan keyin
2. Varaq ustiga hover qiling
3. "Tekshirish" tugmasi paydo bo'ladi
4. Tugmani bosing

---

### Muammo 4: Aniqlik past

**Sabab**: Skan sifati yoki to'ldirish sifati

**Yechim**:

1. Yuqori sifatli skan (300+ DPI)
2. Doirachalarni to'liq to'ldiring
3. Qora qalam ishlating
4. Yorug'lik yaxshi bo'lsin

---

## 📊 KUTILGAN NATIJALAR

### Backend Logs

```
INFO - === NEW GRADING REQUEST ===
INFO - File: exam_sheet.jpg
INFO - STEP 1/6: Image Processing...
INFO - Found 4 corner markers
INFO - STEP 2/6: QR Code Detection...
INFO - ✅ QR code detected!
INFO - STEP 3/6: Coordinate Calculation...
INFO - STEP 4/6: OMR Detection (Advanced)...
INFO - Found 250 potential bubbles
INFO - Detection: 50/50, uncertain: 2
INFO - STEP 5/6: AI Verification skipped
INFO - STEP 6/6: Grading...
INFO - STEP 6/6: Image Annotation...
INFO - === GRADING COMPLETE ===
INFO - Duration: 2.34s
INFO - Score: 90/100 (90.0%)
```

### Frontend

- ✅ Backend status: Available
- ✅ Varaq yuklandi
- ✅ "Tekshirish" tugmasi ko'rinadi
- ✅ Processing animation
- ✅ Natijalar ko'rsatiladi
- ✅ Annotated image

---

## 🎯 XULOSA

### Minimal Workflow

1. ✅ Backend ishga tushirish
2. ✅ Frontend ishga tushirish
3. ✅ Imtihon yaratish
4. ✅ **Javob kalitlarini belgilash** ⚠️ MUHIM!
5. ✅ PDF yaratish va chop etish
6. ✅ Varaqni to'ldirish
7. ✅ Skan qilish
8. ✅ Backend status tekshirish
9. ✅ Varaqni yuklash
10. ✅ **"Tekshirish" tugmasini bosish** ⚠️ MUHIM!
11. ✅ Natijalarni ko'rish

### Eng Ko'p Uchraydigan Xatolar

1. ❌ Answer key yaratilmagan → Avval yarating!
2. ❌ Backend ishlamayapti → `python main.py`
3. ❌ "Tekshirish" tugmasi bosilmagan → Bosing!
4. ❌ Skan sifati past → 300+ DPI

---

**Omad!** 🎯

Agar muammolar davom etsa, backend terminal'dagi loglarni yuboring.
