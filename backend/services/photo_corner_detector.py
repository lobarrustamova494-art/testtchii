"""
Photo Corner Detector
Specialized corner detection for photos (not PDF scans)
"""
import cv2
import numpy as np
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PhotoCornerDetector:
    """
    Foto'lar uchun maxsus corner detection
    
    Features:
    - Adaptive thresholding for poor lighting
    - Multiple detection methods
    - Lenient size and darkness requirements
    - Fallback strategies
    """
    
    def __init__(self):
        # Photo-specific parameters (more lenient)
        self.min_darkness = 0.3  # 30% dark (vs 50% for PDF)
        self.min_uniformity = 0.2  # 20% uniform (vs 40% for PDF)
        self.size_tolerance = 3.0  # 3x size variation (vs 2.5x for PDF)
        self.aspect_tolerance = 2.5  # More lenient aspect ratio
        
    def detect_corners(self, image: np.ndarray) -> Optional[List[Tuple[float, float]]]:
        """
        Detect 4 corner markers in photo
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            list: [(x, y), ...] for 4 corners or None if failed
        """
        logger.info("Starting photo corner detection...")
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        height, width = gray.shape
        logger.info(f"Image size: {width}x{height}")
        
        # Try multiple detection methods
        methods = [
            self._detect_with_adaptive_threshold,
            self._detect_with_otsu_threshold,
            self._detect_with_canny_edges,
            self._detect_with_template_matching
        ]
        
        for i, method in enumerate(methods):
            logger.info(f"Trying method {i+1}: {method.__name__}")
            
            try:
                corners = method(gray)
                if corners and len(corners) == 4:
                    logger.info(f"✅ Success with method {i+1}")
                    return self._order_corners(corners)
            except Exception as e:
                logger.warning(f"Method {i+1} failed: {e}")
                continue
        
        logger.warning("All corner detection methods failed")
        return None
    
    def _detect_with_adaptive_threshold(self, gray: np.ndarray) -> Optional[List]:
        """
        Method 1: Adaptive thresholding (best for uneven lighting)
        """
        # Adaptive threshold with larger block size
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 21, 10
        )
        
        return self._find_corner_contours(binary, gray)
    
    def _detect_with_otsu_threshold(self, gray: np.ndarray) -> Optional[List]:
        """
        Method 2: OTSU thresholding (good for uniform lighting)
        """
        # OTSU threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        return self._find_corner_contours(binary, gray)
    
    def _detect_with_canny_edges(self, gray: np.ndarray) -> Optional[List]:
        """
        Method 3: Canny edge detection + contours
        """
        # Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dilate to connect edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return self._find_corner_contours(edges, gray)
    
    def _detect_with_template_matching(self, gray: np.ndarray) -> Optional[List]:
        """
        Method 4: Template matching (fallback)
        """
        # Create simple square template
        template_size = 30
        template = np.zeros((template_size, template_size), dtype=np.uint8)
        cv2.rectangle(template, (5, 5), (25, 25), 255, -1)
        
        # Match template
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        
        # Find peaks
        threshold = 0.3  # Lower threshold for photos
        locations = np.where(result >= threshold)
        
        if len(locations[0]) < 4:
            return None
        
        # Convert to corner points
        corners = []
        for y, x in zip(locations[0], locations[1]):
            corners.append((x + template_size // 2, y + template_size // 2))
        
        # Filter to 4 corners (one in each quadrant)
        return self._filter_to_four_corners(corners, gray.shape)
    
    def _find_corner_contours(self, binary: np.ndarray, gray: np.ndarray) -> Optional[List]:
        """
        Find corner markers using contour analysis
        """
        height, width = gray.shape
        
        # Morphological operations
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        logger.info(f"Found {len(contours)} contours")
        
        # Calculate expected marker size (more lenient)
        px_per_mm = min(width / 210, height / 297)
        expected_size = 15 * px_per_mm  # 15mm marker
        
        min_size = expected_size * 0.2  # Very lenient (20% of expected)
        max_size = expected_size * self.size_tolerance
        
        logger.info(f"Expected size: {expected_size:.1f}px, range: {min_size:.1f}-{max_size:.1f}px")
        
        # Define corner regions (larger search areas)
        search_margin = 0.15  # 15% of image size
        regions = [
            {'name': 'top-left', 'x_range': (0, width * search_margin), 'y_range': (0, height * search_margin)},
            {'name': 'top-right', 'x_range': (width * (1 - search_margin), width), 'y_range': (0, height * search_margin)},
            {'name': 'bottom-left', 'x_range': (0, width * search_margin), 'y_range': (height * (1 - search_margin), height)},
            {'name': 'bottom-right', 'x_range': (width * (1 - search_margin), width), 'y_range': (height * (1 - search_margin), height)}
        ]
        
        corners = []
        
        for region in regions:
            best_candidate = None
            best_score = 0
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cx, cy = x + w / 2, y + h / 2
                
                # Check if in region
                if not (region['x_range'][0] <= cx <= region['x_range'][1] and 
                        region['y_range'][0] <= cy <= region['y_range'][1]):
                    continue
                
                # Size check (very lenient)
                marker_size = min(w, h)
                if not (min_size <= marker_size <= max_size):
                    continue
                
                # Aspect ratio check (very lenient)
                if h > 0:
                    aspect_ratio = w / float(h)
                    if not (1/self.aspect_tolerance <= aspect_ratio <= self.aspect_tolerance):
                        continue
                
                # Darkness check (lenient)
                roi = gray[y:y+h, x:x+w]
                if roi.size == 0:
                    continue
                
                avg_intensity = np.mean(roi)
                darkness = (255 - avg_intensity) / 255.0
                
                if darkness < self.min_darkness:
                    continue
                
                # Calculate score
                size_score = 1.0 - abs(marker_size - expected_size) / expected_size
                darkness_score = darkness
                aspect_score = 1.0 - abs(aspect_ratio - 1.0)
                
                total_score = (size_score + darkness_score + aspect_score) / 3
                
                if total_score > best_score:
                    best_score = total_score
                    best_candidate = (cx, cy)
            
            if best_candidate:
                corners.append(best_candidate)
                logger.info(f"Found {region['name']}: {best_candidate} (score: {best_score:.3f})")
            else:
                logger.warning(f"No candidate found for {region['name']}")
        
        return corners if len(corners) == 4 else None
    
    def _filter_to_four_corners(self, points: List, image_shape: Tuple) -> Optional[List]:
        """
        Filter points to 4 corners (one in each quadrant)
        """
        height, width = image_shape
        
        # Divide into quadrants
        quadrants = {
            'top-left': [],
            'top-right': [],
            'bottom-left': [],
            'bottom-right': []
        }
        
        for x, y in points:
            if x < width / 2 and y < height / 2:
                quadrants['top-left'].append((x, y))
            elif x >= width / 2 and y < height / 2:
                quadrants['top-right'].append((x, y))
            elif x < width / 2 and y >= height / 2:
                quadrants['bottom-left'].append((x, y))
            else:
                quadrants['bottom-right'].append((x, y))
        
        # Select best point from each quadrant
        corners = []
        for quadrant_name, quadrant_points in quadrants.items():
            if not quadrant_points:
                return None
            
            # Select point closest to expected corner position
            if quadrant_name == 'top-left':
                best = min(quadrant_points, key=lambda p: p[0] + p[1])
            elif quadrant_name == 'top-right':
                best = min(quadrant_points, key=lambda p: (width - p[0]) + p[1])
            elif quadrant_name == 'bottom-left':
                best = min(quadrant_points, key=lambda p: p[0] + (height - p[1]))
            else:  # bottom-right
                best = min(quadrant_points, key=lambda p: (width - p[0]) + (height - p[1]))
            
            corners.append(best)
        
        return corners
    
    def _order_corners(self, corners: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Order corners as [top-left, top-right, bottom-left, bottom-right]
        """
        # Sort by y-coordinate first
        corners_sorted = sorted(corners, key=lambda p: p[1])
        
        # Top two points
        top_points = corners_sorted[:2]
        bottom_points = corners_sorted[2:]
        
        # Sort top points by x-coordinate
        top_left, top_right = sorted(top_points, key=lambda p: p[0])
        
        # Sort bottom points by x-coordinate
        bottom_left, bottom_right = sorted(bottom_points, key=lambda p: p[0])
        
        return [top_left, top_right, bottom_left, bottom_right]
    
    def visualize_detection(
        self,
        image: np.ndarray,
        corners: Optional[List[Tuple[float, float]]],
        output_path: str = 'photo_corner_detection.jpg'
    ):
        """
        Visualize corner detection results
        """
        vis = image.copy()
        if len(vis.shape) == 2:
            vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)
        
        if corners and len(corners) == 4:
            corner_names = ['TL', 'TR', 'BL', 'BR']
            colors = [(0, 255, 0), (0, 255, 255), (255, 0, 0), (255, 0, 255)]
            
            for i, (corner, name, color) in enumerate(zip(corners, corner_names, colors)):
                x, y = int(corner[0]), int(corner[1])
                
                # Draw circle
                cv2.circle(vis, (x, y), 20, color, 3)
                
                # Draw label
                cv2.putText(vis, name, (x + 25, y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        cv2.imwrite(output_path, vis)
        logger.info(f"Visualization saved: {output_path}")