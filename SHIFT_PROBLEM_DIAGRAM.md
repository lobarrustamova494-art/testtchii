# Shift Problem Visualization

## Scenario: User says "rectangles shifted RIGHT by 1 position"

### What the user sees:

```
PDF Bubbles:     [A]  [B]  [C]  [D]  [E]
Rectangles:           [B]  [C]  [D]  [E]  [?]
```

The rectangle that should be at A is actually at B.
The rectangle that should be at B is actually at C.
etc.

### This means:

- When we calculate coordinates for bubble A, we're getting bubble B's position
- Our X coordinates are 8mm (1 bubble) TOO LARGE
- We need to SUBTRACT 8mm from all bubble X coordinates

### Current calculation:

```
bubble_x_mm = question_x_mm + 8 + (v_idx * 8)

For question at x=25mm:
- Bubble A (v_idx=0): 25 + 8 + 0 = 33mm
- Bubble B (v_idx=1): 25 + 8 + 8 = 41mm
- Bubble C (v_idx=2): 25 + 8 + 16 = 49mm
```

### If we change first_bubble_offset_mm from 8 to 0:

```
bubble_x_mm = question_x_mm + 0 + (v_idx * 8)

For question at x=25mm:
- Bubble A (v_idx=0): 25 + 0 + 0 = 25mm  ← 8mm LEFT
- Bubble B (v_idx=1): 25 + 0 + 8 = 33mm  ← 8mm LEFT
- Bubble C (v_idx=2): 25 + 0 + 16 = 41mm ← 8mm LEFT
```

This shifts all coordinates LEFT by 8mm, which compensates for the RIGHT shift!

### Result after fix:

```
PDF Bubbles:     [A]  [B]  [C]  [D]  [E]
Rectangles:      [A]  [B]  [C]  [D]  [E]  ✅ ALIGNED!
```

## BUT WAIT - Why is the PDF code using +8?

Looking at PDF generator:

```typescript
const bubbleX = xPos + 8 + vIndex * bubbleSpacing
```

The `+8` is to leave space for the question number text "1." which is drawn at `xPos`.

**HYPOTHESIS:** Maybe the question number text doesn't actually take up 8mm of space?
Or maybe jsPDF's text positioning works differently than we think?

## Alternative Hypothesis: PDF is wrong

Maybe the PDF generator should NOT have `+8`:

```typescript
// Current (wrong?):
const bubbleX = xPos + 8 + vIndex * bubbleSpacing

// Should be:
const bubbleX = xPos + vIndex * bubbleSpacing
```

But this would make bubbles overlap with the question number text!

## Conclusion

The safest fix is to change `first_bubble_offset_mm` from 8 to 0 in the coordinate mapper.
This will shift all annotation rectangles LEFT by 8mm, compensating for the RIGHT shift.

If this causes issues (rectangles now shifted LEFT), then the problem is elsewhere.
