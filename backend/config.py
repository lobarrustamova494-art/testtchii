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
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Database
    MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'evalbee_omr')
    USE_DATABASE = os.getenv('USE_DATABASE', 'true').lower() == 'true'
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8001))
    
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
    
    # OMR Detection - CORRECTED PARAMETERS
    BUBBLE_RADIUS = 29  # FIXED: 2.5mm * 11.81 px/mm = 29.5 pixels (was 8!)
    MIN_DARKNESS = 12.0  # % - MAXIMUM SENSITIVITY for very light marks
    MIN_COVERAGE = 20.0  # % - FURTHER LOWERED from 25.0 for partial marks
    MIN_INNER_FILL = 15.0  # % - MAXIMUM SENSITIVITY for light marks
    MIN_DIFFERENCE = 4.0  # % - MAXIMUM SENSITIVITY for closer marks
    MULTIPLE_MARKS_THRESHOLD = 4.0  # % - MAXIMUM SENSITIVITY
    
    # Corner Detection - IMPROVED SCORING WEIGHTS
    CORNER_ASPECT_WEIGHT = 0.15  # Square shape (increased)
    CORNER_SIZE_WEIGHT = 0.20  # Correct size (increased)
    CORNER_DIST_WEIGHT = 0.30  # Near expected position (increased)
    CORNER_DARKNESS_WEIGHT = 0.25  # Darkness (decreased)
    CORNER_UNIFORMITY_WEIGHT = 0.10  # Uniform color (decreased)
    CORNER_MIN_SCORE = 0.3  # LOWERED from 0.4 for better detection
    
    # CORS
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS', 
        'http://localhost:3000,http://localhost:5173,http://10.64.226.226:3000,https://evalbee-frontend.onrender.com'
    ).split(',')
    
    # AI Verification - TEMPORARILY DISABLED due to quota limit
    ENABLE_AI_VERIFICATION = False  # Temporarily disabled due to OpenAI quota
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')  # 'openai' or 'groq'
    
    # OpenAI Settings
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')  # GPT-4 Omni with vision
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.1))
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 200))
    
    # Groq Settings (fallback)
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')  # Updated to available model
    GROQ_TEMPERATURE = float(os.getenv('GROQ_TEMPERATURE', 0.1))
    GROQ_MAX_TOKENS = int(os.getenv('GROQ_MAX_TOKENS', 200))

settings = Settings()
