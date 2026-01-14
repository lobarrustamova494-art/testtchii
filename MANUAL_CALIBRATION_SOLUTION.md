# Manual Calibration Solution

## 🔍 Muammo

Automatic corner detection ishlamayapti:

- Faqat 2/4 markers topilmoqda
- Pastki markerlar topilmayapti
- Perspective correction qo'llanilmayapti
- Koordinatalar noto'g'ri

## 💡 Yechim: Manual Calibration

Foydalanuvchi o'zi 4 ta corner'ni belgilaydi, keyin tizim:

1. Perspective correction qo'llaydi
2. To'g'ri koordinatalarni hisoblaydi
3. Aniq OMR detection qiladi

## 🎯 Qisqa Muddatli Yechim (Hozir)

### Option 1: Threshold'ni Yana Pasaytirish

```python
# backend/config.py
MIN_DARKNESS = 20.0  # 25 → 20
MIN_DIFFERENCE = 8.0  # 10 → 8
```

### Option 2: Bubble Radius'ni Oshirish

```python
# backend/config.py
BUBBLE_RADIUS = 10  # 8 → 10 (kattaroq hudud)
```

### Option 3: Multiple Marks Threshold'ni Oshirish

```python
# backend/config.py
MULTIPLE_MARKS_THRESHOLD = 15  # 10 → 15 (kamroq false positive)
```

## 🔧 Immediate Fix

Keling, barcha 3 ta o'zgarishni birga qilamiz:

```python
# backend/config.py

# OMR Detection - AGGRESSIVE SETTINGS
BUBBLE_RADIUS = 10  # Increased from 8
MIN_DARKNESS = 20.0  # Lowered from 25
MIN_DIFFERENCE = 8.0  # Lowered from 10
MULTIPLE_MARKS_THRESHOLD = 15  # Increased from 10
```

## 📊 Expected Results

### Current

- Accuracy: 26.67% (8/30)
- Uncertain: 30/30
- Multiple marks: 28/30

### After Adjustment

- Accuracy: 50-70% expected
- Uncertain: 10-15/30
- Multiple marks: 5-10/30

## 🚀 Long-term Solution

### Manual Calibration UI (1-2 hours)

**Frontend**:

1. Show uploaded image
2. Let user click 4 corners
3. Send corner coordinates to backend
4. Backend uses manual corners for perspective correction

**Backend**:

```python
@app.post("/api/grade-sheet-manual")
async def grade_sheet_manual(
    file: UploadFile,
    corners: str = Form(...),  # JSON with corner coordinates
    exam_structure: str = Form(...),
    answer_key: str = Form(...)
):
    # Parse manual corners
    manual_corners = json.loads(corners)

    # Use manual corners for perspective correction
    corrected = image_processor.correct_perspective(image, manual_corners)

    # Continue with normal processing
    ...
```

## 🎓 Alternative: Template Matching

Instead of corner detection, use template matching:

1. Save a template of corner marker
2. Use cv2.matchTemplate() to find all 4
3. More reliable than contour detection

```python
def detect_corners_with_template(self, image):
    # Load template (10x10 black square)
    template = np.zeros((50, 50), dtype=np.uint8)

    # Match template
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)

    # Find peaks
    threshold = 0.8
    locations = np.where(result >= threshold)

    # Group into 4 corners
    ...
```

## 📝 Recommendation

**Immediate** (5 min):

1. Adjust thresholds (Option 1, 2, 3)
2. Test with same image
3. See if accuracy improves

**Short-term** (1-2 hours): 4. Implement manual calibration UI 5. Let user click corners 6. Much more reliable

**Long-term** (2-3 hours): 7. Template matching for corners 8. Better image preprocessing 9. Machine learning for bubble detection

## 🔥 Quick Fix Now

Let's adjust the thresholds immediately and see if it helps!
