"""
Check darkness of filled bubbles in simulated image
"""
import cv2
import numpy as np

print("=" * 80)
print("CHECK FILLED BUBBLE DARKNESS")
print("=" * 80)
print()

# Load image
img = cv2.imread('test_images/5-imtihon-simulated.jpg', cv2.IMREAD_GRAYSCALE)
if img is None:
    print("ERROR: Cannot load image!")
    exit(1)

print(f"Image size: {img.shape[1]}x{img.shape[0]}")
print()

# Q1 bubble A should be filled (correct answer)
# Position: X=390, Y=1782, R=27

px_per_mm = img.shape[1] / 210

# Calculate Q1 bubble positions
grid_start_x_mm = 25
grid_start_y_mm = 149
first_bubble_offset_mm = 8
bubble_spacing_mm = 8

q1_y = int((grid_start_y_mm + 2) * px_per_mm)
q1_x_base = int(grid_start_x_mm * px_per_mm)

print("Checking Q1 bubbles:")
print("-" * 80)

variants = ['A', 'B', 'C', 'D', 'E']
correct_answer = 'A'  # Q1 correct answer

for i, variant in enumerate(variants):
    x = int(q1_x_base + (first_bubble_offset_mm + i * bubble_spacing_mm) * px_per_mm)
    y = q1_y
    r = int(2.5 * px_per_mm)  # bubble radius
    
    # Extract ROI
    roi = img[y-r:y+r, x-r:x+r]
    
    if roi.size == 0:
        print(f"{variant}: ERROR - ROI empty")
        continue
    
    # Create circular mask
    mask = np.zeros(roi.shape, dtype=np.uint8)
    cv2.circle(mask, (r, r), r, 255, -1)
    
    # Get pixels inside circle
    circle_pixels = roi[mask > 0]
    
    if len(circle_pixels) == 0:
        print(f"{variant}: ERROR - No pixels in circle")
        continue
    
    # Calculate darkness
    mean_brightness = np.mean(circle_pixels)
    darkness = (255 - mean_brightness) / 255 * 100
    
    # Check if filled
    is_filled = variant == correct_answer
    status = "✅ FILLED" if is_filled else "⚪ EMPTY"
    
    print(f"{variant}: Brightness={mean_brightness:.1f}, Darkness={darkness:.1f}% {status}")

print()

# Check a few more questions
print("Checking Q2-Q5 (first bubble of each):")
print("-" * 80)

correct_answers = ['A', 'B', 'C', 'D', 'E']  # Q1-Q5

for q_num in range(1, 6):
    row = (q_num - 1) // 2
    col = (q_num - 1) % 2
    
    q_y_mm = grid_start_y_mm + (row * 5.5) + 2
    q_x_mm = grid_start_x_mm + (col * 90)
    
    q_y = int(q_y_mm * px_per_mm)
    q_x_base = int(q_x_mm * px_per_mm)
    
    correct_answer = correct_answers[q_num - 1]
    
    # Check all bubbles
    for i, variant in enumerate(variants):
        x = int(q_x_base + (first_bubble_offset_mm + i * bubble_spacing_mm) * px_per_mm)
        y = q_y
        r = int(2.5 * px_per_mm)
        
        # Extract ROI
        roi = img[y-r:y+r, x-r:x+r]
        
        if roi.size == 0:
            continue
        
        # Create circular mask
        mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(mask, (r, r), r, 255, -1)
        
        # Get pixels
        circle_pixels = roi[mask > 0]
        
        if len(circle_pixels) == 0:
            continue
        
        # Calculate darkness
        mean_brightness = np.mean(circle_pixels)
        darkness = (255 - mean_brightness) / 255 * 100
        
        # Only show filled bubble
        if variant == correct_answer:
            print(f"Q{q_num} {variant}: Brightness={mean_brightness:.1f}, Darkness={darkness:.1f}% ✅ FILLED")

print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print("Filled bubbles should have:")
print("  - Low brightness (close to 0)")
print("  - High darkness (close to 100%)")
print()
print("If darkness < 35%, MIN_DARKNESS threshold needs to be lowered")
print()
print("=" * 80)
