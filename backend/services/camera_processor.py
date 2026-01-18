"""
Professional Camera-based OMR Processing Service
Based on camera_system.md specifications

Features:
- Document scanner-like processing pipeline
- Automatic perspective correction
- Paper detection and validation
- Corner marker detection within cropped paper
- Template-based coordinate mapping
- Professional bubble analysis
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class CameraProcessor:
    """
    Professional camera-based OMR processor
    Implements the complete pipeline from camera_system.md
    """
    
    def __init__(self):
        self.target_width = 2480  # Standard A4 width at 300 DPI
        self.target_height = 3508  # Standard A4 height at 300 DPI
        
    def process_camera_image(
        self,
        image: np.ndarray,
        exam_structure: Dict
    ) -> Dict:
        """
        Complete camera processing pipeline
        
        Args:
            image: Raw camera image (BGR format)
            exam_structure: Exam structure for coordinate mapping
            
        Returns:
            dict: Processing results with cropped paper, corners, and coordinates
        """
        logger.info("🎯 Starting camera-based OMR processing pipeline...")
        
        results = {
            'success': False,
            'cropped_paper': None,
            'corners_found': 0,
            'corner_coordinates': None,
            'paper_coordinates': None,
            'quality_score': 0,
            'error_message': None
        }
        
        try:
            # Step 1: Detect paper in camera frame
            logger.info("📄 Step 1: Detecting paper in camera frame...")
            paper_detection = self._detect_paper_in_frame(image)
            
            if not paper_detection['found']:
                results['error_message'] = 'Qog\'oz kadrda topilmadi'
                return results
            
            # Step 2: Crop and perspective correct the paper
            logger.info("✂️ Step 2: Cropping and correcting perspective...")
            cropped_paper = self._crop_and_correct_paper(
                image, 
                paper_detection['corners']
            )
            
            if cropped_paper is None:
                results['error_message'] = 'Perspektiva tuzatishda xatolik'
                return results
            
            results['cropped_paper'] = cropped_paper
            
            # Step 3: Detect corner markers within cropped paper
            logger.info("🎯 Step 3: Detecting corner markers in cropped paper...")
            corner_detection = self._detect_corner_markers_in_paper(cropped_paper)
            
            results['corners_found'] = len(corner_detection['corners'])
            results['corner_coordinates'] = corner_detection['corners']
            
            if len(corner_detection['corners']) < 4:
                results['error_message'] = f'Faqat {len(corner_detection["corners"])}/4 corner marker topildi'
                return results
            
            # Step 4: Calculate paper coordinates using template matching
            logger.info("📐 Step 4: Calculating coordinates using template matching...")
            coordinate_mapping = self._calculate_template_coordinates(
                corner_detection['corners'],
                exam_structure
            )
            
            results['paper_coordinates'] = coordinate_mapping['coordinates']
            results['quality_score'] = self._assess_paper_quality(cropped_paper)
            results['success'] = True
            
            logger.info("✅ Camera processing pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Camera processing error: {e}")
            results['error_message'] = f'Qayta ishlashda xatolik: {str(e)}'
        
        return results
    
    def _detect_paper_in_frame(self, image: np.ndarray) -> Dict:
        """
        Detect paper document in camera frame
        
        Returns:
            dict: {
                'found': bool,
                'corners': List[Tuple[int, int]],
                'aspect_ratio': float,
                'confidence': float
            }
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        
        # Morphological operations to close gaps
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the largest rectangular contour (paper)
        paper_contour = None
        max_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 10000:  # Minimum area threshold
                continue
            
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's roughly rectangular (4 corners)
            if len(approx) == 4 and area > max_area:
                max_area = area
                paper_contour = approx
        
        if paper_contour is None:
            return {
                'found': False,
                'corners': [],
                'aspect_ratio': 0,
                'confidence': 0
            }
        
        # Extract corner points
        corners = [tuple(point[0]) for point in paper_contour]
        
        # Calculate aspect ratio
        width = np.linalg.norm(np.array(corners[1]) - np.array(corners[0]))
        height = np.linalg.norm(np.array(corners[3]) - np.array(corners[0]))
        aspect_ratio = min(width, height) / max(width, height)
        
        # A4 aspect ratio is approximately 0.707 (210/297)
        a4_similarity = 1 - abs(aspect_ratio - 0.707)
        confidence = min(a4_similarity * 100, 100)
        
        return {
            'found': True,
            'corners': corners,
            'aspect_ratio': aspect_ratio,
            'confidence': confidence
        }
    
    def _crop_and_correct_paper(
        self, 
        image: np.ndarray, 
        corners: List[Tuple[int, int]]
    ) -> Optional[np.ndarray]:
        """
        Crop paper from image and apply perspective correction
        
        Args:
            image: Original camera image
            corners: Four corner points of the paper
            
        Returns:
            np.ndarray: Cropped and corrected paper image (A4 size)
        """
        if len(corners) != 4:
            return None
        
        # Sort corners: top-left, top-right, bottom-right, bottom-left
        corners = np.array(corners, dtype=np.float32)
        
        # Calculate center point
        center = np.mean(corners, axis=0)
        
        # Sort by angle from center
        def angle_from_center(point):
            return np.arctan2(point[1] - center[1], point[0] - center[0])
        
        corners = sorted(corners, key=angle_from_center)
        
        # Reorder to standard format
        # Find top-left (smallest x+y)
        sums = [pt[0] + pt[1] for pt in corners]
        top_left_idx = np.argmin(sums)
        
        # Reorder starting from top-left, going clockwise
        ordered_corners = []
        for i in range(4):
            ordered_corners.append(corners[(top_left_idx + i) % 4])
        
        src_points = np.array(ordered_corners, dtype=np.float32)
        
        # Destination points (A4 rectangle)
        dst_points = np.array([
            [0, 0],                                    # top-left
            [self.target_width, 0],                    # top-right
            [self.target_width, self.target_height],   # bottom-right
            [0, self.target_height]                    # bottom-left
        ], dtype=np.float32)
        
        # Calculate perspective transformation matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # Apply perspective correction
        corrected = cv2.warpPerspective(
            image, 
            matrix, 
            (self.target_width, self.target_height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)
        )
        
        return corrected
    
    def _detect_corner_markers_in_paper(self, paper_image: np.ndarray) -> Dict:
        """
        Detect corner markers within the cropped paper
        Only searches within the paper boundaries (no external background)
        
        Args:
            paper_image: Cropped and corrected paper image
            
        Returns:
            dict: {
                'corners': List[Dict],
                'marker_distance': float
            }
        """
        gray = cv2.cvtColor(paper_image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Calculate expected marker positions (5mm margin, 15mm size)
        px_per_mm_x = width / 210   # A4 width in mm
        px_per_mm_y = height / 297  # A4 height in mm
        
        margin_px = 5 * min(px_per_mm_x, px_per_mm_y)
        marker_size_px = 15 * min(px_per_mm_x, px_per_mm_y)
        
        expected_positions = [
            {
                'name': 'top-left',
                'x': margin_px + marker_size_px / 2,
                'y': margin_px + marker_size_px / 2,
                'search_region': (0, 0, int(margin_px + marker_size_px * 2), int(margin_px + marker_size_px * 2))
            },
            {
                'name': 'top-right', 
                'x': width - margin_px - marker_size_px / 2,
                'y': margin_px + marker_size_px / 2,
                'search_region': (int(width - margin_px - marker_size_px * 2), 0, width, int(margin_px + marker_size_px * 2))
            },
            {
                'name': 'bottom-left',
                'x': margin_px + marker_size_px / 2,
                'y': height - margin_px - marker_size_px / 2,
                'search_region': (0, int(height - margin_px - marker_size_px * 2), int(margin_px + marker_size_px * 2), height)
            },
            {
                'name': 'bottom-right',
                'x': width - margin_px - marker_size_px / 2,
                'y': height - margin_px - marker_size_px / 2,
                'search_region': (int(width - margin_px - marker_size_px * 2), int(height - margin_px - marker_size_px * 2), width, height)
            }
        ]
        
        detected_corners = []
        
        # Binary threshold for marker detection
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        for expected in expected_positions:
            x1, y1, x2, y2 = expected['search_region']
            search_roi = binary[y1:y2, x1:x2]
            
            if search_roi.size == 0:
                continue
            
            # Find contours in search region
            contours, _ = cv2.findContours(search_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best_marker = None
            best_score = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < marker_size_px * marker_size_px * 0.3:  # Minimum area
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio (should be roughly square)
                aspect_ratio = w / float(h) if h > 0 else 0
                if not (0.7 < aspect_ratio < 1.4):
                    continue
                
                # Calculate center in global coordinates
                center_x = x1 + x + w / 2
                center_y = y1 + y + h / 2
                
                # Distance from expected position
                dist = np.sqrt((center_x - expected['x'])**2 + (center_y - expected['y'])**2)
                
                # Score based on size, aspect ratio, and position
                size_score = min(area / (marker_size_px * marker_size_px), 1)
                aspect_score = 1 - abs(1 - aspect_ratio)
                position_score = max(0, 1 - dist / marker_size_px)
                
                score = (size_score + aspect_score + position_score) / 3
                
                if score > best_score and score > 0.5:
                    best_score = score
                    best_marker = {
                        'name': expected['name'],
                        'x': center_x,
                        'y': center_y,
                        'score': score
                    }
            
            if best_marker:
                detected_corners.append(best_marker)
        
        # Calculate marker distance if we have at least 2 corners
        marker_distance = 0
        if len(detected_corners) >= 2:
            # Use top corners for distance calculation
            top_corners = [c for c in detected_corners if 'top' in c['name']]
            if len(top_corners) >= 2:
                c1, c2 = top_corners[0], top_corners[1]
                marker_distance = np.sqrt((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2)
        
        return {
            'corners': detected_corners,
            'marker_distance': marker_distance
        }
    
    def _calculate_template_coordinates(
        self,
        detected_corners: List[Dict],
        exam_structure: Dict
    ) -> Dict:
        """
        Calculate question and bubble coordinates using template matching
        
        Args:
            detected_corners: Detected corner markers with positions
            exam_structure: Exam structure for coordinate generation
            
        Returns:
            dict: Generated coordinates for all questions
        """
        if len(detected_corners) < 4:
            return {'coordinates': {}}
        
        # Calculate scaling factor from template to actual paper
        # Template assumes standard A4 with 5mm margins and 15mm markers
        template_marker_distance = (210 - 2 * 5 - 15) * (self.target_width / 210)  # Distance between marker centers
        
        # Find actual marker distance
        top_corners = [c for c in detected_corners if 'top' in c['name']]
        if len(top_corners) < 2:
            return {'coordinates': {}}
        
        actual_marker_distance = np.sqrt(
            (top_corners[0]['x'] - top_corners[1]['x'])**2 + 
            (top_corners[0]['y'] - top_corners[1]['y'])**2
        )
        
        scale_factor = actual_marker_distance / template_marker_distance
        
        # Generate coordinates using the coordinate mapper
        from utils.coordinate_mapper import CoordinateMapper
        
        mapper = CoordinateMapper(
            self.target_width,
            self.target_height,
            exam_structure
        )
        
        # Generate base coordinates
        base_coordinates = mapper.calculate_all()
        
        # Scale coordinates based on detected markers
        scaled_coordinates = {}
        
        for q_num, coords in base_coordinates.items():
            scaled_coords = {
                'questionNumber': coords['questionNumber'],
                'bubbles': []
            }
            
            for bubble in coords['bubbles']:
                scaled_bubble = {
                    'variant': bubble['variant'],
                    'x': bubble['x'] * scale_factor,
                    'y': bubble['y'] * scale_factor,
                    'radius': bubble['radius'] * scale_factor
                }
                scaled_coords['bubbles'].append(scaled_bubble)
            
            scaled_coordinates[q_num] = scaled_coords
        
        return {'coordinates': scaled_coordinates}
    
    def _assess_paper_quality(self, paper_image: np.ndarray) -> float:
        """
        Assess the quality of the cropped paper image
        
        Args:
            paper_image: Cropped paper image
            
        Returns:
            float: Quality score (0-100)
        """
        gray = cv2.cvtColor(paper_image, cv2.COLOR_BGR2GRAY)
        
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 500, 1) * 100
        
        # Contrast
        contrast = gray.std()
        contrast_score = min(contrast / 50, 1) * 100
        
        # Brightness (should be well-lit)
        brightness = gray.mean()
        brightness_score = 100 - abs(brightness - 200) / 2  # Optimal around 200
        
        # Overall quality
        quality = (sharpness_score + contrast_score + brightness_score) / 3
        
        return max(0, min(100, quality))