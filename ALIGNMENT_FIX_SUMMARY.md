# Alignment Fix Summary

## ✅ Qilingan Ishlar

### 1. To'rtburchak O'lchamini Kichraytirish

- **PADDING**: 5px → 3px
- **THICKNESS**: 3px → 2px
- Natija: To'rtburchaklar endi kichikroq va aniqroq

### 2. Koordinatalarni Yaxshilash

- Rounding qo'shildi: `int(round(x))` - eng yaqin pixelga yaxlitlash
- Bu sub-pixel misalignment muammolarini hal qiladi

### 3. Diagnostic Tools Yaratildi

- `backend/diagnose_alignment.py` - rasm va koordinatalarni tahlil qilish
- `backend/debug_annotation.py` - annotatsiya muammolarini debug qilish

### 4. QR Code Tekshiruvi

- Eski PDF'larni aniqlash uchun warning qo'shildi
- Agar `gridStartY != 149mm` bo'lsa, ogohlantirish beradi

## 🔍 Aniqlangan Muammolar

### Asosiy Muammo: Eski PDF Ishlatilgan Bo'lishi Mumkin

Agar siz test qilayotgan PDF **eski versiya** bilan yaratilgan bo'lsa:

- QR code'da `gridStartY = 113mm` (noto'g'ri)
- Yangi backend `gridStartY = 149mm` kutadi
- Bu 36mm farq = ~213px siljish!

**Yechim**: Yangi PDF yarating!

### Boshqa Ehtimoliy Muammolar

1. **Corner Markers Topilmagan**

   - Agar 4ta burchak marker topilmasa, perspective correction ishlamaydi
   - Rasm to'g'ri scale qilinmaydi
   - Natija: koordinatalar mos kelmaydi

2. **Rasm Sifati Past**

   - Blur, past contrast, yomon skan
   - Bubble detection noto'g'ri ishlaydi

3. **Printer/Scanner Distortion**
   - Printer yoki scanner rasm o'lchamini ozgina o'zgartirishi mumkin
   - A4 (210x297mm) aniq bo'lmasligi mumkin

## 📋 Keyingi Qadamlar

### 1. YANGI PDF YARATING! (Eng Muhim)

```bash
# Frontend'da:
# 1. Imtihon yarating
# 2. PDF yuklab oling
# 3. Chop eting
# 4. To'ldiring
# 5. Skan qiling
# 6. Backend'ga yuklang
```

**MUHIM**: Eski PDF'lar ishlamaydi! Faqat yangi PDF'lar to'g'ri koordinatalarga ega.

### 2. Diagnostic Tool Ishlatish

Agar muammo davom etsa:

```bash
cd backend

# Rasm va koordinatalarni tahlil qilish
python diagnose_alignment.py <image_path> <exam_structure.json>

# Bu yaratadi: debug_alignment.jpg
# Rasmda ko'ring: to'rtburchaklar bubble'larga mos keladimi?
```

### 3. Backend Loglarini Tekshirish

Backend ishga tushganda:

```
INFO: Using layout from QR code  # ✅ Yaxshi
# yoki
WARNING: Using default layout (no QR code)  # ⚠️ QR code o'qilmadi

WARNING: ⚠️  QR code has OLD gridStartY value: 113mm  # ❌ Eski PDF!
```

### 4. Test Qilish

1. **Yangi PDF yarating** (eng muhim!)
2. PDF'ni chop eting
3. Qo'lda to'ldiring (aniq, to'liq)
4. Yuqori sifatli skan qiling (300 DPI yoki yuqori)
5. Backend'ga yuklang
6. Natijani tekshiring

## 🎯 Kutilayotgan Natija

Agar hammasi to'g'ri bo'lsa:

- ✅ Yashil to'rtburchaklar to'g'ri javoblar ustida
- ✅ Ko'k to'rtburchaklar student to'g'ri javoblari ustida
- ✅ Qizil to'rtburchaklar student xato javoblari ustida
- ✅ Hech qanday "bo'sh" to'rtburchaklar yo'q

## 🐛 Agar Hali Ham Muammo Bo'lsa

1. Backend loglarini yuboring
2. Test rasmini yuboring
3. `debug_alignment.jpg` rasmini yuboring
4. Exam structure JSON'ni yuboring

Men aniqroq tahlil qilaman va muammoni topaman.

## 📝 Texnik Tafsilotlar

### Koordinata Hisoblash

```python
# PDF'da:
currentY = 149mm  # Grid start
currentY += 8mm   # Topic header
currentY += 5mm   # Section header
# Har bir qator uchun:
bubbleY = currentY + 2mm
currentY += 5.5mm

# Backend'da (bir xil):
current_y_mm = 149
current_y_mm += 8
current_y_mm += 5
question_y_mm = current_y_mm + (row * 5.5)
bubble_y_mm = question_y_mm + 2
```

### Bubble Pozitsiyalari

```python
# X koordinatasi:
question_x_mm = 25 + (col * 90)  # col=0 (chap) yoki col=1 (o'ng)
bubble_x_mm = question_x_mm + 8 + (variant_index * 8)

# Y koordinatasi:
bubble_y_mm = question_y_mm + 2

# Pixels'ga o'girish:
bubble_x_px = bubble_x_mm * px_per_mm_x
bubble_y_px = bubble_y_mm * px_per_mm_y
```

### Annotatsiya

```python
# To'rtburchak:
x1 = bubble_x - radius - padding
y1 = bubble_y - radius - padding
x2 = bubble_x + radius + padding
y2 = bubble_y + radius + padding

# Hozirgi qiymatlar:
radius = 2.5mm * px_per_mm
padding = 3px
thickness = 2px
```

## ✨ Xulosa

Asosiy muammo ehtimol **eski PDF ishlatilganligi**. Yangi PDF yarating va qayta test qiling!

Agar yangi PDF bilan ham muammo bo'lsa, diagnostic tool'larni ishlating va natijalarni yuboring.
