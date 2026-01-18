"""
Fix Real Coordinate Issue
Haqiqiy rasmda koordinata muammosini hal qilish
"""
import cv2
import numpy as np
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_correct_template():
    """
    Haqiqiy rasm uchun to'g'ri template yaratish
    """
    # Rasmdan o'lchangan haqiqiy parametrlar
    template = {
        "version": "2.0",
        "timestamp": "2026-01-17T12:00:00Z",
        "cornerMarkers": {
            "topLeft": {"x": 12.5, "y": 12.5},
            "topRight": {"x": 197.5, "y": 12.5},
            "bottomLeft": {"x": 12.5, "y": 284.5},
            "bottomRight": {"x": 197.5, "y": 284.5}
        },
        "layout": {
            "paperWidth": 210,
            "paperHeight": 297,
            "questionsPerRow": 2,
            "bubbleSpacing": 8,
            "bubbleRadius": 2.5,
            "rowHeight": 5.5,
            "gridStartX": 25,
            "gridStartY": 149,
            "questionSpacing": 90,
            "firstBubbleOffset": 8
        },
        "questions": {}
    }
    
    # 35 ta savol uchun koordinatalar yaratish
    question_number = 1
    current_y_mm = template["layout"]["gridStartY"]
    
    for row in range(18):  # 18 ta row (35 savol uchun)
        for col in range(2):  # 2 ta column
            if question_number > 35:
                break
                
            # Question position (mm)
            question_x_mm = template["layout"]["gridStartX"] + (col * template["layout"]["questionSpacing"])
            question_y_mm = current_y_mm
            
            # Bubble coordinates
            bubbles = []
            variants = ['A', 'B', 'C', 'D', 'E']
            
            for v_idx, variant in enumerate(variants):
                bubble_x_mm = question_x_mm + template["layout"]["firstBubbleOffset"] + (v_idx * template["layout"]["bubbleSpacing"])
                bubble_y_mm = question_y_mm + 2  # +2mm offset
                
                # Convert to relative coordinates (0-1)
                relative_x = bubble_x_mm / template["layout"]["paperWidth"]
                relative_y = bubble_y_mm / template["layout"]["paperHeight"]
                
                bubbles.append({
                    "variant": variant,
                    "relativeX": relative_x,
                    "relativeY": relative_y
                })
            
            template["questions"][str(question_number)] = {
                "bubbles": bubbles
            }
            
            question_number += 1
        
        current_y_mm += template["layout"]["rowHeight"]
    
    return template

def fix_coordinate_issue():
    """
    Koordinata muammosini hal qilish
    """
    logger.info("🔧 FIXING REAL COORDINATE ISSUE")
    logger.info("=" * 50)
    
    # Rasmni yuklash
    image_path = "../5-imtihon-test-varag'i.jpg"
    
    if not Path(image_path).exists():
        logger.error(f"❌ Image not found: {image_path}")
        return
    
    image = cv2.imread(image_path)
    if image is None:
        logger.error("❌ Failed to load image")
        return
    
    logger.info(f"✅ Image loaded: {image.shape[1]}x{image.shape[0]}")
    
    # 1. To'g'ri template yaratish
    logger.info("\n📐 STEP 1: Creating Correct Template")
    logger.info("-" * 40)
    
    template = create_correct_template()
    logger.info(f"✅ Template created with {len(template['questions'])} questions")
    
    # Template'ni saqlash
    with open("correct_template.json", "w") as f:
        json.dump(template, f, indent=2)
    logger.info("✅ Template saved: correct_template.json")
    
    # 2. Corner detection
    logger.info("\n📍 STEP 2: Corner Detection")
    logger.info("-" * 40)
    
    try:
        from services.improved_corner_detector import ImprovedCornerDetector
        
        detector = ImprovedCornerDetector()
        corners = detector.detect_corners(image)
        
        if corners and len(corners) == 4:
            logger.info("✅ Corners detected:")
            for corner in corners:
                logger.info(f"  {corner['name']}: ({corner['x']:.1f}, {corner['y']:.1f})")
        else:
            logger.error("❌ Corner detection failed")
            return
            
    except Exception as e:
        logger.error(f"Corner detection error: {e}")
        return
    
    # 3. Template-based coordinate calculation
    logger.info("\n📊 STEP 3: Template-based Coordinate Calculation")
    logger.info("-" * 40)
    
    try:
        from utils.template_coordinate_mapper import TemplateCoordinateMapper
        
        mapper = TemplateCoordinateMapper(corners, template)
        coordinates = mapper.calculate_all()
        
        logger.info(f"✅ Coordinates calculated for {len(coordinates)} questions")
        
        # Birinchi 5 ta savolning koordinatalarini ko'rsatish
        for q_num in range(1, min(6, len(coordinates) + 1)):
            if q_num in coordinates:
                bubbles = coordinates[q_num]['bubbles']
                logger.info(f"  Q{q_num}:")
                for bubble in bubbles:
                    logger.info(f"    {bubble['variant']}: ({bubble['x']:.1f}, {bubble['y']:.1f})")
        
    except Exception as e:
        logger.error(f"Coordinate calculation error: {e}")
        return
    
    # 4. Visual verification
    logger.info("\n🖼️ STEP 4: Visual Verification")
    logger.info("-" * 40)
    
    annotated = image.copy()
    
    # Draw calculated coordinates
    for q_num, q_data in coordinates.items():
        for bubble in q_data['bubbles']:
            x, y = int(bubble['x']), int(bubble['y'])
            radius = int(bubble.get('radius', 8))
            
            # Draw bubble circle
            cv2.circle(annotated, (x, y), radius, (0, 255, 0), 2)
            
            # Draw variant label
            cv2.putText(annotated, bubble['variant'], (x-5, y+5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        
        # Draw question number
        if q_data['bubbles']:
            first_bubble = q_data['bubbles'][0]
            x, y = int(first_bubble['x'] - 20), int(first_bubble['y'])
            cv2.putText(annotated, str(q_num), (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    # Draw corners
    for corner in corners:
        x, y = int(corner['x']), int(corner['y'])
        cv2.circle(annotated, (x, y), 10, (255, 0, 0), -1)
        cv2.putText(annotated, corner['name'], (x-30, y-15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # Save annotated image
    output_path = "fixed_coordinates_verification.jpg"
    cv2.imwrite(output_path, annotated)
    logger.info(f"✅ Verification image saved: {output_path}")
    
    # 5. Test OMR detection
    logger.info("\n🔍 STEP 5: Test OMR Detection")
    logger.info("-" * 40)
    
    try:
        from services.omr_detector import OMRDetector
        
        # Test exam structure
        exam_structure = {
            'subjects': [
                {
                    'id': 'subject1',
                    'name': 'Test Subject',
                    'sections': [
                        {
                            'id': 'section1',
                            'name': 'Test Section',
                            'questionCount': 35
                        }
                    ]
                }
            ]
        }
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        detector = OMRDetector()
        results = detector.detect_all_answers(gray, coordinates, exam_structure)
        
        logger.info(f"✅ OMR Detection Results:")
        logger.info(f"  Total: {results['statistics']['total']}")
        logger.info(f"  Detected: {results['statistics']['detected']}")
        logger.info(f"  No mark: {results['statistics']['no_mark']}")
        logger.info(f"  Multiple marks: {results['statistics']['multiple_marks']}")
        
        # Show first 10 detections
        logger.info("\nFirst 10 detections:")
        count = 0
        for topic_id, topic_data in results['answers'].items():
            for section_id, section_data in topic_data.items():
                for answer in section_data:
                    if count < 10:
                        q_num = answer['questionNumber']
                        detected = answer.get('answer', 'None')
                        confidence = answer.get('confidence', 0)
                        logger.info(f"  Q{q_num}: {detected} (confidence: {confidence:.1f})")
                        count += 1
        
    except Exception as e:
        logger.error(f"OMR detection error: {e}")
    
    # 6. Create final annotated image with results
    logger.info("\n🎨 STEP 6: Create Final Annotated Image")
    logger.info("-" * 40)
    
    try:
        final_annotated = image.copy()
        
        # Draw all coordinates and detection results
        for topic_id, topic_data in results['answers'].items():
            for section_id, section_data in topic_data.items():
                for answer in section_data:
                    q_num = answer['questionNumber']
                    detected_answer = answer.get('answer')
                    confidence = answer.get('confidence', 0)
                    
                    if q_num in coordinates:
                        bubbles = coordinates[q_num]['bubbles']
                        
                        for bubble in bubbles:
                            x, y = int(bubble['x']), int(bubble['y'])
                            radius = int(bubble.get('radius', 8))
                            
                            # Color based on detection
                            if bubble['variant'] == detected_answer:
                                if confidence > 70:
                                    color = (0, 255, 0)  # Green - high confidence
                                else:
                                    color = (0, 255, 255)  # Yellow - low confidence
                            else:
                                color = (128, 128, 128)  # Gray - not detected
                            
                            cv2.circle(final_annotated, (x, y), radius, color, 2)
                            cv2.putText(final_annotated, bubble['variant'], (x-5, y+5), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Save final image
        final_output_path = "final_coordinate_fix_result.jpg"
        cv2.imwrite(final_output_path, final_annotated)
        logger.info(f"✅ Final result saved: {final_output_path}")
        
    except Exception as e:
        logger.error(f"Final annotation error: {e}")
    
    logger.info("\n✅ COORDINATE ISSUE FIX COMPLETE!")
    logger.info("Check the following files:")
    logger.info("1. correct_template.json - Corrected template")
    logger.info("2. fixed_coordinates_verification.jpg - Coordinate verification")
    logger.info("3. final_coordinate_fix_result.jpg - Final result with detection")

if __name__ == "__main__":
    fix_coordinate_issue()