"""
Debug annotation issues
"""
import cv2
import numpy as np
import json
import sys

def debug_annotation(image_path: str, grading_results_path: str, coordinates_path: str):
    """
    Annotatsiya muammolarini debug qilish
    """
    print("=" * 60)
    print("ANNOTATION DEBUG TOOL")
    print("=" * 60)
    
    # Load data
    with open(grading_results_path, 'r', encoding='utf-8') as f:
        grading_results = json.load(f)
    
    with open(coordinates_path, 'r', encoding='utf-8') as f:
        coordinates = json.load(f)
    
    # Load image
    image = cv2.imread(image_path)
    if len(image.shape) == 2:
        annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        annotated = image.copy()
    
    print(f"\nImage size: {image.shape[1]}x{image.shape[0]}")
    print(f"Total questions in coordinates: {len(coordinates)}")
    
    # Process each question
    question_count = 0
    for topic_data in grading_results.get('topicResults', []):
        for section_data in topic_data.get('sections', []):
            for question in section_data.get('questions', []):
                q_num = question['questionNumber']
                correct_answer = question.get('correctAnswer')
                student_answer = question.get('studentAnswer')
                is_correct = question.get('isCorrect', False)
                
                if str(q_num) not in coordinates:
                    print(f"⚠️  Q{q_num}: Coordinates not found!")
                    continue
                
                coords = coordinates[str(q_num)]
                bubbles = coords['bubbles']
                
                question_count += 1
                
                # Print debug info for first 10 questions
                if question_count <= 10:
                    print(f"\nQ{q_num}:")
                    print(f"  Correct: {correct_answer}, Student: {student_answer}, IsCorrect: {is_correct}")
                    print(f"  Bubbles:")
                    for bubble in bubbles:
                        x, y, r = int(bubble['x']), int(bubble['y']), int(bubble['radius'])
                        print(f"    {bubble['variant']}: X={x}px, Y={y}px, R={r}px")
                
                # Draw annotations
                for bubble in bubbles:
                    variant = bubble['variant']
                    x = int(round(bubble['x']))
                    y = int(round(bubble['y']))
                    radius = int(round(bubble['radius']))
                    
                    padding = 3
                    thickness = 2
                    
                    x1 = x - radius - padding
                    y1 = y - radius - padding
                    x2 = x + radius + padding
                    y2 = y + radius + padding
                    
                    # Draw correct answer (GREEN)
                    if variant == correct_answer:
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), thickness)
                        # Add label
                        cv2.putText(annotated, f"Q{q_num}-{variant}", (x1, y1-5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
                    
                    # Draw student answer
                    if variant == student_answer:
                        if is_correct:
                            # BLUE
                            cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 128, 0), thickness)
                        else:
                            # RED
                            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                    
                    # Draw center dot for reference
                    cv2.circle(annotated, (x, y), 1, (255, 0, 255), -1)
    
    print(f"\nTotal questions annotated: {question_count}")
    
    # Save debug image
    output_path = 'debug_annotation.jpg'
    cv2.imwrite(output_path, annotated)
    print(f"\nDebug image saved: {output_path}")
    print("Check this image to see annotation alignment!")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python debug_annotation.py <image> <grading_results.json> <coordinates.json>")
        sys.exit(1)
    
    debug_annotation(sys.argv[1], sys.argv[2], sys.argv[3])
