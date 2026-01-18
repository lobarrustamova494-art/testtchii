"""
Check if there are actually filled bubbles in the image
Look for dark circular regions that could be filled answers
"""
import cv2
import numpy as np

print("=" * 80)
print("CHECKING FOR FILLED BUBBLES")
print("=" * 80)
print()

# Load image
img = cv2.imread('test_images/5-imtihon.jpg')
if img is None:
    print("ERROR: Cannot load image!")
    exit(1)

print(f"Image size: {img.shape[1]}x{img.shape[0]}")
print()

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Show brightness statistics
print("Brightness statistics:")
print(f"  Mean: {gray.mean():.1f}")
print(f"  Min: {gray.min()}")
print(f"  Max: {gray.max()}")
print(f"  Std: {gray.std():.1f}")
print()

# Find very dark regions (potential filled bubbles)
# Filled bubbles should be significantly darker than background
dark_threshold = gray.mean() - gray.std() * 1.5
very_dark = gray < dark_threshold

print(f"Dark threshold: {dark_threshold:.1f}")
print(f"Dark pixels: {very_dark.sum()} ({very_dark.sum() / very_dark.size * 100:.1f}%)")
print()

# Find contours in dark regions
contours, _ = cv2.findContours(
    very_dark.astype(np.uint8) * 255,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

print(f"Found {len(contours)} dark regions")
print()

# Filter for circular dark regions (filled bubbles)
filled_bubbles = []
for contour in contours:
    area = cv2.contourArea(contour)
    if area < 50 or area > 1000:  # Size filter
        continue
    
    # Check circularity
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        continue
    
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    if circularity > 0.6:  # Circular enough
        (x, y), radius = cv2.minEnclosingCircle(contour)
        
        # Check if it's actually dark
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask, (int(x), int(y)), int(radius), 255, -1)
        mean_darkness = 255 - gray[mask > 0].mean()
        
        if mean_darkness > 30:  # At least 30% dark
            filled_bubbles.append({
                'x': int(x),
                'y': int(y),
                'radius': int(radius),
                'darkness': mean_darkness,
                'circularity': circularity
            })

print(f"Found {len(filled_bubbles)} potential filled bubbles")
print()

if filled_bubbles:
    # Sort by darkness (darkest first)
    filled_bubbles.sort(key=lambda b: b['darkness'], reverse=True)
    
    print("Top 20 darkest circular regions:")
    print("-" * 80)
    for i, bubble in enumerate(filled_bubbles[:20]):
        print(f"{i+1:2d}. Pos=({bubble['x']:4d}, {bubble['y']:4d}) "
              f"R={bubble['radius']:2d} "
              f"Darkness={bubble['darkness']:5.1f}% "
              f"Circularity={bubble['circularity']:.2f}")
    
    print()
    
    # Draw on image
    output = img.copy()
    for bubble in filled_bubbles:
        cv2.circle(output, (bubble['x'], bubble['y']), bubble['radius'], (0, 255, 0), 2)
        cv2.circle(output, (bubble['x'], bubble['y']), 2, (0, 0, 255), -1)
    
    cv2.imwrite('test_images/5-imtihon_filled_bubbles.jpg', output)
    print(f"✅ Saved: test_images/5-imtihon_filled_bubbles.jpg")
    print()
    
    # Try to group by rows
    filled_bubbles.sort(key=lambda b: b['y'])
    
    rows = []
    current_row = []
    last_y = -100
    
    for bubble in filled_bubbles:
        if abs(bubble['y'] - last_y) < 40:  # Same row
            current_row.append(bubble)
        else:
            if current_row:
                rows.append(current_row)
            current_row = [bubble]
        last_y = bubble['y']
    
    if current_row:
        rows.append(current_row)
    
    print(f"Grouped into {len(rows)} rows")
    print()
    
    # Show rows
    print("Rows of filled bubbles:")
    print("-" * 80)
    for i, row in enumerate(rows):
        row.sort(key=lambda b: b['x'])
        avg_y = sum(b['y'] for b in row) / len(row)
        print(f"Row {i+1}: {len(row)} bubbles at Y≈{avg_y:.0f}")
        for j, bubble in enumerate(row):
            print(f"  {j+1}. X={bubble['x']}, Darkness={bubble['darkness']:.1f}%")
    
    print()
    
    # Expected pattern: 40 questions, so 40 filled bubbles
    if len(filled_bubbles) >= 35:
        print("✅ Found enough filled bubbles (35+)")
        print("   This image appears to have answers marked")
    elif len(filled_bubbles) >= 20:
        print("⚠️  Found some filled bubbles (20-34)")
        print("   Some answers may be marked, but detection is incomplete")
    else:
        print("❌ Too few filled bubbles (<20)")
        print("   Either answers are not marked, or detection needs improvement")
else:
    print("❌ No filled bubbles detected!")
    print()
    print("Possible reasons:")
    print("  1. Answers are not marked on this sheet")
    print("  2. Image quality is too low")
    print("  3. Marks are too light")
    print("  4. This is a blank answer sheet")

print()
print("=" * 80)
