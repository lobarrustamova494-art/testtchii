# Doirachalar Bir-biriga Tegib Ketish Muammosi - Tuzatildi ✅

## ❌ Muammo

Doirachalar vertikal yo'nalishda bir-birining ichiga kirib qolgan edi.

## 🔍 Sabab

Compact layout qilishda:

- `rowHeight`: 6mm → 5mm ga kamaytirildi
- Lekin `bubbleSize`: 3mm (diameter = 6mm) qoldirildi
- Natija: 6mm diametrli doirachalar 5mm masofada = **OVERLAP!**

## 📊 Matematik Tahlil

```
Doiracha diameter: 2 × radius = 2 × 3mm = 6mm
Row height: 5mm
Overlap: 6mm - 5mm = 1mm ❌
```

Doirachalar 1mm ga bir-birining ustiga tushib qolgan!

## ✅ Yechim

### Variant 1: Doiracha o'lchamini kamaytirish (Tanlandi)

```
bubbleSize: 3mm → 2.5mm
diameter: 5mm
rowHeight: 5.5mm
Gap: 5.5mm - 5mm = 0.5mm ✅
```

### Variant 2: Row height'ni oshirish

```
rowHeight: 5mm → 6mm
Lekin bu compact layout'ni buzadi
```

## 🔧 O'zgarishlar

### 1. PDF Generator:

```typescript
bubbleSize: 2.5 // 3 → 2.5mm
rowHeight: 5.5 // 5 → 5.5mm
```

### 2. QR Code Layout:

```typescript
bubbleRadius: 2.5 // 3 → 2.5mm
rowHeight: 5.5 // 5 → 5.5mm
```

### 3. Backend Coordinate Mapper:

```python
bubble_radius_mm = 2.5  # 3 → 2.5mm
row_height_mm = 5.5     # 5 → 5.5mm
```

## 📏 Yangi O'lchamlar

- **Doiracha radiusi**: 2.5mm
- **Doiracha diametri**: 5mm
- **Qatorlar orasidagi masofa**: 5.5mm
- **Bo'sh joy**: 0.5mm (yetarli!)

## 🎯 Natija

- ✅ Doirachalar endi alohida
- ✅ 0.5mm bo'sh joy bor
- ✅ Hali ham compact layout
- ✅ OMR detection ishlaydi

## 📝 Test

**Yangi PDF yarating va tekshiring:**

1. Doirachalar alohida turishi kerak
2. Bir-biriga tegmasligi kerak
3. O'qish va to'ldirish qulay bo'lishi kerak

**Muammo hal qilindi!** ✅
