# QR Code Ma'lumotlar Tuzilishi

## Umumiy Ma'lumot

PDF faylda chiqarilayotgan QR code ichida **JSON formatda** quyidagi ma'lumotlar saqlanadi:

---

## QR Code Ma'lumotlari

### 1. **Asosiy Ma'lumotlar**

```json
{
	"examId": "unique-exam-id",
	"examName": "Imtihon nomi",
	"setNumber": 1,
	"version": "2.0",
	"timestamp": "2026-01-15T12:34:56.789Z"
}
```

**Tafsilot:**

- `examId` - Imtihonning unique identifikatori
- `examName` - Imtihon nomi (masalan: "Matematika Oraliq Nazorat")
- `setNumber` - To'plam raqami (1, 2, 3, ... → A, B, C, ...)
- `version` - QR code format versiyasi (hozirda "2.0")
- `timestamp` - PDF yaratilgan vaqt (ISO 8601 format)

---

### 2. **Layout Ma'lumotlari** (Eng Muhim!)

```json
{
	"layout": {
		"questionsPerRow": 2,
		"bubbleSpacing": 8,
		"bubbleRadius": 2.5,
		"rowHeight": 5.5,
		"gridStartX": 25,
		"gridStartY": 149,
		"questionSpacing": 90,
		"firstBubbleOffset": 8
	}
}
```

**Tafsilot:**

| Parametr            | Qiymat | Birlik | Tavsif                                       |
| ------------------- | ------ | ------ | -------------------------------------------- |
| `questionsPerRow`   | 2      | -      | Har qatorda nechta savol (2 ustun)           |
| `bubbleSpacing`     | 8      | mm     | Bubble'lar orasidagi masofa                  |
| `bubbleRadius`      | 2.5    | mm     | Bubble radiusi                               |
| `rowHeight`         | 5.5    | mm     | Savollar qatori balandligi                   |
| `gridStartX`        | 25     | mm     | Grid boshlanish X koordinatasi               |
| `gridStartY`        | 149    | mm     | Grid boshlanish Y koordinatasi               |
| `questionSpacing`   | 90     | mm     | Ustunlar orasidagi masofa                    |
| `firstBubbleOffset` | 8      | mm     | Savol raqamidan birinchi bubble'gacha masofa |

**Muhim:** Bu parametrlar backend'da koordinatalarni hisoblash uchun ishlatiladi!

---

### 3. **Imtihon Tuzilishi**

```json
{
	"structure": {
		"totalQuestions": 35,
		"subjects": [
			{
				"id": "subject-1",
				"name": "Mavzu 1",
				"sections": [
					{
						"id": "section-1",
						"name": "Bo'lim 1.1",
						"questionCount": 10
					},
					{
						"id": "section-2",
						"name": "Bo'lim 1.2",
						"questionCount": 5
					}
				]
			},
			{
				"id": "subject-2",
				"name": "Mavzu 2",
				"sections": [
					{
						"id": "section-3",
						"name": "Bo'lim 2.1",
						"questionCount": 20
					}
				]
			}
		]
	}
}
```

**Tafsilot:**

- `totalQuestions` - Jami savollar soni
- `subjects` - Mavzular ro'yxati
  - `id` - Mavzu ID
  - `name` - Mavzu nomi
  - `sections` - Bo'limlar ro'yxati
    - `id` - Bo'lim ID
    - `name` - Bo'lim nomi
    - `questionCount` - Bu bo'limdagi savollar soni

---

## To'liq Misol

```json
{
	"examId": "exam-123456",
	"examName": "Matematika Oraliq Nazorat",
	"setNumber": 1,
	"version": "2.0",
	"timestamp": "2026-01-15T12:34:56.789Z",
	"layout": {
		"questionsPerRow": 2,
		"bubbleSpacing": 8,
		"bubbleRadius": 2.5,
		"rowHeight": 5.5,
		"gridStartX": 25,
		"gridStartY": 149,
		"questionSpacing": 90,
		"firstBubbleOffset": 8
	},
	"structure": {
		"totalQuestions": 35,
		"subjects": [
			{
				"id": "algebra",
				"name": "Algebra",
				"sections": [
					{
						"id": "linear-equations",
						"name": "Chiziqli tenglamalar",
						"questionCount": 10
					},
					{
						"id": "quadratic-equations",
						"name": "Kvadrat tenglamalar",
						"questionCount": 8
					}
				]
			},
			{
				"id": "geometry",
				"name": "Geometriya",
				"sections": [
					{
						"id": "triangles",
						"name": "Uchburchaklar",
						"questionCount": 12
					},
					{
						"id": "circles",
						"name": "Doiralar",
						"questionCount": 5
					}
				]
			}
		]
	}
}
```

---

## QR Code Parametrlari

### Yaratish Parametrlari

```typescript
QRCode.toDataURL(JSON.stringify(layoutData), {
	errorCorrectionLevel: 'H', // Yuqori xatolikni tuzatish darajasi
	type: 'image/png',
	width: 150, // 150px kenglik
	margin: 1, // 1 modul margin
})
```

### PDF'dagi Pozitsiyasi

```typescript
// QR code pozitsiyasi (mm)
X: 160mm  // Chapdan
Y: 10mm   // Yuqoridan
Width: 25mm
Height: 25mm

// Corner marker bilan to'qnashmaslik uchun:
// Corner marker: 190mm (o'ng tomonda)
// QR code tugaydi: 160 + 25 = 185mm
// Xavfsiz masofa: 5mm
```

---

## Backend'da Ishlatilishi

### 1. QR Code O'qish

```python
from services.qr_reader import QRCodeReader

qr_reader = QRCodeReader()
qr_data = qr_reader.read_qr_code(image)

if qr_data:
    print(f"Exam: {qr_data['examName']}")
    print(f"Version: {qr_data['version']}")
    print(f"Total Questions: {qr_data['structure']['totalQuestions']}")
```

### 2. Layout Parametrlarini Olish

```python
layout = qr_reader.get_layout_from_qr(qr_data)

# Natija:
{
    'questions_per_row': 2,
    'bubble_spacing_mm': 8,
    'bubble_radius_mm': 2.5,
    'row_height_mm': 5.5,
    'grid_start_x_mm': 25,
    'grid_start_y_mm': 149,
    'question_spacing_mm': 90,
    'first_bubble_offset_mm': 8
}
```

### 3. Koordinatalarni Hisoblash

```python
from utils.coordinate_mapper import CoordinateMapper

mapper = CoordinateMapper(
    image_width=1240,
    image_height=1754,
    exam_structure=qr_data['structure'],
    qr_layout=layout  # QR code'dan olingan layout
)

coordinates = mapper.calculate_all()
```

---

## Afzalliklari

### ✅ 1. 100% Aniq Layout

- Hardcoded qiymatlar o'rniga QR code'dan olinadi
- PDF va backend bir xil parametrlarni ishlatadi
- Hech qanday mismatch bo'lmaydi

### ✅ 2. Versiyalash

- `version` field orqali format o'zgarishlarini kuzatish
- Eski PDF'lar bilan backward compatibility

### ✅ 3. Exam Identifikatsiyasi

- `examId` orqali qaysi imtihon ekanligini aniqlash
- `setNumber` orqali qaysi to'plam ekanligini bilish

### ✅ 4. Tuzilma Ma'lumotlari

- Mavzular va bo'limlar strukturasi
- Har bo'limdagi savollar soni
- Grading uchun kerakli barcha ma'lumotlar

### ✅ 5. Timestamp

- PDF qachon yaratilganini bilish
- Audit trail uchun foydali

---

## Validation

Backend QR code ma'lumotlarini validate qiladi:

```python
def _validate_layout_data(data: Dict) -> bool:
    # Required fields
    required_fields = ['examId', 'version', 'layout', 'structure']

    # Required layout fields
    required_layout_fields = [
        'questionsPerRow', 'bubbleSpacing', 'bubbleRadius',
        'rowHeight', 'gridStartX', 'gridStartY'
    ]

    # Check all fields exist
    # ...
```

---

## QR Code O'qish Jarayoni

### 1. Kutubxonalar

Backend 2 ta kutubxona ishlatadi:

1. **pyzbar** (birinchi tanlov)

   - Tezroq
   - Aniqroq
   - Lekin qo'shimcha dependency kerak

2. **OpenCV QRCodeDetector** (fallback)
   - OpenCV bilan birga keladi
   - Qo'shimcha dependency yo'q
   - Biroz sekinroq

### 2. O'qish Strategiyasi

```python
# Try 1: To'liq image'dan o'qish
qr_codes = pyzbar.decode(gray)

# Try 2: Enhanced image (CLAHE + denoising)
if not qr_codes:
    enhanced = enhance_for_qr_detection(gray)
    qr_codes = pyzbar.decode(enhanced)

# Try 3: Faqat o'ng yuqori burchak (QR code joylashgan joy)
if not qr_codes:
    corner_region = gray[0:15%, 75%:100%]
    qr_codes = pyzbar.decode(corner_region)
```

### 3. Xatolik Tuzatish

QR code `errorCorrectionLevel: 'H'` bilan yaratilgan:

- **H (High)** - 30% gacha xatolikni tuzatadi
- Agar QR code qisman shikastlangan bo'lsa ham o'qiydi

---

## Xulosa

QR code ichida **3 ta asosiy ma'lumot guruhi** saqlanadi:

1. **Identifikatsiya** - examId, examName, setNumber, version, timestamp
2. **Layout** - 8 ta parametr (bubble size, spacing, grid position, etc.)
3. **Tuzilma** - subjects, sections, questionCount

Bu ma'lumotlar backend'da:

- ✅ Koordinatalarni aniq hisoblash
- ✅ Imtihonni identifikatsiya qilish
- ✅ Grading uchun tuzilmani bilish
- ✅ Versiyalash va compatibility

uchun ishlatiladi.

**Eng muhim:** Layout parametrlari PDF generator va backend o'rtasida 100% mos kelishini ta'minlaydi!
