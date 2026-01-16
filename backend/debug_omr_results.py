"""
Debug OMR Detection Results
OMR detection natijalarini tekshirish
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("OMR DETECTION RESULTS DEBUG")
print("=" * 60)

# Sample exam structure
exam_structure = {
    'subjects': [
        {
            'id': 'subject-1',
            'name': 'Test Subject',
            'sections': [
                {
                    'id': 'section-1',
                    'name': 'Test Section',
                    'questionCount': 10
                }
            ]
        }
    ]
}

# Sample answer key (all A)
answer_key = {i: 'A' for i in range(1, 11)}

print("\n1. Answer Key:")
for q, ans in answer_key.items():
    print(f"   Q{q}: {ans}")

print("\n2. Expected Behavior:")
print("   - If student marked A → BLUE (correct)")
print("   - If student marked B → RED (wrong) + GREEN (correct A)")
print("   - If student marked nothing → NO ANNOTATION")

print("\n3. Rasmda ko'rinayotgan muammo:")
print("   - Annotation'lar chapga siljigan")
print("   - Savol raqamlarida annotation bor")
print("   - Bu X koordinata muammosi")

print("\n4. Mumkin bo'lgan sabablar:")
print("   a) OMR detection noto'g'ri bubble'ni topmoqda")
print("   b) Koordinatalar noto'g'ri hisoblangan")
print("   c) Bubble pozitsiyalari PDF'da noto'g'ri")

print("\n5. Tekshirish kerak:")
print("   - OMR detection log'larini ko'rish")
print("   - Qaysi bubble'lar 'detected' deb topilgan")
print("   - Koordinatalar to'g'rimi")

print("\n" + "=" * 60)
