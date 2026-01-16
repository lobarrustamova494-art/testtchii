"""
Diagnose coordinate calculation issues
Compare PDF generator formulas with coordinate mapper
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.coordinate_mapper import CoordinateMapper

print("=" * 80)
print("COORDINATE DIAGNOSIS")
print("=" * 80)

# Simulate exam structure
exam_structure = {
    'subjects': [
        {
            'id': 'topic1',
            'name': 'Mavzu 1',
            'sections': [
                {
                    'id': 'section1',
                    'name': 'Bo\'lim 1.1',
                    'questionCount': 35
                }
            ]
        }
    ]
}

# Create mapper
mapper = CoordinateMapper(1240, 1754, exam_structure)
coords = mapper.calculate_all()

print("\nPDF GENERATOR FORMULAS:")
print("-" * 80)
print("const xPos = xStart + j * 90")
print("const bubbleX = xPos + 8 + vIndex * bubbleSpacing")
print("const bubbleY = currentY + 2")
print()
print("For first column (j=0):")
print("  xPos = 25mm")
print("  Bubble A (vIndex=0): 25 + 8 + 0*8 = 33mm")
print("  Bubble B (vIndex=1): 25 + 8 + 1*8 = 41mm")
print("  Bubble C (vIndex=2): 25 + 8 + 2*8 = 49mm")
print("  Bubble D (vIndex=3): 25 + 8 + 3*8 = 57mm")
print("  Bubble E (vIndex=4): 25 + 8 + 4*8 = 65mm")

print("\nCOORDINATE MAPPER CALCULATIONS:")
print("-" * 80)
print(f"grid_start_x_mm: {mapper.grid_start_x_mm}mm")
print(f"first_bubble_offset_mm: {mapper.first_bubble_offset_mm}mm")
print(f"bubble_spacing_mm: {mapper.bubble_spacing_mm}mm")
print(f"question_spacing_mm: {mapper.question_spacing_mm}mm")
print()

# Check Question 1 (first column)
q1 = coords[1]
print("Question 1 (first column):")
for bubble in q1['bubbles']:
    x_mm = bubble['x'] / mapper.px_per_mm_x
    print(f"  Bubble {bubble['variant']}: {x_mm:.2f}mm ({bubble['x']:.1f}px)")

# Check Question 2 (second column)
q2 = coords[2]
print("\nQuestion 2 (second column):")
for bubble in q2['bubbles']:
    x_mm = bubble['x'] / mapper.px_per_mm_x
    print(f"  Bubble {bubble['variant']}: {x_mm:.2f}mm ({bubble['x']:.1f}px)")

print("\nCOMPARISON:")
print("-" * 80)

# Expected values from PDF
expected_q1 = {
    'A': 33, 'B': 41, 'C': 49, 'D': 57, 'E': 65
}
expected_q2 = {
    'A': 123, 'B': 131, 'C': 139, 'D': 147, 'E': 155
}

print("Question 1:")
for bubble in q1['bubbles']:
    x_mm = bubble['x'] / mapper.px_per_mm_x
    expected = expected_q1[bubble['variant']]
    diff = x_mm - expected
    status = "✅" if abs(diff) < 0.1 else "❌"
    print(f"  {bubble['variant']}: Expected {expected}mm, Got {x_mm:.2f}mm, Diff {diff:+.2f}mm {status}")

print("\nQuestion 2:")
for bubble in q2['bubbles']:
    x_mm = bubble['x'] / mapper.px_per_mm_x
    expected = expected_q2[bubble['variant']]
    diff = x_mm - expected
    status = "✅" if abs(diff) < 0.1 else "❌"
    print(f"  {bubble['variant']}: Expected {expected}mm, Got {x_mm:.2f}mm, Diff {diff:+.2f}mm {status}")

print("\n" + "=" * 80)
print("Y-COORDINATE CHECK")
print("=" * 80)

print(f"\ngrid_start_y_mm: {mapper.grid_start_y_mm}mm")
print(f"row_height_mm: {mapper.row_height_mm}mm")
print()

# Check first few questions
for q_num in [1, 2, 3, 5, 7, 11, 13]:
    if q_num in coords:
        q = coords[q_num]
        y_mm = q['bubbles'][0]['y'] / mapper.px_per_mm_y
        print(f"Question {q_num}: Y = {y_mm:.2f}mm ({q['bubbles'][0]['y']:.1f}px)")

print("\n" + "=" * 80)
