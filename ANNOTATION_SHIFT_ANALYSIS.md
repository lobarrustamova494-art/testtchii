# Annotation Shift Analysis

## Problem Description

User reports that annotation rectangles are shifted RIGHT by 1 position:

- When answer is A, rectangle appears at B
- When answer is B, rectangle appears at C
- etc.

## Code Analysis

### PDF Generation (pdfGenerator.ts)

```typescript
const xPos = xStart + j * 90 // xStart = 25mm
const bubbleX = xPos + 8 + vIndex * bubbleSpacing // bubbleSpacing = 8mm

// For first question (j=0):
// xPos = 25mm
// Bubble A (vIndex=0): 25 + 8 + 0*8 = 33mm
// Bubble B (vIndex=1): 25 + 8 + 1*8 = 41mm
// Bubble C (vIndex=2): 25 + 8 + 2*8 = 49mm
// Bubble D (vIndex=3): 25 + 8 + 3*8 = 57mm
// Bubble E (vIndex=4): 25 + 8 + 4*8 = 65mm
```

### Coordinate Calculation (coordinate_mapper.py)

```python
question_x_mm = 25  # grid_start_x_mm
bubble_x_mm = question_x_mm + 8 + (v_idx * 8)  # first_bubble_offset_mm=8, bubble_spacing_mm=8

# For first question:
# Bubble A (v_idx=0): 25 + 8 + 0*8 = 33mm
# Bubble B (v_idx=1): 25 + 8 + 1*8 = 41mm
# Bubble C (v_idx=2): 25 + 8 + 2*8 = 49mm
# Bubble D (v_idx=3): 25 + 8 + 3*8 = 57mm
# Bubble E (v_idx=4): 25 + 8 + 4*8 = 65mm
```

**✅ FORMULAS MATCH PERFECTLY**

### Annotation Logic (image_annotator.py)

```python
for bubble in bubbles:
    variant = bubble['variant']  # 'A', 'B', 'C', 'D', or 'E'
    x = int(round(bubble['x']))  # X coordinate from coordinate_mapper

    if variant == correct_answer:
        draw_rectangle_at(x)  # Draw at bubble's X position
```

**✅ LOGIC IS CORRECT**

## Test Results

### Test 1: Bubble Positions

```
Bubble A: X=194.9px (33mm)
Bubble B: X=242.1px (41mm)
Bubble C: X=289.3px (49mm)
Bubble D: X=336.6px (47mm)
Bubble E: X=383.8px (65mm)
Spacing: 47.24px (8mm)
```

### Test 2: Annotation Flow

```
Question 1: Answer=B
  → Draw rectangle at variant B, X=242px ✅ CORRECT

Question 2: Answer=A
  → Draw rectangle at variant A, X=726px ✅ CORRECT

Question 3: Answer=D
  → Draw rectangle at variant D, X=337px ✅ CORRECT
```

## Possible Causes

### ❌ Ruled Out:

1. Formula mismatch - Formulas are identical
2. Question numbering - Starts at 1, increments correctly
3. Variant indexing - A=0, B=1, C=2, D=3, E=4 (correct)
4. Coordinate lookup - Uses question number correctly
5. Annotation logic - Matches variant correctly

### 🤔 Possible Causes:

1. **PDF actual bubble positions differ from code** - Maybe jsPDF draws circles at different positions?
2. **Image transformation** - Maybe the scanned image has scaling/offset issues?
3. **first_bubble_offset_mm is wrong** - Should it be 0 instead of 8?
4. **Question number text width** - Maybe the text "1." pushes bubbles right?

## Next Steps

### Hypothesis 1: first_bubble_offset_mm should be 0

If we change `first_bubble_offset_mm` from 8 to 0:

- Bubble A would be at: 25 + 0 + 0\*8 = 25mm (instead of 33mm)
- This would shift all bubbles LEFT by 8mm (1 position)
- This would FIX the right-shift issue!

### Hypothesis 2: Question number text adds extra space

The question number "1." is drawn at `xPos`, and bubbles start at `xPos + 8`.
Maybe the text width is not accounted for, and bubbles should start further right?

### Test Plan:

1. Check actual PDF - measure bubble positions with a ruler/tool
2. Try setting `first_bubble_offset_mm = 0` in coordinate_mapper.py
3. Check if question number text width affects layout

## Recommendation

**TRY THIS FIX:**
Change `first_bubble_offset_mm` from 8 to 0 in `coordinate_mapper.py`.

This would shift all coordinate calculations LEFT by 8mm (1 bubble position), which should compensate for the RIGHT shift the user is seeing.
