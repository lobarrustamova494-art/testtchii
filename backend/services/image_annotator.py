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
    
    THICKNESS = 6  # Very thick lines for maximum visibility
    PADDING = 3    # Increased padding for better visual separation
    
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
        
        # Convert grayscale to BGR for colored annotations
        if len(image.shape) == 2:
            annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            annotated = image.copy()
        
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
        
        Yangi mantiq:
        - YASHIL: To'g'ri javob (har doim)
        - KO'K: Student to'g'ri belgilagan
        - QIZIL: Student xato belgilagan
        """
        bubbles = coords['bubbles']
        
        for bubble in bubbles:
            variant = bubble['variant']
            x = int(round(bubble['x']))  # Round to nearest pixel
            y = int(round(bubble['y']))  # Round to nearest pixel
            radius = int(round(bubble['radius']))  # Round to nearest pixel
            
            # Calculate rectangle coordinates
            x1 = x - radius - self.PADDING
            y1 = y - radius - self.PADDING
            x2 = x + radius + self.PADDING
            y2 = y + radius + self.PADDING
            
            # BIRINCHI: To'g'ri javobni YASHIL bilan belgilash (har doim)
            if variant == correct_answer:
                cv2.rectangle(
                    image, (x1, y1), (x2, y2),
                    self.COLOR_CORRECT_ANSWER,
                    self.THICKNESS
                )
            
            # IKKINCHI: Student javobini belgilash
            if variant == student_answer:
                if is_correct:
                    # Student to'g'ri belgilagan - KO'K (yashil ustiga)
                    cv2.rectangle(
                        image, (x1, y1), (x2, y2),
                        self.COLOR_STUDENT_CORRECT,
                        self.THICKNESS
                    )
                else:
                    # Student xato belgilagan - QIZIL
                    cv2.rectangle(
                        image, (x1, y1), (x2, y2),
                        self.COLOR_STUDENT_WRONG,
                        self.THICKNESS
                    )
