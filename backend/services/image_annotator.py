"""
Image Annotator - Javoblarni vizual ko'rsatish
To'g'ri javoblar, xato javoblar va o'quvchi javoblarini belgilash
"""
import cv2
import numpy as np
import base64
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class ImageAnnotator:
    """
    Tekshirilgan varaqni vizual ko'rsatish uchun annotate qilish
    """
    
    # Colors (BGR format for OpenCV)
    COLOR_CORRECT_ANSWER = (0, 255, 0)      # Yashil - to'g'ri javob
    COLOR_STUDENT_CORRECT = (255, 128, 0)   # Ko'k - o'quvchi to'g'ri belgilagan
    COLOR_STUDENT_WRONG = (0, 0, 255)       # Qizil - o'quvchi xato belgilagan
    COLOR_NO_ANSWER = (128, 128, 128)       # Kulrang - javob yo'q
    
    THICKNESS = 2  # Thinner lines - bubble o'lchamiga mos
    PADDING = 0    # NO PADDING - bubble o'lchamiga teng
    
    # NO OFFSET - Coordinates should be accurate from coordinate_mapper
    X_OFFSET = 0  # No horizontal offset
    Y_OFFSET = 0  # No vertical offset
    
    def __init__(self):
        pass
    
    def annotate_sheet(
        self,
        image: np.ndarray,
        grading_results: Dict,
        coordinates: Dict,
        answer_key: Dict
    ) -> str:
        """
        Varaqni annotate qilish va base64 string qaytarish
        
        Args:
            image: Original grayscale image
            grading_results: Grading results from grader
            coordinates: Question coordinates
            answer_key: Correct answers
            
        Returns:
            str: Base64 encoded annotated image
        """
        logger.info("Starting image annotation...")
        
        # CRITICAL: Ensure we have a BGR image for colored annotations
        # The input image should be grayscale (processed image from OMR detection)
        if len(image.shape) == 2:
            # Grayscale → BGR
            annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            # Already BGR
            annotated = image.copy()
        
        logger.info(f"Annotation image shape: {annotated.shape}, dtype: {annotated.dtype}")
        
        # Annotate each question
        total_annotated = 0
        
        # Use topicResults from grading_results
        for topic_data in grading_results.get('topicResults', []):
            for section_data in topic_data.get('sections', []):
                for question in section_data.get('questions', []):
                    q_num = question['questionNumber']
                    
                    if q_num not in coordinates:
                        logger.warning(f"Coordinates not found for Q{q_num}")
                        continue
                    
                    # Get answers from question result
                    correct_answer = question.get('correctAnswer')
                    student_answer = question.get('studentAnswer')
                    is_correct = question.get('isCorrect', False)
                    
                    # Annotate bubbles
                    self._annotate_question(
                        annotated,
                        coordinates[q_num],
                        correct_answer,
                        student_answer,
                        is_correct
                    )
                    
                    total_annotated += 1
        
        logger.info(f"Annotated {total_annotated} questions")
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{img_base64}"
    
    def _annotate_question(
        self,
        image: np.ndarray,
        coords: Dict,
        correct_answer: str,
        student_answer: str,
        is_correct: bool
    ):
        """
        Bitta savolni annotate qilish
        
        YANGI MANTIQ (MINIMAL ANNOTATION):
        - Faqat KERAKLI bubble'larni annotation qilish
        - To'g'ri javob: YASHIL
        - Student to'g'ri belgilagan: KO'K
        - Student xato belgilagan: QIZIL
        - Boshqa bubble'lar: annotation qilinmaydi
        """
        bubbles = coords['bubbles']
        
        # DEBUG: Log first bubble coordinates
        if coords['questionNumber'] == 1:
            logger.info(f"Q1 Bubble A coordinates: x={bubbles[0]['x']:.1f}, y={bubbles[0]['y']:.1f}, radius={bubbles[0]['radius']:.1f}")
            logger.info(f"Q1 Correct answer: {correct_answer}, Student answer: {student_answer}, Is correct: {is_correct}")
        
        for bubble in bubbles:
            variant = bubble['variant']
            x = int(round(bubble['x'])) + self.X_OFFSET
            y = int(round(bubble['y'])) + self.Y_OFFSET
            radius = int(round(bubble['radius']))
            
            # Calculate rectangle coordinates
            x1 = x - radius - self.PADDING
            y1 = y - radius - self.PADDING
            x2 = x + radius + self.PADDING
            y2 = y + radius + self.PADDING
            
            # FAQAT KERAKLI BUBBLE'LARNI ANNOTATION QILISH
            
            # Case 1: Student to'g'ri javob bergan (to'g'ri javob == student javobi)
            if variant == correct_answer and variant == student_answer:
                # KO'K - student to'g'ri belgilagan
                cv2.rectangle(
                    image, (x1, y1), (x2, y2),
                    self.COLOR_STUDENT_CORRECT,
                    self.THICKNESS
                )
            
            # Case 2: Student xato javob bergan
            elif variant == student_answer and not is_correct:
                # QIZIL - student xato belgilagan
                cv2.rectangle(
                    image, (x1, y1), (x2, y2),
                    self.COLOR_STUDENT_WRONG,
                    self.THICKNESS
                )
                # YASHIL - to'g'ri javobni ham ko'rsatish
                # (agar student xato bergan bo'lsa, to'g'ri javobni ko'rsatish kerak)
                for b in bubbles:
                    if b['variant'] == correct_answer:
                        bx = int(round(b['x'])) + self.X_OFFSET
                        by = int(round(b['y'])) + self.Y_OFFSET
                        br = int(round(b['radius']))
                        cv2.rectangle(
                            image, 
                            (bx - br - self.PADDING, by - br - self.PADDING),
                            (bx + br + self.PADDING, by + br + self.PADDING),
                            self.COLOR_CORRECT_ANSWER,
                            self.THICKNESS
                        )
                        break
            
            # Case 3: Student javob bermagan (student_answer is None)
            elif student_answer is None and variant == correct_answer:
                # YASHIL - faqat to'g'ri javobni ko'rsatish
                cv2.rectangle(
                    image, (x1, y1), (x2, y2),
                    self.COLOR_CORRECT_ANSWER,
                    self.THICKNESS
                )
