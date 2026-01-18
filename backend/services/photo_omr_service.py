"""
Photo OMR Service - Specialized for photos (not PDF-generated sheets)
Uses template matching and adaptive detection
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PhotoOMRService:
    """
    Foto'lar uchun maxsus OMR service
    
    Features:
    - Automatic bubble detection (Hough Circle Transform)
    - Adaptive coordinate mapping
    - Lenient thresholds for photo quality
    - Template matching support
    """
    
    def __init__(self):
        # Photo-specific parameters (ULTRA-SENSITIVE for photos)
        self.min_darkness = 8.0  # ULTRA-LOW for photos (was 20.0)
        self.min_difference = 3.0  # ULTRA-LOW for photos (was 5.0)
        self.multiple_marks_threshold = 3.0  # ULTRA-LOW for photos (was 5.0)
        self.use_relative_detection = True  # Use relative comparison
        self.relative_threshold = 1.5  # LOWERED minimum difference from mean (was 2.0)
        self.use_ocr_anchors = True  # Try OCR anchors first
        
    def detect_bubbles_automatically(
        self,
        image: np.ndarray,
        expected_count: int = 200
    ) -> List[Dict]:
        """
        Automatically detect all bubbles in image using Hough Circle Transform
        
        Args:
            image: Grayscale image
            expected_count: Expected number of bubbles (40 questions x 5 variants = 200)
            
        Returns:
            list: [{'x': px, 'y': px, 'radius': px}, ...]
        """
        logger.info(f"Detecting bubbles automatically (expected: {expected_count})...")
        
        # Enhanced preprocessing for photos
        # 1. Contrast enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(image)
        
        # 2. Gaussian blur
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)  # Smaller kernel
        
        # Try multiple parameter sets to find bubbles
        param_sets = [
            {'minRadius': 8, 'maxRadius': 25, 'param2': 25},  # Original parameters
            {'minRadius': 10, 'maxRadius': 30, 'param2': 20},
            {'minRadius': 6, 'maxRadius': 20, 'param2': 30},
            {'minRadius': 12, 'maxRadius': 35, 'param2': 15},
        ]
        
        best_circles = None
        best_count_diff = float('inf')
        
        for params in param_sets:
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=25,
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
            logger.warning("No circles found with any parameter set!")
            return []
        
        circles = np.round(best_circles[0, :]).astype("int")
        logger.info(f"✅ Found {len(circles)} bubbles")
        
        # Convert to dict format
        bubbles = []
        for x, y, r in circles:
            bubbles.append({
                'x': float(x),
                'y': float(y),
                'radius': float(r)
            })
        
        return bubbles
    
    def map_bubbles_to_questions(
        self,
        bubbles: List[Dict],
        total_questions: int = 40,
        variants_per_question: int = 5
    ) -> Dict[int, Dict]:
        """
        Map detected bubbles to questions
        
        Assumes:
        - 2 questions per row
        - 5 variants per question (A, B, C, D, E)
        - Bubbles are arranged in grid pattern
        
        Args:
            bubbles: List of detected bubbles
            total_questions: Total number of questions
            variants_per_question: Number of variants per question
            
        Returns:
            dict: {questionNumber: {'questionNumber': int, 'bubbles': [...]}}
        """
        logger.info(f"Mapping {len(bubbles)} bubbles to {total_questions} questions...")
        
        # Sort bubbles by Y (top to bottom), then X (left to right)
        bubbles_sorted = sorted(bubbles, key=lambda b: (b['y'], b['x']))
        
        # Group into rows
        rows = []
        current_row = []
        last_y = -100
        
        for bubble in bubbles_sorted:
            if abs(bubble['y'] - last_y) < 30:  # Same row (30px tolerance)
                current_row.append(bubble)
            else:
                if current_row:
                    rows.append(current_row)
                current_row = [bubble]
            last_y = bubble['y']
        
        if current_row:
            rows.append(current_row)
        
        logger.info(f"Grouped into {len(rows)} rows")
        
        # Map to questions
        coordinates = {}
        question_num = 1
        
        for row_idx, row in enumerate(rows):
            # Sort by X
            row_sorted = sorted(row, key=lambda b: b['x'])
            
            # Skip rows with too few bubbles
            if len(row_sorted) < 8:
                logger.debug(f"Row {row_idx + 1}: Only {len(row_sorted)} bubbles (skipping)")
                continue
            
            # Split into 2 groups (2 questions per row)
            mid_x = (row_sorted[0]['x'] + row_sorted[-1]['x']) / 2
            left_group = [b for b in row_sorted if b['x'] < mid_x]
            right_group = [b for b in row_sorted if b['x'] >= mid_x]
            
            # Process left question
            if len(left_group) >= variants_per_question and question_num <= total_questions:
                bubbles_list = []
                for i in range(variants_per_question):
                    if i < len(left_group):
                        bubble = left_group[i]
                        bubbles_list.append({
                            'variant': ['A', 'B', 'C', 'D', 'E'][i],
                            'x': bubble['x'],
                            'y': bubble['y'],
                            'radius': bubble['radius']
                        })
                
                if len(bubbles_list) == variants_per_question:
                    coordinates[question_num] = {
                        'questionNumber': question_num,
                        'bubbles': bubbles_list
                    }
                    question_num += 1
            
            # Process right question
            if len(right_group) >= variants_per_question and question_num <= total_questions:
                bubbles_list = []
                for i in range(variants_per_question):
                    if i < len(right_group):
                        bubble = right_group[i]
                        bubbles_list.append({
                            'variant': ['A', 'B', 'C', 'D', 'E'][i],
                            'x': bubble['x'],
                            'y': bubble['y'],
                            'radius': bubble['radius']
                        })
                
                if len(bubbles_list) == variants_per_question:
                    coordinates[question_num] = {
                        'questionNumber': question_num,
                        'bubbles': bubbles_list
                    }
                    question_num += 1
        
        logger.info(f"✅ Mapped {len(coordinates)} questions")
        
        return coordinates
    
    def detect_answers(
        self,
        image: np.ndarray,
        coordinates: Dict,
        exam_structure: Dict
    ) -> Dict:
        """
        Detect answers using photo-optimized algorithm
        
        Args:
            image: Grayscale image
            coordinates: Question coordinates
            exam_structure: Exam structure
            
        Returns:
            dict: OMR results
        """
        logger.info("Starting Photo OMR detection...")
        
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
                
                # Process all questions in the section
                for i in range(section['questionCount']):
                    q_num = i + 1  # Question numbers start from 1
                    coords = coordinates.get(q_num)
                    
                    stats['total'] += 1
                    
                    if not coords:
                        # Create a dummy result for unmapped questions
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
                        # Detect single question
                        result = self._detect_single_question(image, coords)
                        
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
        
        logger.info(
            f"Photo OMR complete: {stats['detected']}/{stats['total']} detected"
        )
        
        return {
            'answers': results,
            'statistics': stats
        }
    
    def _detect_single_question(
        self,
        image: np.ndarray,
        coords: Dict
    ) -> Dict:
        """
        Detect single question with photo-optimized algorithm
        """
        bubbles = coords['bubbles']
        analyses = []
        
        for bubble in bubbles:
            analysis = self._analyze_bubble(image, bubble)
            analyses.append({
                'variant': bubble['variant'],
                **analysis
            })
        
        # Make decision
        decision = self._make_decision(analyses)
        
        return {
            'questionNumber': coords['questionNumber'],
            'answer': decision['answer'],
            'confidence': decision['confidence'],
            'warning': decision['warning'],
            'allScores': analyses,
            'debugScores': ' '.join([f"{a['variant']}:{a['score']:.1f}" for a in analyses])
        }
    
    def _analyze_bubble(
        self,
        image: np.ndarray,
        bubble: Dict
    ) -> Dict:
        """
        Analyze single bubble (photo-optimized with ULTRA-SENSITIVITY)
        """
        x, y = int(bubble['x']), int(bubble['y'])
        radius = int(bubble['radius'])
        
        # ROI extraction (larger for photos)
        roi_radius = int(radius * 1.3)  # Increased from 1.2 to 1.3
        x1 = max(0, x - roi_radius)
        y1 = max(0, y - roi_radius)
        x2 = min(image.shape[1], x + roi_radius)
        y2 = min(image.shape[0], y + roi_radius)
        
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return {'darkness': 0, 'coverage': 0, 'score': 0}
        
        # Create masks (full and inner)
        center_x = x - x1
        center_y = y - y1
        
        # Full circle mask
        full_mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(full_mask, (center_x, center_y), radius, 255, -1)
        
        # Inner circle mask (70% radius for photos - more lenient)
        inner_radius = int(radius * 0.7)  # Reduced from 0.8 to 0.7
        inner_mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(inner_mask, (center_x, center_y), inner_radius, 255, -1)
        
        full_pixels = roi[full_mask > 0]
        inner_pixels = roi[inner_mask > 0] if inner_radius > 0 else full_pixels
        
        if len(full_pixels) == 0:
            return {'darkness': 0, 'coverage': 0, 'score': 0}
        
        # Calculate darkness (inverted brightness)
        mean_brightness = np.mean(full_pixels)
        darkness = (255 - mean_brightness) / 255 * 100
        
        # Calculate coverage using multiple thresholding methods
        # Method 1: Otsu thresholding (adaptive)
        _, binary_otsu = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coverage_otsu = np.sum(binary_otsu[full_mask > 0] > 0) / len(full_pixels) * 100
        
        # Method 2: Fixed threshold (more sensitive for photos)
        threshold_fixed = max(100, mean_brightness - 30)  # Dynamic threshold
        _, binary_fixed = cv2.threshold(roi, threshold_fixed, 255, cv2.THRESH_BINARY_INV)
        coverage_fixed = np.sum(binary_fixed[full_mask > 0] > 0) / len(full_pixels) * 100
        
        # Use the higher coverage (more sensitive)
        coverage = max(coverage_otsu, coverage_fixed)
        
        # Inner fill analysis (for photos, be more lenient)
        if len(inner_pixels) > 0:
            inner_brightness = np.mean(inner_pixels)
            inner_darkness = (255 - inner_brightness) / 255 * 100
            
            # Inner coverage
            _, inner_binary = cv2.threshold(roi, threshold_fixed, 255, cv2.THRESH_BINARY_INV)
            inner_coverage = np.sum(inner_binary[inner_mask > 0] > 0) / len(inner_pixels) * 100 if len(inner_pixels) > 0 else 0
        else:
            inner_darkness = darkness
            inner_coverage = coverage
        
        # PHOTO-OPTIMIZED SCORING
        # Weight inner analysis more heavily, but be more forgiving
        if inner_darkness > 5 or inner_coverage > 10:  # Any detectable mark
            # Boost score for any detectable inner mark
            score = (
                darkness * 0.3 +           # Reduced weight for full darkness
                coverage * 0.2 +           # Reduced weight for full coverage  
                inner_darkness * 0.3 +     # Inner darkness (important)
                inner_coverage * 0.2       # Inner coverage (important)
            )
            
            # Additional boost for photos
            if inner_darkness > 10 or inner_coverage > 15:
                score *= 1.2  # 20% boost for clearer marks
                
        else:
            # Very light or no mark
            score = darkness * 0.5 + coverage * 0.5
        
        return {
            'darkness': round(darkness, 2),
            'coverage': round(coverage, 2),
            'inner_darkness': round(inner_darkness, 2),
            'inner_coverage': round(inner_coverage, 2),
            'score': round(score, 2)
        }
    
    def _make_decision(self, analyses: List[Dict]) -> Dict:
        """
        Make decision (photo-optimized, more lenient)
        Uses RELATIVE comparison for photos with poor contrast
        """
        sorted_analyses = sorted(
            analyses,
            key=lambda x: x['score'],
            reverse=True
        )
        
        first = sorted_analyses[0]
        second = sorted_analyses[1] if len(sorted_analyses) > 1 else None
        
        decision = {
            'answer': None,
            'confidence': 0,
            'warning': None
        }
        
        # For photos, use relative comparison
        if self.use_relative_detection:
            # Calculate mean score of all bubbles
            mean_score = np.mean([a['score'] for a in analyses])
            std_score = np.std([a['score'] for a in analyses])
            
            # ULTRA-SENSITIVE: If first is above mean + 1 std deviation OR above mean + threshold
            threshold_dynamic = min(self.relative_threshold, std_score * 0.8)  # Dynamic threshold
            
            if first['score'] > mean_score + threshold_dynamic or first['score'] > mean_score + 1.0:
                decision['answer'] = first['variant']
                
                # Check for multiple marks (more lenient for photos)
                if second and second['score'] > mean_score + (threshold_dynamic * 0.4):
                    difference = first['score'] - second['score']
                    if difference < self.multiple_marks_threshold:
                        # For photos, still give the answer but with warning
                        decision['warning'] = 'MULTIPLE_MARKS'
                        decision['confidence'] = 50  # Lower confidence but still give answer
                        return decision
                
                # Calculate confidence based on relative position
                confidence = 55 + (first['score'] - mean_score) * 4  # Higher multiplier
                if second:
                    confidence += (first['score'] - second['score']) * 2  # Higher boost
                
                decision['confidence'] = min(100, round(confidence))
                
                if decision['confidence'] < 60:  # Lower threshold for photos
                    decision['warning'] = 'LOW_CONFIDENCE'
                
                return decision
            else:
                # No clear mark
                decision['warning'] = 'NO_MARK'
                return decision
        
        # Fallback to absolute threshold (original logic)
        # Very low score - NO MARK
        if first['score'] < self.min_darkness:
            decision['warning'] = 'NO_MARK'
            return decision
        
        # Check for multiple marks
        if second and second['score'] > self.min_darkness:
            difference = first['score'] - second['score']
            
            if difference < self.multiple_marks_threshold:
                decision['warning'] = 'MULTIPLE_MARKS'
                return decision
        
        # Clear mark
        decision['answer'] = first['variant']
        
        # Calculate confidence
        confidence = first['score']
        if second:
            confidence += (first['score'] - second['score']) * 0.5
        
        decision['confidence'] = min(100, round(confidence))
        
        if decision['confidence'] < 70:
            decision['warning'] = 'LOW_CONFIDENCE'
        
        return decision
    
    def process_photo(
        self,
        image_path: str,
        exam_structure: Dict,
        answer_key: Dict
    ) -> Dict:
        """
        Complete photo processing pipeline with improved corner detection
        
        Args:
            image_path: Path to photo
            exam_structure: Exam structure
            answer_key: Answer key
            
        Returns:
            dict: Complete results with grading
        """
        logger.info(f"Processing photo: {image_path}")
        
        # Load image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        logger.info(f"Image loaded: {image.shape[1]}x{image.shape[0]}")
        
        # Calculate total questions
        total_questions = sum(
            section['questionCount']
            for subject in exam_structure['subjects']
            for section in subject['sections']
        )
        
        coordinates = None
        
        # Try improved corner detection first
        try:
            from services.photo_corner_detector import PhotoCornerDetector
            
            # Load color image for corner detection
            color_image = cv2.imread(image_path)
            corner_detector = PhotoCornerDetector()
            corners = corner_detector.detect_corners(color_image)
            
            if corners and len(corners) == 4:
                logger.info("✅ Photo corner detection successful")
                
                # Format corners for RelativeCoordinateMapper
                corners_formatted = [
                    {'name': 'top-left', 'x': corners[0][0], 'y': corners[0][1]},
                    {'name': 'top-right', 'x': corners[1][0], 'y': corners[1][1]},
                    {'name': 'bottom-left', 'x': corners[2][0], 'y': corners[2][1]},
                    {'name': 'bottom-right', 'x': corners[3][0], 'y': corners[3][1]}
                ]
                
                # Use corner-based coordinate mapping
                from utils.relative_coordinate_mapper import RelativeCoordinateMapper
                coord_mapper = RelativeCoordinateMapper(corners_formatted, exam_structure)
                coordinates = coord_mapper.calculate_all()
                
                logger.info(f"✅ Corner-based coordinates: {len(coordinates)} questions")
            else:
                logger.warning("Photo corner detection failed, falling back to bubble detection")
        except Exception as e:
            logger.warning(f"Corner detection error: {e}")
        
        # Try OCR anchor detection if corner detection failed
        if not coordinates and self.use_ocr_anchors:
            try:
                from services.ocr_anchor_detector import OCRAnchorDetector
                ocr_detector = OCRAnchorDetector()
                coordinates = ocr_detector.detect_all_with_anchors(image, exam_structure)
                
                if coordinates:
                    logger.info(f"✅ OCR anchor detection successful: {len(coordinates)} questions")
                else:
                    logger.warning("OCR anchor detection failed, falling back to Hough circles")
            except Exception as e:
                logger.warning(f"OCR anchor detection error: {e}")
                logger.info("Falling back to Hough circle detection")
        
        # Fallback to Hough circle detection
        if not coordinates:
            # Step 1: Detect bubbles
            bubbles = self.detect_bubbles_automatically(
                image,
                expected_count=total_questions * 5
            )
            
            if len(bubbles) < total_questions * 3:  # At least 60% of expected
                logger.warning(f"Only {len(bubbles)} bubbles found (expected {total_questions * 5})")
            
            # Step 2: Map to questions
            coordinates = self.map_bubbles_to_questions(
                bubbles,
                total_questions=total_questions
            )
            
            if len(coordinates) < total_questions * 0.8:  # At least 80%
                logger.warning(f"Only {len(coordinates)} questions mapped (expected {total_questions})")
        
        # Step 3: Detect answers
        omr_results = self.detect_answers(
            image,
            coordinates,
            exam_structure
        )
        
        # Step 4: Grade
        from services.grader import AnswerGrader
        grader = AnswerGrader(answer_key, exam_structure)
        grading_results = grader.grade(omr_results['answers'])  # Pass answers, not omr_results
        
        return {
            'omr_results': omr_results,
            'grading_results': grading_results,
            'coordinates': coordinates,
            'bubbles_found': len(coordinates) * 5 if coordinates else 0,
            'questions_mapped': len(coordinates) if coordinates else 0,
            'detection_method': 'corner_based' if coordinates and len(coordinates) >= total_questions * 0.8 else 'bubble_detection'
        }
