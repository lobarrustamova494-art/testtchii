"""
Improved Photo Processor
Advanced photo processing with multiple fallback strategies
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ImprovedPhotoProcessor:
    """
    Yaxshilangan foto processor
    
    Features:
    - Advanced preprocessing
    - Multiple bubble detection strategies
    - Relative comparison algorithm
    - Quality assessment
    - Template matching fallback
    """
    
    def __init__(self):
        # Adaptive parameters
        self.min_darkness_relative = 2.0  # Minimum difference from mean
        self.confidence_threshold = 60.0
        self.multiple_marks_threshold = 3.0
        
    def preprocess_photo(self, image: np.ndarray) -> np.ndarray:
        """
        Advanced photo preprocessing
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            np.ndarray: Preprocessed grayscale image
        """
        logger.info("Starting advanced photo preprocessing...")
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 1. Noise reduction
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # 2. Contrast enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 3. Sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # 4. Normalization
        normalized = cv2.normalize(sharpened, None, 0, 255, cv2.NORM_MINMAX)
        
        logger.info("✅ Photo preprocessing complete")
        return normalized
    
    def detect_bubbles_advanced(
        self,
        image: np.ndarray,
        expected_count: int = 200
    ) -> List[Dict]:
        """
        Advanced bubble detection with multiple strategies
        
        Args:
            image: Preprocessed grayscale image
            expected_count: Expected number of bubbles
            
        Returns:
            list: Detected bubbles with metadata
        """
        logger.info("Starting advanced bubble detection...")
        
        # Strategy 1: Hough Circle Transform (multiple parameter sets)
        bubbles = self._detect_with_hough_circles(image, expected_count)
        
        if len(bubbles) >= expected_count * 0.7:  # 70% success
            logger.info(f"✅ Hough circles successful: {len(bubbles)} bubbles")
            return bubbles
        
        # Strategy 2: Contour-based detection
        logger.info("Trying contour-based detection...")
        bubbles = self._detect_with_contours(image, expected_count)
        
        if len(bubbles) >= expected_count * 0.6:  # 60% success
            logger.info(f"✅ Contour detection successful: {len(bubbles)} bubbles")
            return bubbles
        
        # Strategy 3: Template matching
        logger.info("Trying template matching...")
        bubbles = self._detect_with_template_matching(image, expected_count)
        
        logger.info(f"Template matching result: {len(bubbles)} bubbles")
        return bubbles
    
    def _detect_with_hough_circles(
        self,
        image: np.ndarray,
        expected_count: int
    ) -> List[Dict]:
        """
        Hough Circle Transform with multiple parameter sets
        """
        # Enhanced preprocessing for circle detection
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Multiple parameter sets (more comprehensive)
        param_sets = [
            {'minRadius': 8, 'maxRadius': 25, 'param2': 25, 'minDist': 20},
            {'minRadius': 10, 'maxRadius': 30, 'param2': 20, 'minDist': 25},
            {'minRadius': 6, 'maxRadius': 20, 'param2': 30, 'minDist': 15},
            {'minRadius': 12, 'maxRadius': 35, 'param2': 15, 'minDist': 30},
            {'minRadius': 5, 'maxRadius': 18, 'param2': 35, 'minDist': 12},
            {'minRadius': 15, 'maxRadius': 40, 'param2': 12, 'minDist': 35},
        ]
        
        best_circles = None
        best_count_diff = float('inf')
        
        for params in param_sets:
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=params['minDist'],
                param1=50,
                param2=params['param2'],
                minRadius=params['minRadius'],
                maxRadius=params['maxRadius']
            )
            
            if circles is not None:
                count = len(circles[0])
                count_diff = abs(count - expected_count)
                
                logger.info(f"  Params {params}: Found {count} circles (diff: {count_diff})")
                
                if count_diff < best_count_diff:
                    best_count_diff = count_diff
                    best_circles = circles
        
        if best_circles is None:
            return []
        
        circles = np.round(best_circles[0, :]).astype("int")
        
        # Convert to dict format with quality assessment
        bubbles = []
        for x, y, r in circles:
            # Assess bubble quality
            quality = self._assess_bubble_quality(image, x, y, r)
            
            bubbles.append({
                'x': float(x),
                'y': float(y),
                'radius': float(r),
                'quality': quality,
                'method': 'hough_circles'
            })
        
        return bubbles
    
    def _detect_with_contours(
        self,
        image: np.ndarray,
        expected_count: int
    ) -> List[Dict]:
        """
        Contour-based bubble detection
        """
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours
        bubbles = []
        height, width = image.shape
        
        # Expected bubble size
        px_per_mm = min(width / 210, height / 297)
        expected_radius = 2.5 * px_per_mm  # 2.5mm radius
        
        min_radius = expected_radius * 0.3
        max_radius = expected_radius * 3.0
        
        for contour in contours:
            # Get bounding circle
            (x, y), radius = cv2.minEnclosingCircle(contour)
            
            # Size filter
            if not (min_radius <= radius <= max_radius):
                continue
            
            # Circularity check
            area = cv2.contourArea(contour)
            if area < 10:  # Too small
                continue
            
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.3:  # Not circular enough
                continue
            
            # Quality assessment
            quality = self._assess_bubble_quality(image, int(x), int(y), int(radius))
            
            bubbles.append({
                'x': float(x),
                'y': float(y),
                'radius': float(radius),
                'quality': quality,
                'circularity': circularity,
                'method': 'contours'
            })
        
        # Sort by quality and take best candidates
        bubbles.sort(key=lambda b: b['quality'], reverse=True)
        return bubbles[:expected_count * 2]  # Take up to 2x expected
    
    def _detect_with_template_matching(
        self,
        image: np.ndarray,
        expected_count: int
    ) -> List[Dict]:
        """
        Template matching for bubble detection
        """
        bubbles = []
        
        # Create multiple templates
        template_sizes = [15, 20, 25, 30]
        
        for size in template_sizes:
            # Create filled circle template
            template = np.zeros((size * 2, size * 2), dtype=np.uint8)
            cv2.circle(template, (size, size), size - 2, 255, -1)
            
            # Match template
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            
            # Find matches
            threshold = 0.4  # Moderate threshold
            locations = np.where(result >= threshold)
            
            for y, x in zip(locations[0], locations[1]):
                center_x = x + size
                center_y = y + size
                
                # Quality assessment
                quality = self._assess_bubble_quality(image, center_x, center_y, size)
                
                bubbles.append({
                    'x': float(center_x),
                    'y': float(center_y),
                    'radius': float(size),
                    'quality': quality,
                    'template_size': size,
                    'method': 'template_matching'
                })
        
        # Remove duplicates (nearby bubbles)
        bubbles = self._remove_duplicate_bubbles(bubbles, min_distance=15)
        
        # Sort by quality
        bubbles.sort(key=lambda b: b['quality'], reverse=True)
        return bubbles[:expected_count]
    
    def _assess_bubble_quality(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        radius: int
    ) -> float:
        """
        Assess bubble quality (0-100)
        """
        # ROI extraction
        roi_radius = int(radius * 1.2)
        x1 = max(0, x - roi_radius)
        y1 = max(0, y - roi_radius)
        x2 = min(image.shape[1], x + roi_radius)
        y2 = min(image.shape[0], y + roi_radius)
        
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return 0
        
        # Create mask
        center_x = x - x1
        center_y = y - y1
        
        mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        
        pixels = roi[mask > 0]
        
        if len(pixels) == 0:
            return 0
        
        # Calculate metrics
        mean_intensity = np.mean(pixels)
        std_intensity = np.std(pixels)
        
        # Quality score
        darkness = (255 - mean_intensity) / 255 * 100
        uniformity = max(0, 100 - std_intensity)
        
        quality = (darkness + uniformity) / 2
        return min(100, max(0, quality))
    
    def _remove_duplicate_bubbles(
        self,
        bubbles: List[Dict],
        min_distance: float = 20
    ) -> List[Dict]:
        """
        Remove duplicate bubbles that are too close
        """
        if not bubbles:
            return bubbles
        
        # Sort by quality (best first)
        bubbles.sort(key=lambda b: b['quality'], reverse=True)
        
        filtered = []
        
        for bubble in bubbles:
            is_duplicate = False
            
            for existing in filtered:
                distance = np.sqrt(
                    (bubble['x'] - existing['x']) ** 2 +
                    (bubble['y'] - existing['y']) ** 2
                )
                
                if distance < min_distance:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(bubble)
        
        return filtered
    
    def analyze_bubble_relative(
        self,
        image: np.ndarray,
        bubble: Dict
    ) -> Dict:
        """
        Analyze bubble using relative comparison
        """
        x, y = int(bubble['x']), int(bubble['y'])
        radius = int(bubble['radius'])
        
        # ROI extraction
        roi_radius = int(radius * 1.5)
        x1 = max(0, x - roi_radius)
        y1 = max(0, y - roi_radius)
        x2 = min(image.shape[1], x + roi_radius)
        y2 = min(image.shape[0], y + roi_radius)
        
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return {'darkness': 0, 'score': 0, 'filled': False}
        
        # Create masks
        center_x = x - x1
        center_y = y - y1
        
        # Inner circle (bubble area)
        inner_mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(inner_mask, (center_x, center_y), radius, 255, -1)
        
        # Outer ring (background area)
        outer_mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(outer_mask, (center_x, center_y), int(radius * 1.4), 255, -1)
        cv2.circle(outer_mask, (center_x, center_y), int(radius * 1.1), 0, -1)
        
        # Extract pixels
        inner_pixels = roi[inner_mask > 0]
        outer_pixels = roi[outer_mask > 0]
        
        if len(inner_pixels) == 0 or len(outer_pixels) == 0:
            return {'darkness': 0, 'score': 0, 'filled': False}
        
        # Calculate relative darkness
        inner_mean = np.mean(inner_pixels)
        outer_mean = np.mean(outer_pixels)
        
        # Relative comparison
        relative_darkness = outer_mean - inner_mean  # Higher = darker bubble
        darkness_percentage = (255 - inner_mean) / 255 * 100
        
        # Adaptive threshold based on image quality
        adaptive_threshold = max(10, outer_mean * 0.15)
        
        # Decision
        is_filled = relative_darkness > adaptive_threshold
        
        # Score calculation
        score = relative_darkness + darkness_percentage * 0.5
        
        return {
            'darkness': round(darkness_percentage, 2),
            'relative_darkness': round(relative_darkness, 2),
            'score': round(score, 2),
            'filled': is_filled,
            'inner_mean': round(inner_mean, 2),
            'outer_mean': round(outer_mean, 2),
            'threshold': round(adaptive_threshold, 2)
        }
    
    def make_decision_relative(
        self,
        analyses: List[Dict],
        question_number: int
    ) -> Dict:
        """
        Make decision using relative comparison
        """
        if not analyses:
            return {
                'answer': None,
                'confidence': 0,
                'warning': 'NO_ANALYSIS',
                'method': 'relative'
            }
        
        # Sort by score
        sorted_analyses = sorted(analyses, key=lambda x: x['score'], reverse=True)
        
        first = sorted_analyses[0]
        second = sorted_analyses[1] if len(sorted_analyses) > 1 else None
        
        # Calculate mean score
        mean_score = np.mean([a['score'] for a in analyses])
        
        # Decision logic
        decision = {
            'answer': None,
            'confidence': 0,
            'warning': None,
            'method': 'relative',
            'debug': {
                'mean_score': round(mean_score, 2),
                'first_score': round(first['score'], 2),
                'second_score': round(second['score'], 2) if second else 0
            }
        }
        
        # Check if first is significantly above mean
        if first['score'] > mean_score + self.min_darkness_relative:
            decision['answer'] = first['variant']
            
            # Check for multiple marks
            if second and second['score'] > mean_score + (self.min_darkness_relative * 0.7):
                difference = first['score'] - second['score']
                if difference < self.multiple_marks_threshold:
                    decision['warning'] = 'MULTIPLE_MARKS'
                    decision['answer'] = None
                    return decision
            
            # Calculate confidence
            confidence = 50 + (first['score'] - mean_score) * 2
            if second:
                confidence += (first['score'] - second['score']) * 1.5
            
            decision['confidence'] = min(100, round(confidence))
            
            if decision['confidence'] < self.confidence_threshold:
                decision['warning'] = 'LOW_CONFIDENCE'
            
        else:
            # No clear mark
            decision['warning'] = 'NO_MARK'
        
        return decision
    
    def process_photo_complete(
        self,
        image_path: str,
        exam_structure: Dict,
        answer_key: Dict
    ) -> Dict:
        """
        Complete photo processing pipeline
        """
        logger.info(f"Processing photo with improved processor: {image_path}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        # Preprocess
        processed = self.preprocess_photo(image)
        
        # Calculate total questions
        total_questions = sum(
            section['questionCount']
            for subject in exam_structure['subjects']
            for section in subject['sections']
        )
        
        # Detect bubbles
        bubbles = self.detect_bubbles_advanced(processed, total_questions * 5)
        
        # Map to questions (reuse existing logic)
        from services.photo_omr_service import PhotoOMRService
        photo_service = PhotoOMRService()
        coordinates = photo_service.map_bubbles_to_questions(
            bubbles, total_questions
        )
        
        # Analyze answers with improved algorithm
        results = self._analyze_answers_improved(processed, coordinates, exam_structure)
        
        # Grade
        from services.grader import AnswerGrader
        grader = AnswerGrader(answer_key, exam_structure)
        grading_results = grader.grade(results['answers'])
        
        return {
            'omr_results': results,
            'grading_results': grading_results,
            'coordinates': coordinates,
            'bubbles_found': len(bubbles),
            'questions_mapped': len(coordinates),
            'detection_method': 'improved_photo_processor'
        }
    
    def _analyze_answers_improved(
        self,
        image: np.ndarray,
        coordinates: Dict,
        exam_structure: Dict
    ) -> Dict:
        """
        Analyze answers with improved algorithm
        """
        logger.info("Starting improved answer analysis...")
        
        results = {}
        stats = {
            'total': 0,
            'detected': 0,
            'uncertain': 0,
            'no_mark': 0,
            'multiple_marks': 0
        }
        
        for topic in exam_structure['subjects']:
            results[topic['id']] = {}
            
            for section in topic['sections']:
                section_results = []
                
                for i in range(section['questionCount']):
                    q_num = i + 1
                    coords = coordinates.get(q_num)
                    
                    stats['total'] += 1
                    
                    if not coords:
                        result = {
                            'questionNumber': q_num,
                            'answer': None,
                            'confidence': 0,
                            'warning': 'NO_COORDINATES',
                            'allScores': [],
                            'debugScores': 'No coordinates found'
                        }
                        stats['no_mark'] += 1
                    else:
                        # Analyze with improved algorithm
                        analyses = []
                        for bubble in coords['bubbles']:
                            analysis = self.analyze_bubble_relative(image, bubble)
                            analyses.append({
                                'variant': bubble['variant'],
                                **analysis
                            })
                        
                        # Make decision
                        decision = self.make_decision_relative(analyses, q_num)
                        
                        result = {
                            'questionNumber': q_num,
                            'answer': decision['answer'],
                            'confidence': decision['confidence'],
                            'warning': decision['warning'],
                            'allScores': analyses,
                            'debugScores': ' '.join([f"{a['variant']}:{a['score']:.1f}" for a in analyses]),
                            'method': decision['method']
                        }
                        
                        # Update statistics
                        if result['answer']:
                            stats['detected'] += 1
                        else:
                            stats['no_mark'] += 1
                        
                        if result['confidence'] < 70:
                            stats['uncertain'] += 1
                        
                        if result['warning'] == 'MULTIPLE_MARKS':
                            stats['multiple_marks'] += 1
                    
                    section_results.append(result)
                
                results[topic['id']][section['id']] = section_results
        
        logger.info(f"Improved analysis complete: {stats['detected']}/{stats['total']} detected")
        
        return {
            'answers': results,
            'statistics': stats
        }