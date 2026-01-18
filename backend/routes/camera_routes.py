"""
Camera System API Routes
Professional camera-based OMR processing endpoints
"""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import json
import logging
from typing import Dict, Any

from services.camera_processor import CameraProcessor
from services.adaptive_omr_detector import AdaptiveOMRDetector
from services.grader import AnswerGrader
from services.image_annotator import ImageAnnotator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/camera", tags=["camera"])

# Initialize services
camera_processor = CameraProcessor()
omr_detector = AdaptiveOMRDetector()

@router.post("/process-frame")
async def process_camera_frame(
    image: UploadFile = File(...),
    exam_structure: str = Form(...)
):
    """
    Process a single camera frame for paper detection and validation
    
    Args:
        image: Camera frame image
        exam_structure: JSON string of exam structure
        
    Returns:
        dict: Frame analysis results
    """
    try:
        # Parse exam structure
        exam_data = json.loads(exam_structure)
        
        # Read image
        image_bytes = await image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        logger.info(f"Processing camera frame: {cv_image.shape}")
        
        # Process frame for paper detection
        results = camera_processor.process_camera_image(cv_image, exam_data)
        
        return JSONResponse(content={
            'success': results['success'],
            'paper_detected': results['success'],
            'corners_found': results['corners_found'],
            'quality_score': results['quality_score'],
            'message': results.get('error_message', 'Frame processed successfully'),
            'ready_to_capture': results['success'] and results['corners_found'] == 4
        })
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid exam structure JSON")
    except Exception as e:
        logger.error(f"Frame processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.post("/capture-and-grade")
async def capture_and_grade_sheet(
    image: UploadFile = File(...),
    exam_structure: str = Form(...),
    answer_key: str = Form(...)
):
    """
    Complete camera capture and grading pipeline
    
    Args:
        image: Captured camera image
        exam_structure: JSON string of exam structure  
        answer_key: JSON string of answer key
        
    Returns:
        dict: Complete grading results with annotations
    """
    try:
        # Parse inputs
        exam_data = json.loads(exam_structure)
        answers = json.loads(answer_key)
        
        # Read image
        image_bytes = await image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        logger.info(f"🎯 Starting camera capture and grade pipeline...")
        logger.info(f"Image size: {cv_image.shape}")
        
        # Step 1: Process camera image (crop, correct, detect corners)
        logger.info("📄 Step 1: Processing camera image...")
        processing_results = camera_processor.process_camera_image(cv_image, exam_data)
        
        if not processing_results['success']:
            return JSONResponse(content={
                'success': False,
                'error': processing_results['error_message'],
                'step': 'image_processing'
            })
        
        cropped_paper = processing_results['cropped_paper']
        paper_coordinates = processing_results['paper_coordinates']
        
        logger.info(f"✅ Paper processed: {len(paper_coordinates)} questions mapped")
        
        # Step 2: OMR Detection on cropped paper
        logger.info("🔍 Step 2: OMR detection on cropped paper...")
        
        # Convert to grayscale for OMR detection
        gray_paper = cv2.cvtColor(cropped_paper, cv2.COLOR_BGR2GRAY)
        
        # Detect answers using adaptive OMR
        omr_results = omr_detector.detect_all_answers(
            gray_paper,
            paper_coordinates,
            exam_data
        )
        
        logger.info(f"✅ OMR detection complete: {omr_results['statistics']}")
        
        # Step 3: Grade the results
        logger.info("📊 Step 3: Grading results...")
        grader = AnswerGrader(answers, exam_data)
        grading_results = grader.grade(omr_results['answers'])
        
        logger.info(f"✅ Grading complete: {grading_results['score']}/{grading_results['total']}")
        
        # Step 4: Generate annotated image
        logger.info("🎨 Step 4: Generating annotated image...")
        annotator = ImageAnnotator()
        
        # Use the cropped paper for annotation
        annotated_image = annotator.annotate_results(
            cropped_paper,
            paper_coordinates,
            omr_results['answers'],
            answers,
            grading_results
        )
        
        # Convert annotated image to base64
        import base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        logger.info("✅ Camera capture and grading pipeline completed successfully")
        
        return JSONResponse(content={
            'success': True,
            'processing_results': {
                'corners_found': processing_results['corners_found'],
                'quality_score': processing_results['quality_score']
            },
            'omr_results': omr_results,
            'grading_results': grading_results,
            'annotated_image': f"data:image/jpeg;base64,{annotated_base64}",
            'statistics': {
                'total_questions': grading_results['total'],
                'correct_answers': grading_results['correct'],
                'accuracy_percentage': grading_results['percentage'],
                'processing_method': 'camera_system'
            }
        })
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Camera capture and grade error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.post("/validate-paper")
async def validate_paper_quality(
    image: UploadFile = File(...)
):
    """
    Validate paper quality and readiness for capture
    
    Args:
        image: Camera frame image
        
    Returns:
        dict: Validation results
    """
    try:
        # Read image
        image_bytes = await image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Quick paper detection
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Simple quality metrics
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = gray.mean()
        contrast = gray.std()
        
        # Paper detection (simplified)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find largest rectangular contour
        paper_found = False
        corners_count = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000:  # Minimum area
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) == 4:
                    paper_found = True
                    corners_count = 4
                    break
        
        # Calculate readiness score
        sharpness_score = min(sharpness / 500, 1)
        brightness_score = 1 - abs(brightness - 200) / 200
        contrast_score = min(contrast / 50, 1)
        
        overall_score = (sharpness_score + brightness_score + contrast_score) / 3
        ready_to_capture = paper_found and overall_score > 0.6
        
        return JSONResponse(content={
            'paper_found': paper_found,
            'corners_detected': corners_count,
            'quality_metrics': {
                'sharpness': round(sharpness, 2),
                'brightness': round(brightness, 2),
                'contrast': round(contrast, 2),
                'overall_score': round(overall_score * 100, 1)
            },
            'ready_to_capture': ready_to_capture,
            'recommendations': [
                'Qog\'ozni to\'liq kadrga joylashtiring' if not paper_found else None,
                'Yaxshiroq yorug\'lik ta\'minlang' if brightness < 150 else None,
                'Kamerani barqaror ushlab turing' if sharpness < 200 else None,
                'Kontrastni oshiring' if contrast < 30 else None
            ]
        })
        
    except Exception as e:
        logger.error(f"Paper validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.get("/system-status")
async def get_camera_system_status():
    """
    Get camera system status and capabilities
    
    Returns:
        dict: System status information
    """
    return JSONResponse(content={
        'system_name': 'Professional Camera OMR System',
        'version': '1.0.0',
        'capabilities': [
            'Real-time paper detection',
            'Automatic perspective correction', 
            'Corner marker detection',
            'Template-based coordinate mapping',
            'Professional bubble analysis',
            'Quality assessment'
        ],
        'supported_formats': ['JPEG', 'PNG'],
        'max_image_size': '10MB',
        'recommended_resolution': '1920x1080 or higher',
        'status': 'operational'
    })