"""
Template Matching Service for Photo Support
Matches photo-based answer sheets with PDF templates
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class TemplateMatchingService:
    """
    Template matching for photo-based OMR sheets
    
    This service:
    1. Takes a photo of filled answer sheet
    2. Matches it with the original PDF template
    3. Extracts bubble positions using template matching
    4. Works without corner markers (for photos)
    """
    
    def __init__(self):
        self.template_cache = {}
        
    def create_template_from_pdf(
        self,
        pdf_image: np.ndarray,
        coordinate_template: Dict
    ) -> Dict:
        """
        Create matching template from PDF image
        
        Args:
            pdf_image: Clean PDF image (grayscale)
            coordinate_template: Coordinate template data
            
        Returns:
            dict: Template data for matching
        """
        logger.info("Creating template from PDF image...")
        
        # Extract bubble regions as templates
        bubble_templates = []
        questions = coordinate_template.get('questions', {})
        
        for q_num, question_data in questions.items():
            for bubble in question_data['bubbles']:
                # Get bubble position in PDF
                x = int(bubble['absoluteX'] * pdf_image.shape[1] / 210)  # Convert mm to pixels
                y = int(bubble['absoluteY'] * pdf_image.shape[0] / 297)  # Convert mm to pixels
                
                # Extract bubble template (empty bubble)
                radius = 15  # Approximate bubble radius in pixels
                x1, y1 = max(0, x - radius), max(0, y - radius)
                x2, y2 = min(pdf_image.shape[1], x + radius), min(pdf_image.shape[0], y + radius)
                
                bubble_template = pdf_image[y1:y2, x1:x2]
                
                if bubble_template.size > 0:
                    bubble_templates.append({
                        'question': int(q_num),
                        'variant': bubble['variant'],
                        'template': bubble_template,
                        'center': (x, y),
                        'radius': radius
                    })
        
        template_data = {
            'pdf_image': pdf_image,
            'bubble_templates': bubble_templates,
            'coordinate_template': coordinate_template,
            'image_size': pdf_image.shape
        }
        
        logger.info(f"Template created with {len(bubble_templates)} bubble templates")
        return template_data
    
    def match_photo_with_template(
        self,
        photo: np.ndarray,
        template_data: Dict,
        confidence_threshold: float = 0.6
    ) -> Dict:
        """
        Match photo with PDF template
        
        Args:
            photo: Photo of filled answer sheet
            template_data: Template data from create_template_from_pdf
            confidence_threshold: Minimum matching confidence
            
        Returns:
            dict: Matched coordinates and bubble positions
        """
        logger.info("Matching photo with template...")
        
        # Preprocess photo
        photo_processed = self._preprocess_photo(photo)
        
        # Find overall alignment using template matching
        alignment = self._find_alignment(photo_processed, template_data['pdf_image'])
        
        if not alignment:
            logger.error("Failed to align photo with template")
            return {'success': False, 'error': 'Alignment failed'}
        
        # Extract bubble positions using alignment
        bubble_positions = self._extract_bubble_positions(
            photo_processed,
            template_data,
            alignment,
            confidence_threshold
        )
        
        return {
            'success': True,
            'alignment': alignment,
            'bubble_positions': bubble_positions,
            'total_bubbles': len(bubble_positions)
        }
    
    def _preprocess_photo(self, photo: np.ndarray) -> np.ndarray:
        """
        Preprocess photo for better matching
        """
        # Convert to grayscale if needed
        if len(photo.shape) == 3:
            photo = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        photo = clahe.apply(photo)
        
        # Reduce noise
        photo = cv2.bilateralFilter(photo, 9, 75, 75)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        photo = cv2.filter2D(photo, -1, kernel)
        
        return photo
    
    def _find_alignment(
        self,
        photo: np.ndarray,
        template: np.ndarray
    ) -> Optional[Dict]:
        """
        Find alignment between photo and template using feature matching
        """
        try:
            # Use ORB feature detector
            orb = cv2.ORB_create(nfeatures=1000)
            
            # Find keypoints and descriptors
            kp1, des1 = orb.detectAndCompute(template, None)
            kp2, des2 = orb.detectAndCompute(photo, None)
            
            if des1 is None or des2 is None:
                logger.warning("No features found for alignment")
                return None
            
            # Match features
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            
            if len(matches) < 10:
                logger.warning(f"Too few matches found: {len(matches)}")
                return None
            
            # Sort matches by distance
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Extract matched points
            src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
            
            # Find homography
            homography, mask = cv2.findHomography(
                src_pts, dst_pts, 
                cv2.RANSAC, 
                5.0
            )
            
            if homography is None:
                logger.warning("Failed to compute homography")
                return None
            
            # Calculate alignment quality
            inliers = np.sum(mask)
            quality = inliers / len(matches)
            
            logger.info(f"Alignment found: {inliers}/{len(matches)} inliers, quality: {quality:.2f}")
            
            return {
                'homography': homography,
                'quality': quality,
                'inliers': int(inliers),
                'total_matches': len(matches)
            }
            
        except Exception as e:
            logger.error(f"Alignment failed: {e}")
            return None
    
    def _extract_bubble_positions(
        self,
        photo: np.ndarray,
        template_data: Dict,
        alignment: Dict,
        confidence_threshold: float
    ) -> List[Dict]:
        """
        Extract bubble positions using template alignment
        """
        bubble_positions = []
        homography = alignment['homography']
        
        for bubble_template_data in template_data['bubble_templates']:
            try:
                # Transform template bubble position to photo coordinates
                template_center = np.array([[bubble_template_data['center']]], dtype=np.float32)
                photo_center = cv2.perspectiveTransform(template_center, homography)[0][0]
                
                x, y = int(photo_center[0]), int(photo_center[1])
                radius = bubble_template_data['radius']
                
                # Check if position is within photo bounds
                if (x - radius < 0 or x + radius >= photo.shape[1] or 
                    y - radius < 0 or y + radius >= photo.shape[0]):
                    continue
                
                # Extract bubble region from photo
                bubble_region = photo[y-radius:y+radius, x-radius:x+radius]
                
                if bubble_region.size == 0:
                    continue
                
                # Analyze bubble (filled or empty)
                bubble_analysis = self._analyze_bubble_region(bubble_region)
                
                bubble_positions.append({
                    'question': bubble_template_data['question'],
                    'variant': bubble_template_data['variant'],
                    'x': x,
                    'y': y,
                    'radius': radius,
                    'filled': bubble_analysis['filled'],
                    'confidence': bubble_analysis['confidence'],
                    'darkness': bubble_analysis['darkness']
                })
                
            except Exception as e:
                logger.warning(f"Failed to extract bubble position: {e}")
                continue
        
        logger.info(f"Extracted {len(bubble_positions)} bubble positions")
        return bubble_positions
    
    def _analyze_bubble_region(self, bubble_region: np.ndarray) -> Dict:
        """
        Analyze if bubble is filled or empty
        """
        # Create circular mask
        h, w = bubble_region.shape
        center = (w // 2, h // 2)
        radius = min(w, h) // 2 - 2
        
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, center, radius, 255, -1)
        
        # Calculate darkness within circle
        masked_region = cv2.bitwise_and(bubble_region, bubble_region, mask=mask)
        circle_pixels = masked_region[mask > 0]
        
        if len(circle_pixels) == 0:
            return {'filled': False, 'confidence': 0.0, 'darkness': 0.0}
        
        # Calculate metrics
        mean_darkness = 255 - np.mean(circle_pixels)  # Invert: higher = darker
        darkness_percentage = mean_darkness / 255 * 100
        
        # Determine if filled
        filled = darkness_percentage > 30  # Threshold for filled bubble
        confidence = min(100, darkness_percentage * 2) if filled else min(100, (100 - darkness_percentage) * 2)
        
        return {
            'filled': filled,
            'confidence': confidence,
            'darkness': darkness_percentage
        }
    
    def convert_to_omr_format(
        self,
        bubble_positions: List[Dict],
        exam_structure: Dict
    ) -> Dict:
        """
        Convert bubble positions to OMR detection format
        """
        coordinates = {}
        
        # Group bubbles by question
        questions = {}
        for bubble in bubble_positions:
            q_num = bubble['question']
            if q_num not in questions:
                questions[q_num] = []
            questions[q_num].append(bubble)
        
        # Convert to OMR format
        for q_num, bubbles in questions.items():
            coordinates[q_num] = {
                'questionNumber': q_num,
                'bubbles': [
                    {
                        'variant': b['variant'],
                        'x': b['x'],
                        'y': b['y'],
                        'radius': b['radius']
                    }
                    for b in bubbles
                ]
            }
        
        return coordinates
    
    def detect_answers_from_template_matching(
        self,
        bubble_positions: List[Dict]
    ) -> Dict:
        """
        Detect answers from template matching results
        """
        answers = {}
        
        # Group by question
        questions = {}
        for bubble in bubble_positions:
            q_num = bubble['question']
            if q_num not in questions:
                questions[q_num] = []
            questions[q_num].append(bubble)
        
        # Analyze each question
        for q_num, bubbles in questions.items():
            filled_bubbles = [b for b in bubbles if b['filled']]
            
            if len(filled_bubbles) == 0:
                answer = None
                confidence = 0
                warning = 'NO_MARK'
            elif len(filled_bubbles) == 1:
                answer = filled_bubbles[0]['variant']
                confidence = filled_bubbles[0]['confidence']
                warning = None
            else:
                # Multiple marks - choose darkest
                darkest = max(filled_bubbles, key=lambda x: x['darkness'])
                answer = darkest['variant']
                confidence = darkest['confidence'] * 0.7  # Reduce confidence
                warning = 'MULTIPLE_MARKS'
            
            answers[q_num] = {
                'questionNumber': q_num,
                'answer': answer,
                'confidence': confidence,
                'warning': warning,
                'method': 'template_matching'
            }
        
        return answers