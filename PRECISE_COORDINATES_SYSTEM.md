# Precise Coordinate System - PDF-Based Mapping

## 📐 PDF Generator Spetsifikatsiyalari

### Corner Markers (Burchak Belgilari)

```typescript
// From pdfGenerator.ts
const size = 10;      // 10mm x 10mm
const margin = 5;     // 5mm from edges

Positions:
- Top Left: (5mm, 5mm)
- Top Right: (195mm, 5mm)  // 210 - 5 - 10
- Bottom Left: (5mm, 282mm)  // 297 - 5 - 10
- Bottom Right: (195mm, 282mm)
```

### Answer Grid Layout

```typescript
// Grid parameters
const xStart = 25 // 25mm from left
const questionsPerRow = 2 // 2 questions per row
const questionSpacing = 90 // 90mm between questions
const rowHeight = 6 // 6mm between rows

// Bubble parameters
const bubbleSize = 3 // 3mm radius
const bubbleSpacing = 8 // 8mm between bubbles
const firstBubbleOffset = 8 // 8mm from question number
```

### Bubble Positions

```
Question N at position (x, y):
  Bubble A: x + 8mm,  y + 2mm
  Bubble B: x + 16mm, y + 2mm
  Bubble C: x + 24mm, y + 2mm
  Bubble D: x + 32mm, y + 2mm
  Bubble E: x + 40mm, y + 2mm
```

### Y-Axis Calculation

```
Start Y = 123mm (after header + student info + instructions)

For each topic:
  Topic header: +10mm

  For each section:
    Section header: +6mm

    For each question row:
      Question Y = current_Y + (row_index * 6mm)

    Section spacing: +3mm

  Topic spacing: +5mm
```

## 🔧 Implementation

### 1. CoordinateMapper Class

**File**: `backend/utils/coordinate_mapper.py`

```python
class CoordinateMapper:
    # A4 dimensions
    paper_width_mm = 210
    paper_height_mm = 297

    # Calculate pixels per mm
    px_per_mm_x = image_width / 210
    px_per_mm_y = image_height / 297

    # Layout constants (from PDF)
    grid_start_x_mm = 25
    questions_per_row = 2
    question_spacing_mm = 90
    bubble_radius_mm = 3
    bubble_spacing_mm = 8
    row_height_mm = 6
    first_bubble_offset_mm = 8
```

**Key Methods**:

- `calculate_all()` - Calculate all bubble coordinates
- `get_corner_markers()` - Get corner marker positions
- `mm_to_px()` - Convert mm to pixels
- `px_to_mm()` - Convert pixels to mm

### 2. Improved Corner Detection

**File**: `backend/services/image_processor.py`

**Improvements**:

- Precise search regions based on PDF specs
- Score-based matching (aspect ratio + size + distance)
- Better threshold for black markers
- Morphological operations for cleanup

```python
# Expected marker size
px_per_mm = width / 210
expected_size = 10 * px_per_mm  # 10mm
margin = 5 * px_per_mm  # 5mm

# Search regions
regions = [
    {'center_x': margin + expected_size/2, 'center_y': margin + expected_size/2},
    # ... other corners
]

# Scoring
aspect_score = 1.0 - abs(1.0 - aspect_ratio)
size_score = 1.0 - abs(1.0 - size_ratio)
dist_score = 1.0 - (dist / search_radius)
total_score = aspect_score * 0.3 + size_score * 0.4 + dist_score * 0.3
```

## 📊 Coordinate Calculation Example

### Example: Question 1, Bubble A

**PDF Coordinates**:

- Question X: 25mm (grid start)
- Question Y: 123mm (start Y)
- Bubble A X: 25mm + 8mm = 33mm
- Bubble A Y: 123mm + 2mm = 125mm

**Pixel Conversion** (for 1240x1754 image):

- px_per_mm_x = 1240 / 210 = 5.90 px/mm
- px_per_mm_y = 1754 / 297 = 5.91 px/mm

- Bubble A X: 33mm \* 5.90 = 194.7 px
- Bubble A Y: 125mm \* 5.91 = 738.75 px
- Bubble radius: 3mm \* 5.90 = 17.7 px

### Example: Question 2, Bubble C

**PDF Coordinates**:

- Question X: 25mm + 90mm = 115mm (second column)
- Question Y: 123mm (same row)
- Bubble C X: 115mm + 8mm + (2 \* 8mm) = 139mm
- Bubble C Y: 123mm + 2mm = 125mm

**Pixel Conversion**:

- Bubble C X: 139mm \* 5.90 = 820.1 px
- Bubble C Y: 125mm \* 5.91 = 738.75 px

## 🎯 Accuracy Improvements

### Before (Old System)

- ❌ Hardcoded coordinates
- ❌ No PDF alignment
- ❌ Corner markers not used
- ❌ Inaccurate bubble positions
- ❌ 10% accuracy

### After (New System)

- ✅ PDF-based coordinates
- ✅ Precise mm-to-pixel conversion
- ✅ Corner marker detection
- ✅ Exact bubble positions
- ✅ Expected: 80-90% accuracy

## 🧪 Testing Strategy

### 1. Corner Marker Detection

```python
# Check if all 4 markers found
markers = image_processor.detect_corner_markers(image)
assert len(markers) == 4

# Check marker positions
assert markers[0]['name'] == 'top-left'
assert markers[0]['score'] > 0.5
```

### 2. Coordinate Accuracy

```python
# Test known bubble position
coords = mapper.calculate_all()
bubble_a = coords[1]['bubbles'][0]  # Q1, Bubble A

# Expected position (±5px tolerance)
assert abs(bubble_a['x'] - 194.7) < 5
assert abs(bubble_a['y'] - 738.75) < 5
```

### 3. Visual Verification

- Upload test image
- Check annotated image
- Verify rectangles align with bubbles
- Count correct detections

## 📈 Expected Results

### Corner Detection

- **Success Rate**: 90%+ (with good image quality)
- **Fallback**: Use full image if markers not found
- **Tolerance**: ±10px from expected position

### Bubble Detection

- **Accuracy**: 80-90% (with corner markers)
- **Accuracy**: 60-70% (without corner markers)
- **False Positives**: <5%
- **False Negatives**: <10%

## 🔍 Debugging

### Check Coordinate Calculation

```python
# Log coordinates
logger.info(f"Q1 Bubble A: x={bubble_x:.1f}, y={bubble_y:.1f}, r={radius:.1f}")

# Verify mm-to-px conversion
logger.info(f"Pixels per mm: x={px_per_mm_x:.2f}, y={px_per_mm_y:.2f}")
```

### Check Corner Detection

```python
# Log marker detection
logger.info(f"Found {marker['name']} at ({marker['x']}, {marker['y']}) score={marker['score']:.2f}")
```

### Visual Debug

- Save annotated image with:
  - Corner markers (blue circles)
  - Bubble centers (red dots)
  - Detection regions (green rectangles)

## 📝 Configuration

### Adjustable Parameters

**In `backend/config.py`**:

```python
# Image dimensions
TARGET_WIDTH = 1240
TARGET_HEIGHT = 1754

# Bubble detection
BUBBLE_RADIUS = 8  # Search radius in pixels
MIN_DARKNESS = 25.0  # Darkness threshold
MIN_DIFFERENCE = 10.0  # Comparative threshold
```

**In `backend/utils/coordinate_mapper.py`**:

```python
# All measurements in mm (from PDF)
grid_start_x_mm = 25
questions_per_row = 2
question_spacing_mm = 90
bubble_radius_mm = 3
bubble_spacing_mm = 8
row_height_mm = 6
```

## 🚀 Deployment

### Files Modified

- ✅ `backend/utils/coordinate_mapper.py` - **COMPLETELY REWRITTEN**
- ✅ `backend/services/image_processor.py` - Corner detection improved
- ✅ `backend/config.py` - Thresholds optimized

### Files Analyzed

- ✅ `src/utils/pdfGenerator.ts` - Extracted exact measurements
- ✅ `pdf_format.md` - Verified specifications

### Status

- ✅ Backend running: http://localhost:8000
- ✅ Coordinate system: PDF-aligned
- ✅ Corner detection: Improved
- ⏳ Testing: Ready for upload

## 🎓 Key Learnings

1. **PDF = Source of Truth**: All coordinates must match PDF generator exactly
2. **mm-to-px Conversion**: Critical for accuracy
3. **Corner Markers**: Essential for perspective correction
4. **Tolerance**: Allow ±5-10px for real-world variations
5. **Scoring**: Multi-factor scoring better than binary checks

---

**Date**: January 14, 2026  
**Status**: ✅ **IMPLEMENTED - READY FOR TESTING**  
**Expected Improvement**: 10% → 80-90% accuracy
