"""
Template Matching OMR System
Automatically detects bubble positions from any exam layout
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TemplateMatchingOMR:
    """
    Template matching approach for unknown exam layouts
    
    Steps:
    1. Detect all circular objects (bubbles)
    2. Group them by rows and columns
    3. Identify question structure
    4. Analyze each bubble for fill status
    """
    
    def __init__(self):
        self.min_radius = 15  # Minimum bubble radius in pixels
        self.max_radius = 40  # Maximum bubble radius in pixels
        self.min_distance = 30  # Minimum distance between bubbles
        
    def detect_bubbles(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all circular bubbles in the image
        """
        logger.info("Detecting bubbles using Hough Circle Transform...")
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using HoughCircles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=self.min_distance,
            param1=50,
            param2=30,
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )
        
        bubbles = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            
            for (x, y, r) in circles:
                bubbles.append({
                    'x': int(x),
                    'y': int(y),
                    'radius': int(r),
                    'darkness': self._calculate_darkness(gray, x, y, r),
                    'fill_ratio': self._calculate_fill_ratio(gray, x, y, r)
                })
        
        logger.info(f"Found {len(bubbles)} bubble candidates")
        return bubbles
    
    def group_bubbles_by_questions(self, bubbles: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Group bubbles by question rows
        """
        logger.info("Grouping bubbles by questions...")
        
        # Sort bubbles by Y coordinate (top to bottom)
        sorted_bubbles = sorted(bubbles, key=lambda b: b['y'])
        
        # Group by rows (similar Y coordinates)
        rows = []
        current_row = []
        row_threshold = 20  # pixels
        
        for bubble in sorted_bubbles:
            if not current_row:
                current_row.append(bubble)
            else:
                # Check if this bubble is in the same row
                avg_y = sum(b['y'] for b in current_row) / len(current_row)
                if abs(bubble['y'] - avg_y) <= row_threshold:
                    current_row.append(bubble)
                else:
                    # Start new row
                    if len(current_row) >= 3:  # At least 3 bubbles for a valid question
                        rows.append(current_row)
                    current_row = [bubble]
        
        # Add last row
        if len(current_row) >= 3:
            rows.append(current_row)
        
        # Convert to question format
        questions = {}
        for i, row in enumerate(rows):
            # Sort bubbles in row by X coordinate (left to right)
            row_sorted = sorted(row, key=lambda b: b['x'])
            
            # Assign variants (A, B, C, D, E)
            variants = ['A', 'B', 'C', 'D', 'E']
            for j, bubble in enumerate(row_sorted[:5]):  # Max 5 variants
                bubble['variant'] = variants[j] if j < len(variants) else f'V{j+1}'
            
            questions[i + 1] = row_sorted[:5]  # Max 5 variants per question
        
        logger.info(f"Grouped into {len(questions)} questions")
        return questions
    
    def analyze_question(self, bubbles: List[Dict]) -> Dict:
        """
        Analyze a single question to determine the answer
        """
        # Calculate scores for each bubble
        scores = []
        for bubble in bubbles:
            # Weighted score: darkness (40%) + fill_ratio (60%)
            score = (bubble['darkness'] * 0.4) + (bubble['fill_ratio'] * 0.6)
            scores.append({
                'variant': bubble['variant'],
                'score': score,
                'darkness': bubble['darkness'],
                'fill_ratio': bubble['fill_ratio'],
                'bubble': bubble
            })
        
        # Sort by score (highest first)
        scores.sort(key=lambda s: s['score'], reverse=True)
        
        # Determine answer
        if not scores:
            return {
                'answer': None,
                'confidence': 0,
                'warning': 'NO_BUBBLES',
                'scores': []
            }
        
        best = scores[0]
        second_best = scores[1] if len(scores) > 1 else None
        
        # Check if best score is significant enough
        min_score = 20.0  # Minimum score to consider as filled
        if best['score'] < min_score:
            return {
                'answer': None,
                'confidence': 0,
                'warning': 'NO_MARK',
                'scores': scores
            }
        
        # Check for multiple marks (close scores)
        confidence = 100
        warning = None
        
        if second_best and (best['score'] - second_best['score']) < 5.0:
            warning = 'MULTIPLE_MARKS'
            confidence = 60
        elif best['score'] < 30.0:
            warning = 'LOW_CONFIDENCE'
            confidence = 70
        
        return {
            'answer': best['variant'],
            'confidence': confidence,
            'warning': warning,
            'scores': scores
        }
    
    def process_image(self, image: np.ndarray) -> Dict:
        """
        Process entire image and return all answers
        """
        logger.info("Starting template matching OMR processing...")
        
        # Step 1: Detect all bubbles
        bubbles = self.detect_bubbles(image)
        
        if not bubbles:
            return {
                'answers': {},
                'statistics': {
                    'total': 0,
                    'detected': 0,
                    'bubbles_found': 0
                },
                'error': 'No bubbles detected'
            }
        
        # Step 2: Group bubbles by questions
        questions = self.group_bubbles_by_questions(bubbles)
        
        # Step 3: Analyze each question
        answers = {}
        stats = {
            'total': len(questions),
            'detected': 0,
            'uncertain': 0,
            'no_mark': 0,
            'multiple_marks': 0,
            'bubbles_found': len(bubbles)
        }
        
        for q_num, q_bubbles in questions.items():
            result = self.analyze_question(q_bubbles)
            
            answers[q_num] = {
                'questionNumber': q_num,
                'answer': result['answer'],
                'confidence': result['confidence'],
                'warning': result['warning'],
                'debugScores': result['scores']
            }
            
            # Update statistics
            if result['answer']:
                stats['detected'] += 1
            else:
                stats['no_mark'] += 1
            
            if result['warning'] == 'MULTIPLE_MARKS':
                stats['multiple_marks'] += 1
            elif result['confidence'] < 80:
                stats['uncertain'] += 1
        
        logger.info(f"Template matching complete: {stats['detected']}/{stats['total']} detected")
        
        return {
            'answers': answers,
            'statistics': stats,
            'bubbles': bubbles,
            'questions': questions
        }
    
    def _calculate_darkness(self, gray: np.ndarray, x: int, y: int, radius: int) -> float:
        """
        Calculate darkness percentage in bubble area
        """
        # Create circular mask
        mask = np.zeros(gray.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (x, y), radius, 255, -1)
        
        # Extract pixels in circle
        pixels = gray[mask == 255]
        
        if len(pixels) == 0:
            return 0.0
        
        # Calculate darkness (inverted brightness)
        avg_brightness = np.mean(pixels)
        darkness = (255 - avg_brightness) / 255 * 100
        
        return darkness
    
    def _calculate_fill_ratio(self, gray: np.ndarray, x: int, y: int, radius: int) -> float:
        """
        Calculate fill ratio (percentage of dark pixels)
        """
        # Create circular mask
        mask = np.zeros(gray.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (x, y), radius, 255, -1)
        
        # Extract pixels in circle
        pixels = gray[mask == 255]
        
        if len(pixels) == 0:
            return 0.0
        
        # Threshold for "dark" pixels
        threshold = 180  # Pixels darker than this are considered "filled"
        dark_pixels = np.sum(pixels < threshold)
        total_pixels = len(pixels)
        
        fill_ratio = (dark_pixels / total_pixels) * 100
        return fill_ratio
    
    def create_annotated_image(self, image: np.ndarray, results: Dict) -> np.ndarray:
        """
        Create annotated image showing detected bubbles and answers
        """
        # Convert to BGR if grayscale
        if len(image.shape) == 2:
            annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            annotated = image.copy()
        
        # Draw bubbles and answers
        for q_num, answer_data in results['answers'].items():
            if q_num in results['questions']:
                bubbles = results['questions'][q_num]
                
                for bubble in bubbles:
                    x, y, r = bubble['x'], bubble['y'], bubble['radius']
                    variant = bubble['variant']
                    
                    # Color based on answer
                    if answer_data['answer'] == variant:
                        color = (0, 255, 0)  # Green for selected answer
                        thickness = 3
                    else:
                        color = (200, 200, 200)  # Gray for unselected
                        thickness = 1
                    
                    # Draw circle
                    cv2.circle(annotated, (x, y), r, color, thickness)
                    
                    # Draw variant label
                    cv2.putText(
                        annotated,
                        variant,
                        (x - 5, y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 0, 0),
                        1
                    )
                
                # Draw question number
                if bubbles:
                    first_bubble = bubbles[0]
                    cv2.putText(
                        annotated,
                        f"Q{q_num}",
                        (first_bubble['x'] - 30, first_bubble['y']),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 0, 0),
                        2
                    )
        
        return annotated
    
    def detect_layout_fallback(self, image: np.ndarray, exam_structure: Dict) -> Dict:
        """
        Fallback coordinate detection when corner detection fails
        Uses bubble pattern recognition to estimate layout
        """
        logger.info("🔄 Template matching fallback coordinate detection...")
        
        try:
            # Detect bubbles first
            bubbles = self.detect_bubbles(image)
            
            if len(bubbles) < 10:  # Need minimum bubbles
                return {'success': False, 'error': 'Insufficient bubbles for layout detection'}
            
            # Group bubbles by questions
            questions = self.group_bubbles_by_questions(bubbles)
            
            if len(questions) < 5:  # Need minimum questions
                return {'success': False, 'error': 'Insufficient questions detected'}
            
            # Generate coordinate template from detected bubbles
            coordinates = {}
            
            for q_num, q_bubbles in questions.items():
                bubble_coords = []
                
                for bubble in q_bubbles:
                    bubble_coords.append({
                        'variant': bubble['variant'],
                        'x': bubble['x'],
                        'y': bubble['y'],
                        'radius': bubble['radius']
                    })
                
                coordinates[q_num] = {
                    'questionNumber': q_num,
                    'bubbles': bubble_coords
                }
            
            logger.info(f"✅ Fallback detection successful: {len(coordinates)} questions mapped")
            
            return {
                'success': True,
                'coordinates': coordinates,
                'method': 'template_matching_fallback',
                'bubbles_detected': len(bubbles),
                'questions_mapped': len(questions)
            }
            
        except Exception as e:
            logger.error(f"Template matching fallback failed: {e}")
            return {'success': False, 'error': str(e)}