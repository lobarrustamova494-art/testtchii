"""
Measure Real Bubbles
Haqiqiy rasmdan bubble pozitsiyalarini o'lchash va to'g'ri koordinatalar yaratish
"""
import cv2
import numpy as np
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def measure_real_bubbles():
    """
    Haqiqiy rasmdan bubble pozitsiyalarini o'lchash
    """
    logger.info("📏 MEASURING REAL BUBBLE POSITIONS")
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
    
    # 1. Bubble detection bilan haqiqiy pozitsiyalarni topish
    logger.info("\n🔍 STEP 1: Detecting Real Bubble Positions")
    logger.info("-" * 40)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Multiple HoughCircles parameters for better detection
    bubble_candidates = []
    
    # Parameter set 1: Conservative
    circles1 = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=15,
        param1=50, param2=25, minRadius=8, maxRadius=20
    )
    if circles1 is not None:
        for (x, y, r) in np.round(circles1[0, :]).astype("int"):
            bubble_candidates.append((x, y, r, 'conservative'))
    
    # Parameter set 2: Aggressive
    circles2 = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=12,
        param1=40, param2=20, minRadius=6, maxRadius=25
    )
    if circles2 is not None:
        for (x, y, r) in np.round(circles2[0, :]).astype("int"):
            bubble_candidates.append((x, y, r, 'aggressive'))
    
    # Parameter set 3: Sensitive
    circles3 = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=10,
        param1=30, param2=15, minRadius=5, maxRadius=30
    )
    if circles3 is not None:
        for (x, y, r) in np.round(circles3[0, :]).astype("int"):
            bubble_candidates.append((x, y, r, 'sensitive'))
    
    logger.info(f"✅ Found {len(bubble_candidates)} bubble candidates")
    
    # 2. Duplicate removal va filtering
    logger.info("\n🔧 STEP 2: Filtering and Deduplication")
    logger.info("-" * 40)
    
    # Remove duplicates (bubbles too close to each other)
    filtered_bubbles = []
    min_distance = 15
    
    for candidate in bubble_candidates:
        x, y, r, method = candidate
        is_duplicate = False
        
        for existing in filtered_bubbles:
            ex_x, ex_y, ex_r, ex_method = existing
            distance = np.sqrt((x - ex_x)**2 + (y - ex_y)**2)
            if distance < min_distance:
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_bubbles.append(candidate)
    
    logger.info(f"✅ After filtering: {len(filtered_bubbles)} unique bubbles")
    
    # 3. Row detection va analysis
    logger.info("\n📊 STEP 3: Row Detection and Analysis")
    logger.info("-" * 40)
    
    # Sort by Y coordinate
    bubbles_sorted = sorted(filtered_bubbles, key=lambda b: (b[1], b[0]))
    
    # Group into rows
    rows = []
    current_row = []
    row_tolerance = 20
    
    for bubble in bubbles_sorted:
        x, y, r, method = bubble
        if not current_row:
            current_row.append(bubble)
        else:
            avg_y = sum(b[1] for b in current_row) / len(current_row)
            if abs(y - avg_y) <= row_tolerance:
                current_row.append(bubble)
            else:
                if len(current_row) >= 3:  # Minimum bubbles per row
                    rows.append(current_row)
                current_row = [bubble]
    
    if len(current_row) >= 3:
        rows.append(current_row)
    
    logger.info(f"✅ Detected {len(rows)} rows")
    
    # Analyze each row
    row_analysis = []
    for i, row in enumerate(rows):
        row_sorted = sorted(row, key=lambda b: b[0])  # Sort by X
        y_avg = sum(b[1] for b in row) / len(row)
        x_positions = [b[0] for b in row_sorted]
        
        # Calculate spacings
        spacings = []
        if len(x_positions) > 1:
            spacings = [x_positions[j+1] - x_positions[j] for j in range(len(x_positions)-1)]
        
        row_info = {
            'row_index': i,
            'y_position': y_avg,
            'bubble_count': len(row),
            'x_positions': x_positions,
            'spacings': spacings,
            'avg_spacing': np.mean(spacings) if spacings else 0
        }
        row_analysis.append(row_info)
        
        logger.info(f"  Row {i+1}: Y={y_avg:.1f}, {len(row)} bubbles, avg_spacing={row_info['avg_spacing']:.1f}")
    
    # 4. Question structure analysis
    logger.info("\n🎯 STEP 4: Question Structure Analysis")
    logger.info("-" * 40)
    
    # Analyze bubble patterns to identify questions
    # Assumption: 5 bubbles per question (A, B, C, D, E)
    questions_detected = []
    
    for row_info in row_analysis:
        if row_info['bubble_count'] >= 5:
            # Try to group bubbles into questions
            x_positions = row_info['x_positions']
            spacings = row_info['spacings']
            
            # Find larger gaps (between questions)
            if spacings:
                avg_spacing = np.mean(spacings)
                large_gaps = [i for i, spacing in enumerate(spacings) if spacing > avg_spacing * 1.5]
                
                # Split into questions based on large gaps
                question_starts = [0] + [gap + 1 for gap in large_gaps]
                
                for start_idx in question_starts:
                    end_idx = min(start_idx + 5, len(x_positions))
                    if end_idx - start_idx >= 5:
                        question_bubbles = []
                        for j in range(start_idx, start_idx + 5):
                            if j < len(x_positions):
                                question_bubbles.append({
                                    'variant': ['A', 'B', 'C', 'D', 'E'][j - start_idx],
                                    'x': x_positions[j],
                                    'y': row_info['y_position']
                                })
                        
                        if len(question_bubbles) == 5:
                            questions_detected.append(question_bubbles)
    
    logger.info(f"✅ Detected {len(questions_detected)} complete questions")
    
    # 5. Create corrected coordinate template
    logger.info("\n📐 STEP 5: Creating Corrected Coordinate Template")
    logger.info("-" * 40)
    
    if len(questions_detected) >= 5:  # Need at least 5 questions for analysis
        # Calculate layout parameters from detected questions
        first_question = questions_detected[0]
        second_question = questions_detected[1] if len(questions_detected) > 1 else None
        
        # Bubble spacing (within question)
        bubble_spacing_px = 0
        if len(first_question) >= 2:
            bubble_spacing_px = first_question[1]['x'] - first_question[0]['x']
        
        # Row height (between questions)
        row_height_px = 0
        if second_question:
            row_height_px = second_question[0]['y'] - first_question[0]['y']
        
        # Question spacing (between questions in same row)
        question_spacing_px = 0
        if len(questions_detected) >= 2:
            # Find questions in same row
            same_row_questions = [q for q in questions_detected if abs(q[0]['y'] - first_question[0]['y']) < 10]
            if len(same_row_questions) >= 2:
                question_spacing_px = same_row_questions[1][0]['x'] - same_row_questions[0][0]['x']
        
        logger.info(f"Measured parameters:")
        logger.info(f"  Bubble spacing: {bubble_spacing_px:.1f} px")
        logger.info(f"  Row height: {row_height_px:.1f} px")
        logger.info(f"  Question spacing: {question_spacing_px:.1f} px")
        
        # Create manual calibration points
        calibration_points = []
        for i, question in enumerate(questions_detected[:10]):  # First 10 questions
            for bubble in question:
                calibration_points.append({
                    'question': i + 1,
                    'variant': bubble['variant'],
                    'x': int(bubble['x']),
                    'y': int(bubble['y'])
                })
        
        # Save calibration points
        with open("manual_calibration_points.json", "w") as f:
            json.dump(calibration_points, f, indent=2)
        
        logger.info(f"✅ Created {len(calibration_points)} calibration points")
        logger.info("✅ Saved: manual_calibration_points.json")
    
    # 6. Visual verification
    logger.info("\n🖼️ STEP 6: Visual Verification")
    logger.info("-" * 40)
    
    annotated = image.copy()
    
    # Draw all detected bubbles
    for i, (x, y, r, method) in enumerate(filtered_bubbles):
        color = (0, 255, 0) if method == 'conservative' else (0, 255, 255) if method == 'aggressive' else (255, 0, 255)
        cv2.circle(annotated, (x, y), r, color, 2)
        cv2.putText(annotated, str(i+1), (x-5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
    
    # Draw detected questions
    for i, question in enumerate(questions_detected):
        for bubble in question:
            x, y = int(bubble['x']), int(bubble['y'])
            cv2.circle(annotated, (x, y), 12, (255, 0, 0), 3)
            cv2.putText(annotated, f"Q{i+1}-{bubble['variant']}", (x-15, y-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    # Draw row lines
    for row_info in row_analysis:
        y = int(row_info['y_position'])
        cv2.line(annotated, (0, y), (image.shape[1], y), (128, 128, 128), 1)
    
    # Save annotated image
    output_path = "bubble_measurement_analysis.jpg"
    cv2.imwrite(output_path, annotated)
    logger.info(f"✅ Analysis image saved: {output_path}")
    
    # 7. Test with manual calibration
    if 'calibration_points' in locals() and len(calibration_points) > 0:
        logger.info("\n🧪 STEP 7: Test Manual Calibration")
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
                image, calibration_points, exam_structure
            )
            
            if calibration_result['success']:
                logger.info("✅ Manual calibration successful!")
                logger.info(f"  Accuracy: {calibration_result['accuracy_estimate']}%")
                logger.info(f"  Coordinates generated: {len(calibration_result['coordinates'])}")
                
                # Test OMR detection with calibrated coordinates
                from services.adaptive_omr_detector import AdaptiveOMRDetector
                
                adaptive_detector = AdaptiveOMRDetector()
                omr_results = adaptive_detector.detect_all_answers(
                    gray, calibration_result['coordinates'], exam_structure
                )
                
                logger.info(f"✅ OMR Detection with calibrated coordinates:")
                logger.info(f"  Total: {omr_results['statistics']['total']}")
                logger.info(f"  Detected: {omr_results['statistics']['detected']}")
                logger.info(f"  High confidence: {omr_results['statistics']['high_confidence']}")
                logger.info(f"  Medium confidence: {omr_results['statistics']['medium_confidence']}")
                logger.info(f"  Low confidence: {omr_results['statistics']['low_confidence']}")
                
            else:
                logger.warning("❌ Manual calibration failed")
                
        except Exception as e:
            logger.error(f"Manual calibration test error: {e}")
    
    logger.info("\n✅ BUBBLE MEASUREMENT COMPLETE!")
    logger.info("Files created:")
    logger.info("1. bubble_measurement_analysis.jpg - Visual analysis")
    if 'calibration_points' in locals():
        logger.info("2. manual_calibration_points.json - Calibration points")
    
    return {
        'bubbles_found': len(filtered_bubbles),
        'rows_detected': len(rows),
        'questions_detected': len(questions_detected),
        'calibration_points': len(calibration_points) if 'calibration_points' in locals() else 0
    }

if __name__ == "__main__":
    result = measure_real_bubbles()
    print(f"\nMeasurement complete: {result}")