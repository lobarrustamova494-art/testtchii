"""
Diagnose 5-imtihon image to understand what we're working with
"""
import cv2
import numpy as np
from pathlib import Path

def diagnose_image():
    print("=" * 80)
    print("🔍 DIAGNOSING 5-IMTIHON IMAGE")
    print("=" * 80)
    print()
    
    # Load image
    image_path = Path("test_images/5-imtihon.jpg")
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    print(f"📸 Image Info:")
    print(f"   Size: {img.shape[1]}x{img.shape[0]} pixels")
    print(f"   Channels: {img.shape[2]}")
    print(f"   Type: {img.dtype}")
    print()
    
    print(f"📊 Image Statistics:")
    print(f"   Mean brightness: {gray.mean():.1f} / 255")
    print(f"   Std deviation: {gray.std():.1f}")
    print(f"   Min: {gray.min()}")
    print(f"   Max: {gray.max()}")
    print(f"   Contrast: {gray.std() / 128 * 100:.1f}%")
    print()
    
    # Check for very dark pixels (potential bubbles)
    dark_threshold = 100
    dark_pixels = np.sum(gray < dark_threshold)
    dark_percentage = dark_pixels / gray.size * 100
    
    print(f"🎯 Dark Pixel Analysis (< {dark_threshold}):")
    print(f"   Dark pixels: {dark_pixels:,}")
    print(f"   Percentage: {dark_percentage:.2f}%")
    print()
    
    # Check different regions
    height, width = gray.shape
    regions = {
        'Top-left': gray[0:height//4, 0:width//4],
        'Top-right': gray[0:height//4, 3*width//4:width],
        'Center': gray[height//4:3*height//4, width//4:3*width//4],
        'Bottom-left': gray[3*height//4:height, 0:width//4],
        'Bottom-right': gray[3*height//4:height, 3*width//4:width]
    }
    
    print(f"📍 Regional Analysis:")
    for name, region in regions.items():
        print(f"   {name:15s}: mean={region.mean():.1f}, std={region.std():.1f}")
    print()
    
    # Try to find bubbles using contour detection
    print(f"🔍 Bubble Detection Test:")
    
    # Apply threshold
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"   Total contours found: {len(contours)}")
    
    # Filter for bubble-like shapes
    bubble_candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 50 or area > 5000:  # Too small or too large
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        if h == 0 or w == 0:
            continue
        
        aspect_ratio = w / float(h)
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:  # Not circular enough
            continue
        
        bubble_candidates.append({
            'x': x + w//2,
            'y': y + h//2,
            'area': area,
            'aspect': aspect_ratio
        })
    
    print(f"   Bubble candidates: {len(bubble_candidates)}")
    
    if bubble_candidates:
        print(f"   First 5 candidates:")
        for i, bubble in enumerate(bubble_candidates[:5]):
            print(f"      {i+1}. pos=({bubble['x']}, {bubble['y']}), area={bubble['area']:.0f}, aspect={bubble['aspect']:.2f}")
    print()
    
    # Check if this looks like a PDF-generated exam or a photo
    print(f"🎨 Image Type Analysis:")
    
    # PDF-generated images typically have:
    # - Very high contrast (std > 60)
    # - Clear black/white separation
    # - Corner markers
    
    # Photos typically have:
    # - Lower contrast (std < 50)
    # - Gradual transitions
    # - No corner markers
    # - Shadows, lighting variations
    
    if gray.std() > 60:
        print(f"   ✅ High contrast ({gray.std():.1f}) - likely PDF-generated")
    else:
        print(f"   ⚠️  Low contrast ({gray.std():.1f}) - likely a photo")
    
    # Check for corner markers
    corner_size = 100
    corners = {
        'top-left': gray[0:corner_size, 0:corner_size],
        'top-right': gray[0:corner_size, width-corner_size:width],
        'bottom-left': gray[height-corner_size:height, 0:corner_size],
        'bottom-right': gray[height-corner_size:height, width-corner_size:width]
    }
    
    corner_markers_found = 0
    for name, corner in corners.items():
        # Check if corner has a dark square
        dark_ratio = np.sum(corner < 100) / corner.size
        if dark_ratio > 0.1:  # At least 10% dark pixels
            corner_markers_found += 1
    
    if corner_markers_found >= 3:
        print(f"   ✅ Corner markers found: {corner_markers_found}/4")
    else:
        print(f"   ❌ Corner markers NOT found: {corner_markers_found}/4")
        print(f"      This is likely a PHOTO, not a PDF-generated exam")
    
    print()
    
    # Recommendations
    print(f"💡 Recommendations:")
    
    if gray.std() < 50:
        print(f"   1. ⚠️  Image has low contrast - apply CLAHE enhancement")
        print(f"   2. ⚠️  Increase contrast before bubble detection")
    
    if corner_markers_found < 3:
        print(f"   3. ⚠️  No corner markers - this is a PHOTO of an exam")
        print(f"      - Cannot use perspective correction")
        print(f"      - Need to manually align or use different approach")
        print(f"      - Consider using template matching instead")
    
    if len(bubble_candidates) < 100:
        print(f"   4. ⚠️  Very few bubble candidates ({len(bubble_candidates)})")
        print(f"      - Adjust threshold (currently 127)")
        print(f"      - Try adaptive thresholding")
        print(f"      - Check if bubbles are filled")
    
    if dark_percentage < 5:
        print(f"   5. ⚠️  Very few dark pixels ({dark_percentage:.2f}%)")
        print(f"      - Image may be too bright")
        print(f"      - Bubbles may not be filled")
        print(f"      - Or this is a blank exam sheet")
    
    print()
    print("=" * 80)
    print("Diagnosis complete!")
    print("=" * 80)

if __name__ == "__main__":
    diagnose_image()
