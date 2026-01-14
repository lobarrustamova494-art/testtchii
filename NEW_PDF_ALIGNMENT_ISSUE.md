# Yangi PDF Bilan Alignment Muammosi

## 🔍 Rasmdan Aniqlangan Xatolar

### Muammoli Savollar

**Chap ustun** (toq savollar): 1, 5, 7, 9, 11, 15, 17, 21, 27, 31

- Yashil kataklar doirachalardan **chap tomonda**

**O'ng ustun** (juft savollar): 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34

- Qizil/ko'k kataklar doirachalardan **chap tomonda**

**To'g'ri ishlayotgan**: Faqat 3, 13, 19, 23, 25, 29, 33, 35

### Pattern Tahlili

- **Barcha** kataklar doirachalardan chap tomonda
- Bu X koordinatasi **juda katta** ekanligini anglatadi
- Vertikal siljish ham bor (Y koordinatasi ham noto'g'ri)

## 🎯 Muammoning Sababi

### Ehtimol 1: QR Code O'qilmayapti ✅

Backend loglarida:

```
QR code reading will be disabled - using default layout
```

**Sabab**: `pyzbar` kutubxonasi Windows'da ishlamayapti

**Natija**: Default layout ishlatilmoqda (config'dan)

### Ehtimol 2: Rasm To'g'ri Scale Qilinmagan ✅

- Corner markers topilmagan
- Perspective correction ishlamagan
- Rasm default corners bilan ishlatilmoqda

### Ehtimol 3: Config Hali Eski Layout'da ❌

Config'da `USE_OLD_PDF_LAYOUT = False` qildik, lekin backend qayta ishga tushirilmagan bo'lishi mumkin.

## ✅ Yechim

### 1. Backend'ni Qayta Ishga Tushiring

```bash
cd backend
# Eski processni to'xtating
taskkill /F /PID <process_id>

# Yangi processni ishga tushiring
python main.py
```

### 2. Backend Loglarini Tekshiring

Qidiring:

```
✅ YAXSHI:
✅ Using NEW gridStartY=149mm

❌ XATO:
⚠️  Using OLD gridStartY=113mm
```

### 3. Test Qiling

1. Yangi PDF yarating (allaqachon qildingiz ✅)
2. Chop eting va to'ldiring
3. Yuqori sifatli skan qiling (300+ DPI)
4. Backend'ga yuklang

### 4. Agar Hali Ham Muammo Bo'lsa

#### A. Corner Markers Tekshirish

Backend loglarida qidiring:

```
Found 4 corner markers  # ✅ Yaxshi
Only X/4 corner markers found  # ❌ Muammo
```

Agar corner markers topilmasa:

- Skan sifatini oshiring
- Yorug'likni yaxshilang
- Burchaklarni kesib qo'ymang

#### B. Manual Calibration

Agar corner markers hech qachon topilmasa, manual calibration qo'shish mumkin:

```python
# backend/config.py
MANUAL_CALIBRATION = True
CALIBRATION_POINTS = [
    {'x': 100, 'y': 100},  # Top-left
    {'x': 1140, 'y': 100},  # Top-right
    {'x': 100, 'y': 1654},  # Bottom-left
    {'x': 1140, 'y': 1654}  # Bottom-right
]
```

## 🔧 Qo'shimcha Tuzatishlar

### 1. Bubble Radius Tekshirish

Ehtimol bubble radius juda katta:

```python
# backend/utils/coordinate_mapper.py
bubble_radius_mm = 2.5  # Tekshiring

# backend/services/image_annotator.py
PADDING = 3  # Kamaytirishni sinab ko'ring (2 yoki 1)
```

### 2. Image Processing Yaxshilash

```python
# backend/services/image_processor.py
# Perspective correction'ni yaxshilash
# Corner marker detection'ni yaxshilash
```

### 3. Coordinate Mapper Debug

```python
# backend/utils/coordinate_mapper.py
# Har bir savol uchun koordinatalarni log qilish
logger.debug(f"Q{q_num}: bubble_x={bubble_x_px:.1f}px, bubble_y={bubble_y_px:.1f}px")
```

## 📊 Kutilayotgan Natija

To'g'ri sozlamalar bilan:

- ✅ Barcha kataklar doirachalar ustida
- ✅ Chap va o'ng ustunlar to'g'ri
- ✅ Vertikal siljish yo'q
- ✅ Barcha savollar to'g'ri

## 🐛 Debug Qadamlari

### 1. Backend Loglarini To'liq Ko'ring

```bash
cd backend
python main.py
# Loglarni diqqat bilan o'qing
```

### 2. Test Rasmi Bilan Sinab Ko'ring

```bash
cd backend
python diagnose_alignment.py <image_path> <exam_structure.json>
# debug_alignment.jpg yaratiladi
```

### 3. Koordinatalarni Tekshiring

```bash
cd backend
python test_x_coordinates.py
python verify_coordinates.py
```

## ✨ Xulosa

**Asosiy muammo**: Yangi PDF yaratilgan, lekin:

1. QR code o'qilmayapti (pyzbar ishlamayapti)
2. Default layout ishlatilmoqda
3. Ehtimol corner markers topilmayapti
4. Rasm to'g'ri scale qilinmayapti

**Yechim**:

1. ✅ Config'da `USE_OLD_PDF_LAYOUT = False` qildik
2. ✅ Backend'ni qayta ishga tushirdik
3. ⏳ Qayta test qilish kerak
4. ⏳ Agar muammo davom etsa, manual calibration qo'shish

**Keyingi qadam**: Qayta test qiling va natijani yuboring!
