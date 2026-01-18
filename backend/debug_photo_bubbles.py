"""
Debug photo bubble darkness values
"""
import cv2
import numpy as np
import json

print("=" * 80)
print("DEBUG PHOTO BUBBLE DARKNESS")
print("=" * 80)
print()

# Load image
image = cv2.imread('test_images/5-imtihon.jpg', cv2.IMREAD_GRAYSCALE)
print(f"Image loaded: {image.shape[1]}x{image.shape[0]}")
print()

# Load answer key
with open('test_images/5-imtihon-data.json', 'r') as f:
    data = json.load(f)

answer_key = data['answerKey']
print(f"Answer key loaded: {len(answer_key)} questions")
print()

# Detect bubbles
from services.photo_omr_service import PhotoOMRService

service = PhotoOMRService()

print("Detecting bubbles...")
bubbles = service.detect_bubbles_automatically(image, expected_count=200)
print(f"Found {len(bubbles)} bubbles")
print()

print("Mapping to questions...")
coordinates = service.map_bubbles_to_questions(bubbles, total_questions=40)
print(f"Mapped {len(coordinates)} questions")
print()

# Analyze first 5 questions
print("=" * 80)
print("ANALYZING FIRST 5 QUESTIONS")
print("=" * 80)
print()

for q_num in range(1, 6):
    if q_num not in coordinates:
        print(f"Q{q_num}: NOT MAPPED")
        continue
    
    coords = coordinates[q_num]
    correct_answer = answer_key[str(q_num)]
    
    print(f"Q{q_num}: Correct answer = {correct_answer}")
    print("-" * 80)
    
    for bubble in coords['bubbles']:
        variant = bubble['variant']
        x, y = int(bubble['x']), int(bubble['y'])
        radius = int(bubble['radius'])
        
        # Extract ROI
        roi_radius = int(radius * 1.2)
        x1 = max(0, x - roi_radius)
        y1 = max(0, y - roi_radius)
        x2 = min(image.shape[1], x + roi_radius)
        y2 = min(image.shape[0], y + roi_radius)
        
        roi = image[y1:y2, x1:x2]
        
        # Create mask
        center_x = x - x1
        center_y = y - y1
        mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        
        pixels = roi[mask > 0]
        
        if len(pixels) == 0:
            print(f"  {variant}: NO PIXELS")
            continue
        
        # Calculate darkness
        mean_brightness = np.mean(pixels)
        darkness = (255 - mean_brightness) / 255 * 100
        
        # Calculate coverage (OTSU)
        _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        dark_pixels = np.sum(binary[mask > 0] > 0)
        coverage = dark_pixels / len(pixels) * 100
        
        # Score
        score = darkness * 0.6 + coverage * 0.4
        
        marker = "✅" if variant == correct_answer else "  "
        print(f"  {marker} {variant}: darkness={darkness:.1f}%, coverage={coverage:.1f}%, score={score:.1f}")
    
    print()

print("=" * 80)
print("THRESHOLD ANALYSIS")
print("=" * 80)
print()

# Collect all scores
all_scores = []
filled_scores = []
empty_scores = []

for q_num in range(1, min(41, len(coordinates) + 1)):
    if q_num not in coordinates:
        continue
    
    coords = coordinates[q_num]
    correct_answer = answer_key[str(q_num)]
    
    for bubble in coords['bubbles']:
        variant = bubble['variant']
        x, y = int(bubble['x']), int(bubble['y'])
        radius = int(bubble['radius'])
        
        # Extract ROI
        roi_radius = int(radius * 1.2)
        x1 = max(0, x - roi_radius)
        y1 = max(0, y - roi_radius)
        x2 = min(image.shape[1], x + roi_radius)
        y2 = min(image.shape[0], y + roi_radius)
        
        roi = image[y1:y2, x1:x2]
        
        # Create mask
        center_x = x - x1
        center_y = y - y1
        mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        
        pixels = roi[mask > 0]
        
        if len(pixels) == 0:
            continue
        
        # Calculate darkness
        mean_brightness = np.mean(pixels)
        darkness = (255 - mean_brightness) / 255 * 100
        
        # Calculate coverage
        _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        dark_pixels = np.sum(binary[mask > 0] > 0)
        coverage = dark_pixels / len(pixels) * 100
        
        # Score
        score = darkness * 0.6 + coverage * 0.4
        
        all_scores.append(score)
        
        if variant == correct_answer:
            filled_scores.append(score)
        else:
            empty_scores.append(score)

print(f"Total bubbles analyzed: {len(all_scores)}")
print(f"Filled bubbles: {len(filled_scores)}")
print(f"Empty bubbles: {len(empty_scores)}")
print()

if filled_scores:
    print("FILLED BUBBLES (should be detected):")
    print(f"  Min: {min(filled_scores):.1f}")
    print(f"  Max: {max(filled_scores):.1f}")
    print(f"  Mean: {np.mean(filled_scores):.1f}")
    print(f"  Median: {np.median(filled_scores):.1f}")
    print()

if empty_scores:
    print("EMPTY BUBBLES (should NOT be detected):")
    print(f"  Min: {min(empty_scores):.1f}")
    print(f"  Max: {max(empty_scores):.1f}")
    print(f"  Mean: {np.mean(empty_scores):.1f}")
    print(f"  Median: {np.median(empty_scores):.1f}")
    print()

if filled_scores and empty_scores:
    # Find optimal threshold
    filled_min = min(filled_scores)
    empty_max = max(empty_scores)
    
    print("THRESHOLD RECOMMENDATION:")
    print(f"  Filled min: {filled_min:.1f}")
    print(f"  Empty max: {empty_max:.1f}")
    
    if filled_min > empty_max:
        optimal = (filled_min + empty_max) / 2
        print(f"  ✅ OPTIMAL THRESHOLD: {optimal:.1f}")
        print(f"     (Perfect separation possible)")
    else:
        print(f"  ⚠️  OVERLAP DETECTED!")
        print(f"     Gap: {empty_max - filled_min:.1f}")
        print(f"     Suggested threshold: {filled_min * 0.9:.1f}")
        print(f"     (Will have some false positives)")

print()
print("=" * 80)
