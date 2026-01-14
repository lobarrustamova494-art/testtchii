# PDF Koordinatalarini Hisoblash

## PDF Generator'da (pdfGenerator.ts)

```typescript
function drawAnswerGrid(pdf: jsPDF, exam: Exam, startY: number): number {
	let currentY = startY // startY = 113mm (from drawTitleSheet)
	let questionNumber = 1

	exam.subjects.forEach((subject, topicIndex) => {
		// TOPIC HEADER
		pdf.rect(15, currentY, 180, 8, 'F') // Rectangle AT currentY, height 8mm
		pdf.text(`MAVZU...`, 20, currentY + 5) // Text at currentY + 5

		currentY += 10 // AFTER topic header: currentY = 113 + 10 = 123mm

		subject.sections.forEach((section, sectionIndex) => {
			// SECTION HEADER
			pdf.text(`Bo'lim...`, 20, currentY + 4) // Text at currentY + 4 = 123 + 4 = 127mm

			currentY += 6 // AFTER section header: currentY = 123 + 6 = 129mm

			for (let i = 0; i < section.questionCount; i += questionsPerRow) {
				// QUESTIONS
				// Question number at: currentY + 4 = 129 + 4 = 133mm
				// Bubble center at: currentY + 2 = 129 + 2 = 131mm

				currentY += rowHeight // After row: currentY = 129 + 6 = 135mm
			}

			currentY += 3 // After section: currentY = 135 + 3 = 138mm
		})

		currentY += 5 // After topic: currentY = 138 + 5 = 143mm
	})
}
```

## Birinchi Savol Uchun Hisoblash

### PDF'da:

```
startY = 113mm (grid boshlanishi)

Topic 1:
  - Topic header rectangle: 113mm (8mm balandlik)
  - currentY += 10 → currentY = 123mm

  Section 1:
    - Section text: 123 + 4 = 127mm
    - currentY += 6 → currentY = 129mm

    Question 1 (row 0, col 0):
      - Question number: 129 + 4 = 133mm
      - Bubble center: 129 + 2 = 131mm ✅
```

### Coordinate Mapper'da (kerak):

```python
current_y_mm = 113  # grid_start_y_mm

Topic 1:
  current_y_mm += 10  # → 123mm (topic header'dan keyin)

  Section 1:
    current_y_mm += 6  # → 129mm (section header'dan keyin)

    Question 1 (row 0):
      question_y_mm = 129 + (0 * 6) = 129mm
      bubble_y_mm = 129 + 2 = 131mm ✅
```

## Ikkinchi Savol (row 0, col 1)

### PDF'da:

```
currentY = 129mm (section header'dan keyin)
Question 2 (row 0, col 1):
  - Bubble center: 129 + 2 = 131mm ✅

(Qator tugadi)
currentY += 6 → currentY = 135mm
```

### Coordinate Mapper'da:

```python
current_y_mm = 129mm

Question 2 (row 0, col 1):
  question_y_mm = 129 + (0 * 6) = 129mm
  bubble_y_mm = 129 + 2 = 131mm ✅
```

## Uchinchi Savol (row 1, col 0)

### PDF'da:

```
currentY = 135mm (birinchi qator'dan keyin)
Question 3 (row 1, col 0):
  - Bubble center: 135 + 2 = 137mm ✅
```

### Coordinate Mapper'da:

```python
current_y_mm = 129mm (section header'dan keyin)

Question 3 (row 1, col 0):
  question_y_mm = 129 + (1 * 6) = 135mm
  bubble_y_mm = 135 + 2 = 137mm ✅
```

## Xulosa

Coordinate mapper kodi TO'G'RI! Muammo boshqa joyda bo'lishi kerak.

Ehtimol:

1. `grid_start_y_mm` noto'g'ri (113mm bo'lishi kerak)
2. `row_height_mm` noto'g'ri (6mm bo'lishi kerak)
3. Yoki PDF'da `startY` noto'g'ri qiymat
