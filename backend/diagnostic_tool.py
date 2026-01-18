#!/usr/bin/env python3
"""
OMR Diagnostic Tool
Helps diagnose issues with image processing and coordinate detection
"""
import cv2
import numpy as np
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_image(image_path: str):
    """
    Comprehensive image diagnosis for OMR processing
    """
    print("=" * 60)
    print("OMR IMAGE DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ ERROR: Cannot load image from {image_path}")
        return
    
    print(f"✅ Image loaded: {image_path}")
    
    # Basic image info
    height, width = image.shape[:2]
    print(f"📐 Dimensions: {width}x{height} pixels")
    
    # Check aspect ratio
    aspect_ratio = width / height
    a4_ratio = 210 / 297  # A4 aspect ratio
    print(f"📏 Aspect ratio: {aspect_ratio:.3f} (A4 expected: {a4_ratio:.3f})")
    
    if abs(aspect_ratio - a4_ratio) > 0.1:
        print("⚠️  WARNING: Aspect ratio doesn't match A4 format")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Image quality metrics
    print("\n📊 IMAGE QUALITY ANALYSIS:")
    
    # Brightness
    brightness = np.mean(gray)
    print(f"💡 Brightness: {brightness:.1f}/255 ", end="")
    if brightness < 100:
        print("(Too dark)")
    elif brightness > 200:
        print("(Too bright)")
    else:
        print("(Good)")
    
    # Contrast
    contrast = np.std(gray)
    print(f"🎨 Contrast: {contrast:.1f} ", end="")
    if contrast < 30:
        print("(Low contrast)")
    elif contrast > 80:
        print("(High contrast)")
    else:
        print("(Good)")
    
    # Sharpness (using Laplacian variance)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = laplacian.var()
    print(f"🔍 Sharpness: {sharpness:.1f} ", end="")
    if sharpness < 100:
        print("(Blurry)")
    elif sharpness > 500:
        print("(Very sharp)")
    else:
        print("(Good)")
    
    # Corner detection test
    print("\n🔍 CORNER DETECTION TEST:")
    
    try:
        from services.improved_corner_detector import ImprovedCornerDetector
        corner_detector = ImprovedCornerDetector()
        corners = corner_detector.detect_corners(image)
        
        if corners and len(corners) == 4:
            print("✅ Corner detection: SUCCESS")
            for corner in corners:
                print(f"   {corner['name']}: ({corner['x']}, {corner['y']}) confidence: {corner['confidence']:.3f}")
        else:
            print("❌ Corner detection: FAILED")
            if corners:
                print(f"   Found {len(corners)} corners (expected 4)")
            else:
                print("   No corners detected")
    except Exception as e:
        print(f"❌ Corner detection error: {e}")
    
    # Bubble detection test
    print("\n🔵 BUBBLE DETECTION TEST:")
    
    try:
        from services.template_matching_omr import TemplateMatchingOMR
        template_omr = TemplateMatchingOMR()
        bubbles = template_omr.detect_bubbles(gray)
        
        print(f"🔵 Bubbles detected: {len(bubbles)}")
        
        if len(bubbles) > 0:
            # Analyze bubble quality
            avg_radius = np.mean([b['radius'] for b in bubbles])
            avg_darkness = np.mean([b['darkness'] for b in bubbles])
            
            print(f"   Average radius: {avg_radius:.1f} pixels")
            print(f"   Average darkness: {avg_darkness:.1f}%")
            
            if len(bubbles) < 20:
                print("⚠️  WARNING: Very few bubbles detected")
            elif len(bubbles) > 200:
                print("⚠️  WARNING: Too many bubbles detected (may include noise)")
            else:
                print("✅ Bubble count looks reasonable")
        else:
            print("❌ No bubbles detected")
            print("   Possible issues:")
            print("   - Image too blurry or low quality")
            print("   - Bubbles too small or too large")
            print("   - Poor contrast between bubbles and background")
            
    except Exception as e:
        print(f"❌ Bubble detection error: {e}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    recommendations = []
    
    if brightness < 100:
        recommendations.append("📸 Increase image brightness or use better lighting")
    elif brightness > 200:
        recommendations.append("📸 Reduce image brightness or avoid overexposure")
    
    if contrast < 30:
        recommendations.append("🎨 Improve image contrast")
    
    if sharpness < 100:
        recommendations.append("🔍 Use a sharper image (avoid camera shake, focus properly)")
    
    if abs(aspect_ratio - a4_ratio) > 0.1:
        recommendations.append("📏 Ensure the entire answer sheet is visible and properly aligned")
    
    if not corners or len(corners) != 4:
        recommendations.append("🔲 Ensure corner markers (black squares) are clearly visible in all four corners")
    
    if len(bubbles) < 20:
        recommendations.append("🔵 Ensure answer bubbles are clearly visible and properly sized")
    
    if not recommendations:
        recommendations.append("✅ Image looks good for OMR processing!")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print("\n" + "=" * 60)

def main():
    if len(sys.argv) != 2:
        print("Usage: python diagnostic_tool.py <image_path>")
        print("Example: python diagnostic_tool.py test_image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"❌ ERROR: Image file not found: {image_path}")
        sys.exit(1)
    
    diagnose_image(image_path)

if __name__ == "__main__":
    main()