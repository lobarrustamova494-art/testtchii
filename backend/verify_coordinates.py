"""
Verify coordinate calculation matches PDF generator
"""

# Simulate both PDF and backend coordinate calculation

print("=" * 60)
print("COORDINATE VERIFICATION")
print("=" * 60)

# Constants
grid_start_y_mm = 149
row_height_mm = 5.5
questions_per_row = 2

# Simulate 35 questions in one section
section_question_count = 35

print("\n### PDF GENERATOR SIMULATION ###\n")

currentY = grid_start_y_mm
currentY += 8  # Topic header
currentY += 5  # Section header

pdf_coords = {}

for i in range(section_question_count):
    if i % questions_per_row == 0 and i > 0:
        # New row in PDF
        currentY += row_height_mm
    
    q_num = i + 1
    bubble_y = currentY + 2
    
    pdf_coords[q_num] = bubble_y
    
    if q_num in [1, 10, 11, 20, 21, 30, 31]:
        print(f"Q{q_num}: currentY={currentY}mm, bubbleY={bubble_y}mm")

print("\n### BACKEND SIMULATION ###\n")

current_y_mm = grid_start_y_mm
current_y_mm += 8  # Topic header
current_y_mm += 5  # Section header

backend_coords = {}

for i in range(section_question_count):
    row = i // questions_per_row
    
    q_num = i + 1
    question_y_mm = current_y_mm + (row * row_height_mm)
    bubble_y_mm = question_y_mm + 2
    
    backend_coords[q_num] = bubble_y_mm
    
    if q_num in [1, 10, 11, 20, 21, 30, 31]:
        print(f"Q{q_num}: question_y={question_y_mm}mm, bubbleY={bubble_y_mm}mm")

print("\n### COMPARISON ###\n")

all_match = True
for q_num in [1, 10, 11, 20, 21, 30, 31]:
    pdf_y = pdf_coords[q_num]
    backend_y = backend_coords[q_num]
    match = "✅" if abs(pdf_y - backend_y) < 0.1 else "❌"
    
    print(f"Q{q_num}: PDF={pdf_y}mm, Backend={backend_y}mm, Diff={abs(pdf_y - backend_y):.2f}mm {match}")
    
    if abs(pdf_y - backend_y) >= 0.1:
        all_match = False

print("\n" + "=" * 60)
if all_match:
    print("✅ ALL COORDINATES MATCH!")
else:
    print("❌ COORDINATES DON'T MATCH!")
print("=" * 60)
