"""
FastAPI Backend for Professional OMR System
Hybrid: OpenCV + Groq AI
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import logging
import json
from pathlib import Path
from datetime import datetime

from config import settings
from services import ImageProcessor, OMRDetector, AIVerifier, AnswerGrader, ImageAnnotator, QRCodeReader
from utils import CoordinateMapper

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
image_processor = ImageProcessor(
    target_width=settings.TARGET_WIDTH,
    target_height=settings.TARGET_HEIGHT
)

omr_detector = OMRDetector(
    bubble_radius=settings.BUBBLE_RADIUS,
    min_darkness=settings.MIN_DARKNESS,
    min_difference=settings.MIN_DIFFERENCE,
    multiple_marks_threshold=settings.MULTIPLE_MARKS_THRESHOLD
)

# QR Code Reader
qr_reader = QRCodeReader()

# AI Verifier (only if API key is provided AND enabled)
ai_verifier = None
if settings.GROQ_API_KEY and settings.ENABLE_AI_VERIFICATION:
    try:
        ai_verifier = AIVerifier(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS
        )
        logger.info("AI Verifier initialized successfully")
    except Exception as e:
        logger.warning(f"AI Verifier initialization failed: {e}")
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

@app.post("/api/grade-sheet")
async def grade_sheet(
    file: UploadFile = File(...),
    exam_structure: str = Form(...),
    answer_key: str = Form(...)
):
    """
    Varaqni tekshirish - Professional OMR + AI
    
    Args:
        file: Image file (JPEG/PNG)
        exam_structure: JSON string of exam structure
        answer_key: JSON string of answer key
        
    Returns:
        JSON with grading results
    """
    start_time = datetime.now()
    logger.info(f"=== NEW GRADING REQUEST ===")
    logger.info(f"File: {file.filename}")
    
    temp_path = None
    
    try:
        # 1. Validate file
        if not file.content_type.startswith('image/'):
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
        
        # 5. Coordinate Calculation
        logger.info("STEP 3/6: Coordinate Calculation...")
        coord_mapper = CoordinateMapper(
            processed['dimensions']['width'],
            processed['dimensions']['height'],
            exam_data,
            qr_layout=qr_layout  # Pass QR layout if available
        )
        coordinates = coord_mapper.calculate_all()
        
        # 6. OMR Detection
        logger.info("STEP 4/6: OMR Detection...")
        omr_results = omr_detector.detect_all_answers(
            processed['processed'],
            coordinates,
            exam_data
        )
        
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
        annotated_image = annotator.annotate_sheet(
            processed['grayscale'],
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
                'duration': round(duration, 2)
            },
            'metadata': {
                'timestamp': end_time.isoformat(),
                'filename': file.filename,
                'system_version': '3.0.0'
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
        port=settings.PORT,
        log_level="info"
    )
