# Annotation Coordinate Shift - ASOSIY MUAMMO TOPILDI VA TUZATILDI!

## 🔍 Muammo Tahlili

### Rasmda Ko'ringan Muammo

Annotation kvadratlari bubble'larning **pastroqda** turibdi. Bu barcha savollarda bir xil miqdorda siljish.

### Sabab

**CRITICAL BUG:** Perspective correction'dan keyin corner koordinatalari **noto'g'ri** hisoblangan!

#### Nima Bo'lgan?

1. **Image Processor** perspective correction qiladi
2. Perspective correction sahifani **to'g'ri to'rtburchak**ka keltiradi
3. Bu degani, sahifa burchaklari endi **(0, 0), (width, 0), (0, height), (width, height)** da
4. Lekin kod corner'larni **marker markazlarida** deb o'ylagan!

#### Noto'g'ri Kod:

```python
# NOTO'G'RI - Marker markazlarini hisoblayapti
transformed_corners = [
    {
        'x': (margin_mm + marker_size_mm/2) * px_per_mm_x,  # 12.5mm * scale
        'y': (margin_mm + marker_size_mm/2) * px_per_mm_y,  # 12.5mm * scale
        'name': 'top-left'
    },
    # ...
]
```

Bu degani:

- Top-left corner: (12.5mm, 12.5mm) → ~(148px, 148px) deb hisoblangan
- Lekin aslida: (0, 0) bo'lishi kerak!

#### Natija:

Barcha koordinatalar **12.5mm pastroqda va o'ngda** hisoblangan!

12.5mm = ~148 piksel (2480x3508 image'da)

Shuning uchun annotation'lar bubble'lardan **pastroqda** ko'rinmoqda!

## ✅ Yechim

### 1. Image Processor Tuzatildi

**Fayl:** `backend/services/image_processor.py`

**O'zgarish:**

```python
def _transform_corners_after_processing(...):
    """
    CRITICAL FIX: Perspective correction'dan keyin, corner'lar
    SAHIFA BURCHAKLARIDA, marker markazida EMAS!
    """
    transformed_corners = [
        {'x': 0.0, 'y': 0.0, 'name': 'top-left'},
        {'x': float(target_width), 'y': 0.0, 'name': 'top-right'},
        {'x': 0.0, 'y': float(target_height), 'name': 'bottom-left'},
        {'x': float(target_width), 'y': float(target_height), 'name': 'bottom-right'}
    ]
    return transformed_corners
```

### 2. Relative Coordinate Mapper Tuzatildi

**Fayl:** `backend/utils/relative_coordinate_mapper.py`

**O'zgarish 1:** Corner pozitsiyalari

```python
# TUZATILDI - Sahifa burchaklari
self.corner_center_mm = {
    'top-left': {'x': 0.0, 'y': 0.0},
    'top-right': {'x': 210.0, 'y': 0.0},
    'bottom-left': {'x': 0.0, 'y': 297.0},
    'bottom-right': {'x': 210.0, 'y': 297.0}
}

# TUZATILDI - To'liq sahifa o'lchami
self.width_mm = 210.0   # Eski: 185.0mm (noto'g'ri!)
self.height_mm = 297.0  # Eski: 272.0mm (noto'g'ri!)
```

**O'zgarish 2:** Relative koordinatalar hisoblash

```python
def mm_to_relative(self, x_mm: float, y_mm: float) -> tuple:
    """
    TUZATILDI: Corner'lar sahifa burchaklarida,
    shuning uchun to'g'ridan-to'g'ri normalize qilamiz
    """
    relative_x = x_mm / self.width_mm   # 210mm
    relative_y = y_mm / self.height_mm  # 297mm
    return (relative_x, relative_y)
```

## 📊 Natija

### Oldin (Noto'g'ri):

```
Corner reference: (12.5mm, 12.5mm) = (148px, 148px)
Page size: 185mm x 272mm

Bubble at (33mm, 151mm) in PDF:
  Relative: (33-12.5)/185 = 0.111, (151-12.5)/272 = 0.509
  Pixel: 148 + 0.111*2184 = 390px, 148 + 0.509*3212 = 1783px

NOTO'G'RI! 148px offset bor!
```

### Keyin (To'g'ri):

```
Corner reference: (0mm, 0mm) = (0px, 0px)
Page size: 210mm x 297mm

Bubble at (33mm, 151mm) in PDF:
  Relative: 33/210 = 0.157, 151/297 = 0.508
  Pixel: 0 + 0.157*2480 = 390px, 0 + 0.508*3508 = 1782px

TO'G'RI! Offset yo'q!
```

## 🧪 Test Qilish

### 1. Backend'ni Qayta Ishga Tushiring

```cmd
cd backend
python main.py
```

### 2. Frontend'da Varaq Yuklang

### 3. Backend Log'ni Kuzating

```
STEP 1/6: Image Processing...
✅ Image processed
   Corners found: 4/4

✅ Corner coordinates set to PAGE CORNERS (after perspective correction)
   top-left: (0.0, 0.0) px
   top-right: (2480.0, 0.0) px
   bottom-left: (0.0, 3508.0) px
   bottom-right: (2480.0, 3508.0) px

STEP 3/6: Coordinate Calculation...
✅ Using corner-based coordinate system (100% accurate)
  PDF corner distance: 210.0 x 297.0 mm
```

### 4. Annotated Image'ni Tekshiring

Endi annotation kvadratlari **aynan bubble'lar ustida** bo'lishi kerak!

## 📝 Texnik Tafsilotlar

### Perspective Correction Qanday Ishlaydi?

1. **Input:** Distorted image + 4 corner markers
2. **Process:**
   - Corner marker'larni topadi
   - Perspective transformation matrix hisoblaydi
   - Image'ni to'g'ri to'rtburchakka keltiradi
3. **Output:** Corrected image where corners are at (0,0), (w,0), (0,h), (w,h)

### Nima Uchun Bu Muhim?

Perspective correction **sahifa burchaklarini** (0,0) ga keltiradi, **marker markazlarini** emas!

Agar biz marker markazlarini (12.5mm, 12.5mm) deb hisoblasak:

- Barcha koordinatalar 12.5mm siljiydi
- Bu ~148 piksel (2480x3508 image'da)
- Annotation'lar noto'g'ri joyda chiziladi

### To'g'ri Yondashuv:

1. Perspective correction'dan keyin corner'lar = sahifa burchaklari
2. Sahifa burchaklari = (0, 0), (210mm, 0), (0, 297mm), (210mm, 297mm)
3. Barcha koordinatalarni sahifa burchaklaridan hisoblash
4. Marker'lar sahifa ichida (margin + size/2) joylashgan, lekin biz ularni reference sifatida ishlatmaymiz

## 🎯 Xulosa

**Muammo:** Annotation koordinatalari 12.5mm (~148px) siljigan edi

**Sabab:** Perspective correction'dan keyin corner'lar marker markazida deb o'ylangan

**Yechim:** Corner'larni sahifa burchaklarida deb hisoblash

**Natija:** Annotation'lar endi aynan bubble'lar ustida!

---

**Test qiling va natijani yuboring!** 🎉
