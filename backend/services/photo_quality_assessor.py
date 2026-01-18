"""
Photo Quality Assessor
Assesses photo quality and provides recommendations
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PhotoQualityAssessor:
    """
    Foto sifatini baholash va tavsiyalar berish
    
    Features:
    - Sharpness assessment
    - Contrast assessment
    - Lighting assessment
    - Perspective assessment
    - Overall quality score
    - Improvement recommendations
    """
    
    def __init__(self):
        # Quality thresholds
        self.min_sharpness = 50.0
        self.min_contrast = 30.0
        self.min_brightness = 80.0
        self.max_brightness = 200.0
        self.min_overall_quality = 60.0
        
    def assess_photo_quality(self, image: np.ndarray) -> Dict:
        """
        Comprehensive photo quality assessment
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            dict: Quality assessment results
        """
        logger.info("Starting photo quality assessment...")
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Individual assessments
        sharpness = self._assess_sharpness(gray)
        contrast = self._assess_contrast(gray)
        lighting = self._assess_lighting(gray)
        perspective = self._assess_perspective(gray)
        noise = self._assess_noise(gray)
        
        # Calculate overall quality
        overall_quality = self._calculate_overall_quality(
            sharpness, contrast, lighting, perspective, noise
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            sharpness, contrast, lighting, perspective, noise
        )
        
        # Determine suitability for OMR
        omr_suitability = self._assess_omr_suitability(overall_quality)
        
        result = {
            'overall_quality': round(overall_quality, 1),
            'omr_suitability': omr_suitability,
            'metrics': {
                'sharpness': round(sharpness, 1),
                'contrast': round(contrast, 1),
                'lighting': round(lighting, 1),
                'perspective': round(perspective, 1),
                'noise': round(noise, 1)
            },
            'recommendations': recommendations,
            'image_info': {
                'width': gray.shape[1],
                'height': gray.shape[0],
                'aspect_ratio': round(gray.shape[1] / gray.shape[0], 2)
            }
        }
        
        logger.info(f"Quality assessment complete: {overall_quality:.1f}/100")
        return result
    
    def _assess_sharpness(self, gray: np.ndarray) -> float:
        """
        Assess image sharpness using Laplacian variance
        """
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Normalize to 0-100 scale
        sharpness = min(100, variance / 10)
        
        return sharpness
    
    def _assess_contrast(self, gray: np.ndarray) -> float:
        """
        Assess image contrast using standard deviation
        """
        std_dev = np.std(gray)
        
        # Normalize to 0-100 scale
        contrast = min(100, std_dev * 2)
        
        return contrast
    
    def _assess_lighting(self, gray: np.ndarray) -> float:
        """
        Assess lighting quality
        """
        mean_brightness = np.mean(gray)
        
        # Ideal brightness is around 128 (middle gray)
        brightness_score = 100 - abs(mean_brightness - 128) * 2
        brightness_score = max(0, brightness_score)
        
        # Check for overexposure/underexposure
        overexposed = np.sum(gray > 240) / gray.size * 100
        underexposed = np.sum(gray < 15) / gray.size * 100
        
        exposure_penalty = (overexposed + underexposed) * 2
        lighting_score = max(0, brightness_score - exposure_penalty)
        
        return lighting_score
    
    def _assess_perspective(self, gray: np.ndarray) -> float:
        """
        Assess perspective distortion
        """
        height, width = gray.shape
        
        # Expected A4 aspect ratio
        expected_ratio = 297 / 210  # A4 height/width
        actual_ratio = height / width
        
        # Calculate deviation from expected ratio
        ratio_deviation = abs(actual_ratio - expected_ratio) / expected_ratio
        
        # Perspective score (lower deviation = higher score)
        perspective_score = max(0, 100 - ratio_deviation * 200)
        
        return perspective_score
    
    def _assess_noise(self, gray: np.ndarray) -> float:
        """
        Assess image noise level
        """
        # Apply Gaussian blur and calculate difference
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise_map = cv2.absdiff(gray, blurred)
        
        # Calculate noise level
        noise_level = np.mean(noise_map)
        
        # Normalize to 0-100 scale (lower noise = higher score)
        noise_score = max(0, 100 - noise_level * 4)
        
        return noise_score
    
    def _calculate_overall_quality(
        self,
        sharpness: float,
        contrast: float,
        lighting: float,
        perspective: float,
        noise: float
    ) -> float:
        """
        Calculate weighted overall quality score
        """
        # Weights for different aspects
        weights = {
            'sharpness': 0.25,
            'contrast': 0.25,
            'lighting': 0.20,
            'perspective': 0.15,
            'noise': 0.15
        }
        
        overall = (
            sharpness * weights['sharpness'] +
            contrast * weights['contrast'] +
            lighting * weights['lighting'] +
            perspective * weights['perspective'] +
            noise * weights['noise']
        )
        
        return overall
    
    def _assess_omr_suitability(self, overall_quality: float) -> Dict:
        """
        Assess suitability for OMR processing
        """
        if overall_quality >= 80:
            return {
                'level': 'excellent',
                'expected_accuracy': '90-99%',
                'recommendation': 'Perfect for OMR processing'
            }
        elif overall_quality >= 70:
            return {
                'level': 'good',
                'expected_accuracy': '80-90%',
                'recommendation': 'Good for OMR processing'
            }
        elif overall_quality >= 60:
            return {
                'level': 'moderate',
                'expected_accuracy': '60-80%',
                'recommendation': 'May work but consider improvements'
            }
        elif overall_quality >= 40:
            return {
                'level': 'poor',
                'expected_accuracy': '30-60%',
                'recommendation': 'Significant improvements needed'
            }
        else:
            return {
                'level': 'very_poor',
                'expected_accuracy': '0-30%',
                'recommendation': 'Not suitable for OMR processing'
            }
    
    def _generate_recommendations(
        self,
        sharpness: float,
        contrast: float,
        lighting: float,
        perspective: float,
        noise: float
    ) -> List[str]:
        """
        Generate improvement recommendations
        """
        recommendations = []
        
        if sharpness < self.min_sharpness:
            recommendations.append("📷 Improve focus - ensure the document is in sharp focus")
            recommendations.append("📷 Hold camera steady or use a tripod")
            recommendations.append("📷 Move closer to the document for better detail")
        
        if contrast < self.min_contrast:
            recommendations.append("🔆 Improve contrast - ensure good lighting")
            recommendations.append("🔆 Avoid shadows on the document")
            recommendations.append("🔆 Use uniform lighting from multiple angles")
        
        if lighting < 60:
            recommendations.append("💡 Improve lighting conditions")
            recommendations.append("💡 Avoid direct sunlight or harsh shadows")
            recommendations.append("💡 Use natural daylight or bright indoor lighting")
        
        if perspective < 70:
            recommendations.append("📐 Improve camera angle - hold camera directly above document")
            recommendations.append("📐 Ensure document is flat and not curved")
            recommendations.append("📐 Align camera parallel to document surface")
        
        if noise < 60:
            recommendations.append("🔧 Reduce image noise - use better lighting")
            recommendations.append("🔧 Clean camera lens")
            recommendations.append("🔧 Use lower ISO settings if possible")
        
        if not recommendations:
            recommendations.append("✅ Photo quality is good for OMR processing")
        
        return recommendations
    
    def create_quality_report(self, assessment: Dict) -> str:
        """
        Create a formatted quality report
        """
        report = []
        report.append("=" * 50)
        report.append("PHOTO QUALITY ASSESSMENT REPORT")
        report.append("=" * 50)
        
        # Overall quality
        quality = assessment['overall_quality']
        suitability = assessment['omr_suitability']
        
        report.append(f"\n📊 OVERALL QUALITY: {quality}/100")
        report.append(f"🎯 OMR SUITABILITY: {suitability['level'].upper()}")
        report.append(f"📈 EXPECTED ACCURACY: {suitability['expected_accuracy']}")
        report.append(f"💡 RECOMMENDATION: {suitability['recommendation']}")
        
        # Detailed metrics
        report.append(f"\n📋 DETAILED METRICS:")
        metrics = assessment['metrics']
        report.append(f"  🔍 Sharpness: {metrics['sharpness']}/100")
        report.append(f"  🌓 Contrast: {metrics['contrast']}/100")
        report.append(f"  💡 Lighting: {metrics['lighting']}/100")
        report.append(f"  📐 Perspective: {metrics['perspective']}/100")
        report.append(f"  🔧 Noise Level: {metrics['noise']}/100")
        
        # Image info
        report.append(f"\n📏 IMAGE INFO:")
        info = assessment['image_info']
        report.append(f"  📐 Size: {info['width']}x{info['height']}")
        report.append(f"  📏 Aspect Ratio: {info['aspect_ratio']}")
        
        # Recommendations
        if assessment['recommendations']:
            report.append(f"\n🔧 IMPROVEMENT RECOMMENDATIONS:")
            for i, rec in enumerate(assessment['recommendations'], 1):
                report.append(f"  {i}. {rec}")
        
        report.append("=" * 50)
        
        return "\n".join(report)
    
    def enhance_photo_for_omr(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance photo for better OMR processing
        """
        logger.info("Enhancing photo for OMR processing...")
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 1. Noise reduction
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # 2. Contrast enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 3. Sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # 4. Normalization
        normalized = cv2.normalize(sharpened, None, 0, 255, cv2.NORM_MINMAX)
        
        logger.info("✅ Photo enhancement complete")
        return normalized