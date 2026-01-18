"""
Debug single bubble detection - Q1 bubble A (should be filled)
"""
import cv2
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.image_processor import ImageProcessor
from services.omr_detector import OMRDetector
from config import settings

print("=" * 80)
print("DEBUG SINGLE BUBBLE - Q1 Bubble A")
print("=" * 80)
print()

# Process image
processor = ImageProcessor(
    target_width=settings.TARGET_WIDTH,
    target_height=settings.TARGET_HEIGHT
)

result = processor.process('test_images/5-imtihon-simulated.jpg')
image = result.get('gray_for_omr', result['grayscale'])

print(f"Image processed: {image.shape[1]}x{image.shape[0]}")
print(f"Using: {'gray_for_omr' if 'gray_for_omr' in result else 'grayscale'}")
print()

# Q1 Bubble A coordinates
px_per_mm = image.shape[1] / 210
grid_start_x_mm = 25
grid_start_y_mm = 149
first_bubble_offset_mm = 8

q1_y = int((grid_start_y_mm + 2) * px_per_mm)
q1_x_base = int(grid_start_x_mm * px_per_mm)
bubble_a_x = int(q1_x_base + first_bubble_offset_mm * px_per_mm)
bubble_a_y = q1_y

print(f"Q1 Bubble A position: ({bubble_a_x}, {bubble_a_y})")
print()

# Create detector
detector = OMRDetector(
    bubble_radius=settings.BUBBLE_RADIUS,
    min_darkness=settings.MIN_DARKNESS,
    min_difference=settings.MIN_DIFFERENCE,
    multiple_marks_threshold=settings.MULTIPLE_MARKS_THRESHOLD
)

# Manually call detect_single_bubble
coords = {
    'x': bubble_a_x,
    'y': bubble_a_y,
    'radius': settings.BUBBLE_RADIUS
}

print("Analyzing bubble...")
print(f"  Bubble radius: {settings.BUBBLE_RADIUS} pixels")
print(f"  MIN_DARKNESS: {settings.MIN_DARKNESS}%")
print(f"  MIN_INNER_FILL: {settings.MIN_INNER_FILL}%")
print()

# Extract ROI
x, y, r = coords['x'], coords['y'], coords['radius']

# ROI size
roi_size = r * 3
x1 = max(0, x - roi_size)
y1 = max(0, y - roi_size)
x2 = min(image.shape[1], x + roi_size)
y2 = min(image.shape[0], y + roi_size)

roi = image[y1:y2, x1:x2]

print(f"ROI extracted: {roi.shape[1]}x{roi.shape[0]}")
print(f"  ROI position: ({x1}, {y1}) to ({x2}, {y2})")
print()

# Create masks
mask_full = np.zeros(roi.shape, dtype=np.uint8)
mask_inner = np.zeros(roi.shape, dtype=np.uint8)

# Local center
local_x = x - x1
local_y = y - y1

cv2.circle(mask_full, (local_x, local_y), r, 255, -1)
cv2.circle(mask_inner, (local_x, local_y), int(r * 0.8), 255, -1)

# Get pixels
full_pixels = roi[mask_full > 0]
inner_pixels = roi[mask_inner > 0]

print(f"Pixels in full circle: {len(full_pixels)}")
print(f"Pixels in inner circle: {len(inner_pixels)}")
print()

# Calculate metrics
if len(full_pixels) > 0:
    mean_brightness = np.mean(full_pixels)
    darkness = (255 - mean_brightness) / 255 * 100
    
    print(f"Mean brightness: {mean_brightness:.1f}")
    print(f"Darkness: {darkness:.1f}%")
    print()
    
    # Coverage
    threshold = 127
    dark_pixels = np.sum(full_pixels < threshold)
    coverage = dark_pixels / len(full_pixels) * 100
    
    print(f"Dark pixels (< {threshold}): {dark_pixels}/{len(full_pixels)}")
    print(f"Coverage: {coverage:.1f}%")
    print()
    
    # Inner fill
    if len(inner_pixels) > 0:
        inner_dark = np.sum(inner_pixels < threshold)
        inner_fill = inner_dark / len(inner_pixels) * 100
        
        print(f"Inner dark pixels: {inner_dark}/{len(inner_pixels)}")
        print(f"Inner fill: {inner_fill:.1f}%")
        print()
    
    # Decision
    print("Decision logic:")
    print(f"  1. Inner fill ({inner_fill:.1f}%) >= MIN_INNER_FILL ({settings.MIN_INNER_FILL}%)? ", end="")
    if inner_fill >= settings.MIN_INNER_FILL:
        print("✅ YES")
    else:
        print("❌ NO - REJECTED!")
    
    print(f"  2. Darkness ({darkness:.1f}%) >= MIN_DARKNESS ({settings.MIN_DARKNESS}%)? ", end="")
    if darkness >= settings.MIN_DARKNESS:
        print("✅ YES")
    else:
        print("❌ NO - REJECTED!")
    
    print()
    
    if inner_fill >= settings.MIN_INNER_FILL and darkness >= settings.MIN_DARKNESS:
        print("✅ BUBBLE SHOULD BE DETECTED AS FILLED")
    else:
        print("❌ BUBBLE WILL BE REJECTED")
        print()
        print("Possible issues:")
        if inner_fill < settings.MIN_INNER_FILL:
            print(f"  - Inner fill too low: {inner_fill:.1f}% < {settings.MIN_INNER_FILL}%")
            print("  - Bubble may not be fully filled")
            print("  - Or bubble radius is wrong")
        if darkness < settings.MIN_DARKNESS:
            print(f"  - Darkness too low: {darkness:.1f}% < {settings.MIN_DARKNESS}%")
            print("  - Mark is too light")

else:
    print("❌ ERROR: No pixels in circle!")

print()
print("=" * 80)

# Save debug image
debug_img = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
cv2.circle(debug_img, (local_x, local_y), r, (0, 255, 0), 2)  # Full circle
cv2.circle(debug_img, (local_x, local_y), int(r * 0.8), (0, 0, 255), 2)  # Inner circle
cv2.circle(debug_img, (local_x, local_y), 2, (255, 0, 0), -1)  # Center

cv2.imwrite('test_images/debug_bubble_q1a.jpg', debug_img)
print("Debug image saved: test_images/debug_bubble_q1a.jpg")
print()
print("=" * 80)
