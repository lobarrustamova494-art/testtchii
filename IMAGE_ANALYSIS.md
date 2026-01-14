# Rasm Tahlili - Aniqlangan Xatolar

## 📊 Kuzatilgan Muammolar

### 1. Vertikal Siljish (Y koordinatasi)

- To'rtburchaklar doirachalardan **1-2mm pastroqda**
- Barcha qatorlarda bir xil siljish
- Ehtimol `bubble_y_mm = question_y_mm + 2` da muammo

### 2. Bo'sh Yashil To'rtburchaklar (Chap)

Quyidagi savollar uchun yashil to'rtburchak doirachadan **chap tomonda**:

- 1, 9, 11, 21, 23, 31, 33, 35

**Pattern**: Toq raqamli savollar (1, 3, 5, 7, 9, 11, ...)

**Sabab**: Bu **1-ustundagi savollar** (col = 0)

- Ehtimol X koordinatasi noto'g'ri
- Yoki to'rtburchak juda katta

### 3. Bo'sh Yashil To'rtburchaklar (O'ng)

Quyidagi savollar uchun yashil to'rtburchak doirachadan **o'ng tomonda**:

- 10, 20, 22, 32

**Pattern**: Juft raqamli savollar, lekin hammasi emas

**Sabab**: Bu **2-ustundagi savollar** (col = 1)

- X koordinatasi noto'g'ri
- Yoki to'rtburchak juda katta

### 4. To'g'ri Ishlayotgan Savollar

Ba'zi savollar to'g'ri:

- 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 17, 18, 19, 24, 25, 26, 27, 28, 29, 30, 34

**Pattern**: Ko'pchilik savollar to'g'ri ishlayapti

## 🔍 Gipoteza

### Gipoteza 1: X Koordinatasi Noto'g'ri

```python
# Hozirgi kod:
question_x_mm = grid_start_x_mm + (col * question_spacing_mm)
bubble_x_mm = question_x_mm + first_bubble_offset_mm + (v_idx * bubble_spacing_mm)

# Ehtimol:
# - grid_start_x_mm noto'g'ri
# - question_spacing_mm noto'g'ri
# - first_bubble_offset_mm noto'g'ri
```

### Gipoteza 2: To'rtburchak Juda Katta

```python
# Hozirgi:
PADDING = 5
THICKNESS = 3

# Agar to'rtburchak juda katta bo'lsa:
# - Qo'shni doirachalarni ham qamrab oladi
# - Bo'sh joyda ko'rinadi
```

### Gipoteza 3: Variant Index Noto'g'ri

```python
# Ehtimol to'g'ri javob variant index'i noto'g'ri?
# Masalan: to'g'ri javob "E" lekin biz "A" ni belgilayapmiz?
```

## 📝 Keyingi Qadamlar

1. ✅ To'rtburchaklarni kichraytirdik (PADDING: 5→3, THICKNESS: 3→2)
2. ⏳ X koordinatalarini tekshirish kerak
3. ⏳ To'g'ri javoblar ro'yxatini tekshirish kerak
4. ⏳ Variant mapping'ni tekshirish kerak

## 🎯 Test Uchun Savol

**Savol 1:**

- To'g'ri javob: Qaysi variant? (A/B/C/D/E)
- Student javobi: Qaysi variant?
- Rasmda: Qayerda yashil to'rtburchak?

Agar buni bilsak, muammoni aniqroq topamiz.
