"""
Error Codes and Messages for OMR System
Centralized error handling
"""

ERROR_CODES = {
    # Image Upload Errors (E001-E099)
    'E001': {
        'code': 'E001',
        'message': 'Image upload failed',
        'description': 'Failed to receive or save uploaded image file',
        'solution': 'Check file format (JPG/PNG) and size (< 10MB)'
    },
    'E002': {
        'code': 'E002',
        'message': 'Invalid image format',
        'description': 'Image format not supported',
        'solution': 'Use JPG or PNG format'
    },
    'E003': {
        'code': 'E003',
        'message': 'Image too large',
        'description': 'Image file size exceeds maximum limit',
        'solution': 'Reduce image size to < 10MB'
    },
    'E004': {
        'code': 'E004',
        'message': 'Image corrupted',
        'description': 'Image file is corrupted or unreadable',
        'solution': 'Re-scan or re-capture the image'
    },
    
    # Image Processing Errors (E100-E199)
    'E100': {
        'code': 'E100',
        'message': 'Image processing failed',
        'description': 'Failed to process image',
        'solution': 'Check image quality and format'
    },
    'E101': {
        'code': 'E101',
        'message': 'Corner markers not found',
        'description': 'Could not detect 4 corner markers',
        'solution': 'Ensure corner markers are visible and dark. Use high-quality scan/photo.'
    },
    'E102': {
        'code': 'E102',
        'message': 'Perspective correction failed',
        'description': 'Failed to correct perspective distortion',
        'solution': 'Ensure all 4 corners are detected correctly'
    },
    'E103': {
        'code': 'E103',
        'message': 'Image quality too low',
        'description': 'Image quality below acceptable threshold',
        'solution': 'Use better lighting and higher resolution'
    },
    
    # QR Code Errors (E200-E299)
    'E200': {
        'code': 'E200',
        'message': 'QR code not found',
        'description': 'Could not detect QR code in image',
        'solution': 'Ensure QR code is visible in top-right corner'
    },
    'E201': {
        'code': 'E201',
        'message': 'QR code unreadable',
        'description': 'QR code detected but could not be decoded',
        'solution': 'Improve image quality or regenerate PDF'
    },
    'E202': {
        'code': 'E202',
        'message': 'Invalid QR code data',
        'description': 'QR code data format is invalid',
        'solution': 'Regenerate PDF with latest version'
    },
    
    # Coordinate Errors (E300-E399)
    'E300': {
        'code': 'E300',
        'message': 'Coordinate calculation failed',
        'description': 'Failed to calculate bubble coordinates',
        'solution': 'Check exam structure and layout data'
    },
    'E301': {
        'code': 'E301',
        'message': 'Invalid exam structure',
        'description': 'Exam structure data is invalid or incomplete',
        'solution': 'Verify exam structure JSON format'
    },
    'E302': {
        'code': 'E302',
        'message': 'Coordinate mismatch',
        'description': 'Calculated coordinates do not match expected layout',
        'solution': 'Ensure PDF and exam structure match'
    },
    
    # OMR Detection Errors (E400-E499)
    'E400': {
        'code': 'E400',
        'message': 'OMR detection failed',
        'description': 'Failed to detect bubble marks',
        'solution': 'Check image quality and bubble marking'
    },
    'E401': {
        'code': 'E401',
        'message': 'Too many uncertain answers',
        'description': 'More than 50% of answers have low confidence',
        'solution': 'Improve image quality or bubble marking'
    },
    'E402': {
        'code': 'E402',
        'message': 'No answers detected',
        'description': 'Could not detect any marked bubbles',
        'solution': 'Ensure bubbles are filled with dark pen/pencil'
    },
    
    # Grading Errors (E500-E599)
    'E500': {
        'code': 'E500',
        'message': 'Grading failed',
        'description': 'Failed to grade exam',
        'solution': 'Check answer key format'
    },
    'E501': {
        'code': 'E501',
        'message': 'Invalid answer key',
        'description': 'Answer key format is invalid',
        'solution': 'Verify answer key JSON format'
    },
    'E502': {
        'code': 'E502',
        'message': 'Answer key mismatch',
        'description': 'Answer key does not match exam structure',
        'solution': 'Ensure answer key matches exam questions'
    },
    
    # AI Verification Errors (E600-E699)
    'E600': {
        'code': 'E600',
        'message': 'AI verification failed',
        'description': 'AI verification service unavailable',
        'solution': 'Check GROQ_API_KEY or disable AI verification'
    },
    'E601': {
        'code': 'E601',
        'message': 'AI API error',
        'description': 'Error communicating with AI service',
        'solution': 'Check internet connection and API key'
    },
    
    # Annotation Errors (E700-E799)
    'E700': {
        'code': 'E700',
        'message': 'Annotation failed',
        'description': 'Failed to create annotated image',
        'solution': 'Check image processing results'
    },
    
    # System Errors (E900-E999)
    'E900': {
        'code': 'E900',
        'message': 'Internal server error',
        'description': 'Unexpected server error occurred',
        'solution': 'Contact system administrator'
    },
    'E901': {
        'code': 'E901',
        'message': 'Out of memory',
        'description': 'Server ran out of memory',
        'solution': 'Reduce image size or contact administrator'
    },
    'E902': {
        'code': 'E902',
        'message': 'Timeout',
        'description': 'Processing took too long',
        'solution': 'Try again or reduce image size'
    }
}

class OMRError(Exception):
    """Base exception for OMR system"""
    def __init__(self, error_code: str, details: str = None):
        self.error_code = error_code
        self.error_info = ERROR_CODES.get(error_code, {
            'code': error_code,
            'message': 'Unknown error',
            'description': details or 'An unknown error occurred',
            'solution': 'Contact system administrator'
        })
        self.details = details
        super().__init__(self.error_info['message'])
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'error_code': self.error_code,
            'message': self.error_info['message'],
            'description': self.error_info['description'],
            'solution': self.error_info['solution'],
            'details': self.details
        }

def get_error_info(error_code: str) -> dict:
    """Get error information by code"""
    return ERROR_CODES.get(error_code, {
        'code': error_code,
        'message': 'Unknown error',
        'description': 'Error code not found',
        'solution': 'Contact system administrator'
    })
