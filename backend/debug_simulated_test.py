"""
Debug simulated test - see what OMR detector finds
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.image_processor import ImageProcessor
from services.omr_detector import OMRDetector
from utils.coordinate_mapper import CoordinateMapper
from config import settings

print("=" * 80)
print("DEBUG SIMULATED TEST")
print("=" * 80)
print()

# Load answer key
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

# Process image
print("1. Processing image...")
processor = ImageProcessor(
    target_width=settings.TARGET_WIDTH,
    target_height=settings.TARGET_HEIGHT
)

result = processor.process('test_images/5-imtihon-simulated.jpg')
print(f"✅ Processed: {result['processed'].shape[1]}x{result['processed'].shape[0]}")
print()

# Generate coordinates
print("2. Generating coordinates...")
mapper = CoordinateMapper(
    image_width=result['processed'].shape[1],
    image_height=result['processed'].shape[0],
    exam_structure=exam_structure,
    qr_layout=None
)

coordinates = mapper.calculate_all()
print(f"✅ Generated {len(coordinates)} question coordinates")
print()

# OMR Detection
print("3. OMR Detection...")
detector = OMRDetector(
    bubble_radius=settings.BUBBLE_RADIUS,
    min_darkness=settings.MIN_DARKNESS,
    min_difference=settings.MIN_DIFFERENCE,
    multiple_marks_threshold=settings.MULTIPLE_MARKS_THRESHOLD
)

omr_results = detector.detect_all_answers(
    result['grayscale'],
    coordinates,
    exam_structure
)

print(f"✅ OMR completed")
print(f"   Total: {omr_results['statistics']['total']}")
print(f"   Detected: {omr_results['statistics']['detected']}")
print(f"   No marks: {omr_results['statistics']['no_mark']}")
print()

# Show detailed results
print("4. Detailed OMR Results:")
print("-" * 80)
print(f"{'Q#':<4} {'Correct':<8} {'Detected':<8} {'Match':<6} {'Confidence':<12} {'Debug Scores'}")
print("-" * 80)

correct_count = 0
incorrect_count = 0
no_mark_count = 0

# Navigate through nested structure
for topic_id, topic_data in omr_results['answers'].items():
    for section_id, section_data in topic_data.items():
        for answer_data in section_data:
            q_num = answer_data['questionNumber']
            detected = answer_data['answer'] or 'NONE'
            correct = answer_key[str(q_num)]
            confidence = answer_data['confidence']
            debug_scores = answer_data.get('debugScores', '')
            
            match = "✅" if detected == correct else ("⚪" if detected == 'NONE' else "❌")
            
            if detected == correct:
                correct_count += 1
            elif detected == 'NONE':
                no_mark_count += 1
            else:
                incorrect_count += 1
            
            print(f"{q_num:<4} {correct:<8} {detected:<8} {match:<6} {confidence:<12.1f} {debug_scores}")

print("-" * 80)
print()

# Summary
total = correct_count + incorrect_count + no_mark_count
accuracy = (correct_count / total * 100) if total > 0 else 0

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Questions: {total}")
print(f"Correct: {correct_count}")
print(f"Incorrect: {incorrect_count}")
print(f"No Mark: {no_mark_count}")
print(f"")
print(f"ACCURACY: {accuracy:.1f}%")
print()

if accuracy == 100.0:
    print("🎉 PERFECT! 100% ACCURACY!")
elif accuracy >= 95.0:
    print("✅ EXCELLENT! 95%+ accuracy")
elif accuracy >= 90.0:
    print("✅ GOOD! 90%+ accuracy")
else:
    print("❌ NEEDS IMPROVEMENT")
    print()
    print("Issues:")
    if no_mark_count > 5:
        print(f"  - Too many no marks: {no_mark_count}")
        print("  - Check MIN_DARKNESS threshold")
        print("  - Check coordinate accuracy")
    if incorrect_count > 5:
        print(f"  - Too many incorrect: {incorrect_count}")
        print("  - Check bubble detection algorithm")

print()
print("=" * 80)
