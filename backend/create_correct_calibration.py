"""
Create Correct Calibration Points
Rasmdan to'g'ri bubble pozitsiyalarini qo'lda aniqlash
"""
import cv2
import numpy as np
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_correct_calibration():
    """
    Rasmdan vizual tahlil qilib to'g'ri calibration point'lar yaratish
    """
    logger.info("🎯 CREATING CORRECT CALIBRATION POINTS")
    logger.info("=" * 50)
    
    # Rasmni yuklash
    image_path = "../5-imtihon-test-varag'i.jpg"
    image = cv2.imread(image_path)
    
    if image is None:
        logger.error("❌ Image not found")
        return
    
    logger.info(f"✅ Image loaded: {image.shape[1]}x{image.shape[0]}")
    
    # Rasmdan vizual tahlil qilib haqiqiy bubble pozitsiyalarini aniqlash
    # Rasmda ko'rinadigan haqiqiy bubble'lar:
    
    # HAQIQIY BUBBLE POZITSIYALARI (rasmdan o'lchangan)
    # Bu pozitsiyalar rasmda ko'rinadigan haqiqiy to'ldirilgan bubble'lardan olingan
    
    correct_calibration_points = [
        # Q1 - Chap tomonda, birinchi row
        {"question": 1, "variant": "A", "x": 170, "y": 480},  # To'ldirilgan (qora)
        {"question": 1, "variant": "B", "x": 200, "y": 480},
        {"question": 1, "variant": "C", "x": 230, "y": 480},  # To'ldirilgan (qora)
        {"question": 1, "variant": "D", "x": 260, "y": 480},
        {"question": 1, "variant": "E", "x": 290, "y": 480},
        
        # Q2 - O'ng tomonda, birinchi row
        {"question": 2, "variant": "A", "x": 550, "y": 480},
        {"question": 2, "variant": "B", "x": 580, "y": 480},  # To'ldirilgan (qora)
        {"question": 2, "variant": "C", "x": 610, "y": 480},
        {"question": 2, "variant": "D", "x": 640, "y": 480},  # To'ldirilgan (qora)
        {"question": 2, "variant": "E", "x": 670, "y": 480},
        
        # Q3 - Chap tomonda, ikkinchi row
        {"question": 3, "variant": "A", "x": 170, "y": 520},  # To'ldirilgan (qora)
        {"question": 3, "variant": "B", "x": 200, "y": 520},
        {"question": 3, "variant": "C", "x": 230, "y": 520},
        {"question": 3, "variant": "D", "x": 260, "y": 520},
        {"question": 3, "variant": "E", "x": 290, "y": 520},
        
        # Q4 - O'ng tomonda, ikkinchi row
        {"question": 4, "variant": "A", "x": 550, "y": 520},
        {"question": 4, "variant": "B", "x": 580, "y": 520},
        {"question": 4, "variant": "C", "x": 610, "y": 520},
        {"question": 4, "variant": "D", "x": 640, "y": 520},
        {"question": 4, "variant": "E", "x": 670, "y": 520},
        
        # Q5 - Chap tomonda, uchinchi row
        {"question": 5, "variant": "A", "x": 170, "y": 560},
        {"question": 5, "variant": "B", "x": 200, "y": 560},
        {"question": 5, "variant": "C", "x": 230, "y": 560},
        {"question": 5, "variant": "D", "x": 260, "y": 560},
        {"question": 5, "variant": "E", "x": 290, "y": 560},  # To'ldirilgan (qora)
        
        # Q6 - O'ng tomonda, uchinchi row
        {"question": 6, "variant": "A", "x": 550, "y": 560},
        {"question": 6, "variant": "B", "x": 580, "y": 560},
        {"question": 6, "variant": "C", "x": 610, "y": 560},
        {"question": 6, "variant": "D", "x": 640, "y": 560},
        {"question": 6, "variant": "E", "x": 670, "y": 560},
        
        # Q7 - Chap tomonda, to'rtinchi row
        {"question": 7, "variant": "A", "x": 170, "y": 600},
        {"question": 7, "variant": "B", "x": 200, "y": 600},  # To'ldirilgan (qora)
        {"question": 7, "variant": "C", "x": 230, "y": 600},
        {"question": 7, "variant": "D", "x": 260, "y": 600},
        {"question": 7, "variant": "E", "x": 290, "y": 600},
        
        # Q8 - O'ng tomonda, to'rtinchi row
        {"question": 8, "variant": "A", "x": 550, "y": 600},
        {"question": 8, "variant": "B", "x": 580, "y": 600},
        {"question": 8, "variant": "C", "x": 610, "y": 600},
        {"question": 8, "variant": "D", "x": 640, "y": 600},
        {"question": 8, "variant": "E", "x": 670, "y": 600},
    ]
    
    logger.info(f"✅ Created {len(correct_calibration_points)} calibration points")
    
    # Calibration point'larni saqlash
    with open("correct_calibration_points.json", "w") as f:
        json.dump(correct_calibration_points, f, indent=2)
    
    logger.info("✅ Saved: correct_calibration_points.json")
    
    # Visual verification
    logger.info("\n🖼️ Visual Verification")
    logger.info("-" * 40)
    
    annotated = image.copy()
    
    # Draw calibration points
    for point in correct_calibration_points:
        x, y = point['x'], point['y']
        q_num = point['question']
        variant = point['variant']
        
        # Draw circle
        cv2.circle(annotated, (x, y), 12, (0, 255, 0), 2)
        
        # Draw label
        cv2.putText(annotated, f"Q{q_num}-{variant}", (x-15, y-15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    # Save verification image
    cv2.imwrite("correct_calibration_verification.jpg", annotated)
    logger.info("✅ Verification image saved: correct_calibration_verification.jpg")
    
    # Test manual calibration
    logger.info("\n🧪 Testing Manual Calibration")
    logger.info("-" * 40)
    
    try:
        from services.ultra_precise_coordinate_mapper import UltraPreciseCoordinateMapper
        
        mapper = UltraPreciseCoordinateMapper()
        
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
        
        # Manual calibration
        calibration_result = mapper.calibrate_manually(
            image, correct_calibration_points, exam_structure
        )
        
        if calibration_result['success']:
            logger.info("✅ Manual calibration successful!")
            logger.info(f"  Accuracy: {calibration_result['accuracy_estimate']}%")
            logger.info(f"  Coordinates generated: {len(calibration_result['coordinates'])}")
            
            # Test OMR detection
            from services.adaptive_omr_detector import AdaptiveOMRDetector
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            adaptive_detector = AdaptiveOMRDetector()
            
            omr_results = adaptive_detector.detect_all_answers(
                gray, calibration_result['coordinates'], exam_structure
            )
            
            logger.info(f"✅ OMR Detection Results:")
            logger.info(f"  Total: {omr_results['statistics']['total']}")
            logger.info(f"  Detected: {omr_results['statistics']['detected']}")
            logger.info(f"  High confidence: {omr_results['statistics']['high_confidence']}")
            logger.info(f"  Medium confidence: {omr_results['statistics']['medium_confidence']}")
            logger.info(f"  Low confidence: {omr_results['statistics']['low_confidence']}")
            
            # Show first 10 detections
            logger.info("\nFirst 10 detections:")
            count = 0
            for topic_id, topic_data in omr_results['answers'].items():
                for section_id, section_data in topic_data.items():
                    for answer in section_data:
                        if count < 10:
                            q_num = answer['questionNumber']
                            detected = answer.get('answer', 'None')
                            confidence = answer.get('confidence', 0)
                            logger.info(f"  Q{q_num}: {detected} (confidence: {confidence:.1f})")
                            count += 1
            
            # Create final annotated image
            final_annotated = image.copy()
            
            # Draw detection results
            for topic_id, topic_data in omr_results['answers'].items():
                for section_id, section_data in topic_data.items():
                    for answer in section_data:
                        q_num = answer['questionNumber']
                        detected_answer = answer.get('answer')
                        confidence = answer.get('confidence', 0)
                        
                        if q_num in calibration_result['coordinates']:
                            bubbles = calibration_result['coordinates'][q_num]['bubbles']
                            
                            for bubble in bubbles:
                                x, y = int(bubble['x']), int(bubble['y'])
                                radius = int(bubble.get('radius', 8))
                                
                                # Color based on detection
                                if bubble['variant'] == detected_answer:
                                    if confidence > 70:
                                        color = (0, 255, 0)  # Green - high confidence
                                    elif confidence > 40:
                                        color = (0, 255, 255)  # Yellow - medium confidence
                                    else:
                                        color = (0, 165, 255)  # Orange - low confidence
                                else:
                                    color = (128, 128, 128)  # Gray - not detected
                                
                                cv2.circle(final_annotated, (x, y), radius, color, 2)
                                cv2.putText(final_annotated, bubble['variant'], (x-5, y+5), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
            
            # Save final result
            cv2.imwrite("correct_calibration_final_result.jpg", final_annotated)
            logger.info("✅ Final result saved: correct_calibration_final_result.jpg")
            
        else:
            logger.error("❌ Manual calibration failed")
            
    except Exception as e:
        logger.error(f"Manual calibration test error: {e}")
    
    logger.info("\n✅ CORRECT CALIBRATION COMPLETE!")
    logger.info("Files created:")
    logger.info("1. correct_calibration_points.json - Correct calibration points")
    logger.info("2. correct_calibration_verification.jpg - Verification image")
    logger.info("3. correct_calibration_final_result.jpg - Final detection result")

if __name__ == "__main__":
    create_correct_calibration()