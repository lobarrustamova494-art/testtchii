"""
FULL SYSTEM DEBUG - Barcha qadamlarni tekshirish
Bu script barcha qadamlarni birin-ketin bajaradi va har bir qadamda nima bo'layotganini ko'rsatadi
"""
import cv2
import numpy as np
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.image_processor import ImageProcessor
from services.omr_detector import OMRDetector
from services.qr_reader import QRCodeReader
from services.ocr_anchor_detector import OCRAnchorDetector
from utils.coordinate_mapper import CoordinateMapper
from utils.relative_coordinate_mapper import RelativeCoordinateMapper
from utils.template_coordinate_mapper import TemplateCoordinateMapper

def debug_full_system(image_path: str):
    """
    Barcha qadamlarni debug qilish
    """
    print("=" * 80)
    print("FULL SYSTEM DEBUG")
    print("=" * 80)
    
    # Load image
    print(f"\n📁 Loading image: {image_path}")
    if not Path(image_path).exists():
        print(f"❌ File not found: {image_path}")
        return
    
    # STEP 1: Image Processing
    print("\n" + "=" * 80)
    print("STEP 1: IMAGE PROCESSING")
    print("=" * 80)
    
    processor = ImageProcessor(target_width=2480, target_height=3508)
    processed = processor.process(image_path)
    
    print(f"✅ Image processed")
    print(f"   Dimensions: {processed['dimensions']['width']}x{processed['dimensions']['height']}")
    print(f"   Quality: {processed['quality']}")
    print(f"   Corners found: {len(processed['corners']) if processed['corners'] else 0}/4")
    
    if processed['corners']:
        print(f"   Corner positions:")
        for i, corner in enumerate(processed['corners']):
            print(f"      Corner {i+1}: ({corner[0]:.1f}, {corner[1]:.1f})")
    else:
        print(f"   ⚠️  NO CORNERS FOUND!")
    
    # STEP 2: QR Code Detection
    print("\n" + "=" * 80)
    print("STEP 2: QR CODE DETECTION")
    print("=" * 80)
    
    qr_reader = QRCodeReader()
    qr_data = qr_reader.read_qr_code(processed['grayscale'])
    
    if qr_data:
        print(f"✅ QR Code detected")
        print(f"   Data: {qr_data}")
        qr_layout = qr_reader.get_layout_from_qr(qr_data)
        print(f"   Layout: {qr_layout}")
    else:
        print(f"⚠️  No QR code found")
        qr_layout = None
    
    # STEP 3: Load exam structure (minimal for testing)
    print("\n" + "=" * 80)
    print("STEP 3: EXAM STRUCTURE")
    print("=" * 80)
    
    # Minimal exam structure for 40 questions
    exam_data = {
        'subjects': [
            {
                'id': 'subject1',
                'sections': [
                    {'id': 'section1', 'questionCount': 40}
                ]
            }
        ]
    }
    
    print(f"✅ Using minimal exam structure: 40 questions")
    
    # STEP 4: Coordinate Calculation
    print("\n" + "=" * 80)
    print("STEP 4: COORDINATE CALCULATION")
    print("=" * 80)
    
    coordinates = None
    coord_system = None
    
    # Try OCR Anchor
    print("\n🔍 Trying OCR Anchor Detection...")
    ocr_detector = OCRAnchorDetector()
    coordinates = ocr_detector.detect_all_with_anchors(processed['grayscale'], exam_data)
    
    if coordinates:
        coord_system = "OCR_ANCHOR"
        print(f"✅ OCR Anchor Detection SUCCESS")
        print(f"   Detected {len(coordinates)} questions")
    else:
        print(f"⚠️  OCR Anchor Detection FAILED")
        
        # Try Corner-based
        if processed['corners'] and len(processed['corners']) == 4:
            print("\n🔍 Trying Corner-based System...")
            coord_mapper = RelativeCoordinateMapper(
                processed['corners'],
                exam_data,
                qr_layout=qr_layout
            )
            coordinates = coord_mapper.calculate_all()
            coord_system = "CORNER_BASED"
            print(f"✅ Corner-based System SUCCESS")
            print(f"   Calculated {len(coordinates)} questions")
        else:
            print("\n🔍 Trying Fallback System...")
            coord_mapper = CoordinateMapper(
                processed['dimensions']['width'],
                processed['dimensions']['height'],
                exam_data,
                qr_layout=qr_layout
            )
            coordinates = coord_mapper.calculate_all()
            coord_system = "FALLBACK"
            print(f"⚠️  Using FALLBACK System")
            print(f"   Calculated {len(coordinates)} questions")
    
    # Show sample coordinates
    if coordinates:
        print(f"\n📊 Sample Coordinates (Q1, Q20, Q40):")
        for q_num in [1, 20, 40]:
            if q_num in coordinates:
                coord = coordinates[q_num]
                print(f"   Q{q_num}:")
                print(f"      Question number position: ({coord['questionNumber']['x']:.1f}, {coord['questionNumber']['y']:.1f})")
                print(f"      Bubbles:")
                for bubble in coord['bubbles']:
                    print(f"         {bubble['variant']}: ({bubble['x']:.1f}, {bubble['y']:.1f}) r={bubble['radius']:.1f}")
    
    # STEP 5: OMR Detection
    print("\n" + "=" * 80)
    print("STEP 5: OMR DETECTION")
    print("=" * 80)
    
    omr_detector = OMRDetector()
    omr_results = omr_detector.detect_all_answers(
        processed['processed'],
        coordinates,
        exam_data
    )
    
    print(f"✅ OMR Detection complete")
    print(f"   Total questions: {omr_results['statistics']['total']}")
    print(f"   Detected answers: {omr_results['statistics']['detected']}")
    print(f"   No marks: {omr_results['statistics']['no_mark']}")
    print(f"   Uncertain: {omr_results['statistics']['uncertain']}")
    print(f"   Multiple marks: {omr_results['statistics']['multiple_marks']}")
    
    # Show sample detections
    print(f"\n📊 Sample Detections (Q1-10):")
    for topic in omr_results['answers'].values():
        for section in topic.values():
            for i, result in enumerate(section[:10]):
                q_num = result['questionNumber']
                answer = result['answer'] if result['answer'] else 'NO_MARK'
                confidence = result['confidence']
                warning = result.get('warning', '')
                print(f"   Q{q_num}: {answer} (confidence: {confidence}%) {warning}")
    
    # STEP 6: Visual Debug
    print("\n" + "=" * 80)
    print("STEP 6: VISUAL DEBUG")
    print("=" * 80)
    
    # Create debug image
    debug_img = cv2.cvtColor(processed['grayscale'], cv2.COLOR_GRAY2BGR)
    
    # Draw coordinates for first 10 questions
    for q_num in range(1, min(11, len(coordinates) + 1)):
        if q_num not in coordinates:
            continue
        
        coord = coordinates[q_num]
        
        # Draw question number position (BLUE)
        qn_x = int(coord['questionNumber']['x'])
        qn_y = int(coord['questionNumber']['y'])
        cv2.circle(debug_img, (qn_x, qn_y), 5, (255, 0, 0), -1)
        cv2.putText(debug_img, f"Q{q_num}", (qn_x + 10, qn_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Draw bubbles (GREEN)
        for bubble in coord['bubbles']:
            bx = int(bubble['x'])
            by = int(bubble['y'])
            br = int(bubble['radius'])
            cv2.circle(debug_img, (bx, by), br, (0, 255, 0), 2)
            cv2.putText(debug_img, bubble['variant'], (bx - 5, by + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    # Save debug image
    output_path = "debug_full_system.jpg"
    cv2.imwrite(output_path, debug_img)
    print(f"✅ Debug image saved: {output_path}")
    print(f"   Blue circles = Question number positions")
    print(f"   Green circles = Bubble positions")
    
    # SUMMARY
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Coordinate System: {coord_system}")
    print(f"Corners Found: {len(processed['corners']) if processed['corners'] else 0}/4")
    print(f"QR Code: {'YES' if qr_data else 'NO'}")
    print(f"Questions: {len(coordinates)}")
    print(f"Detected Answers: {omr_results['statistics']['detected']}/{omr_results['statistics']['total']}")
    
    if coord_system == "FALLBACK":
        print("\n⚠️  WARNING: Using FALLBACK system!")
        print("   This means corner detection failed.")
        print("   Coordinates may be inaccurate.")
        print("   Solutions:")
        print("   1. Check if corner markers are visible in the image")
        print("   2. Adjust corner detection threshold")
        print("   3. Improve print quality")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_full_system.py <image_path>")
        print("Example: python debug_full_system.py test_image.jpg")
        sys.exit(1)
    
    debug_full_system(sys.argv[1])
