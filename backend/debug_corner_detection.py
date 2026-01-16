"""
Debug Corner Detection - Rasmda nima bo'layotganini ko'rish
"""
import cv2
import numpy as np
import sys
from pathlib import Path

def debug_corner_detection(image_path: str):
    """
    Corner detection'ni debug qilish
    """
    print(f"Debugging: {image_path}")
    print("=" * 60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image")
        return
    
    height, width = image.shape[:2]
    print(f"✅ Image loaded: {width}x{height}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Try different thresholds
    thresholds = [50, 80, 100, 120, 150]
    
    for thresh_val in thresholds:
        print(f"\n--- Threshold: {thresh_val} ---")
        
        # Threshold
        _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            binary, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        print(f"Total contours: {len(contours)}")
        
        # Calculate expected marker size
        px_per_mm_x = width / 210
        px_per_mm_y = height / 297
        expected_size = 15 * min(px_per_mm_x, px_per_mm_y)
        
        print(f"Expected marker size: {expected_size:.1f} px")
        
        # Filter by size
        min_size = expected_size * 0.5
        max_size = expected_size * 2.0
        
        candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            if h == 0 or w == 0:
                continue
            
            aspect_ratio = w / float(h)
            marker_size = min(w, h)
            
            # Check size and aspect ratio
            if (min_size < marker_size < max_size and 
                0.7 < aspect_ratio < 1.43):
                
                # Check darkness
                roi = gray[y:y+h, x:x+w]
                if roi.size > 0:
                    avg_intensity = np.mean(roi)
                    darkness = (255 - avg_intensity) / 255.0
                    
                    # Check uniformity
                    std_intensity = np.std(roi)
                    uniformity = 1.0 - min(std_intensity / 128.0, 1.0)
                    
                    if darkness > 0.5 and uniformity > 0.4:
                        candidates.append({
                            'x': x + w//2,
                            'y': y + h//2,
                            'w': w,
                            'h': h,
                            'size': marker_size,
                            'aspect': aspect_ratio,
                            'darkness': darkness,
                            'uniformity': uniformity
                        })
        
        print(f"Candidates (size + aspect + darkness + uniformity): {len(candidates)}")
        
        # Show top 10 candidates
        if candidates:
            candidates.sort(key=lambda c: c['darkness'] * c['uniformity'], reverse=True)
            print("\nTop 10 candidates:")
            for i, c in enumerate(candidates[:10]):
                print(f"  {i+1}. pos=({c['x']}, {c['y']}), "
                      f"size={c['size']:.1f}, aspect={c['aspect']:.2f}, "
                      f"darkness={c['darkness']:.2f}, uniformity={c['uniformity']:.2f}")
        
        # Save threshold image
        output_path = image_path.replace('.', f'_thresh{thresh_val}.')
        cv2.imwrite(output_path, binary)
        print(f"Saved: {output_path}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS:")
    print("1. Check threshold images - are corner markers visible?")
    print("2. Which threshold value shows markers best?")
    print("3. Are there too many candidates? (should be ~4)")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_corner_detection.py <image_path>")
        sys.exit(1)
    
    debug_corner_detection(sys.argv[1])
