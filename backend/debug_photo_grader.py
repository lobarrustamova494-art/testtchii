"""
Debug photo grader issue
"""
import json
from services.photo_omr_service import PhotoOMRService
from services.grader import AnswerGrader

print("=" * 80)
print("DEBUG PHOTO GRADER ISSUE")
print("=" * 80)
print()

# Load test data
with open('test_images/5-imtihon-data.json', 'r') as f:
    test_data = json.load(f)

answer_key = test_data['answerKey']

# Exam structure
exam_structure = {
    'subjects': [
        {
            'id': 'subject-1',
            'name': 'Test Subject',
            'sections': [
                {
                    'id': 'section-1',
                    'name': 'Test Section',
                    'questionCount': 40,
                    'correctScore': 1,
                    'wrongScore': 0
                }
            ]
        }
    ]
}

# Create service
service = PhotoOMRService()

print("Processing photo...")
results = service.process_photo(
    'test_images/5-imtihon.jpg',
    exam_structure,
    answer_key
)

print("Results structure:")
print(f"  Keys: {list(results.keys())}")
print()

omr_results = results['omr_results']
print("OMR Results structure:")
print(f"  Keys: {list(omr_results.keys())}")
print()

answers = omr_results['answers']
print("Answers structure:")
print(f"  Keys: {list(answers.keys())}")
print()

subject_answers = answers['subject-1']
print("Subject answers structure:")
print(f"  Keys: {list(subject_answers.keys())}")
print()

section_answers = subject_answers['section-1']
print(f"Section answers count: {len(section_answers)}")
print()

print("First 5 answers:")
for i, answer in enumerate(section_answers[:5]):
    print(f"  Q{answer['questionNumber']}: {answer['answer']} (conf: {answer['confidence']})")

print()
print("=" * 80)
print("TESTING GRADER DIRECTLY")
print("=" * 80)

# Test grader directly
grader = AnswerGrader(answer_key, exam_structure)
grading_results = grader.grade(answers)

print("Grading results:")
print(f"  Total Questions: {grading_results['totalQuestions']}")
print(f"  Correct: {grading_results['correctAnswers']}")
print(f"  Incorrect: {grading_results['incorrectAnswers']}")
print(f"  Unanswered: {grading_results['unanswered']}")
print(f"  Score: {grading_results['totalScore']}/{grading_results['maxScore']}")
print(f"  Percentage: {grading_results['percentage']:.1f}%")

print()
print("=" * 80)