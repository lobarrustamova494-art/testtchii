# Koordinata Muammosi - YAKUNIY YECHIM ✅

## ❌ Muammo

Imtihon varaqlarini tekshirishda rangli belgilar doirachalarning **36mm pastiga** tushib qolgan edi.

## 🔍 Asosiy Sabab

**`gridStartY` qiymatida xatolik!**

- ❌ Noto'g'ri: `gridStartY = 113mm`
- ✅ To'g'ri: `gridStartY = 149mm`

## 📊 Hisoblash

Answer grid qayerdan boshlanadi?

```
Y = 15mm (start)
  + 28mm (header: title + exam name + date)
  + 84mm (student info: fields + ID grid)
  + 22mm (instructions)
  = 149mm ✅
```

## ✅ Tuzatish

### 1. PDF Generator (QR Code):

```typescript
// src/utils/pdfGenerator.ts
gridStartY: 149 // ✅ 113 → 149
```

### 2. Coordinate Mapper (Default):

```python
# backend/utils/coordinate_mapper.py
grid_start_y_mm = 149  # ✅ 113 → 149
```

## ⚠️ MUHIM!

**Eski PDF'lar ishlamaydi!** Faqat **yangi yaratilgan PDF'lar** to'g'ri ishlaydi.

Sabab: Eski PDF'larda QR code'da `gridStartY: 113` yozilgan.

## 🎯 Test Qilish

1. **Yangi PDF yarating** (frontend'da)
2. **Backend'ni qayta ishga tushiring**
3. **Yangi PDF'ni tekshiring** - belgilar endi to'g'ri!

**Muammo hal qilindi!** ✅
