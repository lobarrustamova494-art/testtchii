"""
Quick API Test
Tez API test
"""
import requests
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_api_test():
    """
    Tez API test
    """
    logger.info("⚡ QUICK API TEST")
    logger.info("=" * 30)
    
    # API URL
    api_url = "http://localhost:8001/api/ultra-precise-grade"
    
    # Test image
    image_path = "../5-imtihon-test-varag'i.jpg"
    
    # Simple exam structure (faqat 5 ta savol)
    exam_structure = {
        'subjects': [
            {
                'id': 'subject1',
                'name': 'Test Subject',
                'sections': [
                    {
                        'id': 'section1',
                        'name': 'Test Section',
                        'questionCount': 5,  # Faqat 5 ta savol
                        'correctScore': 1,   # Har bir to'g'ri javob uchun 1 ball
                        'wrongScore': 0      # Noto'g'ri javob uchun 0 ball
                    }
                ]
            }
        ]
    }
    
    # Simple answer key
    answer_key = {
        "1": "A",
        "2": "B", 
        "3": "C",
        "4": "D",
        "5": "E"
    }
    
    # Simple calibration (faqat birinchi savol)
    manual_calibration = [
        {"question": 1, "variant": "A", "x": 170, "y": 480},
        {"question": 1, "variant": "B", "x": 200, "y": 480},
        {"question": 1, "variant": "C", "x": 230, "y": 480},
        {"question": 1, "variant": "D", "x": 260, "y": 480},
        {"question": 1, "variant": "E", "x": 290, "y": 480}
    ]
    
    # Prepare request
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpeg')
    }
    
    data = {
        'exam_structure': json.dumps(exam_structure),
        'answer_key': json.dumps(answer_key),
        'manual_calibration': json.dumps(manual_calibration)
    }
    
    try:
        logger.info("🚀 Sending request...")
        response = requests.post(api_url, files=files, data=data, timeout=30)
        
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result['success']:
                logger.info("✅ SUCCESS!")
                
                # Results
                results = result['results']
                logger.info(f"📊 Score: {results['totalScore']}/{results['maxScore']} ({results['percentage']}%)")
                
                # Statistics
                stats = result['statistics']
                logger.info(f"🔍 Detection: {stats['omr']['detected']}/{stats['omr']['total']}")
                logger.info(f"🎯 Method: {stats['coordinate_detection']['method']} ({stats['coordinate_detection']['accuracy_estimate']}%)")
                logger.info(f"⏱️ Time: {stats['duration']:.2f}s")
                
            else:
                logger.error("❌ API returned success=false")
                
        else:
            logger.error(f"❌ HTTP {response.status_code}")
            logger.error(response.text[:200])
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        files['file'][1].close()

if __name__ == "__main__":
    quick_api_test()