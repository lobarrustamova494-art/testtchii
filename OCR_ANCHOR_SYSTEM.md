# OCR-Based Anchor Detection System

## Umumiy Ma'lumot

**OCR Anchor System** - bu savol raqamlarini OCR (Optical Character Recognition) bilan topib, bubble pozitsiyalarini nisbiy hisoblash tizimi.

## Muammo

Hozirgi tizimda:

- ❌ Koordinatalar **fixed** (qat'iy)
- ❌ Perspective distortion'ga sezgir
- ❌ Skanerlash sifatiga bog'liq
- ❌ Ba'zi holatlarda noto'g'ri

## Yechim: OCR Anchor System

### Asosiy G'oya

1. **Savol raqamlarini topish** - OCR bilan (1., 2., 3., ...)
2. **Nisbiy pozitsiya** - Raqamdan bubble'larga masofa
3. **Har savol mustaqil** - O'z anchor'iga ega

### Algoritm

```
1. OCR Detection
   ↓
   Savol raqamlarini topish (1., 2., 3., ...)
   ↓
2. Anchor Positioning
   ↓
   Har raqamning (x, y) koordinatasi
   ↓
3. Bubble Calculation
   ↓
   anchor.x + offset = Bubble A
   anchor.x + offset + spacing = Bubble B
   ...
```

## Implementatsiya

### 1. OCR Detection

```python
def detect_question_numbers(image, expected_count):
    # Tesseract OCR
    ocr_data = pytesseract.image_to_data(image, config='--psm 6')

    # Parse results
    for text in ocr_data:
        if re.match(r'^\d+\.$', text):  # "1.", "2.", etc.
            # Found question number!
            anchors.append({'number': int(text[:-1]), 'x': x, 'y': y})

    return anchors
```

### 2. Bubble Calculation

```python
def calculate_bubble_positions(anchor):
    bubbles = []

    for v_idx, variant in enumerate(['A', 'B', 'C', 'D', 'E']):
        # Nisbiy pozitsiya
        bubble_x = anchor['x'] + first_bubble_offset + (v_idx * bubble_spacing)
        bubble_y = anchor['y']  # Same row

        bubbles.append({'variant': variant, 'x': bubble_x, 'y': bubble_y})

    return bubbles
```

## Afzalliklari

### ✅ 1. Perspective'dan Mustaqil

Agar rasm qiyshiq bo'lsa ham:

- Har savol o'z raqamiga ega
- Nisbiy masofa saqlanadi
- Koordinatalar to'g'ri

### ✅ 2. Skanerlash Sifatidan Mustaqil

Turli xil skanerlash:

- Telefon kamerasi
- Professional skaner
- Turli xil yoritilish

Hammasi ishlaydi, chunki OCR raqamlarni topadi.

### ✅ 3. Aniq Koordinatalar

Matematik jihatdan aniq:

```
bubble_x = anchor_x + offset + (variant_index * spacing)
```

### ✅ 4. Fallback System

Agar OCR ishlamasa:

- Corner-based system
- Template-based system
- Coordinate-based system

## Texnik Tafsilotlar

### OCR Konfiguratsiya

```python
ocr_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.'
```

**Parametrlar:**

- `--psm 6`: Page segmentation mode (uniform block of text)
- `--oem 3`: OCR Engine Mode (default, based on what is available)
- `-c tessedit_char_whitelist=0123456789.`: Faqat raqamlar va nuqta

### Image Preprocessing

```python
# 1. Binarization
_, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# 2. Morphological operations
kernel = np.ones((2, 2), np.uint8)
cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

# 3. OCR
ocr_data = pytesseract.image_to_data(cleaned, config=ocr_config)
```

### Layout Parametrlari

```python
bubble_radius_mm = 2.5
bubble_spacing_mm = 8
first_bubble_offset_mm = 8  # Raqamdan birinchi bubble'gacha
```

## Foydalanish

### 1. O'rnatish

```bash
# Python package
pip install pytesseract

# Tesseract OCR engine (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install and add to PATH
```

### 2. Test

```bash
cd backend
python test_ocr_anchor.py
```

### 3. Backend Integration

OCR anchor system avtomatik ishlatiladi:

```python
# Priority 0: OCR-based anchor system (MOST ACCURATE!)
coordinates = ocr_anchor_detector.detect_all_with_anchors(image, exam_data)

if coordinates:
    # Use OCR coordinates
else:
    # Fallback to corner-based or template-based
```

## Taqqoslash

### OLD System (Coordinate-based):

```
❌ Fixed coordinates
❌ Perspective-sensitive
❌ Scan quality dependent
✅ Fast
```

### NEW System (OCR Anchor):

```
✅ Dynamic coordinates
✅ Perspective-independent
✅ Scan quality independent
✅ Accurate
❌ Slightly slower (OCR overhead)
```

## Debug

### Anchor Visualization

```python
detector.visualize_anchors(image, anchors, 'anchors_debug.jpg')
```

Bu rasm:

- Qizil nuqta: Anchor pozitsiyasi
- Yashil matn: Savol raqami
- Ko'k to'rtburchak: OCR bounding box

### Log'lar

```
OCR detected 38/40 question numbers
Q1: (147, 968), conf=95%
Q2: (623, 968), conf=92%
...
✅ OCR-based coordinates calculated for 38 questions
```

## Xulosa

OCR Anchor System:

1. ✅ **Savol raqamlarini topadi** - Tesseract OCR
2. ✅ **Nisbiy pozitsiya** - Anchor'dan bubble'larga
3. ✅ **Perspective'dan mustaqil** - Har savol mustaqil
4. ✅ **Aniq koordinatalar** - Matematik hisoblash
5. ✅ **Fallback system** - Agar OCR ishlamasa

**Tavsiya:** OCR anchor system'ni birinchi tanlov sifatida ishlatish!

## Keyingi Qadamlar

1. **Tesseract o'rnatish** - Windows/Linux/Mac
2. **Test qilish** - `test_ocr_anchor.py`
3. **Backend'ni ishga tushirish** - Avtomatik ishlatiladi
4. **Natijalarni ko'rish** - Log'larda "OCR-based" yozuvi

**Tizim tayyor!** 🚀
