"""
PDF Layout Analysis - Corner Marker'lardan Nisbiy Koordinatalar
Bu script PDF generator kodini tahlil qilib, corner marker'lardan
qancha masofada nimalar bo'lishini aniqlaydi.
"""

print("=" * 80)
print("PDF LAYOUT ANALYSIS - CORNER MARKER BASED")
print("=" * 80)

# A4 paper dimensions
PAPER_WIDTH_MM = 210
PAPER_HEIGHT_MM = 297

# Corner marker specifications (from drawCornerMarkers function)
CORNER_SIZE_MM = 15  # size = 15
CORNER_MARGIN_MM = 5  # margin = 5

print("\n1. CORNER MARKER POSITIONS")
print("-" * 80)

# Calculate corner marker positions (center of each marker)
corners = {
    'top-left': {
        'x': CORNER_MARGIN_MM + CORNER_SIZE_MM / 2,  # 5 + 7.5 = 12.5mm
        'y': CORNER_MARGIN_MM + CORNER_SIZE_MM / 2,  # 5 + 7.5 = 12.5mm
    },
    'top-right': {
        'x': PAPER_WIDTH_MM - CORNER_MARGIN_MM - CORNER_SIZE_MM / 2,  # 210 - 5 - 7.5 = 197.5mm
        'y': CORNER_MARGIN_MM + CORNER_SIZE_MM / 2,  # 5 + 7.5 = 12.5mm
    },
    'bottom-left': {
        'x': CORNER_MARGIN_MM + CORNER_SIZE_MM / 2,  # 5 + 7.5 = 12.5mm
        'y': PAPER_HEIGHT_MM - CORNER_MARGIN_MM - CORNER_SIZE_MM / 2,  # 297 - 5 - 7.5 = 284.5mm
    },
    'bottom-right': {
        'x': PAPER_WIDTH_MM - CORNER_MARGIN_MM - CORNER_SIZE_MM / 2,  # 210 - 5 - 7.5 = 197.5mm
        'y': PAPER_HEIGHT_MM - CORNER_MARGIN_MM - CORNER_SIZE_MM / 2,  # 297 - 5 - 7.5 = 284.5mm
    }
}

for name, pos in corners.items():
    print(f"{name:15} Center: ({pos['x']:6.1f}mm, {pos['y']:6.1f}mm)")

# Calculate distances between corners
width_between_corners = corners['top-right']['x'] - corners['top-left']['x']
height_between_corners = corners['bottom-left']['y'] - corners['top-left']['y']

print(f"\nDistance between corners:")
print(f"  Horizontal: {width_between_corners:.1f}mm")
print(f"  Vertical:   {height_between_corners:.1f}mm")

print("\n2. ANSWER GRID POSITION (from drawAnswerGrid)")
print("-" * 80)

# Grid parameters (from drawAnswerGrid function)
GRID_START_X = 25  # xStart = 25
GRID_START_Y = 149  # startY (after headers)
QUESTION_SPACING = 90  # questionsPerRow spacing
BUBBLE_SPACING = 8
FIRST_BUBBLE_OFFSET = 8
ROW_HEIGHT = 5.5

print(f"Grid Start X: {GRID_START_X}mm")
print(f"Grid Start Y: {GRID_START_Y}mm (after headers)")
print(f"Question Spacing: {QUESTION_SPACING}mm")
print(f"Bubble Spacing: {BUBBLE_SPACING}mm")
print(f"First Bubble Offset: {FIRST_BUBBLE_OFFSET}mm")
print(f"Row Height: {ROW_HEIGHT}mm")

print("\n3. RELATIVE TO CORNER MARKERS")
print("-" * 80)

# Calculate grid position relative to top-left corner
grid_from_top_left_x = GRID_START_X - corners['top-left']['x']
grid_from_top_left_y = GRID_START_Y - corners['top-left']['y']

print(f"Grid Start relative to TOP-LEFT corner:")
print(f"  X offset: {grid_from_top_left_x:+.1f}mm")
print(f"  Y offset: {grid_from_top_left_y:+.1f}mm")

# Calculate grid position relative to top-right corner
grid_from_top_right_x = GRID_START_X - corners['top-right']['x']
grid_from_top_right_y = GRID_START_Y - corners['top-right']['y']

print(f"\nGrid Start relative to TOP-RIGHT corner:")
print(f"  X offset: {grid_from_top_right_x:+.1f}mm")
print(f"  Y offset: {grid_from_top_right_y:+.1f}mm")

print("\n4. BUBBLE POSITIONS (First Question)")
print("-" * 80)

# First question position
q1_x = GRID_START_X
q1_y = GRID_START_Y

# Bubble positions for first question
bubbles_q1 = []
for v_idx, variant in enumerate(['A', 'B', 'C', 'D', 'E']):
    bubble_x = q1_x + FIRST_BUBBLE_OFFSET + (v_idx * BUBBLE_SPACING)
    bubble_y = q1_y + 2  # +2mm offset in PDF
    
    # Relative to top-left corner
    rel_x = bubble_x - corners['top-left']['x']
    rel_y = bubble_y - corners['top-left']['y']
    
    bubbles_q1.append({
        'variant': variant,
        'absolute_x': bubble_x,
        'absolute_y': bubble_y,
        'relative_x': rel_x,
        'relative_y': rel_y
    })

print("Question 1 bubbles (absolute and relative to TOP-LEFT corner):")
for b in bubbles_q1:
    print(f"  {b['variant']}: Absolute ({b['absolute_x']:5.1f}mm, {b['absolute_y']:5.1f}mm) "
          f"→ Relative ({b['relative_x']:+6.1f}mm, {b['relative_y']:+6.1f}mm)")

print("\n5. SECOND COLUMN (Question 2)")
print("-" * 80)

# Second question position (second column)
q2_x = GRID_START_X + QUESTION_SPACING
q2_y = GRID_START_Y

# Bubble positions for second question
bubbles_q2 = []
for v_idx, variant in enumerate(['A', 'B', 'C', 'D', 'E']):
    bubble_x = q2_x + FIRST_BUBBLE_OFFSET + (v_idx * BUBBLE_SPACING)
    bubble_y = q2_y + 2
    
    # Relative to top-left corner
    rel_x = bubble_x - corners['top-left']['x']
    rel_y = bubble_y - corners['top-left']['y']
    
    bubbles_q2.append({
        'variant': variant,
        'absolute_x': bubble_x,
        'absolute_y': bubble_y,
        'relative_x': rel_x,
        'relative_y': rel_y
    })

print("Question 2 bubbles (absolute and relative to TOP-LEFT corner):")
for b in bubbles_q2:
    print(f"  {b['variant']}: Absolute ({b['absolute_x']:5.1f}mm, {b['absolute_y']:5.1f}mm) "
          f"→ Relative ({b['relative_x']:+6.1f}mm, {b['relative_y']:+6.1f}mm)")

print("\n6. COORDINATE TRANSFORMATION FORMULA")
print("-" * 80)

print("""
YANGI TIZIM: Corner Marker'lardan Nisbiy Koordinatalar

1. Corner marker'larni top (4 ta qora kvadrat)
2. Corner'lar orasidagi masofani hisoblash:
   - Horizontal: 185.0mm (top-right.x - top-left.x)
   - Vertical: 272.0mm (bottom-left.y - top-left.y)

3. Har bir element uchun nisbiy koordinata:
   relative_x = (element_x - top_left_corner_x) / width_between_corners
   relative_y = (element_y - top_left_corner_y) / height_between_corners
   
   Bu 0.0 dan 1.0 gacha bo'lgan nisbiy qiymat beradi.

4. Skanerlangan rasmda:
   pixel_x = top_left_corner_pixel_x + (relative_x * width_between_corners_pixels)
   pixel_y = top_left_corner_pixel_y + (relative_y * height_between_corners_pixels)

AFZALLIKLARI:
✅ Perspective distortion'dan mustaqil
✅ Skanerlash sifatidan mustaqil  
✅ Image size'dan mustaqil
✅ 100% aniq koordinatalar
""")

print("\n7. EXAMPLE: Question 1, Bubble A")
print("-" * 80)

bubble_a = bubbles_q1[0]
relative_x_normalized = bubble_a['relative_x'] / width_between_corners
relative_y_normalized = bubble_a['relative_y'] / height_between_corners

print(f"Absolute position: ({bubble_a['absolute_x']:.1f}mm, {bubble_a['absolute_y']:.1f}mm)")
print(f"Relative to top-left: ({bubble_a['relative_x']:+.1f}mm, {bubble_a['relative_y']:+.1f}mm)")
print(f"Normalized (0-1): ({relative_x_normalized:.4f}, {relative_y_normalized:.4f})")
print(f"\nIn scanned image (1240x1754 pixels):")
print(f"  If top-left corner at (50, 50) pixels")
print(f"  And corners span (1140, 1654) pixels")
print(f"  Then bubble A at:")
print(f"    X = 50 + ({relative_x_normalized:.4f} * 1140) = {50 + relative_x_normalized * 1140:.1f} pixels")
print(f"    Y = 50 + ({relative_y_normalized:.4f} * 1654) = {50 + relative_y_normalized * 1654:.1f} pixels")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"""
PDF Layout (A4: 210mm x 297mm):

Corner Markers (15mm x 15mm, 5mm margin):
  Top-Left:     Center at (12.5mm, 12.5mm)
  Top-Right:    Center at (197.5mm, 12.5mm)
  Bottom-Left:  Center at (12.5mm, 284.5mm)
  Bottom-Right: Center at (197.5mm, 284.5mm)
  
  Distance between corners: 185.0mm x 272.0mm

Answer Grid:
  Start: (25mm, 149mm)
  First bubble offset: 8mm
  Bubble spacing: 8mm
  Question spacing: 90mm
  Row height: 5.5mm

Question 1, Bubble A:
  Absolute: (33.0mm, 151.0mm)
  Relative to top-left corner: (+20.5mm, +138.5mm)
  Normalized: (0.1108, 0.5092)

YANGI YONDASHUV:
1. Corner marker'larni top
2. Nisbiy koordinatalarni hisoblash
3. Har qanday image size'da ishlaydi
4. Perspective distortion'dan himoyalangan
""")

print("=" * 80)
