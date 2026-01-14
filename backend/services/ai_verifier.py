"""
AI-Powered Answer Verification using Groq LLaMA 3
Verifies uncertain OMR detections with vision AI
"""
from groq import Groq
import base64
import json
import logging
from typing import Dict, List, Optional
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class AIVerifier:
    """
    Groq AI yordamida shubhali javoblarni tekshirish
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.2-90b-vision-preview",
        temperature: float = 0.1,
        max_tokens: int = 200
    ):
        if not api_key:
            raise ValueError("Groq API key is required")
            
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    def verify_uncertain_answers(
        self,
        image: np.ndarray,
        omr_results: Dict,
        coordinates: Dict,
        confidence_threshold: float = 70.0,
        max_verifications: int = 20
    ) -> Dict:
        """
        Past ishonchli javoblarni AI bilan tekshirish
        
        Args:
            image: Grayscale image
            omr_results: OMR detection results
            coordinates: Question coordinates
            confidence_threshold: Minimum confidence for AI verification
            max_verifications: Maximum number of questions to verify
            
        Returns:
            dict: Updated results with AI verifications
        """
        logger.info("Starting AI verification...")
        
        uncertain_questions = []
        verified_results = omr_results.copy()
        
        # Find uncertain questions
        for topic_id, topic_data in omr_results['answers'].items():
            for section_id, section_data in topic_data.items():
                for answer in section_data:
                    if (answer['confidence'] < confidence_threshold or 
                        answer['warning'] in ['MULTIPLE_MARKS', 'LOW_CONFIDENCE', 'NO_MARK']):
                        uncertain_questions.append(answer)
        
        logger.info(f"Found {len(uncertain_questions)} uncertain answers")
        
        if not uncertain_questions:
            logger.info("No uncertain answers to verify")
            return verified_results
        
        # Limit verifications (API cost control)
        questions_to_verify = uncertain_questions[:max_verifications]
        logger.info(f"Verifying {len(questions_to_verify)} answers with AI...")
        
        # AI verification (batch processing)
        verified_count = 0
        corrected_count = 0
        
        for question in questions_to_verify:
            try:
                ai_result = self.verify_single_question(
                    image,
                    question,
                    coordinates[question['questionNumber']]
                )
                
                if ai_result['success']:
                    # Update answer with AI result
                    self._update_answer(
                        verified_results,
                        question['questionNumber'],
                        ai_result
                    )
                    verified_count += 1
                    
                    if ai_result.get('changed'):
                        corrected_count += 1
                        logger.info(
                            f"Q{question['questionNumber']}: "
                            f"OMR={question['answer']} → AI={ai_result['answer']} "
                            f"(confidence: {ai_result['confidence']}%)"
                        )
                    
            except Exception as e:
                logger.error(f"AI verification failed for Q{question['questionNumber']}: {e}")
        
        logger.info(
            f"AI verification complete: {verified_count} verified, "
            f"{corrected_count} corrected"
        )
        
        return verified_results
    
    def verify_single_question(
        self,
        image: np.ndarray,
        question_data: Dict,
        coords: Dict
    ) -> Dict:
        """
        Bitta savolni AI bilan tekshirish
        """
        # Extract question region
        crop = self._extract_question_region(image, coords)
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Create AI prompt
        prompt = self._create_verification_prompt(question_data, coords)
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse AI response
            ai_answer = response.choices[0].message.content.strip()
            
            return self._parse_ai_response(ai_answer, question_data)
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_question_region(
        self,
        image: np.ndarray,
        coords: Dict
    ) -> np.ndarray:
        """
        Savol hududini kesib olish
        """
        bubbles = coords['bubbles']
        
        # Find bounding box for all bubbles
        xs = [b['x'] for b in bubbles]
        ys = [b['y'] for b in bubbles]
        
        padding = 50
        x1 = int(max(0, min(xs) - padding))
        y1 = int(max(0, min(ys) - padding))
        x2 = int(min(image.shape[1], max(xs) + padding))
        y2 = int(min(image.shape[0], max(ys) + padding))
        
        crop = image[y1:y2, x1:x2]
        
        # Enhance crop for better AI recognition
        crop = cv2.equalizeHist(crop)
        
        return crop
    
    def _create_verification_prompt(
        self,
        question_data: Dict,
        coords: Dict
    ) -> str:
        """
        AI uchun prompt yaratish
        """
        variants = [b['variant'] for b in coords['bubbles']]
        
        prompt = f"""You are an expert OMR (Optical Mark Recognition) system analyzing answer sheets.

**Question {question_data['questionNumber']}**

Available variants: {', '.join(variants)}

Current OMR detection:
- Answer: {question_data['answer'] or 'No answer detected'}
- Confidence: {question_data['confidence']}%
- Warning: {question_data['warning'] or 'None'}

**Your Task:**
Analyze the image and determine which ONE bubble (circle) is filled/marked with pen or pencil.

**Rules:**
1. Look for the DARKEST bubble
2. Ignore light marks, scratches, smudges, or stray marks
3. If multiple bubbles are marked, choose the DARKEST one
4. If no bubble is clearly marked, respond with "NONE"
5. Be decisive - choose the most likely answer

**Response Format (EXACTLY):**
ANSWER: [A/B/C/D/E/NONE]
CONFIDENCE: [0-100]
REASON: [brief explanation in one sentence]

**Example:**
ANSWER: B
CONFIDENCE: 95
REASON: Bubble B is completely filled with dark pen, other bubbles are empty.

Now analyze the image and respond:"""
        
        return prompt
    
    def _parse_ai_response(
        self,
        ai_response: str,
        original_data: Dict
    ) -> Dict:
        """
        AI javobini parse qilish
        """
        try:
            lines = [line.strip() for line in ai_response.strip().split('\n') if line.strip()]
            result = {'success': True}
            
            for line in lines:
                if line.startswith('ANSWER:'):
                    answer = line.split(':', 1)[1].strip()
                    result['answer'] = answer if answer != 'NONE' else None
                    
                elif line.startswith('CONFIDENCE:'):
                    confidence_str = line.split(':', 1)[1].strip()
                    # Extract number from string
                    confidence = int(''.join(filter(str.isdigit, confidence_str)))
                    result['confidence'] = min(100, max(0, confidence))
                    
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()
                    result['reason'] = reason
            
            # Check if AI changed the answer
            if result.get('answer') != original_data['answer']:
                result['changed'] = True
                result['original_answer'] = original_data['answer']
                result['original_confidence'] = original_data['confidence']
            else:
                result['changed'] = False
            
            # Validate result
            if 'answer' not in result or 'confidence' not in result:
                raise ValueError("Incomplete AI response")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.error(f"AI response was: {ai_response}")
            return {'success': False, 'error': f'Parse error: {str(e)}'}
    
    def _update_answer(
        self,
        results: Dict,
        question_number: int,
        ai_result: Dict
    ):
        """
        AI natijasini results ga qo'llash
        """
        # Find and update the question
        for topic_data in results['answers'].values():
            for section_data in topic_data.values():
                for answer in section_data:
                    if answer['questionNumber'] == question_number:
                        # Store original OMR result
                        answer['omr_answer'] = answer['answer']
                        answer['omr_confidence'] = answer['confidence']
                        
                        # Update with AI result
                        answer['answer'] = ai_result['answer']
                        answer['confidence'] = ai_result['confidence']
                        answer['ai_verified'] = True
                        answer['ai_reason'] = ai_result.get('reason', '')
                        
                        if ai_result.get('changed'):
                            answer['warning'] = 'AI_CORRECTED'
                        else:
                            answer['warning'] = 'AI_CONFIRMED'
                        
                        return
        
        logger.warning(f"Question {question_number} not found in results")
