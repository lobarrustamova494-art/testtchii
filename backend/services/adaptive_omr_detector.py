"""
Adaptive OMR Detector - 100% Aniqlik
Har xil rasm sifati va sharoitlarga moslashuvchan
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AdaptiveOMRDetector:
    """
    Adaptive OMR Detection - har xil sharoitlarga moslashuvchan
    
    Xususiyatlari:
    - Image quality-based adaptive thresholds
    - Multiple detection algorithms
    - Comparative analysis
    - Confidence scoring
    - False positive filtering
    """
    
    def __init__(self):
        self.detection_methods = [
            'darkness_analysis',
            'contour_analysis', 
            'template_matching',
            'edge_detection',
            'comparative_analysis'
        ]
        
    def detect_all_answers(
        self,
        image: np.ndarray,
        coordinates: Dict,
        exam_structure: Dict,
        image_quality: Optional[Dict] = None
    ) -> Dict:
        """
        Adaptive OMR detection - image quality'ga qarab moslashadi
        """
        logger.info("🎯 Starting ADAPTIVE OMR detection...")
        
        # 1. Image quality assessment
        if image_quality is None:
            image_quality = self._assess_image_quality(image)
        
        # Safe access to overall score
        overall_score = image_quality.get('overall_score', image_quality.get('overall', 50.0))
        logger.info(f"Image quality: {overall_score:.1f}/100")
        
        # 2. Select optimal detection strategy
        detection_strategy = self._select_detection_strategy(image_quality)
        logger.info(f"Selected strategy: {detection_strategy['name']}")
        
        # 3. Prepare image for detection
        prepared_images = self._prepare_images_adaptive(image, image_quality)
        
        # 4. Detect all answers
        results = {}
        stats = {
            'total': 0,
            'detected': 0,
            'uncertain': 0,
            'no_mark': 0,
            'multiple_marks': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0
        }
        
        for topic in exam_structure['subjects']:
            results[topic['id']] = {}
            
            for section in topic['sections']:
                section_results = []
                
                for i in range(section['questionCount']):
                    q_num = stats['total'] + 1
                    coords = coordinates.get(q_num)
                    
                    if not coords:
                        logger.warning(f"Q{q_num}: No coordinates")
                        continue
                    
                    stats['total'] += 1
                    
                    # ADAPTIVE DETECTION
                    result = self._detect_single_question_adaptive(
                        prepared_images,
                        coords,
                        detection_strategy,
                        q_num
                    )
                    
                    # Update statistics
                    if result['answer']:
                        stats['detected'] += 1
                    else:
                        stats['no_mark'] += 1
                    
                    # Confidence statistics
                    if result['confidence'] >= 90:
                        stats['high_confidence'] += 1
                    elif result['confidence'] >= 70:
                        stats['medium_confidence'] += 1
                    else:
                        stats['low_confidence'] += 1
                        stats['uncertain'] += 1
                    
                    if result.get('warning') == 'MULTIPLE_MARKS':
                        stats['multiple_marks'] += 1
                    
                    section_results.append(result)
                
                results[topic['id']][section['id']] = section_results
        
        logger.info(f"✅ Adaptive detection complete:")
        logger.info(f"   Detected: {stats['detected']}/{stats['total']}")
        logger.info(f"   High confidence: {stats['high_confidence']}")
        logger.info(f"   Medium confidence: {stats['medium_confidence']}")
        logger.info(f"   Low confidence: {stats['low_confidence']}")
        
        return {
            'answers': results,
            'statistics': stats,
            'detection_strategy': detection_strategy,
            'image_quality': image_quality
        }
    
    def _assess_image_quality(self, image: np.ndarray) -> Dict:
        """
        Image quality'ni baholash
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 1. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(100, laplacian_var / 10)  # Normalize to 0-100
        
        # 2. Contrast (standard deviation)
        contrast_score = min(100, gray.std() / 2.55)  # Normalize to 0-100
        
        # 3. Brightness
        brightness = gray.mean()
        brightness_score = 100 - abs(brightness - 127) / 1.27  # Optimal around 127
        
        # 4. Noise level
        noise = cv2.fastNlMeansDenoising(gray)
        noise_diff = np.abs(gray.astype(float) - noise.astype(float)).mean()
        noise_score = max(0, 100 - noise_diff * 2)
        
        # 5. Overall score
        overall_score = (sharpness_score + contrast_score + brightness_score + noise_score) / 4
        
        # Quality category
        if overall_score >= 80:
            category = 'EXCELLENT'
        elif overall_score >= 60:
            category = 'GOOD'
        elif overall_score >= 40:
            category = 'FAIR'
        else:
            category = 'POOR'
        
        return {
            'overall_score': overall_score,
            'category': category,
            'sharpness': sharpness_score,
            'contrast': contrast_score,
            'brightness': brightness_score,
            'noise': noise_score,
            'brightness_value': brightness,
            'contrast_value': gray.std()
        }
    
    def _select_detection_strategy(self, image_quality: Dict) -> Dict:
        """
        Image quality'ga qarab optimal detection strategy tanlash
        """
        quality_score = image_quality.get('overall_score', image_quality.get('overall', 50.0))
        category = image_quality.get('category', 'FAIR')
        
        if category == 'EXCELLENT':
            # High quality - use precise methods
            return {
                'name': 'high_precision',
                'methods': ['darkness_analysis', 'contour_analysis'],
                'thresholds': {
                    'min_darkness': 30,
                    'min_difference': 15,
                    'multiple_marks_threshold': 10
                },
                'preprocessing': 'minimal'
            }
        
        elif category == 'GOOD':
            # Good quality - balanced approach
            return {
                'name': 'balanced',
                'methods': ['darkness_analysis', 'comparative_analysis'],
                'thresholds': {
                    'min_darkness': 25,
                    'min_difference': 12,
                    'multiple_marks_threshold': 8
                },
                'preprocessing': 'light_enhancement'
            }
        
        elif category == 'FAIR':
            # Fair quality - adaptive methods
            return {
                'name': 'adaptive',
                'methods': ['comparative_analysis', 'template_matching'],
                'thresholds': {
                    'min_darkness': 20,
                    'min_difference': 8,
                    'multiple_marks_threshold': 6
                },
                'preprocessing': 'moderate_enhancement'
            }
        
        else:  # POOR
            # Poor quality - aggressive methods
            return {
                'name': 'aggressive',
                'methods': ['comparative_analysis', 'edge_detection', 'template_matching'],
                'thresholds': {
                    'min_darkness': 15,
                    'min_difference': 5,
                    'multiple_marks_threshold': 4
                },
                'preprocessing': 'heavy_enhancement'
            }
    
    def _prepare_images_adaptive(self, image: np.ndarray, image_quality: Dict) -> Dict:
        """
        Image quality'ga qarab adaptive preprocessing
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        prepared = {
            'original': gray.copy(),
            'enhanced': None,
            'binary': None,
            'denoised': None
        }
        
        category = image_quality.get('category', 'FAIR')
        
        if category == 'EXCELLENT':
            # Minimal processing for high quality
            prepared['enhanced'] = gray.copy()
            
        elif category == 'GOOD':
            # Light enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            prepared['enhanced'] = clahe.apply(gray)
            
        elif category == 'FAIR':
            # Moderate enhancement
            # Denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Light sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            prepared['enhanced'] = sharpened
            prepared['denoised'] = denoised
            
        else:  # POOR
            # Heavy enhancement
            # Strong denoising
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            
            # Strong CLAHE
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            # Bilateral filter for smoothing
            bilateral = cv2.bilateralFilter(sharpened, 9, 75, 75)
            
            prepared['enhanced'] = bilateral
            prepared['denoised'] = denoised
        
        # Create binary image
        _, prepared['binary'] = cv2.threshold(
            prepared['enhanced'], 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        
        return prepared
    
    def _detect_single_question_adaptive(
        self,
        prepared_images: Dict,
        coords: Dict,
        strategy: Dict,
        question_num: int
    ) -> Dict:
        """
        Bitta savolni adaptive detection bilan aniqlash
        """
        bubbles = coords.get('bubbles', [])
        if not bubbles:
            return {
                'questionNumber': question_num,
                'answer': None,
                'confidence': 0,
                'warning': 'NO_COORDINATES'
            }
        
        # Multiple detection methods
        detection_results = []
        
        for method in strategy['methods']:
            if method == 'darkness_analysis':
                result = self._detect_by_darkness_analysis(
                    prepared_images, bubbles, strategy['thresholds']
                )
            elif method == 'contour_analysis':
                result = self._detect_by_contour_analysis(
                    prepared_images, bubbles, strategy['thresholds']
                )
            elif method == 'comparative_analysis':
                result = self._detect_by_comparative_analysis(
                    prepared_images, bubbles, strategy['thresholds']
                )
            elif method == 'template_matching':
                result = self._detect_by_template_matching(
                    prepared_images, bubbles, strategy['thresholds']
                )
            elif method == 'edge_detection':
                result = self._detect_by_edge_detection(
                    prepared_images, bubbles, strategy['thresholds']
                )
            else:
                continue
            
            if result:
                detection_results.append({
                    'method': method,
                    'result': result
                })
        
        # Combine results
        final_result = self._combine_detection_results(
            detection_results, question_num, strategy
        )
        
        return final_result
    
    def _detect_by_darkness_analysis(
        self, 
        images: Dict, 
        bubbles: List[Dict], 
        thresholds: Dict
    ) -> Optional[Dict]:
        """
        Darkness analysis method
        """
        image = images['enhanced']
        
        bubble_scores = []
        
        for bubble in bubbles:
            x, y = int(bubble['x']), int(bubble['y'])
            radius = int(bubble.get('radius', 8))
            
            # Extract ROI
            roi = self._extract_bubble_roi(image, x, y, radius)
            if roi is None:
                continue
            
            # Calculate darkness
            darkness = 255 - roi.mean()
            
            # Calculate fill percentage
            _, binary_roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            fill_percentage = (binary_roi > 0).sum() / binary_roi.size * 100
            
            bubble_scores.append({
                'variant': bubble['variant'],
                'darkness': darkness,
                'fill_percentage': fill_percentage,
                'score': darkness * (fill_percentage / 100)
            })
        
        if not bubble_scores:
            return None
        
        # Find best bubble
        best_bubble = max(bubble_scores, key=lambda b: b['score'])
        
        # Check thresholds
        if best_bubble['darkness'] < thresholds['min_darkness']:
            return None
        
        # Check for multiple marks
        sorted_bubbles = sorted(bubble_scores, key=lambda b: b['score'], reverse=True)
        if len(sorted_bubbles) > 1:
            difference = sorted_bubbles[0]['score'] - sorted_bubbles[1]['score']
            if difference < thresholds['min_difference']:
                return {
                    'answer': None,
                    'confidence': 30,
                    'warning': 'MULTIPLE_MARKS',
                    'scores': bubble_scores
                }
        
        # Calculate confidence
        confidence = min(100, best_bubble['score'] / 50 * 100)
        
        return {
            'answer': best_bubble['variant'],
            'confidence': confidence,
            'scores': bubble_scores,
            'method': 'darkness_analysis'
        }
    
    def _detect_by_comparative_analysis(
        self, 
        images: Dict, 
        bubbles: List[Dict], 
        thresholds: Dict
    ) -> Optional[Dict]:
        """
        Comparative analysis method - nisbiy taqqoslash
        """
        image = images['enhanced']
        
        bubble_scores = []
        
        for bubble in bubbles:
            x, y = int(bubble['x']), int(bubble['y'])
            radius = int(bubble.get('radius', 8))
            
            # Extract ROI
            roi = self._extract_bubble_roi(image, x, y, radius)
            if roi is None:
                continue
            
            # Multiple metrics
            darkness = 255 - roi.mean()
            std_dev = roi.std()
            
            # Edge density
            edges = cv2.Canny(roi, 50, 150)
            edge_density = (edges > 0).sum() / edges.size * 100
            
            # Combined score
            combined_score = darkness + (std_dev * 0.5) + (edge_density * 0.3)
            
            bubble_scores.append({
                'variant': bubble['variant'],
                'darkness': darkness,
                'std_dev': std_dev,
                'edge_density': edge_density,
                'combined_score': combined_score
            })
        
        if not bubble_scores:
            return None
        
        # Relative comparison
        scores = [b['combined_score'] for b in bubble_scores]
        max_score = max(scores)
        min_score = min(scores)
        
        if max_score - min_score < thresholds['min_difference']:
            return None  # No clear winner
        
        # Find best bubble
        best_bubble = max(bubble_scores, key=lambda b: b['combined_score'])
        
        # Calculate relative confidence
        score_range = max_score - min_score
        confidence = min(100, (score_range / 50) * 100)
        
        return {
            'answer': best_bubble['variant'],
            'confidence': confidence,
            'scores': bubble_scores,
            'method': 'comparative_analysis'
        }
    
    def _detect_by_contour_analysis(
        self, 
        images: Dict, 
        bubbles: List[Dict], 
        thresholds: Dict
    ) -> Optional[Dict]:
        """
        Contour analysis method
        """
        binary = images['binary']
        
        bubble_scores = []
        
        for bubble in bubbles:
            x, y = int(bubble['x']), int(bubble['y'])
            radius = int(bubble.get('radius', 8))
            
            # Extract ROI
            roi = self._extract_bubble_roi(binary, x, y, radius)
            if roi is None:
                continue
            
            # Find contours
            contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                bubble_scores.append({
                    'variant': bubble['variant'],
                    'contour_area': 0,
                    'fill_ratio': 0,
                    'score': 0
                })
                continue
            
            # Largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(largest_contour)
            
            # Fill ratio
            total_area = roi.shape[0] * roi.shape[1]
            fill_ratio = contour_area / total_area
            
            bubble_scores.append({
                'variant': bubble['variant'],
                'contour_area': contour_area,
                'fill_ratio': fill_ratio,
                'score': fill_ratio * 100
            })
        
        if not bubble_scores:
            return None
        
        # Find best bubble
        best_bubble = max(bubble_scores, key=lambda b: b['score'])
        
        if best_bubble['score'] < 20:  # Minimum fill threshold
            return None
        
        # Calculate confidence
        confidence = min(100, best_bubble['score'])
        
        return {
            'answer': best_bubble['variant'],
            'confidence': confidence,
            'scores': bubble_scores,
            'method': 'contour_analysis'
        }
    
    def _detect_by_template_matching(
        self, 
        images: Dict, 
        bubbles: List[Dict], 
        thresholds: Dict
    ) -> Optional[Dict]:
        """
        Template matching method
        """
        # Create filled bubble template
        template_size = 16
        template = np.zeros((template_size, template_size), dtype=np.uint8)
        cv2.circle(template, (template_size//2, template_size//2), template_size//3, 255, -1)
        
        image = images['enhanced']
        bubble_scores = []
        
        for bubble in bubbles:
            x, y = int(bubble['x']), int(bubble['y'])
            radius = int(bubble.get('radius', 8))
            
            # Extract ROI
            roi = self._extract_bubble_roi(image, x, y, radius)
            if roi is None:
                continue
            
            # Resize ROI to match template
            roi_resized = cv2.resize(roi, (template_size, template_size))
            
            # Template matching
            result = cv2.matchTemplate(roi_resized, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            bubble_scores.append({
                'variant': bubble['variant'],
                'match_score': max_val,
                'score': max_val * 100
            })
        
        if not bubble_scores:
            return None
        
        # Find best match
        best_bubble = max(bubble_scores, key=lambda b: b['score'])
        
        if best_bubble['score'] < 30:  # Minimum match threshold
            return None
        
        return {
            'answer': best_bubble['variant'],
            'confidence': best_bubble['score'],
            'scores': bubble_scores,
            'method': 'template_matching'
        }
    
    def _detect_by_edge_detection(
        self, 
        images: Dict, 
        bubbles: List[Dict], 
        thresholds: Dict
    ) -> Optional[Dict]:
        """
        Edge detection method
        """
        image = images['enhanced']
        
        bubble_scores = []
        
        for bubble in bubbles:
            x, y = int(bubble['x']), int(bubble['y'])
            radius = int(bubble.get('radius', 8))
            
            # Extract ROI
            roi = self._extract_bubble_roi(image, x, y, radius)
            if roi is None:
                continue
            
            # Edge detection
            edges = cv2.Canny(roi, 50, 150)
            
            # Edge density in center vs border
            h, w = roi.shape
            center_region = edges[h//4:3*h//4, w//4:3*w//4]
            border_region = edges.copy()
            border_region[h//4:3*h//4, w//4:3*w//4] = 0
            
            center_density = (center_region > 0).sum() / center_region.size * 100
            border_density = (border_region > 0).sum() / border_region.size * 100
            
            # Filled bubbles have more center edges, less border edges
            score = center_density - border_density
            
            bubble_scores.append({
                'variant': bubble['variant'],
                'center_density': center_density,
                'border_density': border_density,
                'score': max(0, score)
            })
        
        if not bubble_scores:
            return None
        
        # Find best bubble
        best_bubble = max(bubble_scores, key=lambda b: b['score'])
        
        if best_bubble['score'] < 5:  # Minimum edge threshold
            return None
        
        return {
            'answer': best_bubble['variant'],
            'confidence': min(100, best_bubble['score'] * 2),
            'scores': bubble_scores,
            'method': 'edge_detection'
        }
    
    def _extract_bubble_roi(
        self, 
        image: np.ndarray, 
        x: int, 
        y: int, 
        radius: int
    ) -> Optional[np.ndarray]:
        """
        Bubble ROI'ni extract qilish
        """
        h, w = image.shape[:2]
        
        # ROI boundaries
        x1 = max(0, x - radius)
        y1 = max(0, y - radius)
        x2 = min(w, x + radius)
        y2 = min(h, y + radius)
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return None
        
        return roi
    
    def _combine_detection_results(
        self, 
        detection_results: List[Dict], 
        question_num: int,
        strategy: Dict
    ) -> Dict:
        """
        Multiple detection natijalarini birlashtirish
        """
        if not detection_results:
            return {
                'questionNumber': question_num,
                'answer': None,
                'confidence': 0,
                'warning': 'NO_DETECTION'
            }
        
        # Collect all answers
        answers = {}
        total_confidence = 0
        
        for detection in detection_results:
            result = detection['result']
            if result and result.get('answer'):
                answer = result['answer']
                confidence = result.get('confidence', 0)
                
                if answer not in answers:
                    answers[answer] = []
                
                answers[answer].append({
                    'method': detection['method'],
                    'confidence': confidence
                })
                
                total_confidence += confidence
        
        if not answers:
            return {
                'questionNumber': question_num,
                'answer': None,
                'confidence': 0,
                'warning': 'NO_CLEAR_ANSWER',
                'detection_results': detection_results
            }
        
        # Find consensus answer
        best_answer = None
        best_score = 0
        
        for answer, detections in answers.items():
            # Calculate weighted score
            score = sum(d['confidence'] for d in detections)
            weight = len(detections)  # More methods = higher weight
            
            weighted_score = score * weight
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_answer = answer
        
        # Calculate final confidence
        if len(answers) == 1:
            # Single answer - high confidence
            final_confidence = min(100, best_score / len(detection_results))
        else:
            # Multiple answers - lower confidence
            final_confidence = min(80, best_score / (len(detection_results) * 2))
        
        # Check for conflicts
        warning = None
        if len(answers) > 1:
            warning = 'CONFLICTING_METHODS'
        
        return {
            'questionNumber': question_num,
            'answer': best_answer,
            'confidence': final_confidence,
            'warning': warning,
            'detection_methods': len(detection_results),
            'consensus_methods': len(answers.get(best_answer, [])),
            'all_answers': answers
        }