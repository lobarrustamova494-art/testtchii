# OMR Detection Improvement Plan

## Current Problem

- Only 3/30 correct (10% accuracy)
- Many false positives and false negatives
- Image quality issues (corner markers not found)

## Root Causes

### 1. **Threshold Too High**

Current: `min_darkness = 35.0`

- Lightly marked bubbles are not detected
- Need to lower threshold

### 2. **Image Processing Issues**

- Corner markers not detected → using full image
- Perspective correction not applied
- Coordinates may be off

### 3. **Bubble Detection Algorithm**

- May need to adjust comparative analysis
- Multiple marks threshold too sensitive

## Solutions

### Solution 1: Lower Detection Thresholds ⭐ RECOMMENDED

```python
# Current (backend/config.py)
MIN_DARKNESS = 35.0
MIN_DIFFERENCE = 15.0

# Proposed
MIN_DARKNESS = 25.0  # Lower to detect lighter marks
MIN_DIFFERENCE = 10.0  # Lower to be more sensitive
```

### Solution 2: Improve Image Preprocessing

- Better contrast enhancement
- Adaptive thresholding adjustment
- Noise reduction tuning

### Solution 3: Add Manual Calibration

- Let user adjust threshold via UI
- Show real-time bubble detection
- Save calibration per exam type

### Solution 4: Disable AI (Temporary)

Since Groq vision model is decommissioned:

- Disable AI verification
- Focus on OMR accuracy
- Re-enable when new vision model available

## Implementation Priority

1. **IMMEDIATE**: Lower thresholds (5 min)
2. **SHORT-TERM**: Disable broken AI (5 min)
3. **MEDIUM-TERM**: Add calibration UI (1-2 hours)
4. **LONG-TERM**: Improve image processing (2-3 hours)

## Testing Strategy

1. Test with current image
2. Adjust thresholds incrementally
3. Compare results
4. Find optimal values
5. Document findings
