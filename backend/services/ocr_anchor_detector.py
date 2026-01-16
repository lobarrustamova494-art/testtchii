"""
OCR-Based Anchor Detection System
Savol raqamlarini OCR bilan topib, bubble'larni nisbiy pozitsiyada aniqlash
"""
import cv2
import numpy as np
import logging
import re
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Try to import pytesseract
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    logger.info("Tesseract OCR available")
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Tesseract OCR not available - OCR anchor detection disabled")

class OCRAnchorDetector:
    """
    OCR yordamida savol raqamlarini topib, bubble'larni aniqlash
    
    Algoritm:
    1. Savol raqamlarini OCR bilan topish (1., 2., 3., ...)
    2. Har raqamdan o'ngga bubble'lar joylashganini bilish
    3. Nisbiy masofa: raqam + offset = bubble A, B, C, D, E
    """
    
    def __init__(self):
        # Layout parametrlari (PDF'dan)
        self.bubble_radius_mm = 2.5
        self.bubble_spacing_mm = 8
        self.first_bubble_offset_mm = 8  # Raqamdan birinchi bubble'gacha
        
        # OCR konfiguratsiya
        self.ocr_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.'
        
    def detect_question_numbers(
        self,
        image: np.ndarray,
        expected_count: int
    ) -> List[Dict]:
        """
        Savol raqamlarini OCR bilan topish
        
        Args:
            image: Grayscale image
            expected_count: Kutilayotgan savollar soni
            
        Returns:
            list: [{'number': 1, 'x': px, 'y': px, 'confidence': 0-100}, ...]
        """
        # Check if Tesseract is available
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract not available - skipping OCR detection")
            return []
        
        logger.info(f"Detecting {expected_count} question numbers using OCR...")
        
        # Image preprocessing for better OCR
        # 1. Binarization
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 2. Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 3. OCR with Tesseract
        try:
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                cleaned,
                config=self.ocr_config,
                output_type=pytesseract.Output.DICT
            )
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return []
        
        # Parse OCR results
        question_numbers = []
        
        for i in range(len(ocr_data['text'])):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            
            # Skip low confidence or empty
            if conf < 50 or not text:
                continue
            
            # Check if it's a question number (e.g., "1.", "2.", "10.")
            match = re.match(r'^(\d+)\.?$', text)
            if match:
                number = int(match.group(1))
                
                # Get bounding box
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                
                # Center of number
                center_x = x + w // 2
                center_y = y + h // 2
                
                question_numbers.append({
                    'number': number,
                    'x': center_x,
                    'y': center_y,
                    'confidence': conf,
                    'bbox': (x, y, w, h)
                })
                
                logger.debug(f"Found Q{number} at ({center_x}, {center_y}), conf={conf}%")
        
        # Sort by number
        question_numbers.sort(key=lambda q: q['number'])
        
        logger.info(f"OCR detected {len(question_numbers)}/{expected_count} question numbers")
        
        return question_numbers
    
    def calculate_bubble_positions(
        self,
        anchor: Dict,
        image_width: int,
        image_height: int
    ) -> List[Dict]:
        """
        Anchor (savol raqami) dan bubble pozitsiyalarini hisoblash
        
        Args:
            anchor: Question number position {'number': 1, 'x': px, 'y': px}
            image_width: Image width in pixels
            image_height: Image height in pixels
            
        Returns:
            list: [{'variant': 'A', 'x': px, 'y': px, 'radius': px}, ...]
        """
        # Calculate scale factor (pixels per mm)
        # Assume A4 paper: 210mm x 297mm
        px_per_mm_x = image_width / 210
        px_per_mm_y = image_height / 297
        
        # Bubble positions relative to anchor
        bubbles = []
        variants = ['A', 'B', 'C', 'D', 'E']
        
        for v_idx, variant in enumerate(variants):
            # Calculate X position
            # anchor.x + firstBubbleOffset + (v_idx * bubbleSpacing)
            bubble_x = anchor['x'] + (self.first_bubble_offset_mm * px_per_mm_x) + (v_idx * self.bubble_spacing_mm * px_per_mm_x)
            
            # Y position same as anchor (approximately)
            bubble_y = anchor['y']
            
            # Bubble radius
            bubble_radius = self.bubble_radius_mm * min(px_per_mm_x, px_per_mm_y)
            
            bubbles.append({
                'variant': variant,
                'x': bubble_x,
                'y': bubble_y,
                'radius': bubble_radius
            })
        
        return bubbles
    
    def detect_all_with_anchors(
        self,
        image: np.ndarray,
        exam_structure: Dict
    ) -> Dict[int, Dict]:
        """
        OCR anchor system bilan barcha savollarni aniqlash
        
        Args:
            image: Grayscale image
            exam_structure: Exam structure data
            
        Returns:
            dict: {questionNumber: {'questionNumber': int, 'bubbles': [...]}}
        """
        # Calculate total questions
        total_questions = sum(
            section['questionCount']
            for subject in exam_structure['subjects']
            for section in subject['sections']
        )
        
        logger.info(f"Starting OCR-based anchor detection for {total_questions} questions")
        
        # Detect question numbers
        anchors = self.detect_question_numbers(image, total_questions)
        
        if len(anchors) < total_questions * 0.8:  # At least 80% detected
            logger.warning(f"Only {len(anchors)}/{total_questions} anchors detected!")
            logger.warning("Falling back to coordinate-based system")
            return None
        
        # Calculate bubble positions for each anchor
        coordinates = {}
        
        for anchor in anchors:
            q_num = anchor['number']
            
            if q_num > total_questions:
                logger.warning(f"Unexpected question number: {q_num}")
                continue
            
            bubbles = self.calculate_bubble_positions(
                anchor,
                image.shape[1],
                image.shape[0]
            )
            
            coordinates[q_num] = {
                'questionNumber': q_num,
                'bubbles': bubbles,
                'anchor': anchor  # Keep anchor for debugging
            }
        
        logger.info(f"✅ OCR-based coordinates calculated for {len(coordinates)} questions")
        
        return coordinates
    
    def visualize_anchors(
        self,
        image: np.ndarray,
        anchors: List[Dict],
        output_path: str = 'anchors_debug.jpg'
    ):
        """
        Anchor'larni vizualizatsiya qilish (debug uchun)
        """
        # Convert to BGR for colored visualization
        if len(image.shape) == 2:
            vis = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            vis = image.copy()
        
        for anchor in anchors:
            x, y = anchor['x'], anchor['y']
            
            # Draw anchor point
            cv2.circle(vis, (x, y), 5, (0, 0, 255), -1)  # Red dot
            
            # Draw question number
            cv2.putText(
                vis,
                f"Q{anchor['number']}",
                (x + 10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )
            
            # Draw bounding box
            if 'bbox' in anchor:
                x, y, w, h = anchor['bbox']
                cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 0), 1)
        
        cv2.imwrite(output_path, vis)
        logger.info(f"Anchor visualization saved: {output_path}")
