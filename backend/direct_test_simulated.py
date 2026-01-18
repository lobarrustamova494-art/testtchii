"""
Direct test - load image without ImageProcessor
"""
import cv2
import numpy as np

print("=" * 80)
print("DIRECT TEST - NO IMAGE PROCESSOR")
print("=" * 80)
print()

# Load image directly
img = cv2.imread('test_images/5-imtihon-simulated.jpg', cv2.IMREAD_GRAYSCALE)
if img is None:
    print("ERROR: Cannot load image!")
    exit(1)

print(f"Image size: {img.shape[1]}x{img.shape[0]}")
print()

# Q1 Bubble A position
px_per_mm = img.shape[1] / 210
grid_start_x_mm = 25
grid_start_y_mm = 149
first_bubble_offset_mm = 8

q1_y = int((grid_start_y_mm + 2) * px_per_mm)
q1_x_base = int(grid_start_x_mm * px_per_mm)
bubble_a_x = int(q1_x_base + first_bubble_offset_mm * px_per_mm)
bubble_a_y = q1_y
radius = 29

print(f"Q1 Bubble A position: ({bubble_a_x}, {bubble_a_y})")
print(f"Radius: {radius}")
print()

# Extract ROI
roi_radius = int(radius * 1.1)
x1 = max(0, bubble_a_x - roi_radius)
y1 = max(0, bubble_a_y - roi_radius)
x2 = min(img.shape[1], bubble_a_x + roi_radius)
y2 = min(img.shape[0], bubble_a_y + roi_radius)

roi = img[y1:y2, x1:x2]

print(f"ROI size: {roi.shape[1]}x{roi.shape[0]}")
print(f"ROI position: ({x1}, {y1}) to ({x2}, {y2})")
print()

# Create mask
center_x = bubble_a_x - x1
center_y = bubble_a_y - y1

mask = np.zeros(roi.shape, dtype=np.uint8)
cv2.circle(mask, (center_x, center_y), radius, 255, -1)

# Get pixels
pixels = roi[mask > 0]

if len(pixels) > 0:
    mean_brightness = np.mean(pixels)
    darkness = (255 - mean_brightness) / 255 * 100
    
    print(f"Mean brightness: {mean_brightness:.1f}")
    print(f"Darkness: {darkness:.1f}%")
    print()
    
    # Check threshold
    _, binary = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY_INV)
    dark_pixels = np.sum(binary[mask > 0] > 0)
    coverage = dark_pixels / len(pixels) * 100
    
    print(f"Dark pixels (< 127): {dark_pixels}/{len(pixels)}")
    print(f"Coverage: {coverage:.1f}%")
    print()
    
    if darkness > 90:
        print("✅ BUBBLE IS FILLED (darkness > 90%)")
    elif darkness > 50:
        print("⚠️  BUBBLE MAY BE FILLED (darkness 50-90%)")
    else:
        print("❌ BUBBLE IS NOT FILLED (darkness < 50%)")
else:
    print("❌ ERROR: No pixels in mask!")

print()
print("=" * 80)

# Save debug image
debug_img = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
cv2.circle(debug_img, (center_x, center_y), radius, (0, 255, 0), 2)
cv2.circle(debug_img, (center_x, center_y), 2, (0, 0, 255), -1)

cv2.imwrite('test_images/debug_direct_test.jpg', debug_img)
print("Debug image saved: test_images/debug_direct_test.jpg")
print()
print("=" * 80)
