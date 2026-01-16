"""
QR Code Reader - Extract layout information from QR code
Professional OMR systems use QR codes for 100% reliable layout detection
"""
import cv2
import numpy as np
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try multiple QR detection libraries
PYZBAR_AVAILABLE = False
OPENCV_QR_AVAILABLE = False

# Try pyzbar first
try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
    logger.info("pyzbar library loaded successfully")
except Exception as e:
    logger.warning(f"pyzbar not available: {e}")

# Try OpenCV QR detector as fallback
try:
    import cv2
    # Test if QRCodeDetector is available
    qr_detector = cv2.QRCodeDetector()
    OPENCV_QR_AVAILABLE = True
    logger.info("OpenCV QRCodeDetector available")
except Exception as e:
    logger.warning(f"OpenCV QRCodeDetector not available: {e}")

if not PYZBAR_AVAILABLE and not OPENCV_QR_AVAILABLE:
    logger.warning("No QR code detection library available - using default layout")

class QRCodeReader:
    """
    QR Code'dan layout ma'lumotlarini o'qish
    """
    
    def __init__(self):
        self.use_pyzbar = PYZBAR_AVAILABLE
        self.use_opencv = OPENCV_QR_AVAILABLE
        
        if not self.use_pyzbar and not self.use_opencv:
            logger.warning("QRCodeReader initialized without any QR detection support")
        elif self.use_pyzbar:
            logger.info("QRCodeReader using pyzbar")
        elif self.use_opencv:
            logger.info("QRCodeReader using OpenCV QRCodeDetector")
    
    def read_qr_code(self, image: np.ndarray) -> Optional[Dict]:
        """
        Image'dan QR code'ni topish va o'qish
        
        Args:
            image: Grayscale or BGR image
            
        Returns:
            dict: Layout data from QR code, or None if not found
        """
        # Try pyzbar first, then OpenCV
        if self.use_pyzbar:
            result = self._read_with_pyzbar(image)
            if result:
                return result
        
        if self.use_opencv:
            result = self._read_with_opencv(image)
            if result:
                return result
        
        return None
    
    def _read_with_pyzbar(self, image: np.ndarray) -> Optional[Dict]:
        """Read QR code using pyzbar"""
        try:
            logger.info("Searching for QR code...")
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Try 1: Direct detection
            qr_codes = pyzbar.decode(gray)
            
            # Try 2: Enhanced detection if first attempt fails
            if not qr_codes:
                logger.info("First attempt failed, trying enhanced detection...")
                enhanced = self.enhance_for_qr_detection(gray)
                qr_codes = pyzbar.decode(enhanced)
            
            # Try 3: Try different regions (top-right corner where QR is located)
            if not qr_codes:
                logger.info("Trying top-right corner region...")
                h, w = gray.shape
                # QR is at 175mm, 10mm, 25mm x 25mm on A4 (210mm x 297mm)
                # That's roughly 83% from left, 3% from top, 12% width, 8% height
                x1 = int(w * 0.75)
                y1 = 0
                x2 = w
                y2 = int(h * 0.15)
                corner_region = gray[y1:y2, x1:x2]
                qr_codes = pyzbar.decode(corner_region)
            
            if not qr_codes:
                logger.warning("No QR code found in image after all attempts")
                return None
            
            # Read first QR code
            qr_data = qr_codes[0].data.decode('utf-8')
            logger.info(f"QR code found! Data length: {len(qr_data)} bytes")
            
            # Parse JSON data
            layout_data = json.loads(qr_data)
            
            # Validate data structure
            if not self._validate_layout_data(layout_data):
                logger.error("Invalid QR code data structure")
                return None
            
            logger.info(f"✅ QR code successfully read: Exam '{layout_data.get('examName')}', Version {layout_data.get('version')}")
            logger.info(f"   Total questions: {layout_data.get('structure', {}).get('totalQuestions')}")
            
            return layout_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse QR code JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading QR code with pyzbar: {e}")
            return None
    
    def _read_with_opencv(self, image: np.ndarray) -> Optional[Dict]:
        """Read QR code using OpenCV QRCodeDetector"""
        try:
            logger.info("Trying OpenCV QRCodeDetector...")
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Create QR detector
            qr_detector = cv2.QRCodeDetector()
            
            # Try 1: Direct detection
            data, bbox, straight_qrcode = qr_detector.detectAndDecode(gray)
            
            # Try 2: Enhanced detection if first attempt fails
            if not data:
                logger.info("First attempt failed, trying enhanced detection...")
                enhanced = self.enhance_for_qr_detection(gray)
                data, bbox, straight_qrcode = qr_detector.detectAndDecode(enhanced)
            
            # Try 3: Try different regions (top-right corner)
            if not data:
                logger.info("Trying top-right corner region...")
                h, w = gray.shape
                x1 = int(w * 0.75)
                y1 = 0
                x2 = w
                y2 = int(h * 0.15)
                corner_region = gray[y1:y2, x1:x2]
                data, bbox, straight_qrcode = qr_detector.detectAndDecode(corner_region)
            
            if not data:
                logger.warning("OpenCV QRCodeDetector: No QR code found")
                return None
            
            logger.info(f"OpenCV QR code found! Data length: {len(data)} bytes")
            
            # Parse JSON data
            layout_data = json.loads(data)
            
            # Validate data structure
            if not self._validate_layout_data(layout_data):
                logger.error("Invalid QR code data structure")
                return None
            
            logger.info(f"✅ QR code successfully read with OpenCV: Exam '{layout_data.get('examName')}', Version {layout_data.get('version')}")
            
            return layout_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse QR code JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading QR code with OpenCV: {e}")
            return None
    
    def _validate_layout_data(self, data: Dict) -> bool:
        """
        QR code data'ni validate qilish
        """
        required_fields = ['examId', 'version', 'layout', 'structure']
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate layout fields
        layout = data['layout']
        required_layout_fields = [
            'questionsPerRow', 'bubbleSpacing', 'bubbleRadius',
            'rowHeight', 'gridStartX', 'gridStartY'
        ]
        
        for field in required_layout_fields:
            if field not in layout:
                logger.error(f"Missing layout field: {field}")
                return False
        
        return True
    
    def get_layout_from_qr(self, qr_data: Dict) -> Dict:
        """
        QR code'dan layout parametrlarini olish
        
        Returns:
            dict: Layout parameters for coordinate calculation
        """
        layout = qr_data['layout']
        
        return {
            'questions_per_row': layout['questionsPerRow'],
            'bubble_spacing_mm': layout['bubbleSpacing'],
            'bubble_radius_mm': layout['bubbleRadius'],
            'row_height_mm': layout['rowHeight'],
            'grid_start_x_mm': layout['gridStartX'],
            'grid_start_y_mm': layout['gridStartY'],
            'question_spacing_mm': layout.get('questionSpacing', 90),
            'first_bubble_offset_mm': layout.get('firstBubbleOffset', 8)
        }
    
    def enhance_for_qr_detection(self, image: np.ndarray) -> np.ndarray:
        """
        QR code detection uchun image'ni yaxshilash
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        return denoised
