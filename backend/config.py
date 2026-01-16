"""
Configuration settings for OMR Backend
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    
    # Processing
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB
    TEMP_DIR = Path(os.getenv('TEMP_DIR', 'temp'))
    AI_CONFIDENCE_THRESHOLD = float(os.getenv('AI_CONFIDENCE_THRESHOLD', 70.0))
    
    # Image Processing
    TARGET_WIDTH = 2480  # Updated to match PDF resolution
    TARGET_HEIGHT = 3508  # Updated to match PDF resolution
    CORNER_MARKER_SIZE = 60  # Increased for better detection
    
    # Adaptive Thresholding - OPTIMAL PARAMETERS
    ADAPTIVE_THRESHOLD_BLOCK_SIZE = 15  # Must be odd
    ADAPTIVE_THRESHOLD_C = 3  # Higher = less black pixels
    
    # Layout Compatibility
    # Set to True to use old PDF layout (gridStartY=113mm)
    # Set to False to use new PDF layout (gridStartY=149mm)
    USE_OLD_PDF_LAYOUT = False  # Changed to False for new PDFs
    
    # OMR Detection - OPTIMAL PARAMETERS (from testing)
    BUBBLE_RADIUS = 8  # pixels in processed image
    MIN_DARKNESS = 35.0  # % - minimum darkness to consider as mark
    MIN_COVERAGE = 40.0  # % - minimum coverage of dark pixels
    MIN_INNER_FILL = 50.0  # % - MOST IMPORTANT! Rejects partial marks
    MIN_DIFFERENCE = 15.0  # % - minimum difference between 1st and 2nd
    MULTIPLE_MARKS_THRESHOLD = 10.0  # % - if difference < this, multiple marks
    
    # Corner Detection - SCORING WEIGHTS
    CORNER_ASPECT_WEIGHT = 0.10  # Square shape
    CORNER_SIZE_WEIGHT = 0.15  # Correct size
    CORNER_DIST_WEIGHT = 0.25  # Near expected position
    CORNER_DARKNESS_WEIGHT = 0.30  # Darkness (most important)
    CORNER_UNIFORMITY_WEIGHT = 0.20  # Uniform color
    CORNER_MIN_SCORE = 0.4  # Minimum score to accept as corner
    
    # CORS
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS', 
        'http://localhost:3000,http://localhost:5173,https://evalbee-frontend.onrender.com'
    ).split(',')
    
    # Groq Model - TEMPORARILY DISABLED (model decommissioned)
    GROQ_MODEL = "llama-3.2-90b-vision-preview"  # Decommissioned
    GROQ_TEMPERATURE = 0.1
    GROQ_MAX_TOKENS = 200
    ENABLE_AI_VERIFICATION = False  # Disabled until new vision model available

settings = Settings()
