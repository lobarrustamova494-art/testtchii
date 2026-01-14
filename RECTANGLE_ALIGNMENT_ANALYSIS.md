# To'rtburchak Alignment Tahlili

## 📊 Rasmdan Aniqlangan Xatolar

### 1. Bo'sh Yashil To'rtburchaklar - Chap Ustun

**Savollar**: 1, 11, 21, 31

**Pattern**: Har 10-savol oralig'ida

**Pozitsiya**: Doirachadan chap tomonda, bo'sh joyda

### 2. Bo'sh Yashil To'rtburchaklar - O'ng Ustun

**Savollar**: 10, 20, 30

**Pattern**: Har 10-savol oralig'ida

**Pozitsiya**: Doirachadan o'ng tomonda, bo'sh joyda

### 3. Vertikal Siljish

**Muammo**: To'rtburchaklar doirachalardan biroz pastroqda

**Qayerda**: Barcha qatorlarda, lekin pastki qatorlarda ko'proq

### 4. To'g'ri Ishlayotgan Savollar

**Savollar**: 2-9, 12-19, 22-29, 32-35

**Xulosa**: Ko'pchilik savollar to'g'ri ishlayapti!

## 🔍 Muammoning Sababi

### Gipoteza 1: Eski PDF Ishlatilgan ✅ (Eng Ehtimol)

Agar test qilingan PDF **eski versiya** bilan yaratilgan bo'lsa:

- QR code'da eski layout: `gridStartY = 113mm`
- Backend kutadi: `gridStartY = 149mm`
- Farq: 36mm = ~213px siljish!

**Dalil**: Bo'sh to'rtburchaklar pattern'i juda aniq (1, 10, 11, 20, 21, 30, 31)

### Gipoteza 2: Corner Markers Topilmagan ✅

Agar 4ta burchak marker topilmasa:

- Perspective correction ishlamaydi
- Default corners ishlatiladi
- Rasm to'g'ri scale qilinmaydi

**Tekshirish**: Backend loglarida "WARNING: Using default layout (no QR code)"

### Gipoteza 3: Section Boundary Muammosi ❌

Pattern har 10-savolda, lekin section boundary'lar boshqacha bo'lishi kerak.

**Xulosa**: Bu section muammosi emas.

## 🎯 Yechim

### 1. YANGI PDF YARATING! (Eng Muhim)

```bash
# Frontend'da:
1. Imtihon yarating yoki mavjudini oching
2. "PDF Yuklab Olish" tugmasini bosing
3. Yangi PDF saqlanadi
```

**MUHIM**: Eski PDF'lar noto'g'ri layout qiymatlari bilan yaratilgan!

### 2. Backend Loglarini Tekshiring

Backend ishga tushganda qidiring:

```
✅ YAXSHI:
INFO - Using layout from QR code
INFO - Layout: gridStartY=149mm

⚠️ OGOHLANTIRISH:
WARNING - Using default layout (no QR code)

❌ XATO:
WARNING - ⚠️  QR code has OLD gridStartY value: 113mm
```

### 3. Yuqori Sifatli Skan

- **DPI**: 300 yoki yuqori
- **Rang**: Rangli yoki grayscale
- **Yo'nalish**: Portrait (tik)
- **Sifat**: Blur bo'lmasin

### 4. To'g'ri Chop Etish

- **Scale**: 100% (kichraytirmasdan!)
- **Qog'oz**: A4 (210mm x 297mm)
- **Sifat**: Yuqori sifat

## 📝 Test Checklist

Qayta test qilishdan oldin:

- [ ] Yangi PDF yaratdingizmi?
- [ ] PDF to'g'ri chop etildimi? (100% scale)
- [ ] Yuqori sifatli skan qildingizmi? (300+ DPI)
- [ ] Backend ishga tushganmi?
- [ ] Backend loglarini tekshirdingizmi?

## 🔧 Qo'shimcha Tuzatishlar

Agar yangi PDF bilan ham muammo bo'lsa:

### 1. Bubble Radius Tekshirish

```python
# backend/utils/coordinate_mapper.py
bubble_radius_mm = 2.5  # PDF'da ham 2.5mm bo'lishi kerak
```

### 2. Grid Start Y Tekshirish

```python
# backend/utils/coordinate_mapper.py
grid_start_y_mm = 149  # PDF'da ham 149mm bo'lishi kerak
```

### 3. Row Height Tekshirish

```python
# backend/utils/coordinate_mapper.py
row_height_mm = 5.5  # PDF'da ham 5.5mm bo'lishi kerak
```

## 💡 Kutilayotgan Natija

Yangi PDF bilan:

- ✅ Barcha yashil to'rtburchaklar to'g'ri javoblar ustida
- ✅ Ko'k to'rtburchaklar student to'g'ri javoblari ustida
- ✅ Qizil to'rtburchaklar student xato javoblari ustida
- ✅ Hech qanday bo'sh to'rtburchaklar yo'q
- ✅ Vertikal siljish yo'q

## 🐛 Agar Muammo Davom Etsa

Quyidagilarni yuboring:

1. Backend loglari (terminal output)
2. Test rasmi (skan qilingan varaq)
3. PDF fayli (yangi yaratilgan)
4. Exam structure JSON

Men batafsil tahlil qilaman va aniq yechim topaman.
