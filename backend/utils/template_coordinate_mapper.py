"""
Template-Based Coordinate Mapper
Imtihon yaratilganda saqlangan koordinata template'dan foydalanadi
EvalBee kabi professional tizim
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class TemplateCoordinateMapper:
    """
    Coordinate template'dan koordinatalarni hisoblash
    
    Bu tizim:
    1. Imtihon yaratilganda koordinata template saqlanadi
    2. Tekshirishda o'sha template ishlatiladi
    3. Corner marker'lar topiladi
    4. Template'dagi nisbiy koordinatalar pixel'ga o'giriladi
    """
    
    def __init__(
        self,
        corners: List[Dict],  # Detected corner positions in pixels
        coordinate_template: Dict  # Saved coordinate template from exam
    ):
        """
        Args:
            corners: Detected corner markers [{'name': 'top-left', 'x': px, 'y': px}, ...]
            coordinate_template: Coordinate template from exam data
        """
        self.corners = self._organize_corners(corners)
        self.template = coordinate_template
        
        # Calculate distance between corners in pixels
        self.width_px = self.corners['top-right']['x'] - self.corners['top-left']['x']
        self.height_px = self.corners['bottom-left']['y'] - self.corners['top-left']['y']
        
        logger.info(f"✅ Template-based coordinate system initialized")
        logger.info(f"   Template version: {self.template.get('version', 'unknown')}")
        logger.info(f"   Template timestamp: {self.template.get('timestamp', 'unknown')}")
        logger.info(f"   Top-left corner: ({self.corners['top-left']['x']:.1f}, {self.corners['top-left']['y']:.1f}) px")
        logger.info(f"   Distance between corners: {self.width_px:.1f} x {self.height_px:.1f} px")
        logger.info(f"   Total questions in template: {len(self.template.get('questions', {}))}")
    
    def _organize_corners(self, corners: List[Dict]) -> Dict:
        """
        Corner'larni tartibga solish
        """
        corner_dict = {}
        for corner in corners:
            name = corner['name'].replace('-', '_')  # 'top-left' → 'top_left'
            corner_dict[name] = {'x': corner['x'], 'y': corner['y']}
        
        # Also add with dashes for compatibility
        corner_dict['top-left'] = corner_dict.get('top_left', corner_dict.get('topLeft', {}))
        corner_dict['top-right'] = corner_dict.get('top_right', corner_dict.get('topRight', {}))
        corner_dict['bottom-left'] = corner_dict.get('bottom_left', corner_dict.get('bottomLeft', {}))
        corner_dict['bottom-right'] = corner_dict.get('bottom_right', corner_dict.get('bottomRight', {}))
        
        return corner_dict
    
    def relative_to_pixels(self, relative_x: float, relative_y: float) -> tuple:
        """
        Nisbiy koordinatalarni (0-1) pixel koordinatalarga o'girish
        
        Args:
            relative_x: Normalized X (0.0 to 1.0)
            relative_y: Normalized Y (0.0 to 1.0)
            
        Returns:
            (pixel_x, pixel_y): Pixel coordinates in scanned image
        """
        pixel_x = self.corners['top-left']['x'] + (relative_x * self.width_px)
        pixel_y = self.corners['top-left']['y'] + (relative_y * self.height_px)
        
        return (pixel_x, pixel_y)
    
    def calculate_all(self) -> Dict[int, Dict]:
        """
        Template'dan barcha koordinatalarni hisoblash
        
        Returns:
            dict: {questionNumber: {'questionNumber': int, 'bubbles': [...]}}
        """
        coordinates = {}
        
        # Get questions from template
        template_questions = self.template.get('questions', {})
        
        if not template_questions:
            logger.error("❌ No questions found in coordinate template!")
            return coordinates
        
        # Get layout for bubble radius calculation
        layout = self.template.get('layout', {})
        bubble_radius_mm = layout.get('bubbleRadius', 2.5)
        
        # Calculate scale factor (pixels per mm)
        # Template has distance between corners in mm
        template_corners = self.template.get('cornerMarkers', {})
        if template_corners:
            template_width_mm = (
                template_corners.get('topRight', {}).get('x', 197.5) - 
                template_corners.get('topLeft', {}).get('x', 12.5)
            )
            scale_factor = self.width_px / template_width_mm
        else:
            # Fallback: assume 185mm between corners
            scale_factor = self.width_px / 185.0
        
        bubble_radius_px = bubble_radius_mm * scale_factor
        
        # Convert each question from template
        for q_num_str, q_data in template_questions.items():
            q_num = int(q_num_str)
            
            bubbles = []
            for bubble_template in q_data.get('bubbles', []):
                # Get relative coordinates from template
                relative_x = bubble_template.get('relativeX', 0)
                relative_y = bubble_template.get('relativeY', 0)
                
                # Convert to pixels
                pixel_x, pixel_y = self.relative_to_pixels(relative_x, relative_y)
                
                bubbles.append({
                    'variant': bubble_template.get('variant'),
                    'x': pixel_x,
                    'y': pixel_y,
                    'radius': bubble_radius_px,
                    'relative_x': relative_x,  # For debugging
                    'relative_y': relative_y   # For debugging
                })
            
            coordinates[q_num] = {
                'questionNumber': q_num,
                'bubbles': bubbles
            }
        
        logger.info(f"✅ Calculated coordinates for {len(coordinates)} questions from template")
        
        return coordinates
