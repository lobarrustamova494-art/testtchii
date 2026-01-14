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
    
    # OMR Detection - AGGRESSIVE SETTINGS FOR BETTER DETECTION
    BUBBLE_RADIUS = 10  # Increased from 8 - larger search area
    MIN_DARKNESS = 20.0  # Lowered from 25 - detect lighter marks
    MIN_DIFFERENCE = 8.0  # Lowered from 10 - more sensitive
    MULTIPLE_MARKS_THRESHOLD = 15  # Increased from 10 - reduce false positives
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Groq Model - TEMPORARILY DISABLED (model decommissioned)
    GROQ_MODEL = "llama-3.2-90b-vision-preview"  # Decommissioned
    GROQ_TEMPERATURE = 0.1
    GROQ_MAX_TOKENS = 200
    ENABLE_AI_VERIFICATION = False  # Disabled until new vision model available

settings = Settings()
