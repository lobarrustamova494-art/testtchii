# Test Script Qo'llanmasi

## Qanday Ishlatish

### 1. Backend Papkasiga O'ting

```bash
cd backend
```

### 2. Test Script'ni Ishga Tushiring

```bash
python test_corner_detection.py path/to/image.jpg
```

Masalan:

```bash
python test_corner_detection.py test_image.jpg
python test_corner_detection.py ../uploads/exam_sheet_1.jpg
python test_corner_detection.py C:\Users\User\Desktop\scan.jpg
```

## Output

### 1. Terminal Log

#### ✅ Muvaffaqiyatli (4/4 corners)

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

✅ Found bottom-right marker: (2354, 3362)
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

#### ⚠️ Qisman Muvaffaqiyat (2/4 corners)

```
Testing corner detection on: exam_sheet_2.jpg
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

❌ Rejected bottom-left marker: score=0.42 (threshold=0.5), darkness=0.35, uniformity=0.48

❌ No candidate found for bottom-right

✅ Visualization saved: exam_sheet_2_corner_debug.jpg
✅ Threshold image saved: exam_sheet_2_threshold.jpg

============================================================
SUMMARY:
  Corners found: 2/4
  ⚠️  Corner detection failed!

TROUBLESHOOTING:
  1. Check threshold image - are corner markers visible?
  2. Check if markers are within yellow search regions
  3. Ensure markers are dark enough (black)
  4. Ensure markers are square-shaped
============================================================
```

### 2. Output Files

#### A. `image_corner_debug.jpg`

Bu fayl quyidagilarni ko'rsatadi:

**Yashil doiralar** = Topilgan corner marker'lar

- Katta yashil doira = Marker pozitsiyasi
- Kichik yashil nuqta = Marker markazi
- Yashil matn = Corner nomi va score

**Sariq to'rtburchaklar** = Search region'lar

- Top-left region (chap yuqori)
- Top-right region (o'ng yuqori)
- Bottom-left region (chap pastki)
- Bottom-right region (o'ng pastki)

**Qanday tahlil qilish:**

- ✅ Yashil doiralar to'g'ri joyda bo'lishi kerak (burchaklarda)
- ✅ Yashil doiralar sariq to'rtburchak ichida bo'lishi kerak
- ✅ 4 ta yashil doira bo'lishi kerak
- ❌ Agar yashil doira yo'q bo'lsa, corner topilmagan
- ❌ Agar yashil doira noto'g'ri joyda bo'lsa, noto'g'ri obyekt topilgan

#### B. `image_threshold.jpg`

Bu fayl binary threshold image:

**Oq rang** = Qora obyektlar (threshold'dan qora)
**Qora rang** = Och obyektlar (threshold'dan och)

**Qanday tahlil qilish:**

- ✅ Corner marker'lar oq rangda ko'rinishi kerak
- ✅ Corner marker'lar to'rtburchak shaklda bo'lishi kerak
- ✅ Corner marker'lar burchaklarda bo'lishi kerak
- ❌ Agar marker ko'rinmasa, juda och rangda
- ❌ Agar marker noaniq bo'lsa, print quality yomon

## Natijalarni Tahlil Qilish

### ✅ Muvaffaqiyatli (4/4)

**Terminal:**

```
✅ All corners detected successfully!
```

**corner_debug.jpg:**

- 4 ta yashil doira
- Barchasi to'g'ri joyda (burchaklarda)
- Barchasi sariq to'rtburchak ichida

**threshold.jpg:**

- 4 ta oq to'rtburchak
- Barchasi burchaklarda
- Aniq va to'rtburchak shaklda

**Xulosa:** Sistema to'g'ri ishlaydi! Frontend'da test qilishingiz mumkin.

### ⚠️ Qisman (2-3/4)

**Terminal:**

```
⚠️  Corner detection failed!
❌ Rejected bottom-left marker: score=0.42, darkness=0.35
```

**corner_debug.jpg:**

- 2-3 ta yashil doira
- Ba'zi burchaklarda yashil doira yo'q

**threshold.jpg:**

- Ba'zi marker'lar ko'rinmaydi yoki noaniq

**Xulosa:** Print quality yomon yoki marker'lar och rangda. Qayta print qiling.

### ❌ Muvaffaqiyatsiz (0-1/4)

**Terminal:**

```
❌ No candidate found for top-left
❌ No candidate found for top-right
```

**corner_debug.jpg:**

- Yashil doira yo'q yoki juda kam

**threshold.jpg:**

- Marker'lar ko'rinmaydi

**Xulosa:** Marker'lar umuman yo'q yoki juda och rangda. PDF'ni tekshiring va qayta print qiling.

## Troubleshooting

### Muammo: Darkness too low

```
❌ Rejected top-left marker: darkness=0.35
```

**Sabab:** Marker juda och rangda (60% dan kam qora)

**Yechim:**

1. Qayta print qiling (qora rangda)
2. Printer settings'ni tekshiring (toner/ink level)
3. Print quality'ni "High" ga o'zgartiring

### Muammo: Uniformity too low

```
❌ Rejected top-right marker: uniformity=0.35
```

**Sabab:** Marker bir xil qoralikda emas (gradient yoki partial fill)

**Yechim:**

1. Print quality yomon
2. Qayta print qiling
3. Printer'ni tozalang

### Muammo: No candidate found

```
❌ No candidate found for bottom-left
```

**Sabab:** Marker search region'da emas yoki umuman yo'q

**Yechim:**

1. PDF'ni tekshiring (marker'lar bor mi?)
2. Scan quality'ni tekshiring
3. Scan to'liq bo'lishi kerak (burchaklar kesilmagan)

### Muammo: Score too low

```
❌ Rejected bottom-right marker: score=0.42 (threshold=0.5)
```

**Sabab:** Marker bir nechta parametrda yomon

**Yechim:**

1. Threshold image'ni tekshiring
2. Marker to'g'ri shaklda va rangdami?
3. Print quality'ni yaxshilang

## Qo'shimcha Maslahatlar

### 1. Print Quality

- **Toner/Ink:** To'liq bo'lishi kerak
- **Quality:** "High" yoki "Best" setting
- **Paper:** Oq, silliq qog'oz
- **Marker:** To'liq qora, bir xil qoralikda

### 2. Scan Quality

- **Resolution:** Kamida 300 DPI
- **Color:** Grayscale yoki Color
- **Brightness:** O'rtacha (juda yorug' yoki qorong'i emas)
- **Contrast:** O'rtacha

### 3. Image Quality

- **Format:** JPEG yoki PNG
- **Size:** Kamida 1000x1400 pixels
- **Clarity:** Aniq, blur emas
- **Alignment:** To'g'ri, burilmagan

## Xulosa

**Test script ishlatish:**

1. ✅ `cd backend`
2. ✅ `python test_corner_detection.py image.jpg`
3. ✅ Terminal log'ni o'qing
4. ✅ `image_corner_debug.jpg` ni oching
5. ✅ `image_threshold.jpg` ni oching
6. ✅ Natijalarni tahlil qiling

**Agar 4/4 corners topilsa:**

- ✅ Sistema to'g'ri ishlaydi
- ✅ Frontend'da test qiling

**Agar corner topilmasa:**

- ⚠️ Troubleshooting bo'limiga qarang
- ⚠️ Print quality'ni yaxshilang
- ⚠️ Qayta test qiling

**Yordam kerak bo'lsa:**

- 📸 `corner_debug.jpg` ni yuboring
- 📸 `threshold.jpg` ni yuboring
- 📋 Terminal log'ni yuboring
