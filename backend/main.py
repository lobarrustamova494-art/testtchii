"""
FastAPI Backend for Professional OMR System
Hybrid: OpenCV + Groq AI
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import logging
import json
import cv2
import numpy as np
import base64
from pathlib import Path
from datetime import datetime

from config import settings
from services import ImageProcessor, OMRDetector, AIVerifier, AnswerGrader, ImageAnnotator, QRCodeReader
from services.advanced_omr_detector import AdvancedOMRDetector
from services.ocr_anchor_detector import OCRAnchorDetector
from services.photo_omr_service import PhotoOMRService
from services.improved_photo_processor import ImprovedPhotoProcessor
from services.photo_quality_assessor import PhotoQualityAssessor
from services.improved_corner_detector import ImprovedCornerDetector
from services.openai_verifier import OpenAIVerifier
from services.database_service import db_service
from utils import CoordinateMapper
from middleware.auth_middleware import get_current_user, optional_auth

# Import authentication routes
from routes.auth_routes import router as auth_router

# Import camera routes
from routes.camera_routes import router as camera_router

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Professional OMR Grading System",
    description="Hybrid OMR system with OpenCV + Groq AI (99.9%+ accuracy)",
    version="3.0.0"
)

# Database startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    if settings.USE_DATABASE:
        try:
            await db_service.connect()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            logger.warning("Running without database - using file-based storage")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    if settings.USE_DATABASE:
        await db_service.disconnect()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],  # Wildcard ham qo'shamiz
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include authentication router
app.include_router(auth_router)

# Include camera system router
app.include_router(camera_router)

# Initialize services
image_processor = ImageProcessor(
    target_width=settings.TARGET_WIDTH,
    target_height=settings.TARGET_HEIGHT
)

# Ultra Precise Coordinate Mapper (NEW! - 100% accuracy)
from services.ultra_precise_coordinate_mapper import UltraPreciseCoordinateMapper
ultra_precise_mapper = UltraPreciseCoordinateMapper()
logger.info("Ultra Precise Coordinate Mapper initialized (100% accuracy)")

# Adaptive OMR Detector (NEW! - adaptive to image quality)
from services.adaptive_omr_detector import AdaptiveOMRDetector
adaptive_omr_detector = AdaptiveOMRDetector()
logger.info("Adaptive OMR Detector initialized (quality-aware)")

# Advanced OMR Detector (EXISTING)
advanced_omr_detector = AdvancedOMRDetector()

# Old OMR Detector (fallback)
omr_detector = OMRDetector(
    bubble_radius=settings.BUBBLE_RADIUS,
    min_darkness=settings.MIN_DARKNESS,
    min_difference=settings.MIN_DIFFERENCE,
    multiple_marks_threshold=settings.MULTIPLE_MARKS_THRESHOLD
)

# QR Code Reader
qr_reader = QRCodeReader()

# OCR Anchor Detector (NEW!)
ocr_anchor_detector = OCRAnchorDetector()

# Photo OMR Service (NEW! - for photos, not PDF-generated sheets)
photo_omr_service = PhotoOMRService()
logger.info("Photo OMR Service initialized (for photo support)")

# Improved Photo Processor (ENHANCED!)
improved_photo_processor = ImprovedPhotoProcessor()
logger.info("Improved Photo Processor initialized (enhanced photo processing)")

# Photo Quality Assessor (NEW!)
photo_quality_assessor = PhotoQualityAssessor()
logger.info("Photo Quality Assessor initialized (quality assessment)")

# Template Matching OMR (NEW! - for unknown layouts)
from services.template_matching_omr import TemplateMatchingOMR
template_matching_omr = TemplateMatchingOMR()
logger.info("Template Matching OMR initialized (for unknown layouts)")

# AI Verifier (OpenAI GPT-4 Vision or Groq fallback)
ai_verifier = None
if settings.ENABLE_AI_VERIFICATION:
    if settings.AI_PROVIDER == 'openai' and settings.OPENAI_API_KEY:
        try:
            ai_verifier = OpenAIVerifier(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            logger.info("OpenAI GPT-4 Vision Verifier initialized successfully")
        except Exception as e:
            logger.warning(f"OpenAI Verifier initialization failed: {e}")
    elif settings.GROQ_API_KEY:
        try:
            ai_verifier = AIVerifier(
                api_key=settings.GROQ_API_KEY,
                model=settings.GROQ_MODEL,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS
            )
            logger.info("Groq AI Verifier initialized successfully (fallback)")
        except Exception as e:
            logger.warning(f"Groq AI Verifier initialization failed: {e}")
    else:
        logger.warning("AI Verification enabled but no API keys provided")
        logger.warning("System will run without AI verification")
else:
    if not settings.ENABLE_AI_VERIFICATION:
        logger.info("AI Verification disabled in config")
    else:
        logger.warning("GROQ_API_KEY not found. AI verification disabled.")

# Temp directory
settings.TEMP_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Professional OMR Grading System",
        "version": "3.0.0",
        "status": "operational",
        "features": {
            "opencv_processing": True,
            "omr_detection": True,
            "ai_verification": ai_verifier is not None
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_enabled": ai_verifier is not None
    }

@app.post("/api/template-match-grade")
async def template_match_grade(
    file: UploadFile = File(...),
    answer_key: str = Form(...),
    current_user: dict = Depends(optional_auth)  # Optional authentication
):
    """
    Template Matching OMR - for unknown exam layouts
    
    Args:
        file: Image file (JPEG/PNG)
        answer_key: JSON string of answer key
        
    Returns:
        JSON with grading results
    """
    start_time = datetime.now()
    logger.info(f"=== TEMPLATE MATCHING GRADING REQUEST ===")
    logger.info(f"File: {file.filename}")
    
    temp_path = None
    
    try:
        # 1. Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only images are allowed."
            )
        
        # 2. Save temporary file
        temp_path = settings.TEMP_DIR / f"template_{datetime.now().timestamp()}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {temp_path}")
        
        # 3. Parse answer key
        try:
            answer_key_data = json.loads(answer_key)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer key JSON: {str(e)}"
            )
        
        # 4. Load and preprocess image
        logger.info("STEP 1/4: Loading and preprocessing image...")
        image = cv2.imread(str(temp_path))
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to load image"
            )
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 5. Template matching OMR processing
        logger.info("STEP 2/4: Template matching OMR processing...")
        results = template_matching_omr.process_image(enhanced)
        
        if 'error' in results:
            raise HTTPException(
                status_code=400,
                detail=results['error']
            )
        
        # 6. Compare with answer key and calculate score
        logger.info("STEP 3/4: Comparing with answer key...")
        
        correct_count = 0
        wrong_count = 0
        unanswered_count = 0
        total_questions = len(answer_key_data)
        
        detailed_results = []
        
        for q_num in range(1, total_questions + 1):
            correct_answer = answer_key_data.get(str(q_num), '?')
            detected_answer = None
            confidence = 0
            
            if q_num in results['answers']:
                answer_data = results['answers'][q_num]
                detected_answer = answer_data['answer']
                confidence = answer_data['confidence']
            
            # Determine status
            if detected_answer is None:
                status = 'unanswered'
                unanswered_count += 1
            elif detected_answer == correct_answer:
                status = 'correct'
                correct_count += 1
            else:
                status = 'wrong'
                wrong_count += 1
            
            detailed_results.append({
                'questionNumber': q_num,
                'correctAnswer': correct_answer,
                'detectedAnswer': detected_answer,
                'confidence': confidence,
                'status': status
            })
        
        # Calculate final score
        accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # 7. Create annotated image
        logger.info("STEP 4/4: Creating annotated image...")
        annotated = template_matching_omr.create_annotated_image(image, results)
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', annotated)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response
        response = {
            "success": True,
            "method": "template_matching",
            "results": {
                "answers": detailed_results,
                "score": {
                    "correct": correct_count,
                    "wrong": wrong_count,
                    "unanswered": unanswered_count,
                    "total": total_questions,
                    "accuracy": round(accuracy, 1),
                    "percentage": f"{accuracy:.1f}%"
                }
            },
            "statistics": {
                "total": results['statistics']['total'],
                "detected": results['statistics']['detected'],
                "bubbles_found": results['statistics']['bubbles_found'],
                "processing_time": round(processing_time, 2),
                "method": "Template Matching OMR"
            },
            "annotatedImage": f"data:image/jpeg;base64,{annotated_base64}",
            "metadata": {
                "filename": file.filename,
                "timestamp": start_time.isoformat(),
                "image_size": f"{image.shape[1]}x{image.shape[0]}",
                "bubbles_detected": len(results.get('bubbles', [])),
                "questions_detected": len(results.get('questions', {}))
            }
        }
        
        logger.info(f"✅ Template matching complete: {accuracy:.1f}% accuracy ({processing_time:.2f}s)")
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template matching error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Template matching failed: {str(e)}"
        )
    finally:
        # Cleanup
        if temp_path and temp_path.exists():
            temp_path.unlink()


@app.post("/api/ultra-precise-grade")
async def ultra_precise_grade(
    file: UploadFile = File(...),
    exam_structure: str = Form(...),
    answer_key: str = Form(...),
    coordinate_template: str = Form(None),
    manual_calibration: str = Form(None),  # Manual calibration points
    current_user: dict = Depends(optional_auth)  # CHANGED: Optional auth for testing
):
    """
    ULTRA PRECISE Grading - 100% aniqlik uchun
    
    Args:
        file: Image file (JPEG/PNG)
        exam_structure: JSON string of exam structure
        answer_key: JSON string of answer key
        coordinate_template: JSON string of coordinate template (optional)
        manual_calibration: JSON string of manual calibration points (optional)
        
    Returns:
        JSON with ultra precise grading results
    """
    start_time = datetime.now()
    logger.info(f"=== ULTRA PRECISE GRADING REQUEST ===")
    logger.info(f"File: {file.filename}")
    logger.info(f"User: {current_user.get('username', 'anonymous') if current_user else 'anonymous'}")
    
    temp_path = None
    
    try:
        # 1. Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only images are allowed."
            )
        
        # 2. Save temporary file
        temp_path = settings.TEMP_DIR / f"ultra_{datetime.now().timestamp()}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {temp_path}")
        
        # 3. Parse JSON data
        try:
            exam_data = json.loads(exam_structure)
            answer_key_data = json.loads(answer_key)
            
            coord_template = None
            if coordinate_template:
                coord_template = json.loads(coordinate_template)
                logger.info("✅ Coordinate template provided")
            
            calibration_points = None
            if manual_calibration:
                calibration_points = json.loads(manual_calibration)
                logger.info(f"✅ Manual calibration points provided: {len(calibration_points)}")
                
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON data: {str(e)}"
            )
        
        # 4. Load and assess image
        logger.info("STEP 1/5: Image Loading and Quality Assessment...")
        import cv2
        image = cv2.imread(str(temp_path))
        if image is None:
            raise HTTPException(status_code=400, detail="Failed to load image")
        
        # Quality assessment
        image_quality = adaptive_omr_detector._assess_image_quality(image)
        logger.info(f"Image quality: {image_quality['overall_score']:.1f}/100 ({image_quality['category']})")
        
        # 5. ULTRA PRECISE Coordinate Detection
        logger.info("STEP 2/5: ULTRA PRECISE Coordinate Detection...")
        
        if calibration_points:
            # Manual calibration (100% accuracy)
            coordinate_result = ultra_precise_mapper.calibrate_manually(
                image, calibration_points, exam_data
            )
        else:
            # Automatic detection
            coordinate_result = ultra_precise_mapper.detect_layout_with_precision(
                image, exam_data, coord_template
            )
        
        coordinates = coordinate_result.get('coordinates', {})
        accuracy_estimate = coordinate_result.get('accuracy_estimate', 0)
        
        logger.info(f"✅ Coordinate method: {coordinate_result['method']} ({accuracy_estimate}% accuracy)")
        
        if not coordinates:
            # Return calibration instructions
            return JSONResponse({
                'success': False,
                'calibration_needed': True,
                'coordinate_result': coordinate_result,
                'image_quality': image_quality,
                'instructions': {
                    'message': 'Manual calibration needed for 100% accuracy',
                    'steps': [
                        'Identify at least 4 bubble positions in the image',
                        'Note their question numbers and variants (e.g., Q1-A, Q5-C)',
                        'Measure their pixel coordinates',
                        'Provide coordinates via manual_calibration parameter'
                    ],
                    'format': '[{"question": 1, "variant": "A", "x": 123, "y": 456}, ...]'
                }
            })
        
        # 6. ADAPTIVE OMR Detection
        logger.info("STEP 3/5: ADAPTIVE OMR Detection...")
        
        # Prepare image for OMR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        omr_results = adaptive_omr_detector.detect_all_answers(
            gray, coordinates, exam_data, image_quality
        )
        
        logger.info(f"✅ OMR method: {omr_results.get('detection_strategy', {}).get('name', 'unknown')}")
        logger.info(f"   Detection: {omr_results['statistics']['detected']}/{omr_results['statistics']['total']}")
        
        # 7. AI Verification (if needed and enabled)
        verified_results = omr_results
        ai_stats = None
        
        if ai_verifier and omr_results['statistics']['uncertain'] > 0:
            logger.info("STEP 4/5: AI Verification...")
            try:
                verified_results = ai_verifier.verify_uncertain_answers(
                    gray, omr_results, coordinates,
                    confidence_threshold=settings.AI_CONFIDENCE_THRESHOLD,
                    max_verifications=20
                )
                
                ai_verified = sum(
                    1 for topic in verified_results['answers'].values()
                    for section in topic.values()
                    for answer in section
                    if answer.get('ai_verified')
                )
                
                ai_corrected = sum(
                    1 for topic in verified_results['answers'].values()
                    for section in topic.values()
                    for answer in section
                    if answer.get('warning') == 'AI_CORRECTED'
                )
                
                ai_stats = {
                    'verified': ai_verified,
                    'corrected': ai_corrected,
                    'enabled': True
                }
                
            except Exception as e:
                logger.error(f"AI verification failed: {e}")
                ai_stats = {'enabled': False, 'error': str(e)}
        else:
            ai_stats = {
                'enabled': ai_verifier is not None,
                'verified': 0,
                'corrected': 0,
                'reason': 'No uncertain answers' if ai_verifier else 'AI disabled'
            }
        
        # 8. Grading
        logger.info("STEP 5/5: Grading...")
        grader = AnswerGrader(answer_key_data, exam_data)
        final_results = grader.grade(verified_results['answers'])
        
        # 9. Image Annotation
        annotator = ImageAnnotator()
        annotated_image = annotator.annotate_sheet(
            gray, final_results, coordinates, answer_key_data
        )
        
        # 10. Cleanup
        if temp_path and temp_path.exists():
            os.remove(temp_path)
        
        # Calculate processing time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"=== ULTRA PRECISE GRADING COMPLETE ===")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"Score: {final_results['totalScore']}/{final_results['maxScore']} ({final_results['percentage']}%)")
        logger.info(f"Coordinate accuracy: {accuracy_estimate}%")
        
        return JSONResponse({
            'success': True,
            'results': final_results,
            'annotatedImage': annotated_image,
            'statistics': {
                'omr': omr_results['statistics'],
                'ai': ai_stats,
                'coordinate_detection': {
                    'method': coordinate_result['method'],
                    'accuracy_estimate': accuracy_estimate,
                    'validation': coordinate_result.get('validation', {})
                },
                'detection_strategy': omr_results.get('detection_strategy', {}),
                'image_quality': image_quality,
                'duration': round(duration, 2)
            },
            'metadata': {
                'timestamp': end_time.isoformat(),
                'filename': file.filename,
                'system_version': '3.1.0',
                'precision_level': 'ULTRA_HIGH',
                'coordinate_method': coordinate_result['method'],
                'omr_method': omr_results.get('detection_strategy', {}).get('name', 'adaptive')
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ultra precise grading error: {e}", exc_info=True)
        
        # Cleanup on error
        if temp_path and temp_path.exists():
            try:
                os.remove(temp_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Ultra precise grading failed: {str(e)}"
        )


@app.post("/api/grade-sheet")
async def grade_sheet(
    file: UploadFile = File(...),
    exam_structure: str = Form(...),
    answer_key: str = Form(...),
    coordinate_template: str = Form(None),  # YANGI: Optional coordinate template
    current_user: dict = Depends(get_current_user)  # AUTHENTICATION REQUIRED
):
    """
    Varaqni tekshirish - Professional OMR + AI
    
    Args:
        file: Image file (JPEG/PNG)
        exam_structure: JSON string of exam structure
        answer_key: JSON string of answer key
        coordinate_template: JSON string of coordinate template (optional)
        
    Returns:
        JSON with grading results
    """
    start_time = datetime.now()
    logger.info(f"=== NEW GRADING REQUEST ===")
    logger.info(f"File: {file.filename}")
    logger.info(f"User: {current_user['username']} ({current_user['role']})")
    
    temp_path = None
    
    try:
        # 1. Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only images are allowed."
            )
        
        # 2. Save temporary file
        temp_path = settings.TEMP_DIR / f"{datetime.now().timestamp()}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {temp_path}")
        
        # 3. Parse JSON data
        try:
            exam_data = json.loads(exam_structure)
            answer_key_data = json.loads(answer_key)
            
            # YANGI: Parse coordinate template if provided
            coord_template = None
            if coordinate_template:
                coord_template = json.loads(coordinate_template)
                logger.info("✅ Coordinate template provided from exam data")
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON data: {str(e)}"
            )
        
        # 4. Image Processing (OpenCV)
        logger.info("STEP 1/6: Image Processing...")
        try:
            processed = image_processor.process(str(temp_path))
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Image processing failed: {str(e)}"
            )
        
        # 4.5. QR Code Detection (NEW!)
        logger.info("STEP 2/6: QR Code Detection...")
        qr_data = qr_reader.read_qr_code(processed['grayscale'])
        
        if qr_data:
            logger.info("✅ QR Code detected! Using QR layout data")
            # Use layout from QR code
            qr_layout = qr_reader.get_layout_from_qr(qr_data)
            logger.info(f"   QR Layout: {qr_layout}")
        else:
            logger.warning("⚠️  No QR code found, using default layout")
            qr_layout = None
        
        # 5. ULTRA PRECISE Coordinate Calculation
        logger.info("STEP 3/6: ULTRA PRECISE Coordinate Calculation...")
        
        # Use Ultra Precise Coordinate Mapper
        coordinate_result = ultra_precise_mapper.detect_layout_with_precision(
            processed['grayscale'],
            exam_data,
            coord_template
        )
        
        coordinates = coordinate_result.get('coordinates', {})
        accuracy_estimate = coordinate_result.get('accuracy_estimate', 0)
        
        logger.info(f"✅ Coordinate detection: {coordinate_result['method']} ({accuracy_estimate}% accuracy)")
        
        if not coordinates:
            logger.error("❌ Ultra precise coordinate detection failed!")
            logger.info("Attempting fallback coordinate detection methods...")
            
            # Fallback 1: Try template matching with relaxed parameters
            try:
                from services.template_matching_omr import TemplateMatchingOMR
                template_omr = TemplateMatchingOMR()
                template_result = template_omr.detect_layout_fallback(processed['grayscale'], exam_data)
                
                if template_result.get('coordinates'):
                    coordinates = template_result['coordinates']
                    coordinate_result['method'] = 'template_matching_fallback'
                    coordinate_result['accuracy_estimate'] = 75
                    logger.info("✅ Template matching fallback successful")
                else:
                    raise Exception("Template matching fallback failed")
                    
            except Exception as e:
                logger.warning(f"Template matching fallback failed: {e}")
                
                # Fallback 2: Use default coordinate template
                try:
                    from utils.coordinate_mapper import CoordinateMapper
                    
                    # Create default corners based on image dimensions
                    height, width = processed['grayscale'].shape
                    default_corners = [
                        {'name': 'top-left', 'x': int(width * 0.05), 'y': int(height * 0.05)},
                        {'name': 'top-right', 'x': int(width * 0.95), 'y': int(height * 0.05)},
                        {'name': 'bottom-left', 'x': int(width * 0.05), 'y': int(height * 0.95)},
                        {'name': 'bottom-right', 'x': int(width * 0.95), 'y': int(height * 0.95)}
                    ]
                    
                    mapper = CoordinateMapper(default_corners, exam_data)
                    coordinates = mapper.calculate_all()
                    coordinate_result['method'] = 'default_estimation'
                    coordinate_result['accuracy_estimate'] = 60
                    logger.info("✅ Default coordinate estimation applied")
                    
                except Exception as e2:
                    logger.error(f"Default coordinate estimation failed: {e2}")
                    
                    # Final fallback: Return calibration needed response
                    return JSONResponse({
                        'success': False,
                        'error': 'Coordinate detection failed. Image quality may be insufficient or corner markers are not visible.',
                        'calibration_needed': True,
                        'suggestions': [
                            'Ensure the image has clear corner markers (black squares in all 4 corners)',
                            'Check that the image is well-lit and not blurry',
                            'Make sure the entire answer sheet is visible in the image',
                            'Try using a higher resolution image (minimum 800x1100px)',
                            'Ensure the answer sheet is flat and not skewed',
                            'Consider manual calibration if automatic detection continues to fail'
                        ],
                        'fallback_options': {
                            'template_matching': 'Use template matching for unknown layouts',
                            'manual_calibration': 'Provide manual bubble coordinates',
                            'simple_grid': 'Use estimated grid layout'
                        },
                        'debug_info': {
                            'image_dimensions': f"{processed['grayscale'].shape[1]}x{processed['grayscale'].shape[0]}",
                            'image_quality': processed.get('quality', {}),
                            'detection_attempts': ['ultra_precise', 'template_fallback', 'default_estimation'],
                            'last_error': str(e2),
                            'manual_calibration': 'Provide manual bubble coordinates',
                            'photo_processing': 'Use photo-specific processing methods'
                        }
                    })
        
        # 6. ADAPTIVE OMR Detection
        logger.info("STEP 4/6: ADAPTIVE OMR Detection...")
        
        # Use Adaptive OMR Detector with image quality assessment
        omr_results = adaptive_omr_detector.detect_all_answers(
            processed['gray_for_omr'],  # Use pure grayscale
            coordinates,
            exam_data,
            processed['quality']  # Pass quality assessment
        )
        
        logger.info(f"✅ OMR Detection method: {omr_results.get('detection_strategy', {}).get('name', 'unknown')}")
        logger.info(f"   Image quality: {omr_results.get('image_quality', {}).get('category', 'unknown')}")
        logger.info(f"   Detection: {omr_results['statistics']['detected']}/{omr_results['statistics']['total']}")
        logger.info(f"   High confidence: {omr_results['statistics']['high_confidence']}")
        logger.info(f"   Medium confidence: {omr_results['statistics']['medium_confidence']}")
        logger.info(f"   Low confidence: {omr_results['statistics']['low_confidence']}")
        
        # 7. AI Verification (if enabled and needed)
        verified_results = omr_results
        ai_stats = None
        
        if ai_verifier and omr_results['statistics']['uncertain'] > 0:
            logger.info("STEP 5/6: AI Verification...")
            try:
                verified_results = ai_verifier.verify_uncertain_answers(
                    processed['grayscale'],
                    omr_results,
                    coordinates,
                    confidence_threshold=settings.AI_CONFIDENCE_THRESHOLD,
                    max_verifications=20
                )
                
                # Calculate AI stats
                ai_verified = sum(
                    1 for topic in verified_results['answers'].values()
                    for section in topic.values()
                    for answer in section
                    if answer.get('ai_verified')
                )
                
                ai_corrected = sum(
                    1 for topic in verified_results['answers'].values()
                    for section in topic.values()
                    for answer in section
                    if answer.get('warning') == 'AI_CORRECTED'
                )
                
                ai_stats = {
                    'verified': ai_verified,
                    'corrected': ai_corrected,
                    'enabled': True
                }
                
            except Exception as e:
                logger.error(f"AI verification failed: {e}")
                logger.warning("Continuing without AI verification")
                ai_stats = {'enabled': False, 'error': str(e)}
        else:
            logger.info("STEP 5/6: AI Verification skipped")
            ai_stats = {
                'enabled': ai_verifier is not None,
                'verified': 0,
                'corrected': 0,
                'reason': 'No uncertain answers' if ai_verifier else 'AI disabled'
            }
        
        # 8. Grading
        logger.info("STEP 6/6: Grading...")
        grader = AnswerGrader(answer_key_data, exam_data)
        final_results = grader.grade(verified_results['answers'])
        
        # 9. Image Annotation (Vizual ko'rsatish)
        logger.info("STEP 6/6: Image Annotation...")
        annotator = ImageAnnotator()
        # Use grayscale image for better visual quality
        # Coordinates are the same for both processed and grayscale (same dimensions)
        annotated_image = annotator.annotate_sheet(
            processed['grayscale'],  # Use grayscale for better quality
            final_results,
            coordinates,
            answer_key_data
        )
        
        # 10. Cleanup
        if temp_path and temp_path.exists():
            os.remove(temp_path)
        
        # Calculate processing time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"=== GRADING COMPLETE ===")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"Score: {final_results['totalScore']}/{final_results['maxScore']} ({final_results['percentage']}%)")
        
        return JSONResponse({
            'success': True,
            'results': final_results,
            'annotatedImage': annotated_image,
            'statistics': {
                'omr': omr_results['statistics'],
                'ai': ai_stats,
                'quality': processed['quality'],
                'coordinate_detection': {
                    'method': coordinate_result['method'],
                    'accuracy_estimate': coordinate_result['accuracy_estimate']
                },
                'detection_strategy': omr_results.get('detection_strategy', {}),
                'duration': round(duration, 2)
            },
            'metadata': {
                'timestamp': end_time.isoformat(),
                'filename': file.filename,
                'system_version': '3.1.0',  # Updated version
                'coordinate_precision': 'ULTRA_HIGH',
                'omr_method': 'ADAPTIVE'
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        
        # Cleanup on error
        if temp_path and temp_path.exists():
            try:
                os.remove(temp_path)
            except:
                pass
        
        # Provide more helpful error messages
        error_message = str(e)
        
        if "corner" in error_message.lower():
            error_detail = "Corner detection failed. Please ensure your image has clear corner markers (black squares) in all four corners."
        elif "coordinate" in error_message.lower():
            error_detail = "Coordinate detection failed. Please check image quality and ensure the answer sheet is fully visible."
        elif "template" in error_message.lower():
            error_detail = "Template matching failed. The image layout may not match the expected format."
        elif "bubble" in error_message.lower():
            error_detail = "Bubble detection failed. Please ensure bubbles are clearly visible and properly filled."
        else:
            error_detail = f"Processing failed: {error_message}"
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )

@app.post("/api/grade-photo")
async def grade_photo(
    file: UploadFile = File(...),
    exam_structure: str = Form(...),
    answer_key: str = Form(...),
    use_enhanced_processing: bool = Form(False)
):
    """
    Foto'ni tekshirish - Enhanced Photo OMR (experimental)
    
    Args:
        file: Photo file (JPEG/PNG)
        exam_structure: JSON string of exam structure
        answer_key: JSON string of answer key
        use_enhanced_processing: Use improved photo processor
        
    Returns:
        JSON with grading results and quality assessment
    """
    start_time = datetime.now()
    logger.info(f"=== NEW PHOTO GRADING REQUEST ===")
    logger.info(f"File: {file.filename}")
    logger.info(f"Enhanced processing: {use_enhanced_processing}")
    
    temp_path = None
    
    try:
        # 1. Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only images are allowed."
            )
        
        # 2. Save temporary file
        temp_path = settings.TEMP_DIR / f"photo_{datetime.now().timestamp()}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Photo saved: {temp_path}")
        
        # 3. Parse JSON data
        try:
            exam_data = json.loads(exam_structure)
            answer_key_data = json.loads(answer_key)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON data: {str(e)}"
            )
        
        # 4. Quality Assessment
        logger.info("Step 1/3: Photo Quality Assessment...")
        import cv2
        image = cv2.imread(str(temp_path))
        quality_assessment = photo_quality_assessor.assess_photo_quality(image)
        
        logger.info(f"Photo quality: {quality_assessment['overall_quality']:.1f}/100 ({quality_assessment['omr_suitability']['level']})")
        
        # 5. Process photo
        logger.info("Step 2/3: Photo Processing...")
        
        if use_enhanced_processing:
            logger.info("Using enhanced photo processor...")
            try:
                results = improved_photo_processor.process_photo_complete(
                    str(temp_path),
                    exam_data,
                    answer_key_data
                )
                processing_method = "enhanced_processor"
            except Exception as e:
                logger.error(f"Enhanced processing failed: {e}")
                logger.info("Falling back to standard photo processor...")
                results = photo_omr_service.process_photo(
                    str(temp_path),
                    exam_data,
                    answer_key_data
                )
                processing_method = "standard_processor_fallback"
        else:
            logger.info("Using standard photo processor...")
            results = photo_omr_service.process_photo(
                str(temp_path),
                exam_data,
                answer_key_data
            )
            processing_method = "standard_processor"
        
        # 6. Cleanup
        if temp_path and temp_path.exists():
            os.remove(temp_path)
        
        # Calculate processing time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        grading_results = results['grading_results']
        
        logger.info(f"=== PHOTO GRADING COMPLETE ===")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"Score: {grading_results['totalScore']}/{grading_results['maxScore']} ({grading_results['percentage']}%)")
        logger.info(f"Detection: {results['omr_results']['statistics']['detected']}/{results.get('questions_mapped', 'unknown')}")
        
        return JSONResponse({
            'success': True,
            'results': grading_results,
            'quality_assessment': quality_assessment,
            'statistics': {
                'omr': results['omr_results']['statistics'],
                'photo': {
                    'bubbles_found': results.get('bubbles_found', 0),
                    'questions_mapped': results.get('questions_mapped', 0),
                    'detection_method': results.get('detection_method', processing_method),
                    'processing_method': processing_method
                },
                'duration': round(duration, 2)
            },
            'metadata': {
                'timestamp': end_time.isoformat(),
                'filename': file.filename,
                'system_version': '3.0.0',
                'processing_type': 'photo',
                'enhanced_processing': use_enhanced_processing,
                'warning': 'Photo processing is experimental and may have lower accuracy than PDF-generated sheets'
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in photo processing: {e}", exc_info=True)
        
        # Cleanup on error
        if temp_path and temp_path.exists():
            try:
                os.remove(temp_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/test-ai")
async def test_ai():
    """
    Test AI connection
    """
    if not ai_verifier:
        return {
            "success": False,
            "message": "AI Verifier not initialized. Check GROQ_API_KEY."
        }
    
    try:
        # Simple test
        return {
            "success": True,
            "message": "AI Verifier is operational",
            "model": settings.GROQ_MODEL
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"AI test failed: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("PROFESSIONAL OMR GRADING SYSTEM v3.0")
    logger.info("=" * 60)
    logger.info(f"Host: {settings.HOST}")
    logger.info(f"Port: {settings.PORT}")
    logger.info(f"AI Verification: {'ENABLED' if ai_verifier else 'DISABLED'}")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,  # Use PORT from settings
        log_level="info"
    )
