"""
Relative Coordinate Mapper - Corner Marker Based System
100% aniq koordinatalar, perspective distortion'dan himoyalangan
"""
import logging
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RelativeCoordinateMapper:
    """
    Corner marker'lardan nisbiy koordinatalar tizimi
    
    Afzalliklari:
    - Perspective distortion'dan mustaqil
    - Image size'dan mustaqil
    - Skanerlash sifatidan mustaqil
    - 100% aniq koordinatalar
    """
    
    def __init__(
        self, 
        corners: List[Dict],  # Detected corner positions in pixels
        exam_structure: Dict,
        qr_layout: Optional[Dict] = None
    ):
        """
        Args:
            corners: List of 4 corner markers with pixel positions
                     [{'name': 'top-left', 'x': px, 'y': px}, ...]
            exam_structure: Exam structure data
            qr_layout: Layout data from QR code (optional)
        """
        self.corners = self._organize_corners(corners)
        self.exam_structure = exam_structure
        self.qr_layout = qr_layout
        
        # Calculate distance between corners in pixels
        self.width_px = self.corners['top-right']['x'] - self.corners['top-left']['x']
        self.height_px = self.corners['bottom-left']['y'] - self.corners['top-left']['y']
        
        logger.info(f"Corner-based coordinate system initialized")
        logger.info(f"  Top-left corner: ({self.corners['top-left']['x']:.1f}, {self.corners['top-left']['y']:.1f}) px")
        logger.info(f"  Distance between corners: {self.width_px:.1f} x {self.height_px:.1f} px")
        
        # PDF Layout Constants (in mm)
        # These are FIXED values from PDF generator
        self.PAPER_WIDTH_MM = 210
        self.PAPER_HEIGHT_MM = 297
        self.CORNER_SIZE_MM = 15
        self.CORNER_MARGIN_MM = 5
        
        # CRITICAL FIX: After perspective correction, corners are at PAGE CORNERS (0,0), (width,0), etc.
        # NOT at marker centers!
        # So we use PAGE CORNERS as reference points
        self.corner_center_mm = {
            'top-left': {
                'x': 0.0,  # Page corner
                'y': 0.0   # Page corner
            },
            'top-right': {
                'x': self.PAPER_WIDTH_MM,  # 210mm
                'y': 0.0
            },
            'bottom-left': {
                'x': 0.0,
                'y': self.PAPER_HEIGHT_MM  # 297mm
            },
            'bottom-right': {
                'x': self.PAPER_WIDTH_MM,  # 210mm
                'y': self.PAPER_HEIGHT_MM  # 297mm
            }
        }
        
        # Distance between corners in PDF (mm) - FULL PAGE SIZE
        self.width_mm = self.PAPER_WIDTH_MM  # 210mm
        self.height_mm = self.PAPER_HEIGHT_MM  # 297mm
        
        logger.info(f"  PDF corner distance: {self.width_mm:.1f} x {self.height_mm:.1f} mm")
        
        # Get layout parameters
        if qr_layout:
            logger.info("Using layout from QR code")
            self.questions_per_row = qr_layout['questions_per_row']
            self.question_spacing_mm = qr_layout['question_spacing_mm']
            self.bubble_radius_mm = qr_layout['bubble_radius_mm']
            self.bubble_spacing_mm = qr_layout['bubble_spacing_mm']
            self.row_height_mm = qr_layout['row_height_mm']
            self.grid_start_x_mm = qr_layout['grid_start_x_mm']
            self.grid_start_y_mm = qr_layout['grid_start_y_mm']
            self.first_bubble_offset_mm = qr_layout['first_bubble_offset_mm']
        else:
            logger.warning("Using default layout (no QR code)")
            self.questions_per_row = 2
            self.question_spacing_mm = 90
            self.bubble_radius_mm = 2.5
            self.bubble_spacing_mm = 8
            self.row_height_mm = 5.5
            self.grid_start_x_mm = 25
            self.grid_start_y_mm = 149
            self.first_bubble_offset_mm = 8
    
    def _organize_corners(self, corners: List[Dict]) -> Dict:
        """
        Corner'larni tartibga solish
        """
        corner_dict = {}
        for corner in corners:
            corner_dict[corner['name']] = {'x': corner['x'], 'y': corner['y']}
        return corner_dict
    
    def mm_to_relative(self, x_mm: float, y_mm: float) -> tuple:
        """
        PDF koordinatalarini (mm) nisbiy koordinatalarga (0-1) o'girish
        
        CRITICAL FIX: Corners are now at PAGE CORNERS (0,0), not marker centers.
        So we calculate relative to page origin (0,0), not marker center.
        
        Args:
            x_mm: X coordinate in mm (absolute in PDF, from page origin)
            y_mm: Y coordinate in mm (absolute in PDF, from page origin)
            
        Returns:
            (relative_x, relative_y): Normalized coordinates (0.0 to 1.0)
        """
        # Calculate relative to page origin (0, 0)
        # No need to subtract corner position since corners ARE at (0, 0)
        relative_x = x_mm / self.width_mm
        relative_y = y_mm / self.height_mm
        
        return (relative_x, relative_y)
    
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
        Barcha savollar uchun koordinatalarni hisoblash
        Corner marker'lardan nisbiy koordinatalar tizimi bilan
        
        Returns:
            dict: {questionNumber: {'questionNumber': int, 'bubbles': [...]}}
        """
        coordinates = {}
        question_number = 1
        
        # Start from grid position
        current_y_mm = self.grid_start_y_mm
        
        for topic_idx, topic in enumerate(self.exam_structure['subjects']):
            logger.info(f"Topic {topic_idx + 1}: {topic['name']}")
            
            # Topic header
            current_y_mm += 8
            
            for section_idx, section in enumerate(topic['sections']):
                logger.info(f"  Section {section_idx + 1}: {section['name']} ({section['questionCount']} questions)")
                
                # Section header
                current_y_mm += 5
                
                # Calculate questions in this section
                for i in range(section['questionCount']):
                    # Determine row and column
                    row = i // self.questions_per_row
                    col = i % self.questions_per_row
                    
                    # Calculate Y position (in mm)
                    question_y_mm = current_y_mm + (row * self.row_height_mm)
                    
                    # Calculate X position (in mm)
                    question_x_mm = self.grid_start_x_mm + (col * self.question_spacing_mm)
                    
                    # Calculate bubble positions
                    bubbles = []
                    variants = ['A', 'B', 'C', 'D', 'E']
                    
                    for v_idx, variant in enumerate(variants):
                        # Bubble position in mm (absolute in PDF)
                        bubble_x_mm = question_x_mm + self.first_bubble_offset_mm + (v_idx * self.bubble_spacing_mm)
                        bubble_y_mm = question_y_mm + 2  # +2mm offset in PDF
                        
                        # Convert to relative coordinates (0-1)
                        relative_x, relative_y = self.mm_to_relative(bubble_x_mm, bubble_y_mm)
                        
                        # Convert to pixel coordinates
                        pixel_x, pixel_y = self.relative_to_pixels(relative_x, relative_y)
                        
                        # Bubble radius in pixels
                        # Use average scale factor
                        scale_x = self.width_px / self.width_mm
                        scale_y = self.height_px / self.height_mm
                        scale_avg = (scale_x + scale_y) / 2
                        bubble_radius_px = self.bubble_radius_mm * scale_avg
                        
                        bubbles.append({
                            'variant': variant,
                            'x': pixel_x,
                            'y': pixel_y,
                            'radius': bubble_radius_px,
                            'relative_x': relative_x,  # For debugging
                            'relative_y': relative_y   # For debugging
                        })
                    
                    coordinates[question_number] = {
                        'questionNumber': question_number,
                        'bubbles': bubbles
                    }
                    
                    question_number += 1
                
                # Update Y for next section
                rows_in_section = (section['questionCount'] + self.questions_per_row - 1) // self.questions_per_row
                current_y_mm += (rows_in_section * self.row_height_mm) + 2
            
            # Space between topics
            current_y_mm += 3
        
        logger.info(f"✅ Calculated coordinates for {question_number - 1} questions using corner-based system")
        return coordinates
