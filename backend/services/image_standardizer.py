"""
Image Standardization Service
Converts any input image to standardized format for reliable OMR processing

WORKFLOW:
1. Accept any image format (JPEG, PNG, HEIC, WebP, etc.)
2. Normalize to standard format (PNG, high quality)
3. Detect corner markers
4. Apply perspective correction
5. Resize to exact dimensions (2480x3508 px = A4 @ 300 DPI)
6. Apply preprocessing (grayscale, threshold, denoise)
7. Return standardized image ready for OMR

BENEFITS:
- Consistent processing regardless of input format
- Better corner detection (normalized image)
- Accurate coordinates (standardized dimensions)
- Reduced errors from format variations
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageStandardizer:
    """
    Har qanday formatdagi rasmni standart formatga o'tkazish
    """
    
    # Standard dimensions (A4 @ 300 DPI)
    STANDARD_WIDTH = 2480  # pixels
    STANDARD_HEIGHT = 3508  # pixels
    STANDARD_DPI = 300
    
    # Corner marker specifications (from PDF)
    MARKER_SIZE_MM = 15  # 15mm x 15mm
    MARKER_MARGIN_MM = 5  # 5mm from edges
    
    def __init__(self):
        self.target_width = self.STANDARD_WIDTH
        self.target_height = self.STANDARD_HEIGHT
        
    def standardize(self, image_data: bytes, source_format: str = None) -> Dict:
        """
        Rasmni standart formatga o'tkazish
        
        Args:
            image_data: Raw image bytes (any format)
            source_format: Optional format hint (jpeg, png, etc.)
            
        Returns:
            dict: {
                'standardized_image': np.ndarray,  # OpenCV format
                'original_format': str,
                'original_size': tuple,
                'standardized_size': tuple,
                'corners_detected': bool,
                'corners': list,
                'quality_score': float,
                'processing_steps': list
            }
        """
        steps = []
        
        # Step 1: Load image (any format)
        logger.info("Step 1: Loading image...")
        pil_image, original_format = self._load_image(image_data)
        steps.append(f"Loaded {original_format} image")
        
        original_size = pil_image.size
        logger.info(f"Original: {original_format}, {original_size[0]}x{original_size[1]}")
        
        # Step 2: Convert to OpenCV format
        logger.info("Step 2: Converting to OpenCV format...")
        cv_image = self._pil_to_cv2(pil_image)
        steps.append("Converted to OpenCV format")
        
        # Step 3: Detect corner markers
        logger.info("Step 3: Detecting corner markers...")
        corners = self._detect_corners(cv_image)
        corners_detected = corners is not None
        
        if corners_detected:
            logger.info(f"✅ Found {len(corners)} corner markers")
            steps.append(f"Detected {len(corners)} corner markers")
        else:
            logger.warning("⚠️  Corner markers not found, using full image")
            corners = self._get_default_corners(cv_image)
            steps.append("Using default corners (no markers found)")
        
        # Step 4: Perspective correction
        logger.info("Step 4: Applying perspective correction...")
        corrected = self._correct_perspective(cv_image, corners)
        steps.append("Applied perspective correction")
        
        # Step 5: Resize to standard dimensions
        logger.info(f"Step 5: Resizing to {self.target_width}x{self.target_height}...")
        standardized = cv2.resize(
            corrected,
            (self.target_width, self.target_height),
            interpolation=cv2.INTER_CUBIC
        )
        steps.append(f"Resized to {self.target_width}x{self.target_height}")
        
        # Step 6: Quality enhancement
        logger.info("Step 6: Enhancing quality...")
        enhanced = self._enhance_quality(standardized)
        steps.append("Enhanced image quality")
        
        # Step 7: Quality assessment
        logger.info("Step 7: Assessing quality...")
        quality_score = self._assess_quality(enhanced)
        steps.append(f"Quality score: {quality_score:.1f}%")
        
        # Step 8: Update corner coordinates for standardized image
        standardized_corners = self._get_standardized_corners()
        
        logger.info(f"✅ Standardization complete! Quality: {quality_score:.1f}%")
        
        return {
            'standardized_image': enhanced,
            'original_format': original_format,
            'original_size': original_size,
            'standardized_size': (self.target_width, self.target_height),
            'corners_detected': corners_detected,
            'corners': standardized_corners,
            'quality_score': quality_score,
            'processing_steps': steps
        }
    
    def _load_image(self, image_data: bytes) -> Tuple[Image.Image, str]:
        """
        Har qanday formatdagi rasmni yuklash
        """
        try:
            # Try to load with PIL (supports many formats)
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            original_format = pil_image.format or 'UNKNOWN'
            
            return pil_image, original_format
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise ValueError(f"Unsupported image format: {e}")
    
    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """
        PIL Image'ni OpenCV formatga o'tkazish
        """
        # PIL uses RGB, OpenCV uses BGR
        rgb_array = np.array(pil_image)
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        return bgr_array
    
    def _detect_corners(self, image: np.ndarray) -> Optional[list]:
        """
        Corner marker'larni topish
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = image.shape[:2]
        
        # Calculate expected marker size
        px_per_mm_x = width / 210  # A4 width = 210mm
        px_per_mm_y = height / 297  # A4 height = 297mm
        expected_size = self.MARKER_SIZE_MM * min(px_per_mm_x, px_per_mm_y)
        
        # Strict thresholding
        _, binary = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Define search regions (4 corners)
        search_region_mm = 20
        regions = [
            {
                'name': 'top-left',
                'x_min': 0,
                'x_max': int(search_region_mm * px_per_mm_x),
                'y_min': 0,
                'y_max': int(search_region_mm * px_per_mm_y),
                'expected_x': (self.MARKER_MARGIN_MM + self.MARKER_SIZE_MM/2) * px_per_mm_x,
                'expected_y': (self.MARKER_MARGIN_MM + self.MARKER_SIZE_MM/2) * px_per_mm_y
            },
            {
                'name': 'top-right',
                'x_min': int(width - search_region_mm * px_per_mm_x),
                'x_max': width,
                'y_min': 0,
                'y_max': int(search_region_mm * px_per_mm_y),
                'expected_x': (210 - self.MARKER_MARGIN_MM - self.MARKER_SIZE_MM/2) * px_per_mm_x,
                'expected_y': (self.MARKER_MARGIN_MM + self.MARKER_SIZE_MM/2) * px_per_mm_y
            },
            {
                'name': 'bottom-left',
                'x_min': 0,
                'x_max': int(search_region_mm * px_per_mm_x),
                'y_min': int(height - search_region_mm * px_per_mm_y),
                'y_max': height,
                'expected_x': (self.MARKER_MARGIN_MM + self.MARKER_SIZE_MM/2) * px_per_mm_x,
                'expected_y': (297 - self.MARKER_MARGIN_MM - self.MARKER_SIZE_MM/2) * px_per_mm_y
            },
            {
                'name': 'bottom-right',
                'x_min': int(width - search_region_mm * px_per_mm_x),
                'x_max': width,
                'y_min': int(height - search_region_mm * px_per_mm_y),
                'y_max': height,
                'expected_x': (210 - self.MARKER_MARGIN_MM - self.MARKER_SIZE_MM/2) * px_per_mm_x,
                'expected_y': (297 - self.MARKER_MARGIN_MM - self.MARKER_SIZE_MM/2) * px_per_mm_y
            }
        ]
        
        markers = []
        
        for region in regions:
            candidates = []
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cx, cy = x + w / 2, y + h / 2
                
                # Check if in region
                if not (region['x_min'] <= cx <= region['x_max'] and
                        region['y_min'] <= cy <= region['y_max']):
                    continue
                
                # Check size and aspect ratio
                if h == 0 or w == 0:
                    continue
                
                aspect_ratio = w / float(h)
                marker_size = min(w, h)
                
                min_size = expected_size * 0.4
                max_size = expected_size * 2.5
                
                if not (min_size < marker_size < max_size):
                    continue
                
                if not (0.6 < aspect_ratio < 1.67):
                    continue
                
                # Check darkness
                roi = gray[y:y+h, x:x+w]
                if roi.size == 0:
                    continue
                
                avg_intensity = np.mean(roi)
                darkness = (255 - avg_intensity) / 255.0
                
                if darkness < 0.5:
                    continue
                
                # Calculate score
                dist = np.sqrt((cx - region['expected_x'])**2 +
                              (cy - region['expected_y'])**2)
                
                score = darkness * 0.6 + (1.0 - min(dist / expected_size, 1.0)) * 0.4
                
                candidates.append({
                    'x': int(cx),
                    'y': int(cy),
                    'score': score
                })
            
            # Select best candidate
            if candidates:
                best = max(candidates, key=lambda c: c['score'])
                if best['score'] > 0.4:
                    markers.append({
                        'x': best['x'],
                        'y': best['y'],
                        'name': region['name']
                    })
        
        return markers if len(markers) == 4 else None
    
    def _get_default_corners(self, image: np.ndarray) -> list:
        """
        Default corners agar marker topilmasa
        """
        height, width = image.shape[:2]
        return [
            {'x': 0, 'y': 0, 'name': 'top-left'},
            {'x': width, 'y': 0, 'name': 'top-right'},
            {'x': 0, 'y': height, 'name': 'bottom-left'},
            {'x': width, 'y': height, 'name': 'bottom-right'}
        ]
    
    def _correct_perspective(self, image: np.ndarray, corners: list) -> np.ndarray:
        """
        Perspective correction
        """
        # Sort corners
        sorted_corners = sorted(corners, key=lambda c: (c['y'], c['x']))
        top_corners = sorted(sorted_corners[:2], key=lambda c: c['x'])
        bottom_corners = sorted(sorted_corners[2:], key=lambda c: c['x'])
        
        # Source points
        pts = np.array([
            [float(top_corners[0]['x']), float(top_corners[0]['y'])],
            [float(top_corners[1]['x']), float(top_corners[1]['y'])],
            [float(bottom_corners[0]['x']), float(bottom_corners[0]['y'])],
            [float(bottom_corners[1]['x']), float(bottom_corners[1]['y'])]
        ], dtype=np.float32)
        
        # Destination points (A4 aspect ratio)
        width, height = self.target_width, self.target_height
        dst = np.array([
            [0.0, 0.0],
            [float(width), 0.0],
            [0.0, float(height)],
            [float(width), float(height)]
        ], dtype=np.float32)
        
        # Transform
        matrix = cv2.getPerspectiveTransform(pts, dst)
        warped = cv2.warpPerspective(
            image,
            matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)
        )
        
        return warped
    
    def _enhance_quality(self, image: np.ndarray) -> np.ndarray:
        """
        Rasm sifatini yaxshilash
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Sharpen
        kernel_sharpen = np.array([[-1, -1, -1],
                                   [-1,  9, -1],
                                   [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
        
        return sharpened
    
    def _assess_quality(self, image: np.ndarray) -> float:
        """
        Rasm sifatini baholash (0-100)
        """
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        sharpness = min(100, laplacian_var / 100)
        
        # Contrast
        contrast = image.std() / 128 * 100
        
        # Brightness
        brightness = image.mean() / 255 * 100
        
        # Overall score
        overall = (sharpness * 0.4 + contrast * 0.4 + brightness * 0.2)
        
        return round(float(overall), 2)
    
    def _get_standardized_corners(self) -> list:
        """
        Standardizatsiyalangan rasm uchun corner koordinatalari
        Perspective correction'dan keyin, sahifa burchaklari aniq ma'lum
        """
        return [
            {'x': 0.0, 'y': 0.0, 'name': 'top-left'},
            {'x': float(self.target_width), 'y': 0.0, 'name': 'top-right'},
            {'x': 0.0, 'y': float(self.target_height), 'name': 'bottom-left'},
            {'x': float(self.target_width), 'y': float(self.target_height), 'name': 'bottom-right'}
        ]
    
    def standardize_from_base64(self, base64_string: str) -> Dict:
        """
        Base64 string'dan standardizatsiya
        """
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Standardize
        return self.standardize(image_data)
    
    def standardize_from_file(self, file_path: str) -> Dict:
        """
        Fayl yo'lidan standardizatsiya
        """
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        return self.standardize(image_data)
