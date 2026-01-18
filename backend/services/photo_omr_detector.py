"""
Photo-Specific OMR Detector
More lenient detection for photos (not PDF-generated exams)
"""
import cv2
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PhotoOMRDetector:
    """
    OMR detector optimized for PHOTOS (not PDF-generated exams)
    
    Key differences from standard detector:
    - Lower thresholds (photos have less contrast)
    - No strict inner_fill requirement (photos have gradual transitions)
    - More lenient scoring (accept partial fills)
    """
    
    def __init__(
        self,
        bubble_radius: int = 8,
        min_darkness: float = 15.0,  # Much lower than standard (35.0)
        min_difference: float = 5.0,  # Much lower than standard (15.0)
        multiple_marks_threshold: float = 5.0  # Much lower than standard (10.0)
    ):
        self.bubble_radius = bubble_radius
        self.min_darkness = min_darkness
        self.min_difference = min_difference
        self.multiple_marks_threshold = multiple_marks_threshold
        
    def detect_all_answers(
        self,
        image: np.ndarray,
        coordinates: Dict,
        exam_structure: Dict
    ) -> Dict:
        """
        Barcha javoblarni aniqlash
        """
        logger.info("Starting Photo OMR detection (lenient mode)...")
        
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
                    q_num = stats['total'] + 1
                    coords = coordinates.get(q_num)
                    
                    if not coords:
                        logger.warning(f"Coordinates not found for Q{q_num}")
                        continue
                    
                    stats['total'] += 1
                    
                    # PHOTO DETECTION (lenient)
                    result = self.detect_single_question(image, coords)
                    
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
            f"Photo OMR Detection complete: {stats['detected']}/{stats['total']} detected, "
            f"{stats['uncertain']} uncertain, {stats['multiple_marks']} multiple marks"
        )
        
        return {
            'answers': results,
            'statistics': stats
        }
    
    def detect_single_question(
        self,
        image: np.ndarray,
        coords: Dict
    ) -> Dict:
        """
        Bitta savolni aniqlash - LENIENT for photos
        """
        bubbles = coords['bubbles']
        analyses = []
        
        # Har bir variantni tahlil qilish
        for bubble in bubbles:
            analysis = self.analyze_bubble(image, bubble)
            analyses.append({
                'variant': bubble['variant'],
                **analysis
            })
        
        # LENIENT DECISION MAKING
        decision = self.make_decision(analyses)
        
        return {
            'questionNumber': coords['questionNumber'],
            'answer': decision['answer'],
            'confidence': decision['confidence'],
            'warning': decision['warning'],
            'allScores': analyses,
            'debugScores': ' '.join([f"{a['variant']}:{a['score']:.1f}" for a in analyses])
        }
    
    def analyze_bubble(
        self,
        image: np.ndarray,
        bubble: Dict
    ) -> Dict:
        """
        LENIENT bubble analysis for photos
        
        Key differences:
        - No strict inner_fill requirement
        - Use simple darkness + coverage
        - Accept partial fills
        """
        x, y = int(bubble['x']), int(bubble['y'])
        radius = int(bubble['radius'])
        
        # ROI extraction
        roi_radius = int(radius * 1.2)  # Slightly larger for photos
        
        x1 = max(0, x - roi_radius)
        y1 = max(0, y - roi_radius)
        x2 = min(image.shape[1], x + roi_radius)
        y2 = min(image.shape[0], y + roi_radius)
        
        roi = image[y1:y2, x1:x2]
        
        # Recalculate center in ROI coordinates
        center_x = x - x1
        center_y = y - y1
        
        if roi.size == 0:
            return {'darkness': 0, 'coverage': 0, 'score': 0}
        
        # Create circle mask
        center = (center_x, center_y)
        mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(mask, center, radius, 255, -1)
        
        # Extract pixels
        masked = cv2.bitwise_and(roi, roi, mask=mask)
        pixels = mask > 0
        
        if np.sum(pixels) == 0:
            return {'darkness': 0, 'coverage': 0, 'score': 0}
        
        # 1. DARKNESS - Average darkness
        inverted = 255 - masked
        darkness = float(np.mean(inverted[pixels]) / 255 * 100)
        
        # 2. COVERAGE - Percentage of dark pixels
        # Use ADAPTIVE threshold for photos (better than fixed threshold)
        _, binary = cv2.threshold(masked, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coverage = float(np.sum(binary[pixels] > 0) / np.sum(pixels) * 100)
        
        # 3. SIMPLE SCORE - Just average of darkness and coverage
        # NO strict inner_fill requirement for photos!
        score = (darkness * 0.5 + coverage * 0.5)
        
        return {
            'darkness': round(darkness, 2),
            'coverage': round(coverage, 2),
            'score': round(score, 2)
        }
    
    def make_decision(self, analyses: List[Dict]) -> Dict:
        """
        LENIENT DECISION MAKING for photos
        """
        # Sort by score
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
        
        # 1. Very low score - NO MARK
        if first['score'] < self.min_darkness:
            decision['warning'] = 'NO_MARK'
            decision['confidence'] = 0
            return decision
        
        # 2. Check for MULTIPLE MARKS
        if second:
            difference = first['score'] - second['score']
            
            # Too close - MULTIPLE MARKS
            if difference < self.multiple_marks_threshold:
                decision['answer'] = None
                decision['confidence'] = 0
                decision['warning'] = 'MULTIPLE_MARKS'
                return decision
            
            # Low difference - LOW CONFIDENCE
            if difference < self.min_difference:
                decision['answer'] = first['variant']
                decision['confidence'] = 65
                decision['warning'] = 'LOW_CONFIDENCE'
                return decision
        
        # 3. Clear mark - HIGH CONFIDENCE
        decision['answer'] = first['variant']
        
        # Calculate confidence
        confidence = first['score']
        if second:
            # Bonus for large difference
            confidence += (first['score'] - second['score']) * 0.5
        
        decision['confidence'] = min(100, round(confidence))
        
        return decision
