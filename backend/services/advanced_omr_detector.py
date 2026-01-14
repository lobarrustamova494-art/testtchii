"""
Advanced OMR Detector - Mukammal aniqlash tizimi
Based on fix_annonatsiya.md solution
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class AdvancedOMRDetector:
    """
    Mukammal OMR detection - adaptive thresholding va comparative analysis
    """
    
    def __init__(self):
        # Detection parametrlari
        self.bubble_radius_range = (6, 12)  # min, max pixels
        self.min_circularity = 0.7  # 0-1, 1 = perfect circle
        self.adaptive_window_size = 15  # adaptive threshold uchun
        
    def detect_all_answers(
        self,
        image: np.ndarray,
        coordinates: Dict,
        exam_structure: Dict
    ) -> Dict:
        """
        YAXSHILANGAN: Barcha javoblarni aniqlash
        """
        logger.info("Starting ADVANCED OMR detection...")
        
        # 1. Rasmni tayyorlash
        prepared = self.prepare_image_for_detection(image)
        
        # 2. Barcha doirachalarni topish
        all_bubbles = self.find_all_bubbles(prepared)
        logger.info(f"Found {len(all_bubbles)} potential bubbles")
        
        # 3. Koordinatalar bilan matching
        matched_bubbles = self.match_bubbles_to_coordinates(
            all_bubbles, 
            coordinates
        )
        
        # 4. Har bir savolni tahlil qilish
        results = {}
        stats = {'total': 0, 'detected': 0, 'uncertain': 0, 'no_mark': 0, 'multiple_marks': 0}
        
        for topic in exam_structure['subjects']:
            results[topic['id']] = {}
            
            for section in topic['sections']:
                section_results = []
                
                for i in range(section['questionCount']):
                    q_num = stats['total'] + 1
                    
                    if q_num not in matched_bubbles:
                        logger.warning(f"Q{q_num}: No bubbles matched")
                        continue
                    
                    stats['total'] += 1
                    
                    # ASOSIY TAHLIL
                    result = self.analyze_question(
                        prepared,
                        matched_bubbles[q_num],
                        q_num
                    )
                    
                    if result['answer']:
                        stats['detected'] += 1
                    else:
                        stats['no_mark'] += 1
                        
                    if result['confidence'] < 70:
                        stats['uncertain'] += 1
                        
                    if result.get('warning') == 'MULTIPLE_MARKS':
                        stats['multiple_marks'] += 1
                    
                    section_results.append(result)
                
                results[topic['id']][section['id']] = section_results
        
        logger.info(f"Detection: {stats['detected']}/{stats['total']}, uncertain: {stats['uncertain']}, multiple: {stats['multiple_marks']}")
        
        return {
            'answers': results,
            'statistics': stats
        }
    
    def prepare_image_for_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Rasmni aniqlash uchun optimal holatga keltirish
        """
        # Grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 1. Gaussian blur (noise reduction)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
        
        # 3. Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        morph = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        
        return morph
    
    def find_all_bubbles(self, image: np.ndarray) -> List[Dict]:
        """
        Rasmdan barcha mumkin bo'lgan doirachalarni topish
        """
        bubbles = []
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,  # Qora obyektlar
            self.adaptive_window_size,
            2
        )
        
        # Morphological cleaning
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Contour detection
        contours, _ = cv2.findContours(
            cleaned,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Har bir contourni tekshirish
        for contour in contours:
            # Minimal area
            area = cv2.contourArea(contour)
            if area < 20 or area > 500:  # Filter by size
                continue
            
            # Bounding circle
            (x, y), radius = cv2.minEnclosingCircle(contour)
            
            # Radius range tekshirish
            if not (self.bubble_radius_range[0] <= radius <= self.bubble_radius_range[1]):
                continue
            
            # Circularity (doira shakliga yaqinlik)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity < self.min_circularity:
                continue
            
            # Bu bubble!
            bubbles.append({
                'center': (int(x), int(y)),
                'radius': int(radius),
                'area': area,
                'circularity': circularity,
                'contour': contour
            })
        
        return bubbles
    
    def match_bubbles_to_coordinates(
        self,
        bubbles: List[Dict],
        coordinates: Dict
    ) -> Dict:
        """
        Topilgan doirachalarni kutilgan koordinatalar bilan moslashtirish
        """
        matched = {}
        
        for q_num, coords in coordinates.items():
            question_bubbles = []
            
            for variant_coord in coords['bubbles']:
                expected_x = variant_coord['x']
                expected_y = variant_coord['y']
                expected_radius = variant_coord['radius']
                
                # Eng yaqin bubbleni topish
                closest_bubble = None
                min_distance = float('inf')
                
                for bubble in bubbles:
                    bx, by = bubble['center']
                    
                    # Distance
                    distance = np.sqrt(
                        (bx - expected_x)**2 + 
                        (by - expected_y)**2
                    )
                    
                    # Radius ham tekshirish
                    radius_diff = abs(bubble['radius'] - expected_radius)
                    
                    # Combined metric
                    metric = distance + radius_diff * 2
                    
                    # Threshold: 20 pixels ichida bo'lishi kerak
                    if metric < min_distance and distance < 20:
                        min_distance = metric
                        closest_bubble = bubble
                
                if closest_bubble:
                    question_bubbles.append({
                        'variant': variant_coord['variant'],
                        'expected': (expected_x, expected_y),
                        'actual': closest_bubble['center'],
                        'radius': closest_bubble['radius'],
                        'bubble_data': closest_bubble
                    })
            
            if question_bubbles:
                matched[q_num] = question_bubbles
        
        return matched
    
    def analyze_question(
        self,
        image: np.ndarray,
        bubbles: List[Dict],
        question_num: int
    ) -> Dict:
        """
        Bir savolning barcha variantlarini taqqoslash
        """
        analyses = []
        
        for bubble_info in bubbles:
            # Har bir variantni tahlil qilish
            analysis = self.analyze_single_bubble(
                image,
                bubble_info['actual'],
                bubble_info['radius']
            )
            
            analyses.append({
                'variant': bubble_info['variant'],
                **analysis
            })
        
        # Qaror qabul qilish (COMPARATIVE METHOD)
        decision = self.make_comparative_decision(analyses)
        
        return {
            'questionNumber': question_num,
            'answer': decision['answer'],
            'confidence': decision['confidence'],
            'warning': decision['warning'],
            'allScores': analyses,
            'debugScores': ' '.join([f"{a['variant']}:{a['score']:.1f}" for a in analyses])
        }
    
    def analyze_single_bubble(
        self,
        image: np.ndarray,
        center: Tuple[int, int],
        radius: int
    ) -> Dict:
        """
        Bitta doirachani batafsil tahlil qilish
        """
        x, y = center
        
        # ROI extraction
        roi_size = int(radius * 2.5)
        x1 = max(0, x - roi_size // 2)
        y1 = max(0, y - roi_size // 2)
        x2 = min(image.shape[1], x1 + roi_size)
        y2 = min(image.shape[0], y1 + roi_size)
        
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return {'score': 0, 'darkness': 0, 'filled_ratio': 0}
        
        # Doiracha maskasi
        mask = np.zeros(roi.shape, dtype=np.uint8)
        local_center = (roi.shape[1] // 2, roi.shape[0] // 2)
        cv2.circle(mask, local_center, radius, 255, -1)
        
        # Faqat doiracha ichidagi piksellar
        circle_pixels = roi[mask > 0]
        
        if len(circle_pixels) == 0:
            return {'score': 0, 'darkness': 0, 'filled_ratio': 0}
        
        # 1. MEAN DARKNESS
        mean_brightness = np.mean(circle_pixels)
        darkness = (255 - mean_brightness) / 255 * 100
        
        # 2. FILLED RATIO (threshold ostidagi piksellar)
        threshold = max(50, np.mean(roi) - 30)
        filled_pixels = np.sum(circle_pixels < threshold)
        filled_ratio = filled_pixels / len(circle_pixels) * 100
        
        # 3. STANDARD DEVIATION (consistency)
        std_dev = np.std(circle_pixels)
        consistency = max(0, 100 - (std_dev / 255 * 100))
        
        # 4. EDGE ANALYSIS
        edge_mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(edge_mask, local_center, radius, 255, 2)
        edge_pixels = roi[edge_mask > 0]
        
        if len(edge_pixels) > 0:
            edge_darkness = (255 - np.mean(edge_pixels)) / 255 * 100
        else:
            edge_darkness = 0
        
        # WEIGHTED SCORE
        score = (
            darkness * 0.35 +
            filled_ratio * 0.35 +
            consistency * 0.15 +
            edge_darkness * 0.15
        )
        
        return {
            'score': round(score, 2),
            'darkness': round(darkness, 2),
            'filled_ratio': round(filled_ratio, 2),
            'consistency': round(consistency, 2),
            'edge_darkness': round(edge_darkness, 2)
        }
    
    def make_comparative_decision(self, analyses: List[Dict]) -> Dict:
        """
        NISBIY TAQQOSLASH - eng muhim qism!
        """
        # Ball bo'yicha saralash
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
        
        # 1. Agar eng yuqori ball juda past bo'lsa
        if first['score'] < 25:  # 25% dan kam
            decision['warning'] = 'NO_MARK'
            return decision
        
        # 2. Nisbiy farqni tekshirish
        if second:
            difference = first['score'] - second['score']
            
            # Farq juda kichik (5% ichida)
            if difference < 5:
                decision['answer'] = first['variant']
                decision['confidence'] = 40
                decision['warning'] = 'MULTIPLE_MARKS'
                return decision
            
            # Farq o'rtacha (5-15% oralig'ida)
            if difference < 15:
                decision['answer'] = first['variant']
                decision['confidence'] = 65
                decision['warning'] = 'LOW_CONFIDENCE'
                return decision
            
            # Aniq farq (15%+)
            decision['answer'] = first['variant']
            
            # Confidence: base score + difference bonus
            confidence = min(100, first['score'] + difference * 0.5)
            
            # Agar ikkinchi variant ham past bo'lsa, ishonch oshadi
            if second['score'] < 30:
                confidence += 10
            
            decision['confidence'] = int(confidence)
            
        else:
            # Faqat bitta variant
            decision['answer'] = first['variant']
            decision['confidence'] = min(100, int(first['score'] * 1.2))
        
        return decision
