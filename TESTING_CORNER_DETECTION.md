# Corner Detection Test - Qo'llanma

## Tezkor Test

### 1. Backend'ni Restart Qiling

```bash
cd backend
python main.py
```

### 2. Test Script bilan Tekshiring

```bash
cd backend
python test_corner_detection.py path/to/your/image.jpg
```

Masalan:

```bash
python test_corner_detection.py ../test_images/exam_sheet_1.jpg
```

### 3. Output'ni Tekshiring

Script 2 ta fayl yaratadi:

1. **`image_corner_debug.jpg`** - Vizualizatsiya

   - Yashil doiralar = Topilgan corner'lar
   - Sariq to'rtburchaklar = Search region'lar
   - Yashil matn = Corner nomi va score

2. **`image_threshold.jpg`** - Binary threshold
   - Oq = Qora obyektlar
   - Qora = Och obyektlar
   - Corner marker'lar oq rangda ko'rinishi kerak

### 4. Log'ni O'qing

Terminal'da quyidagilar ko'rinadi:

```
Testing corner detection on: exam_sheet_1.jpg
============================================================
✅ Image loaded: 2480x3508

✅ Found top-left marker: (124, 142)
    Score: 0.85
    Darkness: 0.92
    Uniformity: 0.78

✅ Found top-right marker: (2356, 138)
    Score: 0.82
    Darkness: 0.88
    Uniformity: 0.75

✅ Found bottom-left marker: (126, 3366)
    Score: 0.79
    Darkness: 0.85
    Uniformity: 0.72

✅ Found top-right marker: (2354, 3362)
    Score: 0.81
    Darkness: 0.87
    Uniformity: 0.74

✅ Visualization saved: exam_sheet_1_corner_debug.jpg
✅ Threshold image saved: exam_sheet_1_threshold.jpg

============================================================
SUMMARY:
  Corners found: 4/4
  ✅ All corners detected successfully!
============================================================
```

## Natijalarni Tahlil Qilish

### ✅ Muvaffaqiyatli (4/4 corners)

Agar barcha 4 ta corner topilsa:

- Frontend'da imtihon tekshiring
- Backend log'da "TEMPLATE-BASED" ko'rinishi kerak
- Koordinatalar 100% to'g'ri bo'lishi kerak

### ⚠️ Qisman Muvaffaqiyat (2-3/4 corners)

Agar 2-3 ta corner topilsa:

1. Threshold image'ni tekshiring
2. Topilmagan corner'lar oq rangda ko'rinishi kerak
3. Agar ko'rinmasa, print quality yomon
4. Agar ko'rinsa, lekin topilmasa, parametrlarni sozlash kerak

### ❌ Muvaffaqiyatsiz (0-1/4 corners)

Agar corner'lar topilmasa:

1. **Threshold image'ni tekshiring**

   - Corner marker'lar oq rangda ko'rinishi kerak
   - Agar ko'rinmasa, marker juda och rangda

2. **Visualization'ni tekshiring**

   - Sariq to'rtburchaklar to'g'ri joyda?
   - Marker'lar sariq to'rtburchak ichida?

3. **Print quality'ni tekshiring**
   - Marker'lar to'liq qora rangda print qilinganmi?
   - Marker'lar bir xil qoralikdami?

## Troubleshooting

### Muammo: "Darkness too low"

```
❌ Rejected top-left marker: score=0.42, darkness=0.35
```

**Yechim:**

- Marker juda och rangda
- Qayta print qiling (qora rangda)
- Yoki printer settings'ni tekshiring

### Muammo: "Uniformity too low"

```
❌ Rejected top-right marker: score=0.45, uniformity=0.35
```

**Yechim:**

- Marker bir xil qoralikda emas (gradient)
- Print quality yomon
- Qayta print qiling

### Muammo: "No candidate found"

```
❌ No candidate found for bottom-left
```

**Yechim:**

- Marker search region'da emas
- PDF margin noto'g'ri
- Yoki marker umuman yo'q

### Muammo: "Score too low"

```
❌ Rejected bottom-right marker: score=0.42 (threshold=0.5)
```

**Yechim:**

- Marker bir nechta parametrda yomon
- Threshold image'ni tekshiring
- Marker to'g'ri shaklda va rangdami?

## Frontend'da Test Qilish

### 1. Yangi Imtihon Yarating

1. Frontend'ni oching
2. Yangi imtihon yarating
3. Console'da tekshiring:
   ```
   ✅ Imtihon koordinata template bilan saqlandi
   ```

### 2. PDF Chiqaring

1. "PDF Chiqarish" tugmasini bosing
2. PDF'ni print qiling yoki save qiling
3. Corner marker'lar to'g'ri joyda va qora rangda bo'lishi kerak

### 3. Tekshiring

1. Print qilingan varaqni scan qiling
2. "Tekshirish" sahifasiga o'ting
3. Imtihonni tanlang
4. Rasm yuklang
5. Backend log'ni kuzating:

```
STEP 1/6: Image Processing...
✅ All 4 corner markers detected successfully

STEP 3/6: Coordinate Calculation...
✅ Using TEMPLATE-BASED coordinate system (EvalBee style)
✅ Calculated coordinates for 40 questions from template
```

## Expected Results

### Backend Log (Muvaffaqiyatli)

```
=== NEW GRADING REQUEST ===
File: exam_sheet_1.jpg
STEP 1/6: Image Processing...
✅ Found top-left marker: score=0.85, darkness=0.92, uniformity=0.78
✅ Found top-right marker: score=0.82, darkness=0.88, uniformity=0.75
✅ Found bottom-left marker: score=0.79, darkness=0.85, uniformity=0.72
✅ Found bottom-right marker: score=0.81, darkness=0.87, uniformity=0.74
✅ All 4 corner markers detected successfully

STEP 2/6: QR Code Detection...
✅ QR Code detected! Using QR layout data

STEP 3/6: Coordinate Calculation...
✅ Using TEMPLATE-BASED coordinate system (EvalBee style)
   Template version: 2.0
   Template timestamp: 2026-01-15T10:30:00
   Top-left corner: (124.0, 142.0) px
   Distance between corners: 2232.0 x 3224.0 px
   Total questions in template: 40
✅ Calculated coordinates for 40 questions from template

STEP 4/6: OMR Detection...
OMR Detection complete: 38/40 detected, 2 uncertain, 0 multiple marks

STEP 5/6: AI Verification skipped

STEP 6/6: Grading...
=== GRADING COMPLETE ===
Duration: 2.34s
Score: 35/40 (87.5%)
```

### Frontend (Muvaffaqiyatli)

- Natijalar to'g'ri ko'rsatiladi
- Annotated image'da belgilar to'g'ri joyda
- Score to'g'ri hisoblanadi

## Qo'shimcha Test

### Test Different Images

Turli xil rasm'larni test qiling:

- Turli resolution'lar
- Turli lighting condition'lar
- Turli perspective angle'lar
- Turli print quality'lar

### Test Edge Cases

- Marker'lar qisman ko'ringan
- Marker'lar burilgan
- Marker'lar och rangda
- Marker'lar yo'q

## Xulosa

**Test workflow:**

1. ✅ Backend restart
2. ✅ Test script ishga tushirish
3. ✅ Output image'larni tekshirish
4. ✅ Log'ni o'qish
5. ✅ Frontend'da test qilish

**Agar muammo bo'lsa:**

1. Test script output'ini tekshiring
2. Threshold image'ni tekshiring
3. Print quality'ni tekshiring
4. Troubleshooting bo'limiga qarang

**Yordam kerak bo'lsa:**

1. Test script output'ini yuboring
2. Backend log'ni yuboring
3. Threshold image'ni yuboring
4. Original image'ni yuboring
