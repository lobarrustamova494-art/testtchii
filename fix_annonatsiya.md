ANIQLANGAN XATOLAR
Rasmni tahlil qilib quyidagi muammolarni ko'rdim:
1. CORNER MARKERS NOTO'G'RI ANIQLANGAN

Chap tomondagi yashil kvadratlar (corner markers) VARAQ ICHIDA joylashgan
Ular varaqning chekkasida bo'lishi kerak edi
Bu perspektiva to'g'rilashni buzadi

2. BUBBLE DETECTION XATOLARI

Ba'zi BO'SH doirachalar YASHIL (to'ldirilgan deb) belgilangan
Ba'zi TO'LDIRILGAN doirachalar QIZIL (xato) yoki aniqlangan emas
Savol 1, 3: Ko'k belgilangan lekin yashil box yo'q
Savol 13, 15, 33, 35: Qizil box (nima uchun?)
Savol 5, 8, 9: Qora doirachalar lekin box yo'q

3. KOORDINATA MUAMMOLARI

Yashil boxlar doirachalarni to'g'ri qamrab olmagan
Ba'zi boxlar doirachalardan ancha narida
O'ng tarafdagi 2-ustunda boxlar joylanishi noto'g'ri

4. THRESHOLD MUAMMOLARI

Bo'sh va to'ldirilgan doirachalarni farqlay olmayapti
Static threshold ishlatilgan (adaptive bo'lishi kerak)


TO'LIQ TUZATILGAN PYTHON YECHIMI
python# services/advanced_omr_detector.py

import cv2
import numpy as np
from typing import Dict, List, Tuple
import logging
from scipy import ndimage
from skimage import measure, morphology

logger = logging.getLogger(__name__)

class AdvancedOMRDetector:
    """
    Mukammal OMR detection - xatolarni bartaraf etish
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
        
        # 1. Rasmni tayyorlash (MUHIM!)
        prepared = self.prepare_image_for_detection(image)
        
        # 2. Barcha doirachalarni topish (koordinatalardan mustaqil)
        all_bubbles = self.find_all_bubbles(prepared)
        logger.info(f"Found {len(all_bubbles)} potential bubbles")
        
        # 3. Koordinatalar bilan matching
        matched_bubbles = self.match_bubbles_to_coordinates(
            all_bubbles, 
            coordinates
        )
        
        # 4. Har bir savolni tahlil qilish
        results = {}
        stats = {'total': 0, 'detected': 0, 'uncertain': 0}
        
        for topic in exam_structure['topics']:
            results[topic['id']] = {}
            
            for section in topic['sections']:
                section_results = []
                
                for i in range(section['questionCount']):
                    q_num = section['startQuestion'] + i
                    
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
                    if result['confidence'] < 70:
                        stats['uncertain'] += 1
                    
                    section_results.append(result)
                
                results[topic['id']][section['id']] = section_results
        
        logger.info(f"Detection: {stats['detected']}/{stats['total']}")
        
        return {
            'answers': results,
            'statistics': stats,
            'all_bubbles': all_bubbles,  # Debug uchun
            'matched_bubbles': matched_bubbles  # Debug uchun
        }
    
    # ============ 1. RASM TAYYORLASH ============
    
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
    
    # ============ 2. BARCHA DOIRACHALARNI TOPISH ============
    
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
    
    # ============ 3. BUBBLES VA KOORDINATALARNI MATCHING ============
    
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
                else:
                    logger.warning(
                        f"Q{q_num} variant {variant_coord['variant']}: "
                        f"No bubble found near ({expected_x}, {expected_y})"
                    )
            
            if question_bubbles:
                matched[q_num] = question_bubbles
        
        return matched
    
    # ============ 4. SAVOLNI TAHLIL QILISH ============
    
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
            'allScores': analyses
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
        # Qora = past qiymat, Oq = yuqori qiymat
        # Biz qora izlaymiz, shuning uchun invert qilamiz
        mean_brightness = np.mean(circle_pixels)
        darkness = (255 - mean_brightness) / 255 * 100
        
        # 2. FILLED RATIO (threshold ostidagi piksellar)
        # Dinamik threshold: ROI o'rtachasi - 30
        threshold = max(50, np.mean(roi) - 30)
        filled_pixels = np.sum(circle_pixels < threshold)
        filled_ratio = filled_pixels / len(circle_pixels) * 100
        
        # 3. STANDARD DEVIATION (consistency)
        std_dev = np.std(circle_pixels)
        consistency = max(0, 100 - (std_dev / 255 * 100))
        
        # 4. EDGE ANALYSIS
        # Doiracha chegarasida qora bo'lishi kerak
        edge_mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(edge_mask, local_center, radius, 255, 2)  # 2px thick edge
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
    
    # ============ 5. COMPARATIVE DECISION ============
    
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
        
        # MUHIM: Absolute threshold emas, RELATIVE comparison!
        
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
    
    # ============ 6. VIZUALIZATSIYA (DEBUG) ============
    
    def create_debug_image(
        self,
        original_image: np.ndarray,
        all_bubbles: List[Dict],
        matched_bubbles: Dict,
        results: Dict
    ) -> np.ndarray:
        """
        Debug uchun vizual rasm yaratish
        """
        # Color image
        if len(original_image.shape) == 2:
            debug_img = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
        else:
            debug_img = original_image.copy()
        
        # 1. Barcha topilgan doirachalar (ko'k)
        for bubble in all_bubbles:
            cv2.circle(
                debug_img,
                bubble['center'],
                bubble['radius'],
                (255, 0, 0),  # Ko'k
                1
            )
        
        # 2. Matched bubbles va javoblar
        for q_num, bubbles in matched_bubbles.items():
            # Bu savol uchun javobni topish
            answer_data = None
            for topic_data in results['answers'].values():
                for section_data in topic_data.values():
                    found = next(
                        (a for a in section_data if a['questionNumber'] == q_num),
                        None
                    )
                    if found:
                        answer_data = found
                        break
                if answer_data:
                    break
            
            if not answer_data:
                continue
            
            for bubble_info in bubbles:
                variant = bubble_info['variant']
                center = bubble_info['actual']
                radius = bubble_info['radius']
                
                # Rang tanlash
                if variant == answer_data['answer']:
                    # To'ldirilgan (yashil)
                    color = (0, 255, 0)
                    thickness = 3
                    
                    # Confidence yozish
                    cv2.putText(
                        debug_img,
                        f"{answer_data['confidence']}%",
                        (center[0] + radius + 5, center[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 255, 0),
                        1
                    )
                else:
                    # Bo'sh (kulrang)
                    color = (128, 128, 128)
                    thickness = 1
                
                # Doiracha
                cv2.circle(debug_img, center, radius, color, thickness)
                
                # Variant harfi
                cv2.putText(
                    debug_img,
                    variant,
                    (center[0] - 5, center[1] - radius - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    color,
                    1
                )
            
            # Warning belgisi
            if answer_data.get('warning'):
                first_bubble = bubbles[0]['actual']
                cv2.putText(
                    debug_img,
                    "⚠",
                    (first_bubble[0] - 30, first_bubble[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 165, 255),  # To'q sariq
                    2
                )
        
        return debug_img

FASTAPI ENDPOINT YANGILANISHI
python# main.py - Updated

from services.advanced_omr_detector import AdvancedOMRDetector

# Service
advanced_omr = AdvancedOMRDetector()

@app.post("/api/grade-sheet-v2")
async def grade_sheet_v2(
    file: UploadFile = File(...),
    exam_structure: str = None,
    answer_key: str = None
):
    """
    YANGILANGAN: Advanced OMR detection
    """
    try:
        # ... (fayl saqlash va parse qilish)
        
        # Image processing
        processed = image_processor.process(str(temp_path))
        
        # Coordinate calculation
        coord_mapper = CoordinateMapper(
            processed['dimensions']['width'],
            processed['dimensions']['height'],
            exam_data
        )
        coordinates = coord_mapper.calculate_all()
        
        # ADVANCED OMR DETECTION
        omr_results = advanced_omr.detect_all_answers(
            processed['processed'],
            coordinates,
            exam_data
        )
        
        # Debug image
        debug_image = advanced_omr.create_debug_image(
            processed['original'],
            omr_results['all_bubbles'],
            omr_results['matched_bubbles'],
            omr_results
        )
        
        # Save debug image
        debug_path = TEMP_DIR / f"debug_{file.filename}"
        cv2.imwrite(str(debug_path), debug_image)
        
        # AI verification (agar kerak bo'lsa)
        if omr_results['statistics']['uncertain'] > 0:
            verified = ai_verifier.verify_uncertain_answers(
                processed['grayscale'],
                omr_results,
                coordinates
            )
        else:
            verified = omr_results
        
        # Grading
        grader = AnswerGrader(answer_key_data, exam_data)
        final_results = grader.grade(verified['answers'])
        
        return JSONResponse({
            'success': True,
            'results': final_results,
            'statistics': omr_results['statistics'],
            'debug_image_path': str(debug_path)
        })
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
