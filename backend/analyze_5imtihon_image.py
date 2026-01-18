"""
Analyze 5-imtihon image to find actual bubble positions
"""
import cv2
import numpy as np
import json

print("=" * 80)
print("5-IMTIHON IMAGE ANALYSIS")
print("=" * 80)
print()

# Load image
img = cv2.imread('test_images/5-imtihon.jpg')
if img is None:
    print("ERROR: Cannot load image!")
    exit(1)

print(f"Original image size: {img.shape[1]}x{img.shape[0]}")
print()

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply CLAHE for better contrast
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
enhanced = clahe.apply(gray)

# Apply adaptive threshold
binary = cv2.adaptiveThreshold(
    enhanced,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV,
    15,
    3
)

# Find contours
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"Found {len(contours)} contours")
print()

# Filter circular contours (bubbles)
bubbles = []
for contour in contours:
    area = cv2.contourArea(contour)
    if area < 30 or area > 800:  # Adjusted size range
        continue
    
    # Check circularity
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        continue
    
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    if circularity > 0.6:  # Lowered threshold
        (x, y), radius = cv2.minEnclosingCircle(contour)
        bubbles.append({
            'x': int(x),
            'y': int(y),
            'radius': int(radius),
            'area': area,
            'circularity': circularity
        })

print(f"Found {len(bubbles)} potential bubbles")
print()

# Sort bubbles by Y position (top to bottom)
bubbles.sort(key=lambda b: b['y'])

# Group bubbles by rows (similar Y positions)
rows = []
current_row = []
last_y = -100

for bubble in bubbles:
    if abs(bubble['y'] - last_y) < 30:  # Same row
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

# Analyze first few rows
print("First 10 rows analysis:")
print("-" * 80)
for i, row in enumerate(rows[:10]):
    # Sort by X position
    row.sort(key=lambda b: b['x'])
    
    avg_y = sum(b['y'] for b in row) / len(row)
    print(f"Row {i+1}: {len(row)} bubbles, Y≈{avg_y:.0f}")
    
    # Show first 5 bubbles in row
    for j, bubble in enumerate(row[:5]):
        print(f"  Bubble {j+1}: ({bubble['x']}, {bubble['y']}) r={bubble['radius']}")

print()

# Try to identify question pattern
# Expected: 2 columns, 5 bubbles per question
print("Pattern Analysis:")
print("-" * 80)

# Find rows with 10 bubbles (2 questions x 5 variants)
question_rows = [row for row in rows if len(row) >= 8]  # At least 8 bubbles

print(f"Found {len(question_rows)} potential question rows")
print()

if question_rows:
    # Analyze first question row
    first_row = question_rows[0]
    first_row.sort(key=lambda b: b['x'])
    
    print("First question row bubbles:")
    for i, bubble in enumerate(first_row):
        print(f"  {i+1}. X={bubble['x']}, Y={bubble['y']}, R={bubble['radius']}")
    
    print()
    
    # Try to identify 2 groups (2 questions)
    if len(first_row) >= 10:
        # Split into left and right groups
        mid_x = (first_row[0]['x'] + first_row[-1]['x']) / 2
        left_group = [b for b in first_row if b['x'] < mid_x]
        right_group = [b for b in first_row if b['x'] >= mid_x]
        
        print(f"Left group (Q1): {len(left_group)} bubbles")
        if left_group:
            print(f"  X range: {left_group[0]['x']} - {left_group[-1]['x']}")
            print(f"  Y average: {sum(b['y'] for b in left_group) / len(left_group):.0f}")
        
        print(f"Right group (Q2): {len(right_group)} bubbles")
        if right_group:
            print(f"  X range: {right_group[0]['x']} - {right_group[-1]['x']}")
            print(f"  Y average: {sum(b['y'] for b in right_group) / len(right_group):.0f}")

print()

# Draw all bubbles on image
output = img.copy()
for bubble in bubbles:
    cv2.circle(output, (bubble['x'], bubble['y']), bubble['radius'], (0, 255, 0), 2)
    cv2.circle(output, (bubble['x'], bubble['y']), 2, (0, 0, 255), -1)  # Center dot

# Draw row lines
for row in rows[:20]:  # First 20 rows
    if row:
        avg_y = int(sum(b['y'] for b in row) / len(row))
        cv2.line(output, (0, avg_y), (img.shape[1], avg_y), (255, 0, 0), 1)

# Save annotated image
cv2.imwrite('test_images/5-imtihon_analysis.jpg', output)
print(f"✅ Saved analysis image: test_images/5-imtihon_analysis.jpg")
print()

# Calculate expected coordinates based on PDF layout
print("Expected Coordinates (from PDF layout):")
print("-" * 80)

# Image will be resized to 2480x3508
target_width = 2480
target_height = 3508

# Original image size
orig_width = img.shape[1]
orig_height = img.shape[0]

# Scale factors
scale_x = target_width / orig_width
scale_y = target_height / orig_height

print(f"Original: {orig_width}x{orig_height}")
print(f"Target: {target_width}x{target_height}")
print(f"Scale: X={scale_x:.3f}, Y={scale_y:.3f}")
print()

# PDF layout (in mm)
paper_width_mm = 210
paper_height_mm = 297
grid_start_x_mm = 25
grid_start_y_mm = 149  # NEW value
bubble_spacing_mm = 8
first_bubble_offset_mm = 8
row_height_mm = 5.5

# Convert to pixels (target size)
px_per_mm_x = target_width / paper_width_mm
px_per_mm_y = target_height / paper_height_mm

print(f"Pixels per mm: X={px_per_mm_x:.2f}, Y={px_per_mm_y:.2f}")
print()

# Calculate Q1 bubble positions (in target size)
q1_y_px = (grid_start_y_mm + 2) * px_per_mm_y  # +2mm offset
q1_x_base_px = grid_start_x_mm * px_per_mm_x

print("Question 1 expected positions (target size):")
variants = ['A', 'B', 'C', 'D', 'E']
for i, variant in enumerate(variants):
    bubble_x_px = q1_x_base_px + (first_bubble_offset_mm + i * bubble_spacing_mm) * px_per_mm_x
    print(f"  {variant}: ({bubble_x_px:.1f}, {q1_y_px:.1f})")

print()

# Scale back to original size
print("Question 1 expected positions (original size):")
for i, variant in enumerate(variants):
    bubble_x_px = q1_x_base_px + (first_bubble_offset_mm + i * bubble_spacing_mm) * px_per_mm_x
    orig_x = bubble_x_px / scale_x
    orig_y = q1_y_px / scale_y
    print(f"  {variant}: ({orig_x:.1f}, {orig_y:.1f})")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total bubbles found: {len(bubbles)}")
print(f"Expected: 40 questions x 5 variants = 200 bubbles")
print(f"Rows detected: {len(rows)}")
print(f"Expected: 20 rows (2 questions per row)")
print()

if len(bubbles) < 150:
    print("⚠️  WARNING: Too few bubbles detected!")
    print("   Possible issues:")
    print("   - This is a PHOTO, not a PDF-generated sheet")
    print("   - Layout is different from expected")
    print("   - Need to use photo-specific detection")
else:
    print("✅ Bubble count looks reasonable")

print()
print("Next step: Check test_images/5-imtihon_analysis.jpg to verify bubble detection")
