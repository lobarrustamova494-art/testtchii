"""
Answer Grading Service
Calculates scores and generates detailed results
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class AnswerGrader:
    """
    Javoblarni tekshirish va ball hisoblash
    """
    
    def __init__(self, answer_key: Dict, exam_structure: Dict):
        self.answer_key = answer_key
        self.exam_structure = exam_structure
        
    def grade(self, detected_answers: Dict) -> Dict:
        """
        Barcha javoblarni tekshirish va ball hisoblash
        """
        logger.info("Starting grading...")
        
        results = {
            'totalQuestions': 0,
            'answeredQuestions': 0,
            'correctAnswers': 0,
            'incorrectAnswers': 0,
            'unanswered': 0,
            'lowConfidence': 0,
            'aiVerified': 0,
            'aiCorrected': 0,
            'warnings': 0,
            'totalScore': 0,
            'maxScore': 0,
            'percentage': 0.0,
            'grade': {'numeric': 2, 'text': 'Qoniqarsiz'},
            'topicResults': [],
            'detailedResults': []
        }
        
        for topic in self.exam_structure['subjects']:
            topic_result = {
                'topicId': topic['id'],
                'topicName': topic['name'],
                'correct': 0,
                'incorrect': 0,
                'unanswered': 0,
                'score': 0,
                'maxScore': 0,
                'sections': []
            }
            
            for section in topic['sections']:
                section_result = {
                    'sectionId': section['id'],
                    'sectionName': section['name'],
                    'correct': 0,
                    'incorrect': 0,
                    'unanswered': 0,
                    'score': 0,
                    'maxScore': section['questionCount'] * section['correctScore'],
                    'questions': []
                }
                
                section_answers = detected_answers.get(topic['id'], {}).get(section['id'], [])
                
                for answer in section_answers:
                    q_num = answer['questionNumber']
                    student_answer = answer['answer']
                    correct_answer = self.answer_key.get(str(q_num), 'A')
                    
                    results['totalQuestions'] += 1
                    
                    question_result = {
                        'questionNumber': q_num,
                        'studentAnswer': student_answer,
                        'correctAnswer': correct_answer,
                        'isCorrect': False,
                        'pointsEarned': 0,
                        'confidence': answer['confidence'],
                        'warning': answer.get('warning'),
                        'aiVerified': answer.get('ai_verified', False),
                        'aiReason': answer.get('ai_reason', ''),
                        'allScores': answer.get('allScores', []),
                        'debugScores': answer.get('debugScores', '')
                    }
                    
                    # AI statistics
                    if answer.get('ai_verified'):
                        results['aiVerified'] += 1
                        if answer.get('warning') == 'AI_CORRECTED':
                            results['aiCorrected'] += 1
                            question_result['omrAnswer'] = answer.get('omr_answer')
                    
                    # Grade the answer
                    if not student_answer:
                        results['unanswered'] += 1
                        section_result['unanswered'] += 1
                        question_result['pointsEarned'] = 0
                    elif student_answer == correct_answer:
                        results['correctAnswers'] += 1
                        results['answeredQuestions'] += 1
                        section_result['correct'] += 1
                        question_result['isCorrect'] = True
                        question_result['pointsEarned'] = section['correctScore']
                        section_result['score'] += section['correctScore']
                    else:
                        results['incorrectAnswers'] += 1
                        results['answeredQuestions'] += 1
                        section_result['incorrect'] += 1
                        question_result['isCorrect'] = False
                        question_result['pointsEarned'] = section['wrongScore']
                        section_result['score'] += section['wrongScore']
                    
                    # Statistics
                    if answer['confidence'] < 70:
                        results['lowConfidence'] += 1
                    
                    if answer.get('warning'):
                        results['warnings'] += 1
                    
                    section_result['questions'].append(question_result)
                    results['detailedResults'].append(question_result)
                
                topic_result['score'] += section_result['score']
                topic_result['maxScore'] += section_result['maxScore']
                topic_result['correct'] += section_result['correct']
                topic_result['incorrect'] += section_result['incorrect']
                topic_result['unanswered'] += section_result['unanswered']
                topic_result['sections'].append(section_result)
            
            results['totalScore'] += topic_result['score']
            results['maxScore'] += topic_result['maxScore']
            results['topicResults'].append(topic_result)
        
        # Calculate percentage and grade
        if results['maxScore'] > 0:
            results['percentage'] = round(
                (results['totalScore'] / results['maxScore']) * 100, 2
            )
        else:
            results['percentage'] = 0.0
        
        results['grade'] = self._calculate_grade(results['percentage'])
        
        logger.info(
            f"Grading complete: {results['correctAnswers']}/{results['totalQuestions']} correct, "
            f"Score: {results['totalScore']}/{results['maxScore']} ({results['percentage']}%), "
            f"Grade: {results['grade']['text']}"
        )
        
        if results['aiVerified'] > 0:
            logger.info(
                f"AI Statistics: {results['aiVerified']} verified, "
                f"{results['aiCorrected']} corrected"
            )
        
        return results
    
    def _calculate_grade(self, percentage: float) -> Dict:
        """
        Foizdan bahoga o'tkazish
        """
        if percentage >= 86:
            return {'numeric': 5, 'text': "A'lo"}
        elif percentage >= 71:
            return {'numeric': 4, 'text': "Yaxshi"}
        elif percentage >= 56:
            return {'numeric': 3, 'text': "Qoniqarli"}
        else:
            return {'numeric': 2, 'text': "Qoniqarsiz"}
