"""
Debug script to analyze bubble positions and understand the 1-position shift
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.coordinate_mapper import CoordinateMapper

# Simulate image dimensions (A4 at 150 DPI)
image_width = 1240
image_height = 1754

# Simple exam structure (just 1 question for testing)
exam_structure = {
    'subjects': [
        {
            'id': 'topic1',
            'name': 'Test Topic',
            'sections': [
                {
                    'id': 'section1',
                    'name': 'Test Section',
                    'questionCount': 1
                }
            ]
        }
    ]
}

# Create mapper
mapper = CoordinateMapper(image_width, image_height, exam_structure)

# Calculate coordinates
coords = mapper.calculate_all()

# Print Question 1 bubble positions
print("=" * 80)
print("QUESTION 1 BUBBLE POSITIONS")
print("=" * 80)

q1 = coords[1]
print(f"\nQuestion Number: {q1['questionNumber']}")
print(f"\nBubbles:")
print(f"{'Variant':<10} {'X (px)':<15} {'Y (px)':<15} {'Radius (px)':<15}")
print("-" * 60)

for bubble in q1['bubbles']:
    print(f"{bubble['variant']:<10} {bubble['x']:<15.2f} {bubble['y']:<15.2f} {bubble['radius']:<15.2f}")

# Calculate spacing between bubbles
print(f"\n{'Spacing Analysis:'}")
print("-" * 60)
for i in range(len(q1['bubbles']) - 1):
    b1 = q1['bubbles'][i]
    b2 = q1['bubbles'][i + 1]
    spacing = b2['x'] - b1['x']
    print(f"{b1['variant']} → {b2['variant']}: {spacing:.2f} px")

# Print PDF layout parameters
print(f"\n{'PDF Layout Parameters:'}")
print("-" * 60)
print(f"Grid Start X: {mapper.grid_start_x_mm} mm = {mapper.grid_start_x_mm * mapper.px_per_mm_x:.2f} px")
print(f"Grid Start Y: {mapper.grid_start_y_mm} mm = {mapper.grid_start_y_mm * mapper.px_per_mm_y:.2f} px")
print(f"First Bubble Offset: {mapper.first_bubble_offset_mm} mm = {mapper.first_bubble_offset_mm * mapper.px_per_mm_x:.2f} px")
print(f"Bubble Spacing: {mapper.bubble_spacing_mm} mm = {mapper.bubble_spacing_mm * mapper.px_per_mm_x:.2f} px")
print(f"Bubble Radius: {mapper.bubble_radius_mm} mm = {mapper.bubble_radius_mm * mapper.px_per_mm_x:.2f} px")

# Calculate expected positions manually
print(f"\n{'Manual Calculation Verification:'}")
print("-" * 60)
question_x_mm = mapper.grid_start_x_mm  # 25mm for first column
question_y_mm = mapper.grid_start_y_mm  # 149mm

print(f"Question X: {question_x_mm} mm")
print(f"Question Y: {question_y_mm} mm")
print(f"\nExpected bubble positions:")

variants = ['A', 'B', 'C', 'D', 'E']
for v_idx, variant in enumerate(variants):
    bubble_x_mm = question_x_mm + mapper.first_bubble_offset_mm + (v_idx * mapper.bubble_spacing_mm)
    bubble_y_mm = question_y_mm + 2  # +2mm offset in PDF
    
    bubble_x_px = bubble_x_mm * mapper.px_per_mm_x
    bubble_y_px = bubble_y_mm * mapper.px_per_mm_y
    
    print(f"{variant}: X={bubble_x_mm}mm ({bubble_x_px:.2f}px), Y={bubble_y_mm}mm ({bubble_y_px:.2f}px)")

print("\n" + "=" * 80)
