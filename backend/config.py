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
    TARGET_WIDTH = 1240
    TARGET_HEIGHT = 1754
    CORNER_MARKER_SIZE = 40
    
    # Layout Compatibility
    # Set to True to use old PDF layout (gridStartY=113mm)
    # Set to False to use new PDF layout (gridStartY=149mm)
    USE_OLD_PDF_LAYOUT = False  # Changed to False for new PDFs
    
    # OMR Detection - BALANCED SETTINGS
    BUBBLE_RADIUS = 10  # Standard search area
    MIN_DARKNESS = 35.0  # Higher threshold - only detect clearly filled bubbles
    MIN_DIFFERENCE = 15.0  # Larger difference required between marks
    MULTIPLE_MARKS_THRESHOLD = 12  # More lenient - reduce false positives
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Groq Model - TEMPORARILY DISABLED (model decommissioned)
    GROQ_MODEL = "llama-3.2-90b-vision-preview"  # Decommissioned
    GROQ_TEMPERATURE = 0.1
    GROQ_MAX_TOKENS = 200
    ENABLE_AI_VERIFICATION = False  # Disabled until new vision model available

settings = Settings()
