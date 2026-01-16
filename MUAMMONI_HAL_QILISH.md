# Annotation Muammosini Hal Qilish - Qadamma-qadam Yo'riqnoma

## 📋 Muammo

Annotation kvadratlari (yashil, qizil, ko'k) noto'g'ri joylarda ko'rinmoqda:

- Savol raqamlarida
- Bubble'lardan siljigan holda
- Ba'zi savollarda to'g'ri, ba'zilarida noto'g'ri

## 🎯 Yechim - 3 Qadam

### QADAM 1: Muammoni Aniqlash

**Windows CMD'da:**

```cmd
cd backend
test_debug.bat path\to\test_image.jpg
```

**Yoki qo'lda:**

```cmd
cd backend
python quick_debug.py path\to\test_image.jpg
```

**Natija:**

Agar corner'lar topilsa:

```
✅ CORNER DETECTION: OK
Corners: 4/4
✅ System should work correctly
```

Agar corner'lar topilmasa:

```
❌ CORNER DETECTION: FAILED
Corners: 0/4
⚠️  System will use FALLBACK coordinates
```

### QADAM 2: Muammoni Tuzatish

#### Variant A: Corner'lar Topilmagan (0/4 yoki 1/4 yoki 2/4 yoki 3/4)

**Sabab:** Corner marker'lar ko'rinmayapti yoki juda och rangda.

**Yechim:**

1. **PDF'ni qayta yarating** - corner marker'lar bilan:

   - Frontend'da "Create Exam" bo'limiga o'ting
   - Exam yarating
   - PDF yuklab oling
   - PDF'da 4 ta burchakda qora kvadratlar borligini tekshiring

2. **Yuqori sifatli skan/foto:**

   - Yaxshi yoritilgan joyda
   - To'g'ri burchak ostida
   - Minimum 300 DPI
   - Barcha 4 ta corner marker ko'rinishi kerak

3. **Qayta test qiling:**

   ```cmd
   python quick_debug.py new_image.jpg
   ```

4. **Debug image'ni tekshiring:**
   - `quick_debug.jpg` faylini oching
   - 4 ta yashil doira ko'rinishi kerak (corner'larda)

#### Variant B: Corner'lar Topilgan (4/4) Lekin Annotation Noto'g'ri

**Sabab:** OMR detection noto'g'ri ishlayapti.

**Yechim:**

1. **Full debug'ni ishga tushiring:**

   ```cmd
   python debug_full_system.py test_image.jpg
   ```

2. **Log'ni o'qing:**

   ```
   STEP 5: OMR DETECTION
   Sample Detections (Q1-10):
      Q1: A (confidence: 35%)  ← PAST CONFIDENCE!
      Q2: NO_MARK (confidence: 0%)
      Q3: A (confidence: 40%)
   ```

3. **Agar confidence past bo'lsa:**

   - Image quality yomon
   - Bubble'lar to'liq bo'yalmagan
   - Yoki OMR detector noto'g'ri sozlangan

4. **Debug image'ni tekshiring:**
   - `debug_full_system.jpg` faylini oching
   - Ko'k doiralar = savol raqamlari
   - Yashil doiralar = bubble'lar
   - Ular to'g'ri joylardami?

#### Variant C: OCR Anchor System'ni Ishlatish (ENG YAXSHI!)

**Sabab:** Corner-based system ham ishlamayapti.

**Yechim:** OCR bilan savol raqamlarini topish.

**1. Tesseract OCR'ni o'rnating:**

Windows uchun:

1. https://github.com/UB-Mannheim/tesseract/wiki ga o'ting
2. "tesseract-ocr-w64-setup-5.x.x.exe" yuklab oling
3. O'rnating (default path: `C:\Program Files\Tesseract-OCR`)
4. PATH'ga qo'shing:
   - "Environment Variables" ni oching
   - "Path" ga `C:\Program Files\Tesseract-OCR` qo'shing

**2. Python package'ni o'rnating:**

```cmd
cd backend
pip install pytesseract
```

**3. Backend'ni qayta ishga tushiring:**

```cmd
python main.py
```

**4. Frontend'da varaq yuklang va log'ni kuzating:**

```
STEP 3/6: Coordinate Calculation...
Trying OCR-based anchor detection...
✅ Using OCR-based anchor system (100% accurate, perspective-independent)
```

**Agar OCR ishlasa:**

- Annotation 100% to'g'ri bo'ladi
- Perspektiva muammosi yo'q
- Har bir savol uchun alohida anchor

### QADAM 3: Natijani Tekshirish

**1. Backend'ni ishga tushiring:**

```cmd
cd backend
python main.py
```

**2. Frontend'da varaq yuklang**

**3. Backend log'ni kuzating:**

```
=== NEW GRADING REQUEST ===
STEP 1/6: Image Processing...
✅ Image processed
   Corners found: 4/4

STEP 3/6: Coordinate Calculation...
✅ Using corner-based coordinate system (100% accurate)

STEP 4/6: OMR Detection...
✅ OMR Detection complete
   Total questions: 40
   Detected answers: 38/40

STEP 6/6: Image Annotation...
✅ Annotated 40 questions

=== GRADING COMPLETE ===
Score: 35/40 (87.5%)
```

**4. Annotated image'ni tekshiring:**

- Yashil kvadratlar to'g'ri javoblarda
- Qizil kvadratlar xato javoblarda
- Ko'k kvadratlar to'g'ri belgilangan javoblarda
- Barcha kvadratlar to'g'ri joylarda

## 🔍 Diagnostika

### Muammo: Annotation hali ham noto'g'ri

**Tekshirish:**

1. **Backend log'da qaysi coordinate system ishlatilgan?**

   - OCR Anchor → Eng yaxshi
   - Corner-based → Yaxshi
   - Fallback → Yomon (noto'g'ri bo'ladi)

2. **Corner'lar topildimi?**

   ```cmd
   python quick_debug.py test_image.jpg
   ```

   - 4/4 → Yaxshi
   - 0/4 → Yomon

3. **OMR detection to'g'rimi?**
   ```cmd
   python debug_full_system.py test_image.jpg
   ```
   - Confidence > 80% → Yaxshi
   - Confidence < 50% → Yomon

### Muammo: Backend ishga tushmayapti

**Xato:** `ModuleNotFoundError: No module named 'cv2'`

**Yechim:**

```cmd
cd backend
pip install -r requirements.txt
```

**Xato:** `pytesseract.pytesseract.TesseractNotFoundError`

**Yechim:**

1. Tesseract OCR'ni o'rnating (yuqoridagi yo'riqnoma)
2. Yoki OCR'siz ishlating (corner-based system)

### Muammo: Debug script ishlamayapti

**Xato:** `python: command not found`

**Yechim:**

```cmd
py quick_debug.py test_image.jpg
```

Yoki:

```cmd
python3 quick_debug.py test_image.jpg
```

## 📊 Natija

### Muvaffaqiyatli Natija:

```
✅ Corner Detection: 4/4
✅ Coordinate System: Corner-based
✅ OMR Detection: 38/40 (95%)
✅ Annotation: To'g'ri joylarda
```

### Muammoli Natija:

```
❌ Corner Detection: 0/4
⚠️  Coordinate System: Fallback
⚠️  OMR Detection: 20/40 (50%)
❌ Annotation: Noto'g'ri joylarda
```

**Yechim:** Corner marker'larni yaxshilang yoki OCR Anchor System'ni ishlating.

## 🎓 Qo'shimcha Ma'lumot

### Debug Image'lar:

1. **quick_debug.jpg**

   - Yashil doiralar = Topilgan corner'lar
   - 4 ta doira bo'lishi kerak (4 ta burchakda)

2. **debug_full_system.jpg**
   - Ko'k doiralar = Savol raqamlari
   - Yashil doiralar = Bubble'lar
   - Har bir savolda 4 ta yashil doira (A, B, C, D)

### Backend Log:

Backend log'da quyidagilarni qidiring:

- `✅ Found 4 corner markers` → Corner detection ishlayapti
- `⚠️  Corner markers not found` → Corner detection ishlamayapti
- `✅ Using corner-based coordinate system` → To'g'ri system
- `⚠️  Using fallback system` → Noto'g'ri system
- `✅ Using OCR-based anchor system` → Eng yaxshi system

## 📞 Yordam

Agar muammo hal bo'lmasa, quyidagilarni yuboring:

1. Backend log (to'liq)
2. `quick_debug.jpg` image
3. `debug_full_system.jpg` image
4. Original test image
5. Annotated image (frontend'dan)

---

**Muvaffaqiyat!** 🎉
