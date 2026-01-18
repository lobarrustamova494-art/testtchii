"""
Quick test for 5-imtihon image
Just check if we can read it and see the bubbles
"""
import cv2
import numpy as np
import json

# Load image
print("Loading image...")
img = cv2.imread('test_images/5-imtihon.jpg')
if img is None:
    print("ERROR: Cannot load image!")
    exit(1)

print(f"✅ Image loaded: {img.shape[1]}x{img.shape[0]} pixels")
print(f"   Mean brightness: {img.mean():.1f}")
print()

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply threshold to see bubbles
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

# Find contours (potential bubbles)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"Found {len(contours)} contours")

# Filter circular contours (bubbles)
bubbles = []
for contour in contours:
    area = cv2.contourArea(contour)
    if area < 50 or area > 500:  # Filter by size
        continue
    
    # Check circularity
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        continue
    
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    if circularity > 0.7:  # Circular enough
        x, y, w, h = cv2.boundingRect(contour)
        bubbles.append((x + w//2, y + h//2, w, h))

print(f"Found {len(bubbles)} potential bubbles")
print()

# Draw bubbles on image
output = img.copy()
for i, (x, y, w, h) in enumerate(bubbles[:100]):  # First 100
    cv2.circle(output, (x, y), max(w, h)//2, (0, 255, 0), 2)
    if i < 10:
        print(f"Bubble {i+1}: pos=({x}, {y}), size={w}x{h}")

# Save annotated image
cv2.imwrite('test_images/5-imtihon_quick_test.jpg', output)
print()
print(f"✅ Saved annotated image: test_images/5-imtihon_quick_test.jpg")
print()

# Load answer key
print("Loading answer key...")
with open('test_images/5-imtihon-data.json', 'r') as f:
    data = json.load(f)

answer_key = data['answerKey']
print(f"✅ Loaded {len(answer_key)} answers")
print()

# Show first 10 answers
print("First 10 correct answers:")
for i in range(1, 11):
    print(f"  Q{i}: {answer_key[str(i)]}")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Image: 1920x2560 pixels")
print(f"Bubbles found: {len(bubbles)}")
print(f"Expected: 40 questions x 5 options = 200 bubbles")
print(f"Answer key: 40 questions (A-B-C-D-E pattern)")
print()

if len(bubbles) < 150:
    print("⚠️  WARNING: Too few bubbles detected!")
    print("   Possible issues:")
    print("   - Image quality too low")
    print("   - Threshold settings need adjustment")
    print("   - Image not properly scanned")
else:
    print("✅ Bubble count looks reasonable")

print()
print("Next steps:")
print("1. Check test_images/5-imtihon_quick_test.jpg")
print("2. Verify bubbles are detected correctly")
print("3. Adjust threshold if needed")
print("4. Run full test")
