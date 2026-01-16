"""
QUICK DEBUG - Tez tekshirish
Faqat asosiy muammolarni topish
"""
import cv2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.image_processor import ImageProcessor

def quick_debug(image_path: str):
    """Tez debug"""
    print("\n🔍 QUICK DEBUG\n")
    
    if not Path(image_path).exists():
        print(f"❌ File not found: {image_path}")
        return
    
    # Process image
    processor = ImageProcessor(target_width=2480, target_height=3508)
    processed = processor.process(image_path)
    
    # Check corners
    corners_found = len(processed['corners']) if processed['corners'] else 0
    
    print(f"Image: {Path(image_path).name}")
    print(f"Size: {processed['dimensions']['width']}x{processed['dimensions']['height']}")
    print(f"Corners: {corners_found}/4")
    
    if corners_found == 4:
        print("✅ CORNER DETECTION: OK")
        print("\nCorner positions:")
        for i, (x, y) in enumerate(processed['corners']):
            print(f"  {i+1}. ({x:.0f}, {y:.0f})")
    elif corners_found > 0:
        print(f"⚠️  CORNER DETECTION: PARTIAL ({corners_found}/4)")
        print("   Some corners not found - will use FALLBACK system")
    else:
        print("❌ CORNER DETECTION: FAILED")
        print("   No corners found - will use FALLBACK system")
        print("\n   Possible reasons:")
        print("   1. Corner markers not visible")
        print("   2. Image quality too low")
        print("   3. Corner markers too light")
        print("   4. Detection threshold too strict")
    
    # Save debug image
    debug_img = cv2.cvtColor(processed['grayscale'], cv2.COLOR_GRAY2BGR)
    
    if processed['corners']:
        for i, (x, y) in enumerate(processed['corners']):
            cv2.circle(debug_img, (int(x), int(y)), 20, (0, 255, 0), 3)
            cv2.putText(debug_img, f"{i+1}", (int(x) + 25, int(y)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    output = "quick_debug.jpg"
    cv2.imwrite(output, debug_img)
    print(f"\n💾 Debug image saved: {output}")
    
    # Recommendation
    print("\n📋 RECOMMENDATION:")
    if corners_found == 4:
        print("   ✅ System should work correctly")
        print("   ✅ Will use CORNER-BASED coordinate system")
    else:
        print("   ⚠️  System will use FALLBACK coordinates")
        print("   ⚠️  Annotations may be inaccurate")
        print("\n   TO FIX:")
        print("   1. Make sure corner markers are printed clearly")
        print("   2. Use high-quality scan/photo")
        print("   3. Ensure good lighting")
        print("   4. Check if markers are 10mm black squares")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_debug.py <image_path>")
        sys.exit(1)
    
    quick_debug(sys.argv[1])
