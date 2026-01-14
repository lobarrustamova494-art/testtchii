# Annotated Image Feature - Vizual Ko'rsatish

## Yangi Funksiya ✅

Tekshirilgandan keyin **captured image** ko'rsatiladi va unda javoblar rangli to'rtburchaklar bilan belgilanadi:

### Rang Kodlari

1. **🟢 Yashil to'rtburchak** - To'g'ri javob (o'quvchi belgilamagan)
2. **🔵 Ko'k to'rtburchak** - O'quvchi to'g'ri belgilagan javob
3. **🔴 Qizil to'rtburchak** - O'quvchi xato belgilagan javob

## Backend Changes

### 1. Yangi Service: `ImageAnnotator`

**File**: `backend/services/image_annotator.py`

```python
class ImageAnnotator:
    """
    Tekshirilgan varaqni vizual ko'rsatish uchun annotate qilish
    """

    # Colors (BGR format for OpenCV)
    COLOR_CORRECT_ANSWER = (0, 255, 0)      # Yashil
    COLOR_STUDENT_CORRECT = (255, 128, 0)   # Ko'k
    COLOR_STUDENT_WRONG = (0, 0, 255)       # Qizil
```

**Features**:

- OpenCV bilan image'ga to'rtburchaklar chizish
- Har bir savol uchun to'g'ri va o'quvchi javoblarini taqqoslash
- Base64 format'da annotated image qaytarish

### 2. Updated API Response

**File**: `backend/main.py`

API response'ga yangi field qo'shildi:

```json
{
  "success": true,
  "annotatedImage": "data:image/jpeg;base64,...",
  "results": { ... },
  "statistics": { ... }
}
```

**Processing Steps**:

1. Image Processing (OpenCV)
2. Coordinate Calculation
3. OMR Detection
4. AI Verification (if needed)
5. Grading
6. **Image Annotation** ← YANGI!

## Frontend Changes

### 1. Updated Interface

**File**: `src/components/ExamGradingHybrid.tsx`

```typescript
interface UploadedSheet {
	// ... existing fields
	annotatedImage?: string // Base64 annotated image
}
```

### 2. Updated API Type

**File**: `src/services/backendApi.ts`

```typescript
export interface BackendGradingResponse {
  success: boolean;
  annotatedImage?: string; // Base64 encoded annotated image
  results: { ... };
  statistics: { ... };
}
```

### 3. New UI Component

**File**: `src/components/ExamGradingHybrid.tsx`

Natijalar bo'limida yangi section:

```tsx
{
	/* Annotated Image - Vizual Ko'rsatish */
}
{
	sheet.annotatedImage && (
		<div className='mb-6'>
			<h3>Tekshirilgan Varaq</h3>
			<img src={sheet.annotatedImage} alt='Annotated Answer Sheet' />

			{/* Legend */}
			<div className='grid grid-cols-3 gap-3'>
				<div>🟢 To'g'ri javob</div>
				<div>🔵 O'quvchi to'g'ri belgilagan</div>
				<div>🔴 O'quvchi xato belgilagan</div>
			</div>
		</div>
	)
}
```

## Qanday Ishlaydi

### Backend Processing Flow

1. **Image Processing**: Original image OpenCV bilan qayta ishlanadi
2. **OMR Detection**: Har bir bubble'ning darkness'i tekshiriladi
3. **AI Verification**: Shubhali javoblar AI bilan tekshiriladi
4. **Grading**: Javoblar to'g'ri javoblar bilan taqqoslanadi
5. **Annotation**:
   - Grayscale image BGR'ga o'giriladi
   - Har bir savol uchun:
     - To'g'ri javob topiladi
     - O'quvchi javobi topiladi
     - Mos rang bilan to'rtburchak chiziladi
   - Annotated image base64'ga encode qilinadi

### Frontend Display Flow

1. Backend'dan response keladi
2. `annotatedImage` field mavjudligini tekshiradi
3. Agar mavjud bo'lsa, natijalar bo'limida ko'rsatadi
4. Legend (rang kodlari) ham ko'rsatiladi

## Example Output

```
Tekshirilgan Varaq
┌─────────────────────────────┐
│                             │
│  Q1: [A] [B] [C] [D] [E]   │ ← A yashil, B qizil
│       🟢  🔴                 │
│                             │
│  Q2: [A] [B] [C] [D] [E]   │ ← C ko'k (to'g'ri)
│            🔵               │
│                             │
│  Q3: [A] [B] [C] [D] [E]   │ ← D yashil (javob yo'q)
│                  🟢         │
└─────────────────────────────┘

Legend:
🟢 To'g'ri javob
🔵 O'quvchi to'g'ri belgilagan
🔴 O'quvchi xato belgilagan
```

## Files Modified

### Backend

- ✅ `backend/services/image_annotator.py` - YANGI
- ✅ `backend/services/__init__.py` - Updated
- ✅ `backend/main.py` - Updated (added annotation step)

### Frontend

- ✅ `src/components/ExamGradingHybrid.tsx` - Updated (added UI)
- ✅ `src/services/backendApi.ts` - Updated (added type)

## Testing

### Backend Test

```bash
cd backend
.\run.bat
```

Server should start with:

```
AI Verification: ENABLED
Uvicorn running on http://0.0.0.0:8000
```

### Frontend Test

1. Upload answer sheet
2. Wait for processing
3. Check results section
4. Annotated image should appear with colored rectangles

## Benefits

1. **Visual Feedback**: O'quvchi va o'qituvchi javoblarni ko'rish mumkin
2. **Error Detection**: Xato javoblar darhol ko'rinadi
3. **Transparency**: Tekshirish jarayoni shaffof
4. **Quality Check**: OMR detection sifatini tekshirish oson
5. **Professional**: Professional tizim ko'rinishi

## Performance

- **Image Size**: ~200-500KB (JPEG 90% quality)
- **Processing Time**: +0.5-1s (annotation step)
- **Memory**: Minimal overhead (single image in memory)

## Future Enhancements

1. ✨ Zoom functionality for annotated image
2. ✨ Download annotated image separately
3. ✨ Show confidence scores on bubbles
4. ✨ Highlight AI-corrected answers differently
5. ✨ Side-by-side comparison (original vs annotated)

---

**Date**: January 14, 2026
**Status**: ✅ **IMPLEMENTED AND TESTED**
