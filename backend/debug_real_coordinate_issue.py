"""
Real Coordinate Issue Debug
Haqiqiy production muammosini hal qilish
"""
import cv2
import numpy as np
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_real_coordinate_issue():
    """
    Haqiqiy koordinata muammosini debug qilish
    """
    logger.info("🔍 REAL COORDINATE ISSUE DEBUG")
    logger.info("=" * 50)
    
    # Test image
    image_path = "../5-imtihon-test-varag'i.jpg"
    
    if not Path(image_path).exists():
        logger.error(f"❌ Image not found: {image_path}")
        return
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        logger.error("❌ Failed to load image")
        return
    
    logger.info(f"✅ Image loaded: {image.shape[1]}x{image.shape[0]}")
    
    # 1. COORDINATE TEMPLATE ANALYSIS
    logger.info("\n📐 STEP 1: Coordinate Template Analysis")
    logger.info("-" * 40)
    
    # Simulate coordinate template from exam creation
    coordinate_template = {
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
            "gridStartY": 149,  # CRITICAL: This might be wrong!
            "questionSpacing": 90,
            "firstBubbleOffset": 8
        }
    }
    
    logger.info(f"Template grid start: ({coordinate_template['layout']['gridStartX']}, {coordinate_template['layout']['gridStartY']})")
    
    # 2. CORNER DETECTION
    logger.info("\n🔍 STEP 2: Corner Detection")
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
            logger.warning("⚠️ Corner detection failed")
            # Use default corners for analysis
            h, w = image.shape[:2]
            corners = [
                {'name': 'top-left', 'x': 0, 'y': 0},
                {'name': 'top-right', 'x': w, 'y': 0},
                {'name': 'bottom-left', 'x': 0, 'y': h},
                {'name': 'bottom-right', 'x': w, 'y': h}
            ]
            logger.info("Using default corners for analysis")
    
    except Exception as e:
        logger.error(f"Corner detection error: {e}")
        return
    
    # 3. COORDINATE CALCULATION WITH TEMPLATE
    logger.info("\n📊 STEP 3: Template-based Coordinate Calculation")
    logger.info("-" * 40)
    
    try:
        from utils.template_coordinate_mapper import TemplateCoordinateMapper
        
        mapper = TemplateCoordinateMapper(corners, coordinate_template)
        coordinates = mapper.calculate_all()
        
        logger.info(f"✅ Coordinates calculated for {len(coordinates)} questions")
        
        # Show first few coordinates
        for q_num in range(1, min(6, len(coordinates) + 1)):
            if q_num in coordinates:
                bubbles = coordinates[q_num]['bubbles']
                logger.info(f"Q{q_num}:")
                for bubble in bubbles:
                    logger.info(f"  {bubble['variant']}: ({bubble['x']:.1f}, {bubble['y']:.1f})")
    
    except Exception as e:
        logger.error(f"Template coordinate calculation error: {e}")
        return
    
    # 4. VISUAL COORDINATE VERIFICATION
    logger.info("\n🎯 STEP 4: Visual Coordinate Verification")
    logger.info("-" * 40)
    
    # Create visualization
    vis_image = image.copy()
    
    # Draw calculated coordinates
    for q_num in range(1, min(11, len(coordinates) + 1)):  # First 10 questions
        if q_num in coordinates:
            bubbles = coordinates[q_num]['bubbles']
            for bubble in bubbles:
                x, y = int(bubble['x']), int(bubble['y'])
                radius = int(bubble.get('radius', 8))
                
                # Draw circle
                cv2.circle(vis_image, (x, y), radius, (0, 255, 0), 2)
                
                # Draw variant label
                cv2.putText(vis_image, f"Q{q_num}-{bubble['variant']}", 
                           (x-10, y-15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
    
    # Save visualization
    output_path = "coordinate_verification.jpg"
    cv2.imwrite(output_path, vis_image)
    logger.info(f"✅ Coordinate visualization saved: {output_path}")
    
    # 5. BUBBLE DETECTION TEST
    logger.info("\n🔍 STEP 5: Bubble Detection Test")
    logger.info("-" * 40)
    
    try:
        from services.omr_detector import OMRDetector
        
        # Create exam structure for testing
        exam_structure = {
            'subjects': [
                {
                    'id': 'subject1',
                    'name': 'Test Subject',
                    'sections': [
                        {
                            'id': 'section1',
                            'name': 'Test Section',
                            'questionCount': 40
                        }
                    ]
                }
            ]
        }
        
        # Test OMR detection
        omr_detector = OMRDetector()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        omr_results = omr_detector.detect_all_answers(gray, coordinates, exam_structure)
        
        logger.info(f"OMR Detection Results:")
        logger.info(f"  Total: {omr_results['statistics']['total']}")
        logger.info(f"  Detected: {omr_results['statistics']['detected']}")
        logger.info(f"  No mark: {omr_results['statistics']['no_mark']}")
        logger.info(f"  Multiple marks: {omr_results['statistics']['multiple_marks']}")
        
        # Show first few detections
        logger.info("\nFirst 10 detections:")
        question_num = 1
        for topic in omr_results['answers'].values():
            for section in topic.values():
                for answer in section[:10]:  # First 10
                    detected = answer.get('answer', 'None')
                    confidence = answer.get('confidence', 0)
                    logger.info(f"  Q{question_num}: {detected} (confidence: {confidence:.1f})")
                    question_num += 1
                    if question_num > 10:
                        break
                if question_num > 10:
                    break
            if question_num > 10:
                break
    
    except Exception as e:
        logger.error(f"OMR detection test error: {e}")
    
    # 6. COORDINATE ADJUSTMENT ANALYSIS
    logger.info("\n🔧 STEP 6: Coordinate Adjustment Analysis")
    logger.info("-" * 40)
    
    # Analyze if coordinates need adjustment
    logger.info("Analyzing coordinate accuracy...")
    
    # Manual verification points (from visual inspection)
    manual_points = [
        # Q1: Should be around these positions (visual estimate)
        {'question': 1, 'variant': 'A', 'expected_x': 150, 'expected_y': 200},
        {'question': 1, 'variant': 'B', 'expected_x': 170, 'expected_y': 200},
        # Add more manual points based on visual inspection
    ]
    
    if coordinates and 1 in coordinates:
        q1_bubbles = coordinates[1]['bubbles']
        logger.info("Q1 coordinate comparison:")
        for bubble in q1_bubbles[:2]:  # A and B
            calculated_x, calculated_y = bubble['x'], bubble['y']
            
            # Find corresponding manual point
            manual_point = next((p for p in manual_points 
                               if p['question'] == 1 and p['variant'] == bubble['variant']), None)
            
            if manual_point:
                expected_x, expected_y = manual_point['expected_x'], manual_point['expected_y']
                diff_x = abs(calculated_x - expected_x)
                diff_y = abs(calculated_y - expected_y)
                
                logger.info(f"  {bubble['variant']}: Calculated({calculated_x:.1f}, {calculated_y:.1f}) vs Expected({expected_x}, {expected_y})")
                logger.info(f"    Difference: ({diff_x:.1f}, {diff_y:.1f}) pixels")
                
                if diff_x > 10 or diff_y > 10:
                    logger.warning(f"    ⚠️ Large difference detected!")
    
    # 7. RECOMMENDATIONS
    logger.info("\n💡 STEP 7: Recommendations")
    logger.info("-" * 40)
    
    logger.info("Based on analysis, here are the recommendations:")
    logger.info("1. Check coordinate_verification.jpg for visual accuracy")
    logger.info("2. If coordinates are off, adjust template parameters")
    logger.info("3. Consider using manual calibration for 100% accuracy")
    logger.info("4. Test with different corner detection strategies")
    
    logger.info("\n✅ Real coordinate issue debug complete!")

if __name__ == "__main__":
    debug_real_coordinate_issue()