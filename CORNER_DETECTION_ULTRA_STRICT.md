# Corner Detection - Ultra Strict Version

## Muammo

Oldingi versiyada corner detection ba'zan noto'g'ri obyektlarni (masalan, ko'k kvadrat) corner marker deb topardi. Bu perspective correction'ni buzardi va koordinatalar noto'g'ri bo'lardi.

## Yechim

### 1. Ultra Strict Corner Detection

**Yangi parametrlar:**

```python
# Threshold - faqat juda qora obyektlar
threshold = 80  # (oldin 100 edi)

# Size range - ancha qat'iy
min_size = expected_size * 0.5   # 50% (oldin 30%)
max_size = expected_size * 2.0   # 200% (oldin 300%)

# Aspect ratio - faqat kvadratga yaqin
0.7 < aspect_ratio < 1.43  # ±45° (oldin 0.5-2.0)

# Search region - faqat burchaklarda
corner_region = 25mm  # Faqat 25mm ichida qidirish
```

**Yangi tekshiruvlar:**

1. **Darkness Check** - Kamida 60% qora bo'lishi kerak
2. **Uniformity Check** - Bir xil qoralikda bo'lishi kerak (50%+)
3. **Strict Boundaries** - Faqat burchak regionida
4. **Distance Check** - Expected center'dan 1.5x radius ichida

### 2. Weighted Scoring System

```python
score = (
    aspect_score * 0.10 +      # Kvadrat shaklmi?
    size_score * 0.15 +        # To'g'ri o'lchammi?
    dist_score * 0.20 +        # To'g'ri joyda?
    darkness_score * 0.35 +    # Qora rangmi? (ENG MUHIM!)
    uniformity_score * 0.20    # Bir xil qoralikdami?
)

# Acceptance threshold
if score > 0.5:  # 50% dan yuqori bo'lishi kerak
    accept_marker()
```

### 3. Detailed Logging

Har bir corner uchun:

- Score (umumiy ball)
- Darkness (qoralik)
- Uniformity (bir xillik)
- Size (o'lcham)
- Aspect ratio (kvadratlik)

## Test Qilish

### 1. Test Script

```bash
cd backend
python test_corner_detection.py path/to/image.jpg
```

Bu script:

- Corner'larni topadi
- Vizualizatsiya qiladi (yashil doiralar)
- Search region'larni ko'rsatadi (sariq to'rtburchaklar)
- Threshold image yaratadi
- Detailed log chiqaradi

### 2. Output Files

- `image_corner_debug.jpg` - Detected corners (yashil)
- `image_threshold.jpg` - Binary threshold image

### 3. Log Output

```
✅ Found top-left marker:
   score=0.85, darkness=0.92, uniformity=0.78,
   size=56.3px, aspect=0.98

✅ Found top-right marker:
   score=0.82, darkness=0.88, uniformity=0.75,
   size=58.1px, aspect=1.02

❌ Rejected bottom-left marker:
   score=0.42 (threshold=0.5), darkness=0.35, uniformity=0.48
```

## Troubleshooting

### Agar corner topilmasa:

1. **Threshold image'ni tekshiring**

   - Corner marker'lar oq rangda ko'rinishi kerak
   - Agar ko'rinmasa, marker juda och rangda

2. **Search region'ni tekshiring**

   - Marker sariq to'rtburchak ichida bo'lishi kerak
   - Agar tashqarida bo'lsa, PDF margin noto'g'ri

3. **Darkness'ni tekshiring**

   - Marker kamida 60% qora bo'lishi kerak
   - Agar och rangda bo'lsa, qayta print qiling

4. **Uniformity'ni tekshiring**
   - Marker bir xil qoralikda bo'lishi kerak
   - Agar gradient bo'lsa, print quality yomon

## Priority System

Backend 3 xil coordinate system ishlatadi:

```python
# Priority 1: Template-based (BEST!)
if coordinate_template and corners:
    use TemplateCoordinateMapper
    # Imtihon yaratilganda saqlangan template

# Priority 2: Corner-based
elif corners:
    use RelativeCoordinateMapper
    # Corner'lardan nisbiy koordinatalar

# Priority 3: Fallback
else:
    use CoordinateMapper
    # Eski tizim (kam aniq)
```

## Expected Behavior

### ✅ To'g'ri ishlash:

```
STEP 1/6: Image Processing...
✅ Found top-left marker: score=0.85, darkness=0.92
✅ Found top-right marker: score=0.82, darkness=0.88
✅ Found bottom-left marker: score=0.79, darkness=0.85
✅ Found bottom-right marker: score=0.81, darkness=0.87
✅ All 4 corner markers detected successfully

STEP 3/6: Coordinate Calculation...
✅ Using TEMPLATE-BASED coordinate system (EvalBee style)
✅ Calculated coordinates for 40 questions from template
```

### ⚠️ Corner topilmasa:

```
STEP 1/6: Image Processing...
✅ Found top-left marker: score=0.85, darkness=0.92
✅ Found top-right marker: score=0.82, darkness=0.88
❌ Rejected bottom-left marker: score=0.42, darkness=0.35
❌ No candidate found for bottom-right
⚠️  Only 2/4 corner markers found
⚠️  Corner markers not found, using fallback system

STEP 3/6: Coordinate Calculation...
⚠️  Corner markers not found, using fallback system
```

## Yangi Xususiyatlar

### 1. Uniformity Check

Marker bir xil qoralikda bo'lishi kerak. Bu gradient yoki partial fill'ni rad etadi.

```python
std_intensity = np.std(roi)
uniformity_score = 1.0 - min(std_intensity / 128.0, 1.0)

if uniformity_score < 0.5:  # 50% dan kam uniform
    reject_marker()
```

### 2. Strict Boundaries

Marker faqat burchak regionida bo'lishi kerak. Bu sahifa o'rtasidagi obyektlarni rad etadi.

```python
corner_region_mm = 25  # Faqat 25mm ichida

if not (region['x_min'] <= cx <= region['x_max'] and
        region['y_min'] <= cy <= region['y_max']):
    reject_marker()
```

### 3. Darkness Priority

Qoralik eng muhim parametr. Marker kamida 60% qora bo'lishi kerak.

```python
darkness_score = (255 - avg_intensity) / 255.0

if darkness_score < 0.6:  # 60% dan kam qora
    reject_marker()
```

## Xulosa

**Yangi ultra strict corner detection:**

1. ✅ Faqat juda qora obyektlarni topadi (60%+)
2. ✅ Faqat kvadrat shakllarni topadi (±45°)
3. ✅ Faqat burchak regionida qidiradi (25mm)
4. ✅ Uniformity tekshiradi (50%+)
5. ✅ Detailed logging (debug uchun)
6. ✅ Test script (vizualizatsiya)

**Foydalanish:**

1. Backend'ni restart qiling: `python main.py`
2. Test script bilan tekshiring: `python test_corner_detection.py image.jpg`
3. Log'larni o'qing va debug qiling
4. Agar corner topilmasa, troubleshooting bo'limiga qarang

**Agar muammo davom etsa:**

1. Test script'ni ishga tushiring
2. Output image'larni tekshiring
3. Log'larni o'qing
4. Marker'lar to'g'ri print qilinganini tekshiring
