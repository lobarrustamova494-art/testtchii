"""
Check where bubbles actually are in the simulated image
"""
import cv2
import numpy as np

print("=" * 80)
print("CHECK ACTUAL BUBBLE POSITIONS")
print("=" * 80)
print()

# Load simulated image
img = cv2.imread('test_images/5-imtihon-simulated.jpg', cv2.IMREAD_GRAYSCALE)
if img is None:
    print("ERROR: Cannot load image!")
    exit(1)

print(f"Image size: {img.shape[1]}x{img.shape[0]}")
print()

# Find circles (bubbles) using Hough Circle Transform
circles = cv2.HoughCircles(
    img,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=30,
    param1=50,
    param2=30,
    minRadius=20,
    maxRadius=40
)

if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    print(f"Found {len(circles)} circles")
    print()
    
    # Sort by Y, then X
    circles = sorted(circles, key=lambda c: (c[1], c[0]))
    
    # Show first 10 circles
    print("First 10 circles (should be Q1 and Q2):")
    print("-" * 80)
    for i, (x, y, r) in enumerate(circles[:10]):
        print(f"{i+1:2d}. X={x:4d}, Y={y:4d}, R={r:2d}")
    
    print()
    
    # Group by rows
    rows = []
    current_row = []
    last_y = -100
    
    for x, y, r in circles:
        if abs(y - last_y) < 20:  # Same row
            current_row.append((x, y, r))
        else:
            if current_row:
                rows.append(current_row)
            current_row = [(x, y, r)]
        last_y = y
    
    if current_row:
        rows.append(current_row)
    
    print(f"Grouped into {len(rows)} rows")
    print()
    
    # Show first 5 rows
    print("First 5 rows (should be Q1-10):")
    print("-" * 80)
    for i, row in enumerate(rows[:5]):
        row_sorted = sorted(row, key=lambda c: c[0])
        avg_y = sum(c[1] for c in row) / len(row)
        print(f"Row {i+1}: {len(row)} bubbles at Y≈{avg_y:.0f}")
        
        # Show X positions
        x_positions = [c[0] for c in row_sorted]
        print(f"  X positions: {x_positions}")
        
        # If 10 bubbles, split into 2 questions
        if len(row_sorted) >= 10:
            q1_bubbles = row_sorted[:5]
            q2_bubbles = row_sorted[5:10]
            
            print(f"  Q{i*2+1} (A-E): X={[c[0] for c in q1_bubbles]}")
            print(f"  Q{i*2+2} (A-E): X={[c[0] for c in q2_bubbles]}")
        
        print()
    
    # Calculate expected coordinates
    print("Expected coordinates (from PDF layout):")
    print("-" * 80)
    
    px_per_mm = img.shape[1] / 210  # 11.81 px/mm
    
    grid_start_x_mm = 25
    grid_start_y_mm = 149
    bubble_spacing_mm = 8
    first_bubble_offset_mm = 8
    question_spacing_mm = 90
    row_height_mm = 5.5
    
    # Q1 position
    q1_y = int((grid_start_y_mm + 2) * px_per_mm)  # +2mm offset
    q1_x_base = int(grid_start_x_mm * px_per_mm)
    
    print(f"Q1 Y position: {q1_y}")
    print(f"Q1 X base: {q1_x_base}")
    print()
    
    print("Q1 bubble positions (expected):")
    for i, variant in enumerate(['A', 'B', 'C', 'D', 'E']):
        x = int(q1_x_base + (first_bubble_offset_mm + i * bubble_spacing_mm) * px_per_mm)
        print(f"  {variant}: X={x}, Y={q1_y}")
    
    print()
    
    # Compare with actual
    if rows:
        first_row = sorted(rows[0], key=lambda c: c[0])
        print("Q1 bubble positions (actual):")
        for i, (x, y, r) in enumerate(first_row[:5]):
            variant = ['A', 'B', 'C', 'D', 'E'][i]
            print(f"  {variant}: X={x}, Y={y}")
        
        print()
        
        # Calculate offset
        expected_x = int(q1_x_base + first_bubble_offset_mm * px_per_mm)
        actual_x = first_row[0][0]
        expected_y = q1_y
        actual_y = first_row[0][1]
        
        offset_x = actual_x - expected_x
        offset_y = actual_y - expected_y
        
        print(f"Offset: X={offset_x}, Y={offset_y}")
        print()
        
        if abs(offset_x) > 10 or abs(offset_y) > 10:
            print("⚠️  SIGNIFICANT OFFSET DETECTED!")
            print("   Coordinates need adjustment")
        else:
            print("✅ Coordinates match well")

else:
    print("❌ No circles found!")
    print("   Try adjusting Hough Circle parameters")

print()
print("=" * 80)
