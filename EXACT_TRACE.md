# Aniq Trace - PDF vs Coordinate Mapper

## PDF Generator (TypeScript)

### Initialization:

```typescript
currentY = 149 // startY from drawTitleSheet
```

### Topic Header:

```typescript
pdf.rect(15, currentY, 180, 6)     // Rectangle at Y=149, height=6mm
pdf.text(..., currentY + 4)         // Text at Y=153
currentY += 8                       // currentY = 157
```

### Section Header:

```typescript
pdf.text(..., currentY + 3)         // Text at Y=160
currentY += 5                       // currentY = 162
```

### Questions Loop:

```typescript
for (let i = 0; i < questionCount; i += questionsPerRow) {
	// Row 0 (questions 1-2):
	for (let j = 0; j < 2; j++) {
		// Question number at currentY + 3.5 = 165.5
		// Bubble at currentY + 2 = 164
		// Letter at currentY + 2.8 = 164.8
	}
	currentY += 5.5 // After row: currentY = 167.5

	// Row 1 (questions 3-4):
	for (let j = 0; j < 2; j++) {
		// Bubble at currentY + 2 = 169.5
	}
	currentY += 5.5 // After row: currentY = 173
}
```

## Coordinate Mapper (Python)

### Current Code:

```python
current_y_mm = 149
current_y_mm += 8   # = 157
current_y_mm += 5   # = 162

# Question 1 (row 0):
question_y_mm = 162 + (0 * 5.5) = 162
bubble_y_mm = 162 + 2 = 164 ✅

# Question 3 (row 1):
question_y_mm = 162 + (1 * 5.5) = 167.5
bubble_y_mm = 167.5 + 2 = 169.5 ✅
```

## Comparison

| Item          | PDF   | Mapper | Match? |
| ------------- | ----- | ------ | ------ |
| Grid start    | 149   | 149    | ✅     |
| After topic   | 157   | 157    | ✅     |
| After section | 162   | 162    | ✅     |
| Q1 bubble     | 164   | 164    | ✅     |
| Q3 bubble     | 169.5 | 169.5  | ✅     |

## Conclusion

**Koordinatalar to'g'ri!** Agar hali ham xatolik bo'lsa, muammo boshqa joyda:

1. **QR code o'qilmayapti** - default layout ishlatilmoqda
2. **Eski PDF ishlatilmoqda** - yangi PDF yaratish kerak
3. **Image processing** - rasm qiyshiq yoki sifatsiz
4. **Bubble radius** - backend'da noto'g'ri

Keyingi qadam: Backend log'larini tekshirish
