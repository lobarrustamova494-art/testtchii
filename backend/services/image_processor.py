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
        self.corner_marker_size = 60  # Increased from 40 to 60 for better detection
        
    def process(self, image_path: str) -> Dict:
        """
        Rasmni to'liq qayta ishlash pipeline
        
        Returns:
            dict: {
                'original': np.ndarray,
                'processed': np.ndarray,
                'grayscale': np.ndarray,
                'gray_for_omr': np.ndarray,  # PURE grayscale for OMR
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
        
        # CRITICAL: If image is already correct size, skip processing!
        # This preserves original quality for OMR detection
        if image.shape[1] == self.target_width and image.shape[0] == self.target_height:
            logger.info("Image already correct size - skipping perspective correction")
            
            # Just convert to grayscale
            gray_for_omr = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_enhanced = gray_for_omr.copy()
            
            # Default corners
            corners = self._get_default_corners(image)
            
            # Quality assessment
            quality = self.assess_quality(gray_for_omr)
            
            return {
                'original': original,
                'processed': gray_for_omr,  # No processing needed
                'grayscale': gray_enhanced,
                'gray_for_omr': gray_for_omr,  # PURE grayscale
                'corners': corners,
                'quality': quality,
                'dimensions': {
                    'width': self.target_width,
                    'height': self.target_height
                }
            }
        
        # 2. Corner markers aniqlash
        logger.info("Detecting corner markers...")
        corners_original = self.detect_corner_markers(image)
        if corners_original is None:
            logger.warning("Corner markers not found, using full image")
            corners_original = self._get_default_corners(image)
        else:
            logger.info(f"Found {len(corners_original)} corner markers")
        
        # 3. Perspective correction
        logger.info("Correcting perspective...")
        corrected = self.correct_perspective(image, corners_original)
        
        # 4. Resize to standard dimensions
        logger.info(f"Resizing to {self.target_width}x{self.target_height}...")
        resized = cv2.resize(
            corrected, 
            (self.target_width, self.target_height),
            interpolation=cv2.INTER_CUBIC
        )
        
        # 5. Transform corner coordinates to match resized image
        # After perspective correction, corners are at standard positions
        # We need to update corner coordinates to match the resized image
        corners = self._transform_corners_after_processing(
            corners_original, 
            image.shape, 
            corrected.shape,
            (self.target_width, self.target_height)
        )
        
        # 5. Grayscale conversion
        logger.info("Converting to grayscale...")
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # CRITICAL: Keep PURE grayscale for OMR detection (no enhancement!)
        # OMR detection works best on pure grayscale
        gray_for_omr = gray.copy()
        
        # 5.5. Enhance grayscale for better annotation quality ONLY
        logger.info("Enhancing grayscale for annotation...")
        # Apply CLAHE for better contrast (for annotation, not OMR!)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_enhanced = clahe.apply(gray)
        
        # 6. Adaptive thresholding (CRITICAL!)
        logger.info("Applying adaptive thresholding...")
        # CRITICAL FIX: Use GRAYSCALE for OMR detection, not thresholded!
        # Thresholded image is only for visualization/annotation
        processed = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15,  # Increased block size from 11 to 15
            3    # Increased C constant from 2 to 3
        )
        
        # CRITICAL: Keep original grayscale for OMR detection
        # OMR detector works MUCH better on grayscale than binary!
        
        # 7. Noise reduction with bilateral filter (preserves edges better)
        logger.info("Reducing noise...")
        # First pass: bilateral filter to preserve edges
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Second pass: morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        # 8. Contrast enhancement with CLAHE
        logger.info("Enhancing contrast...")
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))  # Increased clipLimit
        enhanced = clahe.apply(denoised)
        
        # 9. Gamma correction for light marks detection (NEW!)
        logger.info("Applying gamma correction for light marks...")
        gamma = 0.8  # Brighten the image to detect light marks better
        gamma_corrected = np.power(enhanced / 255.0, gamma) * 255.0
        gamma_corrected = gamma_corrected.astype(np.uint8)
        
        # 10. Final sharpening to improve bubble detection
        logger.info("Sharpening image...")
        kernel_sharpen = np.array([[-1,-1,-1],
                                   [-1, 9,-1],
                                   [-1,-1,-1]])
        sharpened = cv2.filter2D(gamma_corrected, -1, kernel_sharpen)
        
        # 11. Additional light mark enhancement
        logger.info("Enhancing light marks...")
        # Create a mask for potential light marks
        light_mask = cv2.inRange(sharpened, 180, 220)  # Light gray areas
        
        # Darken light marks slightly
        light_enhanced = sharpened.copy()
        light_enhanced[light_mask > 0] = light_enhanced[light_mask > 0] * 0.85
        light_enhanced = light_enhanced.astype(np.uint8)
        
        # 12. Quality assessment
        quality = self.assess_quality(light_enhanced)
        logger.info(f"Image quality: {quality['overall']:.1f}%")
        
        return {
            'original': original,
            'processed': light_enhanced,  # Use light-enhanced image for OMR detection
            'grayscale': gray_enhanced,  # Use enhanced grayscale for annotation
            'gray_for_omr': gray_for_omr,  # CRITICAL: Original grayscale for OMR detection
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
        Corner markers: 15mm x 15mm, 5mm margin from edges
        
        YANGI YONDASHUV: Faqat 4 ta burchakda qidirish, boshqa joyda emas!
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = image.shape[:2]
        
        logger.info(f"Detecting corners in {width}x{height} image")
        
        # Calculate expected marker size in pixels
        px_per_mm_x = width / 210
        px_per_mm_y = height / 297
        expected_size = 15 * min(px_per_mm_x, px_per_mm_y)
        
        logger.info(f"Expected marker size: {expected_size:.1f} px")
        
        # VERY STRICT thresholding - IMPROVED
        # Use Otsu's method for better automatic thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Additional manual threshold for very light images
        if np.mean(binary) < 10:  # If too few black pixels
            _, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)  # Lower threshold
        
        # IMPROVED: More aggressive morphological operations
        kernel = np.ones((5, 5), np.uint8)  # Larger kernel
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Additional: Remove small noise
        kernel_small = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small)
        
        # Find contours
        contours, _ = cv2.findContours(
            binary, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        logger.info(f"Found {len(contours)} total contours")
        
        # Define 4 corner regions - VERY SMALL regions!
        margin_mm = 5
        marker_size_mm = 15
        search_region_mm = 20  # Only 20mm from edge!
        
        regions = [
            {
                'name': 'top-left',
                'x_min': 0,
                'x_max': int(search_region_mm * px_per_mm_x),
                'y_min': 0,
                'y_max': int(search_region_mm * px_per_mm_y),
                'expected_x': (margin_mm + marker_size_mm/2) * px_per_mm_x,
                'expected_y': (margin_mm + marker_size_mm/2) * px_per_mm_y
            },
            {
                'name': 'top-right',
                'x_min': int(width - search_region_mm * px_per_mm_x),
                'x_max': width,
                'y_min': 0,
                'y_max': int(search_region_mm * px_per_mm_y),
                'expected_x': (210 - margin_mm - marker_size_mm/2) * px_per_mm_x,
                'expected_y': (margin_mm + marker_size_mm/2) * px_per_mm_y
            },
            {
                'name': 'bottom-left',
                'x_min': 0,
                'x_max': int(search_region_mm * px_per_mm_x),
                'y_min': int(height - search_region_mm * px_per_mm_y),
                'y_max': height,
                'expected_x': (margin_mm + marker_size_mm/2) * px_per_mm_x,
                'expected_y': (297 - margin_mm - marker_size_mm/2) * px_per_mm_y
            },
            {
                'name': 'bottom-right',
                'x_min': int(width - search_region_mm * px_per_mm_x),
                'x_max': width,
                'y_min': int(height - search_region_mm * px_per_mm_y),
                'y_max': height,
                'expected_x': (210 - margin_mm - marker_size_mm/2) * px_per_mm_x,
                'expected_y': (297 - margin_mm - marker_size_mm/2) * px_per_mm_y
            }
        ]
        
        markers = []
        
        for region in regions:
            logger.info(f"\nSearching for {region['name']} marker...")
            logger.info(f"  Region: x=[{region['x_min']:.0f}, {region['x_max']:.0f}], "
                       f"y=[{region['y_min']:.0f}, {region['y_max']:.0f}]")
            
            candidates = []
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cx, cy = x + w / 2, y + h / 2
                
                # FIRST CHECK: Must be in region
                if not (region['x_min'] <= cx <= region['x_max'] and 
                        region['y_min'] <= cy <= region['y_max']):
                    continue
                
                # SECOND CHECK: Size and aspect ratio
                if h == 0 or w == 0:
                    continue
                
                aspect_ratio = w / float(h)
                marker_size = min(w, h)
                
                min_size = expected_size * 0.4
                max_size = expected_size * 2.5
                
                if not (min_size < marker_size < max_size):
                    continue
                
                if not (0.6 < aspect_ratio < 1.67):  # More lenient
                    continue
                
                # THIRD CHECK: Darkness and uniformity
                roi = gray[y:y+h, x:x+w]
                if roi.size == 0:
                    continue
                
                avg_intensity = np.mean(roi)
                darkness = (255 - avg_intensity) / 255.0
                
                if darkness < 0.5:  # At least 50% dark
                    continue
                
                std_intensity = np.std(roi)
                uniformity = 1.0 - min(std_intensity / 128.0, 1.0)
                
                if uniformity < 0.4:  # At least 40% uniform
                    continue
                
                # FOURTH CHECK: Distance from expected position
                dist = np.sqrt((cx - region['expected_x'])**2 + 
                              (cy - region['expected_y'])**2)
                
                # Calculate score
                aspect_score = 1.0 - min(abs(1.0 - aspect_ratio), 1.0)
                size_score = 1.0 - min(abs(marker_size - expected_size) / expected_size, 1.0)
                dist_score = 1.0 - min(dist / (expected_size * 2), 1.0)
                
                score = (
                    aspect_score * 0.10 + 
                    size_score * 0.15 + 
                    dist_score * 0.25 +
                    darkness * 0.30 +
                    uniformity * 0.20
                )
                
                candidates.append({
                    'x': int(cx),
                    'y': int(cy),
                    'score': score,
                    'darkness': darkness,
                    'uniformity': uniformity,
                    'size': marker_size,
                    'aspect': aspect_ratio,
                    'dist': dist
                })
            
            logger.info(f"  Found {len(candidates)} candidates in region")
            
            # Select best candidate
            if candidates:
                best = max(candidates, key=lambda c: c['score'])
                
                if best['score'] > 0.4:  # Lower threshold
                    markers.append({
                        'x': best['x'],
                        'y': best['y'],
                        'name': region['name'],
                        'score': best['score'],
                        'darkness': best['darkness'],
                        'uniformity': best['uniformity'],
                        'size': best['size'],
                        'aspect': best['aspect']
                    })
                    logger.info(
                        f"  ✅ Selected: pos=({best['x']}, {best['y']}), "
                        f"score={best['score']:.2f}, darkness={best['darkness']:.2f}, "
                        f"uniformity={best['uniformity']:.2f}"
                    )
                else:
                    logger.warning(
                        f"  ❌ Best candidate score too low: {best['score']:.2f}"
                    )
            else:
                logger.warning(f"  ❌ No candidates found in region")
        
        if len(markers) == 4:
            logger.info("\n✅ All 4 corner markers detected successfully!")
            return markers
        else:
            logger.warning(f"\n⚠️  Only {len(markers)}/4 corner markers found")
            logger.warning("Falling back to default corners")
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
    
    def _transform_corners_after_processing(
        self,
        corners_original: list,
        original_shape: tuple,
        corrected_shape: tuple,
        target_size: tuple
    ) -> list:
        """
        Corner koordinatalarini perspective correction va resize'dan keyin yangilash
        
        CRITICAL FIX: Perspective correction'dan keyin, image to'g'ri to'rtburchak bo'ladi.
        Corner marker'lar endi sahifa ichida (margin + marker_size/2) joylashgan.
        
        Lekin biz corner'larni SAHIFA BURCHAKLARIDA deb hisoblashimiz kerak,
        chunki perspective correction sahifani to'g'ri to'rtburchakka keltiradi.
        
        Args:
            corners_original: Original image'dagi corner'lar
            original_shape: Original image shape (height, width)
            corrected_shape: Perspective corrected image shape
            target_size: Target size after resize (width, height)
            
        Returns:
            list: Transformed corner coordinates (PAGE CORNERS, not marker centers!)
        """
        target_width, target_height = target_size
        
        # CRITICAL: After perspective correction, the PAGE CORNERS are at:
        # (0, 0), (width, 0), (0, height), (width, height)
        # 
        # The corner MARKERS are INSIDE the page at:
        # margin + marker_size/2 from each edge
        #
        # But for coordinate calculation, we need to use PAGE CORNERS as reference,
        # because that's what perspective correction gives us!
        
        transformed_corners = [
            {
                'x': 0.0,
                'y': 0.0,
                'name': 'top-left'
            },
            {
                'x': float(target_width),
                'y': 0.0,
                'name': 'top-right'
            },
            {
                'x': 0.0,
                'y': float(target_height),
                'name': 'bottom-left'
            },
            {
                'x': float(target_width),
                'y': float(target_height),
                'name': 'bottom-right'
            }
        ]
        
        logger.info("✅ Corner coordinates set to PAGE CORNERS (after perspective correction)")
        for corner in transformed_corners:
            logger.info(f"   {corner['name']}: ({corner['x']:.1f}, {corner['y']:.1f}) px")
        
        return transformed_corners
    
    def correct_perspective(
        self, 
        image: np.ndarray, 
        corners: list
    ) -> np.ndarray:
        """
        YAXSHILANGAN Perspective transformation
        
        Yangi yondashuv:
        1. Cornerlarni aniq tartibga solish
        2. Sub-pixel accuracy
        3. Bi-cubic interpolation
        4. A4 aspect ratio enforcement
        """
        # Cornerlarni tartibga solish (top-left, top-right, bottom-left, bottom-right)
        sorted_corners = sorted(corners, key=lambda c: (c['y'], c['x']))
        
        # Top two
        top_corners = sorted(sorted_corners[:2], key=lambda c: c['x'])
        # Bottom two
        bottom_corners = sorted(sorted_corners[2:], key=lambda c: c['x'])
        
        # Source points with sub-pixel accuracy
        pts = np.array([
            [float(top_corners[0]['x']), float(top_corners[0]['y'])],      # top-left
            [float(top_corners[1]['x']), float(top_corners[1]['y'])],      # top-right
            [float(bottom_corners[0]['x']), float(bottom_corners[0]['y'])], # bottom-left
            [float(bottom_corners[1]['x']), float(bottom_corners[1]['y'])]  # bottom-right
        ], dtype=np.float32)
        
        # Target rectangle - EXACT A4 dimensions
        width, height = self.target_width, self.target_height
        dst = np.array([
            [0.0, 0.0],
            [float(width), 0.0],
            [0.0, float(height)],
            [float(width), float(height)]
        ], dtype=np.float32)
        
        # Calculate perspective matrix with RANSAC for robustness
        matrix = cv2.getPerspectiveTransform(pts, dst)
        
        # Transform with INTER_CUBIC for better quality
        warped = cv2.warpPerspective(
            image, 
            matrix, 
            (width, height),
            flags=cv2.INTER_CUBIC,  # Better interpolation
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)  # White border
        )
        
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
