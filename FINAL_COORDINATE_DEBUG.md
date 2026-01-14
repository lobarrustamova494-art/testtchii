# Yakuniy Koordinata Debug

## PDF Generator'dagi Aniq Qiymatlar

### Topic Header:

```typescript
pdf.rect(15, currentY, 180, 6, 'F')  // 6mm height (kamaytirildi 8mm dan)
pdf.text(..., currentY + 4)          // Text at +4
currentY += 8                        // After header (kamaytirildi 10mm dan)
```

### Section Header:

```typescript
pdf.text(..., currentY + 3)          // Text at +3 (kamaytirildi 4mm dan)
currentY += 5                        // After header (kamaytirildi 6mm dan)
```

### Questions:

```typescript
bubbleSize = 2.5                     // Radius (kamaytirildi 3mm dan)
rowHeight = 5.5                      // Row height (kamaytirildi 6mm dan)

// Question number
pdf.text(..., currentY + 3.5)        // Text at +3.5 (kamaytirildi 4mm dan)

// Bubble center
drawEmptyBubble(..., currentY + 2, bubbleSize)  // Bubble at +2

// Letter inside
pdf.text(..., currentY + 2.8)        // Letter at +2.8 (kamaytirildi 3mm dan)

currentY += rowHeight                // After row: +5.5mm
```

## Coordinate Mapper'da Kerak Bo'lgan Qiymatlar

### Hozirgi (Noto'g'ri):

```python
current_y_mm = 149  # grid start
current_y_mm += 10  # topic header - NOTO'G'RI! (8 bo'lishi kerak)
current_y_mm += 6   # section header - NOTO'G'RI! (5 bo'lishi kerak)
bubble_y_mm = question_y_mm + 2
```

### To'g'ri Bo'lishi Kerak:

```python
current_y_mm = 149  # grid start
current_y_mm += 8   # topic header (PDF'da currentY += 8)
current_y_mm += 5   # section header (PDF'da currentY += 5)
question_y_mm = current_y_mm + (row * 5.5)  # rowHeight = 5.5
bubble_y_mm = question_y_mm + 2
```

## Birinchi Savol Hisoblash

### PDF'da:

```
currentY = 149 (grid start)
Topic header at 149 (6mm height)
currentY += 8 → currentY = 157
Section header text at 157 + 3 = 160
currentY += 5 → currentY = 162
First bubble at 162 + 2 = 164mm ✅
```

### Coordinate Mapper'da (Hozirgi - NOTO'G'RI):

```
current_y_mm = 149
current_y_mm += 10 → 159  ❌ (8 bo'lishi kerak)
current_y_mm += 6 → 165   ❌ (5 bo'lishi kerak)
bubble_y_mm = 165 + 2 = 167mm ❌

Farq: 167 - 164 = 3mm pastda!
```

### Coordinate Mapper'da (To'g'ri):

```
current_y_mm = 149
current_y_mm += 8 → 157  ✅
current_y_mm += 5 → 162  ✅
bubble_y_mm = 162 + 2 = 164mm ✅

MOS KELDI!
```

## Xulosa

Muammo: Coordinate mapper'da topic va section header spacing'lari yangilanmagan!

Tuzatish kerak:

- Topic header spacing: 10 → 8
- Section header spacing: 6 → 5
- Row height: 6 → 5.5 (allaqachon tuzatilgan)
