"""
Improved Corner Detection Service
Fixes the corner detection issues seen in the test image
"""
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ImprovedCornerDetector:
    """
    Yaxshilangan corner detection - rasmdan ko'rilgan muammolarni hal qilish
    """
    
    def __init__(self):
        self.expected_corners = 4
        self.min_area = 150  # Minimum area for corner marker
        self.max_area = 3000  # Maximum area for corner marker
        self.aspect_ratio_tolerance = 0.4  # Square shape tolerance
        
    def detect_corners(self, image: np.ndarray) -> Optional[List[Dict]]:
        """
        Improved corner detection with multiple strategies
        
        Strategy 1: Template matching
        Strategy 2: Contour-based detection with improved filtering
        Strategy 3: Edge-based detection
        """
        logger.info("Starting improved corner detection...")
        
        # Try multiple strategies
        corners = None
        
        # Strategy 1: Template matching (most reliable)
        corners = self._detect_by_template_matching(image)
        if corners and len(corners) == 4:
            logger.info("✅ Template matching successful")
            return corners
        
        # Strategy 2: Improved contour detection
        corners = self._detect_by_improved_contours(image)
        if corners and len(corners) == 4:
            logger.info("✅ Improved contour detection successful")
            return corners
        
        # Strategy 3: Edge-based detection
        corners = self._detect_by_edges(image)
        if corners and len(corners) == 4:
            logger.info("✅ Edge-based detection successful")
            return corners
        
        logger.warning("❌ All corner detection strategies failed")
        return None
    
    def _detect_by_template_matching(self, image: np.ndarray) -> Optional[List[Dict]]:
        """
        Template matching approach - create ideal corner template
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Calculate expected corner size
            px_per_mm_x = width / 210
            px_per_mm_y = height / 297
            corner_size = int(15 * min(px_per_mm_x, px_per_mm_y))
            
            # Create ideal corner template (black square)
            template = np.zeros((corner_size, corner_size), dtype=np.uint8)
            
            # Match template
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            
            # Find peaks
            threshold = 0.6
            locations = np.where(result >= threshold)
            
            if len(locations[0]) < 4:
                return None
            
            # Convert to corner positions
            corners = []
            for y, x in zip(locations[0], locations[1]):
                center_x = x + corner_size // 2
                center_y = y + corner_size // 2
                corners.append({
                    'x': center_x,
                    'y': center_y,
                    'confidence': float(result[y, x])
                })
            
            # Select best 4 corners (one in each quadrant)
            return self._select_best_corners(corners, width, height)
            
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return None
    
    def _detect_by_improved_contours(self, image: np.ndarray) -> Optional[List[Dict]]:
        """
        Improved contour-based detection with better filtering
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Multiple thresholding approaches
            corners_all = []
            
            # Approach 1: Otsu thresholding
            _, binary1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            corners1 = self._find_corners_in_binary(binary1, width, height)
            if corners1:
                corners_all.extend(corners1)
            
            # Approach 2: Adaptive thresholding
            binary2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY_INV, 15, 10)
            corners2 = self._find_corners_in_binary(binary2, width, height)
            if corners2:
                corners_all.extend(corners2)
            
            # Approach 3: Fixed threshold
            _, binary3 = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
            corners3 = self._find_corners_in_binary(binary3, width, height)
            if corners3:
                corners_all.extend(corners3)
            
            if len(corners_all) < 4:
                return None
            
            # Select best 4 corners
            return self._select_best_corners(corners_all, width, height)
            
        except Exception as e:
            logger.error(f"Improved contour detection failed: {e}")
            return None
    
    def _find_corners_in_binary(self, binary: np.ndarray, width: int, height: int) -> List[Dict]:
        """
        Find corners in binary image using contours
        """
        # Morphological operations
        kernel = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        corners = []
        expected_size = min(width, height) * 0.02  # Expected corner size
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Size filtering
            if area < self.min_area or area > self.max_area:
                continue
            
            # Shape filtering
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            if abs(aspect_ratio - 1.0) > self.aspect_ratio_tolerance:
                continue
            
            # Position filtering (should be near corners)
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Check if near any corner
            margin = width * 0.15  # 15% margin from edges
            
            near_corner = (
                (center_x < margin and center_y < margin) or  # Top-left
                (center_x > width - margin and center_y < margin) or  # Top-right
                (center_x < margin and center_y > height - margin) or  # Bottom-left
                (center_x > width - margin and center_y > height - margin)  # Bottom-right
            )
            
            if not near_corner:
                continue
            
            # Calculate confidence based on shape quality
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # Square should have circularity around 0.785 (π/4)
            shape_score = 1.0 - abs(circularity - 0.785)
            size_score = 1.0 - abs(area - expected_size**2) / (expected_size**2)
            
            confidence = (shape_score + size_score) / 2
            
            corners.append({
                'x': center_x,
                'y': center_y,
                'confidence': confidence,
                'area': area
            })
        
        return corners
    
    def _detect_by_edges(self, image: np.ndarray) -> Optional[List[Dict]]:
        """
        Edge-based corner detection using Harris corner detector
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Harris corner detection
            corners_harris = cv2.cornerHarris(gray, 2, 3, 0.04)
            
            # Dilate corner image to enhance corner points
            corners_harris = cv2.dilate(corners_harris, None)
            
            # Threshold for an optimal value
            threshold = 0.01 * corners_harris.max()
            corner_points = np.where(corners_harris > threshold)
            
            if len(corner_points[0]) < 4:
                return None
            
            corners = []
            for y, x in zip(corner_points[0], corner_points[1]):
                # Filter by position (should be near image corners)
                margin = min(width, height) * 0.15
                
                near_corner = (
                    (x < margin and y < margin) or
                    (x > width - margin and y < margin) or
                    (x < margin and y > height - margin) or
                    (x > width - margin and y > height - margin)
                )
                
                if near_corner:
                    corners.append({
                        'x': int(x),
                        'y': int(y),
                        'confidence': float(corners_harris[y, x])
                    })
            
            if len(corners) < 4:
                return None
            
            return self._select_best_corners(corners, width, height)
            
        except Exception as e:
            logger.error(f"Edge-based detection failed: {e}")
            return None
    
    def _select_best_corners(self, corners: List[Dict], width: int, height: int) -> List[Dict]:
        """
        Select the best 4 corners (one in each quadrant)
        """
        if len(corners) < 4:
            return None
        
        # Define quadrants
        mid_x, mid_y = width // 2, height // 2
        
        quadrants = {
            'top_left': [],
            'top_right': [],
            'bottom_left': [],
            'bottom_right': []
        }
        
        # Assign corners to quadrants
        for corner in corners:
            x, y = corner['x'], corner['y']
            
            if x < mid_x and y < mid_y:
                quadrants['top_left'].append(corner)
            elif x >= mid_x and y < mid_y:
                quadrants['top_right'].append(corner)
            elif x < mid_x and y >= mid_y:
                quadrants['bottom_left'].append(corner)
            else:
                quadrants['bottom_right'].append(corner)
        
        # Select best corner from each quadrant
        selected_corners = []
        corner_names = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        
        for i, (quadrant_name, quadrant_corners) in enumerate(quadrants.items()):
            if not quadrant_corners:
                logger.warning(f"No corners found in {quadrant_name} quadrant")
                return None
            
            # Select corner with highest confidence
            best_corner = max(quadrant_corners, key=lambda c: c['confidence'])
            best_corner['name'] = corner_names[i]
            selected_corners.append(best_corner)
        
        logger.info(f"Selected 4 corners: {[c['name'] for c in selected_corners]}")
        return selected_corners
    
    def validate_corners(self, corners: List[Dict], width: int, height: int) -> bool:
        """
        Validate that corners form a reasonable rectangle
        """
        if len(corners) != 4:
            return False
        
        # Check that corners are reasonably spaced
        corner_dict = {c['name']: (c['x'], c['y']) for c in corners}
        
        # Calculate distances
        top_width = abs(corner_dict['top-right'][0] - corner_dict['top-left'][0])
        bottom_width = abs(corner_dict['bottom-right'][0] - corner_dict['bottom-left'][0])
        left_height = abs(corner_dict['bottom-left'][1] - corner_dict['top-left'][1])
        right_height = abs(corner_dict['bottom-right'][1] - corner_dict['top-right'][1])
        
        # Check aspect ratio (should be close to A4: 210/297 ≈ 0.707)
        avg_width = (top_width + bottom_width) / 2
        avg_height = (left_height + right_height) / 2
        
        if avg_height == 0:
            return False
        
        aspect_ratio = avg_width / avg_height
        expected_ratio = 210 / 297  # A4 ratio
        
        # Allow 20% tolerance
        if abs(aspect_ratio - expected_ratio) > expected_ratio * 0.2:
            logger.warning(f"Invalid aspect ratio: {aspect_ratio:.3f}, expected: {expected_ratio:.3f}")
            return False
        
        return True