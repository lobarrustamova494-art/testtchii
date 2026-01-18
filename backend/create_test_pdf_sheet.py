"""
Create a PDF-generated test sheet with known answers
Then we can test the system with 100% accuracy
"""
import sys
import os

print("=" * 80)
print("CREATE PDF TEST SHEET")
print("=" * 80)
print()

print("To create a PDF test sheet:")
print("1. Open the frontend: http://localhost:5173")
print("2. Login (admin/admin)")
print("3. Create a new exam:")
print("   - Name: 5-Imtihon Test")
print("   - 1 Subject, 1 Section")
print("   - 40 questions")
print("4. Download the PDF")
print("5. Print it")
print("6. Fill in answers according to the pattern:")
print("   Q1-5: A,B,C,D,E")
print("   Q6-10: A,B,C,D,E")
print("   ... (repeating pattern)")
print("7. Scan at 300 DPI")
print("8. Save as 'test_images/5-imtihon-pdf-generated.jpg'")
print("9. Run test_5imtihon_complete.py with the new image")
print()

print("Alternatively, we can test with the current photo image")
print("but we need to manually map the coordinates.")
print()

print("=" * 80)
print()

print("For now, let's create a SIMULATED test with perfect coordinates")
print("to verify the OMR detection algorithm works correctly.")
print()

# Create a simple test image with known bubble positions
import cv2
import numpy as np

print("Creating simulated test image...")

# Create blank A4 image (2480x3508 at 300 DPI)
width = 2480
height = 3508
img = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background

# Draw corner markers (15mm x 15mm at 5mm margin)
px_per_mm = width / 210  # 11.81 px/mm
corner_size = int(15 * px_per_mm)  # 177 px
margin = int(5 * px_per_mm)  # 59 px

# Top-left
cv2.rectangle(img, (margin, margin), (margin + corner_size, margin + corner_size), (0, 0, 0), -1)

# Top-right
cv2.rectangle(img, (width - margin - corner_size, margin), (width - margin, margin + corner_size), (0, 0, 0), -1)

# Bottom-left
cv2.rectangle(img, (margin, height - margin - corner_size), (margin + corner_size, height - margin), (0, 0, 0), -1)

# Bottom-right
cv2.rectangle(img, (width - margin - corner_size, height - margin - corner_size), (width - margin, height - margin), (0, 0, 0), -1)

print("✅ Corner markers drawn")

# Draw answer grid (40 questions, 2 per row)
grid_start_x_mm = 25
grid_start_y_mm = 149
bubble_radius_mm = 2.5
bubble_spacing_mm = 8
first_bubble_offset_mm = 8
question_spacing_mm = 90
row_height_mm = 5.5

# Convert to pixels
grid_start_x = int(grid_start_x_mm * px_per_mm)
grid_start_y = int(grid_start_y_mm * px_per_mm)
bubble_radius = int(bubble_radius_mm * px_per_mm)
bubble_spacing = int(bubble_spacing_mm * px_per_mm)
first_bubble_offset = int(first_bubble_offset_mm * px_per_mm)
question_spacing = int(question_spacing_mm * px_per_mm)
row_height = int(row_height_mm * px_per_mm)

# Answer key (A-B-C-D-E repeating)
answer_key = {}
for i in range(1, 41):
    answer_key[i] = ['A', 'B', 'C', 'D', 'E'][(i - 1) % 5]

print(f"✅ Answer key: {answer_key}")

# Draw questions
question_num = 1
for row in range(20):  # 20 rows
    for col in range(2):  # 2 questions per row
        if question_num > 40:
            break
        
        # Calculate position
        q_x = grid_start_x + (col * question_spacing)
        q_y = grid_start_y + (row * row_height) + int(2 * px_per_mm)  # +2mm offset
        
        # Draw question number
        cv2.putText(img, f"{question_num}.", (q_x - 20, q_y + 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Draw bubbles
        variants = ['A', 'B', 'C', 'D', 'E']
        correct_answer = answer_key[question_num]
        
        for v_idx, variant in enumerate(variants):
            bubble_x = q_x + first_bubble_offset + (v_idx * bubble_spacing)
            bubble_y = q_y
            
            # Draw bubble circle
            cv2.circle(img, (bubble_x, bubble_y), bubble_radius, (0, 0, 0), 2)
            
            # Fill if correct answer
            if variant == correct_answer:
                cv2.circle(img, (bubble_x, bubble_y), bubble_radius - 2, (0, 0, 0), -1)
        
        question_num += 1

print(f"✅ Drew {question_num - 1} questions with filled answers")

# Save image
output_path = 'test_images/5-imtihon-simulated.jpg'
cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])

print(f"✅ Saved: {output_path}")
print()

print("=" * 80)
print("SIMULATED TEST IMAGE CREATED")
print("=" * 80)
print(f"Image: {output_path}")
print(f"Size: {width}x{height} (A4 @ 300 DPI)")
print(f"Questions: 40")
print(f"Answers: A-B-C-D-E repeating pattern")
print(f"Corner markers: 4/4")
print()
print("Next step: Run test_5imtihon_complete.py with this image")
print("Expected result: 100% accuracy")
print()
print("=" * 80)
