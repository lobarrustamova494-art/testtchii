"""
Diagnostic script to identify alignment issues
"""
import cv2
import numpy as np
from services.image_processor import ImageProcessor
from utils.coordinate_mapper import CoordinateMapper
import json

def diagnose_image(image_path: str, exam_structure_path: str):
    """
    Rasmni tahlil qilish va alignment muammolarini topish
    """
    print("=" * 60)
    print("ALIGNMENT DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Load exam structure
    with open(exam_structure_path, 'r', encoding='utf-8') as f:
        exam_structure = json.load(f)
    
    # Process image
    processor = ImageProcessor()
    result = processor.process(image_path)
    
    print(f"\n1. IMAGE PROCESSING")
    print(f"   Original size: {result['original'].shape[1]}x{result['original'].shape[0]}")
    print(f"   Processed size: {result['processed'].shape[1]}x{result['processed'].shape[0]}")
    print(f"   Corners detected: {len(result['corners'])}/4")
    
    if len(result['corners']) < 4:
        print("   ⚠️  WARNING: Not all corners detected! Using default corners.")
        print("   This means NO perspective correction was applied!")
    
    # Calculate coordinates
    mapper = CoordinateMapper(
        result['dimensions']['width'],
        result['dimensions']['height'],
        exam_structure
    )
    coordinates = mapper.calculate_all()
    
    print(f"\n2. COORDINATE CALCULATION")
    print(f"   Image dimensions: {result['dimensions']['width']}x{result['dimensions']['height']}")
    print(f"   Pixels per mm (X): {mapper.px_per_mm_x:.2f}")
    print(f"   Pixels per mm (Y): {mapper.px_per_mm_y:.2f}")
    print(f"   Total questions: {len(coordinates)}")
    
    # Check first few questions
    print(f"\n3. SAMPLE COORDINATES (First 3 questions)")
    for q_num in [1, 2, 3]:
        if q_num in coordinates:
            coords = coordinates[q_num]
            bubbles = coords['bubbles']
            print(f"\n   Question {q_num}:")
            print(f"   Variant A: X={bubbles[0]['x']:.1f}px, Y={bubbles[0]['y']:.1f}px, R={bubbles[0]['radius']:.1f}px")
            print(f"   Variant E: X={bubbles[4]['x']:.1f}px, Y={bubbles[4]['y']:.1f}px, R={bubbles[4]['radius']:.1f}px")
    
    # Check column spacing
    if 1 in coordinates and 2 in coordinates:
        q1_x = coordinates[1]['bubbles'][0]['x']
        q2_x = coordinates[2]['bubbles'][0]['x']
        spacing_px = q2_x - q1_x
        spacing_mm = spacing_px / mapper.px_per_mm_x
        print(f"\n4. COLUMN SPACING")
        print(f"   Q1 to Q2 spacing: {spacing_px:.1f}px ({spacing_mm:.1f}mm)")
        print(f"   Expected: 90mm")
        if abs(spacing_mm - 90) > 2:
            print(f"   ⚠️  WARNING: Spacing mismatch! Expected 90mm, got {spacing_mm:.1f}mm")
    
    # Check row spacing
    if 1 in coordinates and 3 in coordinates:
        q1_y = coordinates[1]['bubbles'][0]['y']
        q3_y = coordinates[3]['bubbles'][0]['y']
        spacing_px = q3_y - q1_y
        spacing_mm = spacing_px / mapper.px_per_mm_y
        print(f"\n5. ROW SPACING")
        print(f"   Q1 to Q3 spacing: {spacing_px:.1f}px ({spacing_mm:.1f}mm)")
        print(f"   Expected: 5.5mm")
        if abs(spacing_mm - 5.5) > 0.5:
            print(f"   ⚠️  WARNING: Spacing mismatch! Expected 5.5mm, got {spacing_mm:.1f}mm")
    
    # Visual check - draw rectangles on image
    print(f"\n6. CREATING VISUAL DEBUG IMAGE")
    annotated = cv2.cvtColor(result['processed'], cv2.COLOR_GRAY2BGR)
    
    # Draw first 10 questions
    for q_num in range(1, min(11, len(coordinates) + 1)):
        if q_num in coordinates:
            coords = coordinates[q_num]
            for bubble in coords['bubbles']:
                x = int(bubble['x'])
                y = int(bubble['y'])
                radius = int(bubble['radius'])
                
                # Draw circle at bubble center
                cv2.circle(annotated, (x, y), 2, (0, 0, 255), -1)  # Red dot
                
                # Draw rectangle
                padding = 3
                x1 = x - radius - padding
                y1 = y - radius - padding
                x2 = x + radius + padding
                y2 = y + radius + padding
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rect
                
                # Draw variant label
                cv2.putText(annotated, bubble['variant'], (x-3, y+3), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
    
    # Save debug image
    output_path = 'debug_alignment.jpg'
    cv2.imwrite(output_path, annotated)
    print(f"   Debug image saved: {output_path}")
    print(f"   Check this image to see if rectangles align with bubbles!")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python diagnose_alignment.py <image_path> <exam_structure_json>")
        print("Example: python diagnose_alignment.py test_image.jpg exam_structure.json")
        sys.exit(1)
    
    diagnose_image(sys.argv[1], sys.argv[2])
