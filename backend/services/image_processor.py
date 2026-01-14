"""
Professional Image Processing with OpenCV
Implements advanced preprocessing pipeline for OMR sheets
"""
import cv2
import numpy as np
from typing import Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    OpenCV yordamida professional darajadagi rasm qayta ishlash
    """
    
    def __init__(self, target_width: int = 1240, target_height: int = 1754):
        self.target_width = target_width
        self.target_height = target_height
        self.corner_marker_size = 40
        
    def process(self, image_path: str) -> Dict:
        """
        Rasmni to'liq qayta ishlash pipeline
        
        Returns:
            dict: {
                'original': np.ndarray,
                'processed': np.ndarray,
                'grayscale': np.ndarray,
                'corners': list,
                'quality': dict,
                'dimensions': dict
            }
        """
        logger.info(f"Processing image: {image_path}")
        
        # 1. Yuklash
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        original = image.copy()
        logger.info(f"Image loaded: {image.shape[1]}x{image.shape[0]}")
        
        # 2. Corner markers aniqlash
        logger.info("Detecting corner markers...")
        corners = self.detect_corner_markers(image)
        if corners is None:
            logger.warning("Corner markers not found, using full image")
            corners = self._get_default_corners(image)
        else:
            logger.info(f"Found {len(corners)} corner markers")
        
        # 3. Perspective correction
        logger.info("Correcting perspective...")
        corrected = self.correct_perspective(image, corners)
        
        # 4. Resize to standard dimensions
        logger.info(f"Resizing to {self.target_width}x{self.target_height}...")
        resized = cv2.resize(
            corrected, 
            (self.target_width, self.target_height),
            interpolation=cv2.INTER_CUBIC
        )
        
        # 5. Grayscale conversion
        logger.info("Converting to grayscale...")
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # 6. Adaptive thresholding (CRITICAL!)
        logger.info("Applying adaptive thresholding...")
        processed = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,  # block size
            2    # C constant
        )
        
        # 7. Noise reduction
        logger.info("Reducing noise...")
        denoised = cv2.fastNlMeansDenoising(processed, None, 10, 7, 21)
        
        # 8. Contrast enhancement with CLAHE
        logger.info("Enhancing contrast...")
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 9. Quality assessment
        quality = self.assess_quality(enhanced)
        logger.info(f"Image quality: {quality['overall']:.1f}%")
        
        return {
            'original': original,
            'processed': enhanced,
            'grayscale': gray,  # For AI verification
            'corners': corners,
            'quality': quality,
            'dimensions': {
                'width': self.target_width,
                'height': self.target_height
            }
        }
    
    def detect_corner_markers(self, image: np.ndarray) -> Optional[list]:
        """
        To'rtta burchak markerlarini topish - PDF spetsifikatsiyalariga asoslangan
        Corner markers: 10mm x 10mm, 5mm margin from edges
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aggressive thresholding for black markers
        _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Contour detection
        contours, _ = cv2.findContours(
            binary, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        markers = []
        height, width = image.shape[:2]
        
        # Calculate expected marker size in pixels
        # A4 paper: 210mm x 297mm
        # Marker: 15mm x 15mm (INCREASED from 10mm for better detection)
        # Positions:
        # - Top markers: Y = 5mm
        # - Bottom markers: Y = 277mm (297 - 5 - 15)
        # - Left markers: X = 5mm  
        # - Right markers: X = 190mm (210 - 5 - 15)
        
        px_per_mm_x = width / 210
        px_per_mm_y = height / 297
        expected_size = 15 * min(px_per_mm_x, px_per_mm_y)  # 15mm in pixels
        
        # Define search regions with exact PDF positions
        search_radius = expected_size * 2  # Search within 2x marker size
        
        regions = [
            {
                'center_x': (5 + 7.5) * px_per_mm_x,  # 5mm margin + 7.5mm to center
                'center_y': (5 + 7.5) * px_per_mm_y,
                'name': 'top-left'
            },
            {
                'center_x': (190 + 7.5) * px_per_mm_x,  # 190mm + 7.5mm to center
                'center_y': (5 + 7.5) * px_per_mm_y,
                'name': 'top-right'
            },
            {
                'center_x': (5 + 7.5) * px_per_mm_x,
                'center_y': (277 + 7.5) * px_per_mm_y,  # 277mm + 7.5mm to center
                'name': 'bottom-left'
            },
            {
                'center_x': (190 + 7.5) * px_per_mm_x,
                'center_y': (277 + 7.5) * px_per_mm_y,
                'name': 'bottom-right'
            }
        ]
        
        for region in regions:
            best_match = None
            best_score = 0
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cx, cy = x + w / 2, y + h / 2
                area = w * h
                
                # Check if in search region
                dist = np.sqrt((cx - region['center_x'])**2 + (cy - region['center_y'])**2)
                if dist > search_radius:
                    continue
                
                # Check marker properties
                if h == 0:
                    continue
                    
                aspect_ratio = w / float(h)
                size_ratio = min(w, h) / expected_size
                
                # Score based on:
                # 1. Square shape (aspect ratio close to 1)
                # 2. Size match (close to expected size)
                # 3. Distance from expected position
                # 4. Darkness (filled area)
                
                if (0.7 < aspect_ratio < 1.3 and  # Reasonably square
                    0.5 < size_ratio < 2.0):  # Reasonable size
                    
                    # Calculate score
                    aspect_score = 1.0 - abs(1.0 - aspect_ratio)
                    size_score = 1.0 - abs(1.0 - size_ratio)
                    dist_score = 1.0 - (dist / search_radius)
                    
                    score = (aspect_score * 0.3 + size_score * 0.4 + dist_score * 0.3)
                    
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'x': int(cx),
                            'y': int(cy),
                            'name': region['name'],
                            'score': score
                        }
            
            if best_match and best_match['score'] > 0.5:
                markers.append(best_match)
                logger.info(f"Found {best_match['name']} marker (score: {best_match['score']:.2f})")
        
        if len(markers) == 4:
            logger.info("All 4 corner markers detected successfully")
            return markers
        else:
            logger.warning(f"Only {len(markers)}/4 corner markers found")
            return None
    
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
    
    def correct_perspective(
        self, 
        image: np.ndarray, 
        corners: list
    ) -> np.ndarray:
        """
        Perspective transformation
        """
        # Cornerlarni tartibga solish (top-left, top-right, bottom-left, bottom-right)
        sorted_corners = sorted(corners, key=lambda c: (c['y'], c['x']))
        
        # Top two
        top_corners = sorted(sorted_corners[:2], key=lambda c: c['x'])
        # Bottom two
        bottom_corners = sorted(sorted_corners[2:], key=lambda c: c['x'])
        
        pts = np.array([
            [top_corners[0]['x'], top_corners[0]['y']],      # top-left
            [top_corners[1]['x'], top_corners[1]['y']],      # top-right
            [bottom_corners[0]['x'], bottom_corners[0]['y']], # bottom-left
            [bottom_corners[1]['x'], bottom_corners[1]['y']]  # bottom-right
        ], dtype=np.float32)
        
        # Target rectangle
        width, height = self.target_width, self.target_height
        dst = np.array([
            [0, 0],
            [width, 0],
            [0, height],
            [width, height]
        ], dtype=np.float32)
        
        # Perspective matrix
        matrix = cv2.getPerspectiveTransform(pts, dst)
        
        # Transform
        warped = cv2.warpPerspective(image, matrix, (width, height))
        
        return warped
    
    def assess_quality(self, image: np.ndarray) -> Dict:
        """
        Rasm sifatini baholash
        """
        # Laplacian variance (sharpness)
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        sharpness = min(100, laplacian_var / 100)
        
        # Contrast
        contrast = image.std() / 128 * 100
        
        # Brightness
        brightness = image.mean() / 255 * 100
        
        # Overall quality score
        overall = (sharpness * 0.4 + contrast * 0.4 + brightness * 0.2)
        
        return {
            'sharpness': round(float(sharpness), 2),
            'contrast': round(float(contrast), 2),
            'brightness': round(float(brightness), 2),
            'overall': round(float(overall), 2)
        }
