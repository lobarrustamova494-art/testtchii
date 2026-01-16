"""
Camera Preview API - Real-time corner detection and coordinate preview
Allows users to see if corners are detected before capturing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import base64
import logging
from typing import Dict, List

from services.image_processor import ImageProcessor
from utils.relative_coordinate_mapper import RelativeCoordinateMapper

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/api/camera/preview")
async def camera_preview(file: UploadFile = File(...)):
    """
    Camera preview endpoint - detect corners and show coordinate overlay
    OPTIMIZED FOR SPEED - Lower resolution and quality for real-time preview
    
    Returns:
        {
            'success': bool,
            'corners_found': int,
            'preview_image': base64 string with overlay,
            'corners': list of corner positions,
            'ready_to_capture': bool
        }
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # OPTIMIZATION: Resize image for faster processing
        height, width = image.shape[:2]
        max_dimension = 800  # Reduced from full resolution
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.info(f"Resized preview image: {image.shape}")
        
        # Detect corners
        processor = ImageProcessor()
        corners = processor.detect_corner_markers(image)
        
        corners_found = len(corners) if corners else 0
        ready_to_capture = corners_found == 4
        
        # Create preview image with overlay
        preview = image.copy()
        
        if corners:
            # Draw detected corners
            for i, corner in enumerate(corners):
                x, y = int(corner['x']), int(corner['y'])
                
                # Draw corner marker (green circle)
                cv2.circle(preview, (x, y), 20, (0, 255, 0), 2)
                cv2.circle(preview, (x, y), 3, (0, 255, 0), -1)
                
                # Draw corner label
                cv2.putText(
                    preview, 
                    f"{i+1}", 
                    (x + 25, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.0, 
                    (0, 255, 0), 
                    2
                )
        
        # If all 4 corners found, show coordinate preview
        if ready_to_capture:
            # Draw connecting lines between corners
            if len(corners) == 4:
                # Sort corners
                sorted_corners = sorted(corners, key=lambda c: (c['y'], c['x']))
                top_corners = sorted(sorted_corners[:2], key=lambda c: c['x'])
                bottom_corners = sorted(sorted_corners[2:], key=lambda c: c['x'])
                
                pts = np.array([
                    [top_corners[0]['x'], top_corners[0]['y']],
                    [top_corners[1]['x'], top_corners[1]['y']],
                    [bottom_corners[1]['x'], bottom_corners[1]['y']],
                    [bottom_corners[0]['x'], bottom_corners[0]['y']]
                ], dtype=np.int32)
                
                # Draw border
                cv2.polylines(preview, [pts], True, (0, 255, 0), 2)
            
            # Add "READY" text (simplified)
            text = "READY"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            thickness = 3
            
            # Get text size
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            
            # Calculate position (top center)
            x = (preview.shape[1] - text_width) // 2
            y = 60
            
            # Draw background rectangle
            cv2.rectangle(
                preview,
                (x - 15, y - text_height - 15),
                (x + text_width + 15, y + 15),
                (0, 255, 0),
                -1
            )
            
            # Draw text
            cv2.putText(
                preview,
                text,
                (x, y),
                font,
                font_scale,
                (0, 0, 0),
                thickness
            )
        else:
            # Show corners count only
            text = f"{corners_found}/4"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.2
            thickness = 2
            
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            x = (preview.shape[1] - text_width) // 2
            y = 60
            
            # Draw background
            color = (0, 165, 255) if corners_found > 0 else (0, 0, 255)
            cv2.rectangle(
                preview,
                (x - 15, y - text_height - 15),
                (x + text_width + 15, y + 15),
                color,
                -1
            )
            
            # Draw text
            cv2.putText(
                preview,
                text,
                (x, y),
                font,
                font_scale,
                (255, 255, 255),
                thickness
            )
        
        # OPTIMIZATION: Lower JPEG quality for faster encoding/transfer
        _, buffer = cv2.imencode('.jpg', preview, [cv2.IMWRITE_JPEG_QUALITY, 60])
        preview_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return JSONResponse({
            'success': True,
            'corners_found': corners_found,
            'preview_image': f"data:image/jpeg;base64,{preview_base64}",
            'corners': corners if corners else [],
            'ready_to_capture': ready_to_capture,
            'message': 'Ready!' if ready_to_capture else f'{corners_found}/4'
        })
        
    except Exception as e:
        logger.error(f"Preview error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/camera/preview-with-bubbles")
async def camera_preview_with_bubbles(
    file: UploadFile = File(...),
    exam_structure: str = None
):
    """
    Advanced preview - show bubble positions overlay
    
    This shows where bubbles will be detected, helping users
    verify alignment before capture
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Detect corners
        processor = ImageProcessor()
        corners = processor.detect_corner_markers(image)
        
        if not corners or len(corners) != 4:
            return JSONResponse({
                'success': False,
                'message': f'Need 4 corners, found {len(corners) if corners else 0}'
            })
        
        # Create preview
        preview = image.copy()
        
        # Draw corners
        for corner in corners:
            x, y = int(corner['x']), int(corner['y'])
            cv2.circle(preview, (x, y), 20, (0, 255, 0), 2)
        
        # If exam structure provided, calculate and draw bubble positions
        if exam_structure:
            import json
            exam_data = json.loads(exam_structure)
            
            # Calculate coordinates
            mapper = RelativeCoordinateMapper(corners, exam_data)
            coordinates = mapper.calculate_all()
            
            # Draw sample bubble positions (first 10 questions)
            for q_num in range(1, min(11, len(coordinates) + 1)):
                if q_num not in coordinates:
                    continue
                
                coord = coordinates[q_num]
                
                # Draw bubbles
                for bubble in coord['bubbles']:
                    x = int(bubble['x'])
                    y = int(bubble['y'])
                    r = int(bubble['radius'])
                    
                    # Draw circle
                    cv2.circle(preview, (x, y), r, (255, 0, 0), 1)
                    
                    # Draw variant label
                    cv2.putText(
                        preview,
                        bubble['variant'],
                        (x - 5, y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 0, 0),
                        1
                    )
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', preview, [cv2.IMWRITE_JPEG_QUALITY, 85])
        preview_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return JSONResponse({
            'success': True,
            'preview_image': f"data:image/jpeg;base64,{preview_base64}",
            'corners_found': 4,
            'ready_to_capture': True
        })
        
    except Exception as e:
        logger.error(f"Preview with bubbles error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/camera/quick-analysis")
async def camera_quick_analysis(
    file: UploadFile = File(...),
    exam_structure: str = None
):
    """
    Quick analysis endpoint - validates capture before submission
    
    This is the EvalBee way:
    1. Capture → analyze → confirm flow
    2. Catch errors before they reach server
    3. Question-level validation
    4. Real-time feedback
    
    Returns:
        {
            'totalQuestions': int,
            'detectedAnswers': int,
            'blankQuestions': int,
            'invalidQuestions': int (multiple marks or unclear),
            'warnings': list of strings,
            'readyToSubmit': bool
        }
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        logger.info(f"Quick analysis - image shape: {image.shape}")
        
        # Detect corners
        processor = ImageProcessor()
        corners = processor.detect_corner_markers(image)
        
        if not corners or len(corners) != 4:
            return JSONResponse({
                'totalQuestions': 0,
                'detectedAnswers': 0,
                'blankQuestions': 0,
                'invalidQuestions': 0,
                'warnings': [f'Only {len(corners) if corners else 0}/4 corners detected - retake required'],
                'readyToSubmit': False
            })
        
        # Apply perspective correction
        corrected = processor.apply_perspective_correction(image, corners)
        
        if corrected is None:
            return JSONResponse({
                'totalQuestions': 0,
                'detectedAnswers': 0,
                'blankQuestions': 0,
                'invalidQuestions': 0,
                'warnings': ['Perspective correction failed - retake required'],
                'readyToSubmit': False
            })
        
        # Parse exam structure
        if not exam_structure:
            return JSONResponse({
                'totalQuestions': 0,
                'detectedAnswers': 0,
                'blankQuestions': 0,
                'invalidQuestions': 0,
                'warnings': ['No exam structure provided'],
                'readyToSubmit': False
            })
        
        import json
        exam_data = json.loads(exam_structure)
        
        # Calculate total questions
        total_questions = 0
        for subject in exam_data.get('subjects', []):
            for section in subject.get('sections', []):
                total_questions += section.get('questionCount', 0)
        
        # Calculate coordinates
        mapper = RelativeCoordinateMapper(corners, exam_data)
        coordinates = mapper.calculate_all()
        
        # Quick OMR detection
        from services.omr_detector import OMRDetector
        omr_detector = OMRDetector()
        
        detected_answers = 0
        blank_questions = 0
        invalid_questions = 0
        warnings = []
        
        for q_num in range(1, total_questions + 1):
            if q_num not in coordinates:
                continue
            
            coord = coordinates[q_num]
            
            # Extract ROI for each bubble
            bubble_scores = []
            for bubble in coord['bubbles']:
                x, y, r = int(bubble['x']), int(bubble['y']), int(bubble['radius'])
                
                # Extract ROI
                roi = corrected[
                    max(0, y - r):min(corrected.shape[0], y + r),
                    max(0, x - r):min(corrected.shape[1], x + r)
                ]
                
                if roi.size == 0:
                    continue
                
                # Calculate darkness
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                darkness = 100 - (np.mean(gray_roi) / 255 * 100)
                
                bubble_scores.append({
                    'variant': bubble['variant'],
                    'darkness': darkness
                })
            
            if not bubble_scores:
                continue
            
            # Find marked bubbles (darkness > 35%)
            marked = [b for b in bubble_scores if b['darkness'] > 35]
            
            if len(marked) == 0:
                blank_questions += 1
            elif len(marked) == 1:
                detected_answers += 1
            else:
                invalid_questions += 1
                warnings.append(f'Question {q_num}: Multiple marks detected')
        
        # Determine if ready to submit
        ready_to_submit = True
        
        # Check 1: All corners detected
        if len(corners) != 4:
            ready_to_submit = False
            warnings.append('Not all corners detected')
        
        # Check 2: Too many invalid questions
        if invalid_questions > total_questions * 0.1:  # More than 10% invalid
            ready_to_submit = False
            warnings.append(f'{invalid_questions} questions have multiple marks')
        
        # Check 3: Too many blank questions
        if blank_questions > total_questions * 0.5:  # More than 50% blank
            warnings.append(f'{blank_questions} questions are blank')
        
        # Check 4: Detection rate
        detection_rate = detected_answers / total_questions if total_questions > 0 else 0
        if detection_rate < 0.3:  # Less than 30% detected
            ready_to_submit = False
            warnings.append(f'Only {detection_rate*100:.0f}% of answers detected - check image quality')
        
        logger.info(f"Quick analysis complete: {detected_answers}/{total_questions} detected, {invalid_questions} invalid")
        
        return JSONResponse({
            'totalQuestions': total_questions,
            'detectedAnswers': detected_answers,
            'blankQuestions': blank_questions,
            'invalidQuestions': invalid_questions,
            'warnings': warnings,
            'readyToSubmit': ready_to_submit
        })
        
    except Exception as e:
        logger.error(f"Quick analysis error: {e}", exc_info=True)
        return JSONResponse({
            'totalQuestions': 0,
            'detectedAnswers': 0,
            'blankQuestions': 0,
            'invalidQuestions': 0,
            'warnings': [f'Analysis failed: {str(e)}'],
            'readyToSubmit': False
        })
