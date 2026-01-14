# To'rtburchak Alignment - Yakuniy Yo'riqnoma

## 📊 Hozirgi Holat

### ✅ Bajarilgan Ishlar

1. **To'rtburchak o'lchamini kichraytirdik**

   - PADDING: 5px → 3px
   - THICKNESS: 3px → 2px

2. **Koordinata hisoblashni yaxshiladik**

   - Rounding qo'shildi (sub-pixel xatolarni oldini olish)
   - Logging yaxshilandi (muammolarni tezroq topish uchun)

3. **Diagnostic tool'lar yaratdik**
   - `diagnose_alignment.py` - rasm va koordinatalarni tahlil qilish
   - `debug_annotation.py` - annotatsiya muammolarini debug qilish

### ⚠️ Aniqlangan Muammolar

Backend loglaridan ko'rinib turibdiki:

1. **QR Code o'qilmayapti**

   ```
   WARNING - ⚠️  No QR code found, using default layout
   ```

   Sabab: Windows'da `pyzbar` kutubxonasi DLL muammosi tufayli ishlamayapti

2. **OMR Detection juda sezgir**

   ```
   35 uncertain, 34 multiple marks
   ```

   Deyarli barcha savollar "multiple marks" deb aniqlanmoqda

3. **Past confidence**
   Barcha 35 savol "uncertain" (past ishonch darajasi)

## 🎯 Asosiy Muammo va Yechim

### Muammo: Eski PDF Ishlatilgan

Agar siz test qilayotgan PDF **eski versiya** bilan yaratilgan bo'lsa:

- QR code'da eski layout qiymatlari bor
- `gridStartY = 113mm` (eski) o'rniga `149mm` (yangi) bo'lishi kerak
- Bu 36mm = ~213px siljish!

### ✅ YECHIM: Yangi PDF Yarating!

**MUHIM**: Barcha eski PDF'lar noto'g'ri ishlaydi. Faqat yangi PDF'lar to'g'ri.

#### Qadamlar:

1. **Frontend'ni ishga tushiring**

   ```bash
   npm run dev
   ```

2. **Yangi imtihon yarating yoki mavjudini oching**

3. **PDF yuklab oling**

   - "PDF Yuklab Olish" tugmasini bosing
   - Yangi PDF saqlanadi

4. **PDF'ni chop eting**

   - Yuqori sifatli printer ishlating
   - A4 qog'oz (210mm x 297mm)
   - Scale: 100% (kichraytirmasdan!)

5. **Qo'lda to'ldiring**

   - Qora qalam ishlating
   - Doirachalarni to'liq to'ldiring
   - Bir savolga faqat bitta javob

6. **Yuqori sifatli skan qiling**

   - 300 DPI yoki yuqori
   - Rangli yoki grayscale
   - To'g'ri yo'nalishda (portrait)

7. **Backend'ga yuklang va test qiling**

## 🔧 Agar Muammo Davom Etsa

### 1. Backend Loglarini Tekshiring

Backend ishga tushganda quyidagilarni qidiring:

```
✅ YAXSHI:
INFO - Using layout from QR code
INFO - Layout: gridStartY=149mm, bubbleRadius=2.5mm, rowHeight=5.5mm

⚠️ OGOHLANTIRISH:
WARNING - Using default layout (no QR code)
# QR code o'qilmadi, default layout ishlatilmoqda

❌ XATO:
WARNING - ⚠️  QR code has OLD gridStartY value: 113mm
# Eski PDF ishlatilgan!
```

### 2. Diagnostic Tool Ishlating

```bash
cd backend

# Exam structure JSON yarating (yoki mavjudini ishlating)
# Keyin:
python diagnose_alignment.py <image_path> <exam_structure.json>
```

Bu `debug_alignment.jpg` yaratadi - rasmda to'rtburchaklar bubble'larga mos keladimi ko'ring.

### 3. OMR Detection Sozlamalarini Tekshiring

Agar juda ko'p "multiple marks" yoki "uncertain" bo'lsa, `backend/config.py` da:

```python
# Hozirgi qiymatlar:
BUBBLE_RADIUS = 10  # Detection uchun radius
MIN_DARKNESS = 20.0  # Minimal qoralik
MIN_DIFFERENCE = 8.0  # Minimal farq
MULTIPLE_MARKS_THRESHOLD = 15  # Multiple marks chegarasi
```

Agar kerak bo'lsa, bu qiymatlarni o'zgartiring:

- `MIN_DARKNESS` ni oshiring (25-30) - faqat qora belgilarni aniqlash
- `MIN_DIFFERENCE` ni oshiring (10-12) - aniqroq farq talab qilish
- `MULTIPLE_MARKS_THRESHOLD` ni kamaytiring (10-12) - multiple marks'ni kamroq aniqlash

## 📋 Test Checklist

Yangi PDF bilan test qilishdan oldin:

- [ ] Yangi PDF yaratdingizmi? (eski PDF'lar ishlamaydi!)
- [ ] PDF to'g'ri chop etildimi? (100% scale, A4 qog'oz)
- [ ] Qo'lda to'g'ri to'ldirdingizmi? (qora qalam, to'liq to'ldirish)
- [ ] Yuqori sifatli skan qildingizmi? (300+ DPI)
- [ ] Backend ishga tushganmi? (`http://localhost:8000`)
- [ ] Frontend ishga tushganmi? (`http://localhost:3000`)

## 🎨 Kutilayotgan Natija

Agar hammasi to'g'ri bo'lsa:

### Tekshirilgan Varaq Rasmida:

- **Yashil to'rtburchak**: To'g'ri javob (har doim ko'rsatiladi)
- **Ko'k to'rtburchak**: Student to'g'ri belgilagan (yashil ustiga)
- **Qizil to'rtburchak**: Student xato belgilagan

### Misol:

```
Savol 1: To'g'ri javob = B, Student javobi = B (to'g'ri)
  A: [ ]
  B: [Yashil + Ko'k]  ← To'g'ri javob va student javobi
  C: [ ]
  D: [ ]
  E: [ ]

Savol 2: To'g'ri javob = C, Student javobi = D (xato)
  A: [ ]
  B: [ ]
  C: [Yashil]  ← To'g'ri javob
  D: [Qizil]   ← Student xato javobi
  E: [ ]

Savol 3: To'g'ri javob = A, Student javobi = yo'q
  A: [Yashil]  ← To'g'ri javob
  B: [ ]
  C: [ ]
  D: [ ]
  E: [ ]
```

## 🐛 Muammo Hal Bo'lmasa

Agar yangi PDF bilan ham muammo bo'lsa, quyidagilarni yuboring:

1. **Backend loglari** (terminal output)
2. **Test rasmi** (skan qilingan varaq)
3. **Exam structure JSON**
4. **PDF fayli** (yangi yaratilgan)

Men batafsil tahlil qilaman va aniq yechim topaman.

## 💡 Qo'shimcha Maslahatlar

### PDF Chop Etish

- **Scale**: 100% (kichraytirmasdan!)
- **Qog'oz**: A4 (210mm x 297mm)
- **Sifat**: Yuqori sifat (draft emas)
- **Ikki tomonlama**: Yo'q (faqat bir tomon)

### Qo'lda To'ldirish

- **Qalam**: Qora qalam (ko'k emas!)
- **To'ldirish**: To'liq to'ldiring (yarim emas)
- **Tozalik**: Qog'ozni ifloslantirib qo'ymang
- **Bitta javob**: Har bir savolga faqat bitta javob

### Skan Qilish

- **DPI**: 300 yoki yuqori
- **Rang**: Rangli yoki grayscale (ikkalasi ham ishlaydi)
- **Yo'nalish**: Portrait (tik)
- **Kesish**: Butun qog'ozni skan qiling (kesib qo'ymang)
- **Sifat**: Blur bo'lmasin, aniq bo'lsin

## ✨ Xulosa

**Eng muhim qadam**: YANGI PDF YARATING!

Eski PDF'lar eski layout qiymatlari bilan yaratilgan va noto'g'ri ishlaydi. Yangi PDF yarating, to'g'ri chop eting, to'g'ri to'ldiring, to'g'ri skan qiling - va hammasi ishlaydi!

Omad! 🚀
