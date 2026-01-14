"""
Precise Coordinate Mapper - Based on PDF Generator Specifications
Maps exact bubble positions from PDF layout to pixel coordinates
"""
import logging
from typing import Dict, List
from ..config import settings

logger = logging.getLogger(__name__)

class CoordinateMapper:
    """
    Aniq koordinatalar tizimi - PDF generator spetsifikatsiyalariga asoslangan
    """
    
    def __init__(self, image_width: int, image_height: int, exam_structure: Dict, qr_layout: Dict = None):
        self.image_width = image_width
        self.image_height = image_height
        self.exam_structure = exam_structure
        self.qr_layout = qr_layout  # QR code'dan olingan layout
        
        # A4 paper dimensions in mm
        self.paper_width_mm = 210
        self.paper_height_mm = 297
        
        # Calculate pixels per mm
        self.px_per_mm_x = image_width / self.paper_width_mm
        self.px_per_mm_y = image_height / self.paper_height_mm
        
        logger.info(f"Image dimensions: {image_width}x{image_height}")
        logger.info(f"Pixels per mm: X={self.px_per_mm_x:.2f}, Y={self.px_per_mm_y:.2f}")
        
        # PDF Layout Constants (from pdfGenerator.ts or QR code)
        if qr_layout:
            # Use layout from QR code (100% accurate!)
            logger.info("Using layout from QR code")
            self.questions_per_row = qr_layout['questions_per_row']
            self.question_spacing_mm = qr_layout['question_spacing_mm']
            self.bubble_radius_mm = qr_layout['bubble_radius_mm']
            self.bubble_spacing_mm = qr_layout['bubble_spacing_mm']
            self.row_height_mm = qr_layout['row_height_mm']
            self.grid_start_x_mm = qr_layout['grid_start_x_mm']
            self.grid_start_y_mm = qr_layout['grid_start_y_mm']
            self.first_bubble_offset_mm = qr_layout['first_bubble_offset_mm']
            
            # CRITICAL CHECK: Verify QR code has correct values
            if self.grid_start_y_mm != 149:
                logger.warning(
                    f"⚠️  QR code has OLD gridStartY value: {self.grid_start_y_mm}mm "
                    f"(should be 149mm). This PDF was generated with old code! "
                    f"Please regenerate the PDF with the latest version."
                )
            
            logger.info(f"Layout: gridStartY={self.grid_start_y_mm}mm, bubbleRadius={self.bubble_radius_mm}mm, rowHeight={self.row_height_mm}mm")
        else:
            # Use default layout (fallback)
            logger.warning("Using default layout (no QR code)")
            self.questions_per_row = 2
            self.question_spacing_mm = 90
            self.bubble_radius_mm = 2.5  # Updated: 3 → 2.5mm to prevent overlap
            self.bubble_spacing_mm = 8
            self.row_height_mm = 5.5  # Updated: 5 → 5.5mm for proper spacing
            self.grid_start_x_mm = 25
            
            # Use old or new layout based on config
            if settings.USE_OLD_PDF_LAYOUT:
                self.grid_start_y_mm = 113  # OLD VALUE for backward compatibility
                logger.warning(f"⚠️  Using OLD gridStartY={self.grid_start_y_mm}mm (backward compatibility mode)")
                logger.warning(f"⚠️  Set USE_OLD_PDF_LAYOUT=False in config.py after regenerating PDFs")
            else:
                self.grid_start_y_mm = 149  # NEW VALUE (correct)
                logger.info(f"✅ Using NEW gridStartY={self.grid_start_y_mm}mm")
            
            self.first_bubble_offset_mm = 8
            
            logger.info(f"Default layout: gridStartY={self.grid_start_y_mm}mm, bubbleRadius={self.bubble_radius_mm}mm, rowHeight={self.row_height_mm}mm")
        
        # Corner markers - INCREASED SIZE for better detection
        self.corner_marker_size_mm = 15  # Increased from 10mm to 15mm
        self.corner_margin_mm = 5
        
        logger.info(f"Calculating coordinates: {self.px_per_mm_x:.2f} px/mm")
    
    def calculate_all(self) -> Dict[int, Dict]:
        """
        Barcha savollar uchun koordinatalarni hisoblash
        
        Returns:
            dict: {
                questionNumber: {
                    'questionNumber': int,
                    'bubbles': [
                        {'variant': 'A', 'x': float, 'y': float, 'radius': float},
                        ...
                    ]
                }
            }
        """
        coordinates = {}
        question_number = 1
        
        # In PDF: currentY = startY (this is where grid starts)
        # This matches grid_start_y_mm (113mm by default)
        current_y_mm = self.grid_start_y_mm
        
        for topic_idx, topic in enumerate(self.exam_structure['subjects']):
            logger.info(f"Topic {topic_idx + 1}: {topic['name']}")
            
            # PDF: Topic header (6mm height, reduced from 8mm)
            # PDF: Text at currentY + 4
            # PDF: Then currentY += 8 (reduced from 10mm)
            current_y_mm += 8  # Skip topic header (6mm) + spacing (2mm)
            
            for section_idx, section in enumerate(topic['sections']):
                logger.info(f"  Section {section_idx + 1}: {section['name']} ({section['questionCount']} questions)")
                
                # PDF: Section text at currentY + 3 (reduced from 4mm)
                # PDF: Then currentY += 5 (reduced from 6mm)
                current_y_mm += 5  # Skip section header
                
                # Calculate questions in this section
                for i in range(section['questionCount']):
                    # Determine row and column
                    row = i // self.questions_per_row
                    col = i % self.questions_per_row
                    
                    # Calculate Y position
                    # In PDF: currentY + 2 for bubble center
                    # currentY + 4 for question number text
                    question_y_mm = current_y_mm + (row * self.row_height_mm)
                    
                    # Calculate X position
                    question_x_mm = self.grid_start_x_mm + (col * self.question_spacing_mm)
                    
                    # Calculate bubble positions
                    bubbles = []
                    variants = ['A', 'B', 'C', 'D', 'E']
                    
                    for v_idx, variant in enumerate(variants):
                        # In PDF: bubbleX = xPos + 8 + (vIndex * bubbleSpacing)
                        # bubbleY = currentY + 2
                        bubble_x_mm = question_x_mm + self.first_bubble_offset_mm + (v_idx * self.bubble_spacing_mm)
                        bubble_y_mm = question_y_mm + 2  # +2mm offset in PDF
                        
                        # Convert to pixels
                        bubble_x_px = bubble_x_mm * self.px_per_mm_x
                        bubble_y_px = bubble_y_mm * self.px_per_mm_y
                        bubble_radius_px = self.bubble_radius_mm * min(self.px_per_mm_x, self.px_per_mm_y)
                        
                        bubbles.append({
                            'variant': variant,
                            'x': bubble_x_px,
                            'y': bubble_y_px,
                            'radius': bubble_radius_px
                        })
                    
                    coordinates[question_number] = {
                        'questionNumber': question_number,
                        'bubbles': bubbles
                    }
                    
                    question_number += 1
                
                # Update Y for next section
                rows_in_section = (section['questionCount'] + self.questions_per_row - 1) // self.questions_per_row
                current_y_mm += (rows_in_section * self.row_height_mm) + 2  # +2mm spacing (reduced from 3mm)
            
            # Space between topics
            current_y_mm += 3  # Reduced from 5mm to 3mm
        
        logger.info(f"Calculated coordinates for {question_number - 1} questions")
        return coordinates
    
    def get_corner_markers(self) -> List[Dict]:
        """
        Burchak markerlarining koordinatalarini qaytarish
        PDF'dagi aniq pozitsiyalar (15mm x 15mm markers):
        - Top markers: Y = 5mm
        - Bottom markers: Y = 277mm (297 - 5 - 15)
        - Left markers: X = 5mm
        - Right markers: X = 190mm (210 - 5 - 15)
        
        Returns:
            list: [
                {'position': 'top-left', 'x': float, 'y': float, 'size': float},
                ...
            ]
        """
        size_px = self.corner_marker_size_mm * min(self.px_per_mm_x, self.px_per_mm_y)
        
        # Exact positions from PDF generator (15mm markers)
        top_y_mm = 5
        bottom_y_mm = 297 - 5 - 15  # 277mm
        left_x_mm = 5
        right_x_mm = 210 - 5 - 15  # 190mm
        
        # Convert to pixels (center of marker)
        top_y_px = (top_y_mm + 7.5) * self.px_per_mm_y  # +7.5 for center
        bottom_y_px = (bottom_y_mm + 7.5) * self.px_per_mm_y  # +7.5 for center
        left_x_px = (left_x_mm + 7.5) * self.px_per_mm_x  # +7.5 for center
        right_x_px = (right_x_mm + 7.5) * self.px_per_mm_x  # +7.5 for center
        
        return [
            {
                'position': 'top-left',
                'x': left_x_px,
                'y': top_y_px,
                'size': size_px
            },
            {
                'position': 'top-right',
                'x': right_x_px,
                'y': top_y_px,
                'size': size_px
            },
            {
                'position': 'bottom-left',
                'x': left_x_px,
                'y': bottom_y_px,
                'size': size_px
            },
            {
                'position': 'bottom-right',
                'x': right_x_px,
                'y': bottom_y_px,
                'size': size_px
            }
        ]
    
    def mm_to_px(self, mm: float, axis: str = 'x') -> float:
        """
        Millimetrni pixelga o'girish
        
        Args:
            mm: Millimetr qiymati
            axis: 'x' yoki 'y' o'qi
            
        Returns:
            float: Pixel qiymati
        """
        if axis == 'x':
            return mm * self.px_per_mm_x
        else:
            return mm * self.px_per_mm_y
    
    def px_to_mm(self, px: float, axis: str = 'x') -> float:
        """
        Pixelni millimetrga o'girish
        
        Args:
            px: Pixel qiymati
            axis: 'x' yoki 'y' o'qi
            
        Returns:
            float: Millimetr qiymati
        """
        if axis == 'x':
            return px / self.px_per_mm_x
        else:
            return px / self.px_per_mm_y
