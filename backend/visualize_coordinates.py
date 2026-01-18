"""
Visualize coordinates on simulated image to see if they match
"""
import sys
import os
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.image_processor import ImageProcessor
from utils.coordinate_mapper import CoordinateMapper
from config import settings

print("=" * 80)
print("VISUALIZE COORDINATES")
print("=" * 80)
print()

# Exam structure
exam_structure = {
    'subjects': [
        {
            'id': 'subject-1',
            'name': 'Test Subject',
            'sections': [
                {
                    'id': 'section-1',
                    'name': 'Test Section',
                    'questionCount': 40,
                    'correctScore': 1,
                    'wrongScore': 0
                }
            ]
        }
    ]
}

# Process image
print("1. Processing image...")
processor = ImageProcessor(
    target_width=settings.TARGET_WIDTH,
    target_height=settings.TARGET_HEIGHT
)

result = processor.process('test_images/5-imtihon-simulated.jpg')
print(f"✅ Processed: {result['processed'].shape[1]}x{result['processed'].shape[0]}")
print()

# Generate coordinates
print("2. Generating coordinates...")
mapper = CoordinateMapper(
    image_width=result['processed'].shape[1],
    image_height=result['processed'].shape[0],
    exam_structure=exam_structure,
    qr_layout=None
)

coordinates = mapper.calculate_all()
print(f"✅ Generated {len(coordinates)} question coordinates")
print()

# Draw coordinates on image
print("3. Drawing coordinates...")
vis = cv2.cvtColor(result['grayscale'], cv2.COLOR_GRAY2BGR)

# Draw first 5 questions
for q_num in range(1, 6):
    if q_num not in coordinates:
        continue
    
    bubbles = coordinates[q_num]['bubbles']
    
    print(f"Question {q_num}:")
    for bubble in bubbles:
        x = int(bubble['x'])
        y = int(bubble['y'])
        r = int(bubble['radius'])
        variant = bubble['variant']
        
        print(f"  {variant}: ({x}, {y}) r={r}")
        
        # Draw circle
        if variant == 'A':
            color = (0, 0, 255)  # Red for A (should be filled)
        elif variant == 'B':
            color = (0, 255, 0)  # Green for B
        elif variant == 'C':
            color = (255, 0, 0)  # Blue for C
        elif variant == 'D':
            color = (0, 255, 255)  # Yellow for D
        else:
            color = (255, 0, 255)  # Magenta for E
        
        cv2.circle(vis, (x, y), r, color, 2)
        cv2.circle(vis, (x, y), 2, color, -1)  # Center dot
        
        # Label
        cv2.putText(vis, variant, (x - 5, y - r - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    print()

# Save
output_path = 'test_images/5-imtihon-simulated-coordinates.jpg'
cv2.imwrite(output_path, vis)

print(f"✅ Saved: {output_path}")
print()
print("Check the image to see if coordinates match the bubbles!")
print("Red (A) should be on filled bubbles for Q1")
print()
print("=" * 80)
