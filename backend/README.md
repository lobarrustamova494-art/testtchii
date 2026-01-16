# EvalBee Backend - Python FastAPI

Professional OMR (Optical Mark Recognition) backend with AI verification.

## Features

- **Professional OMR Detection** - 99%+ accuracy
- **AI Verification** - Groq LLaMA 3.2 90B Vision
- **Camera Preview API** - Real-time corner detection
- **Quick Analysis** - Pre-submission validation
- **QR Code Reading** - Automatic exam identification
- **Image Processing** - OpenCV-based

## Tech Stack

- FastAPI
- OpenCV (cv2)
- NumPy
- Pillow
- Groq AI
- Tesseract OCR
- pyzbar (QR codes)

## Local Development

### Prerequisites

```bash
# Python 3.11+
python --version

# System dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr libzbar0

# System dependencies (macOS)
brew install tesseract zbar

# System dependencies (Windows)
# Download and install:
# - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# - ZBar: http://zbar.sourceforge.net/
```

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
```

### Run Server

```bash
# Development (with auto-reload)
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

Server runs at: http://localhost:8000

API Docs: http://localhost:8000/docs

## Render.com Deployment

### Build Command

```bash
pip install --upgrade pip && pip install -r requirements.txt
```

### Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables (Render)

```
GROQ_API_KEY=your_key_here
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
CORS_ORIGINS=http://localhost:5173,https://evalbee-frontend.onrender.com
```

### Root Directory

```
backend
```

## API Endpoints

### Health Check

```
GET /
GET /health
```

### Grading

```
POST /api/grade-sheet
```

### Camera

```
POST /api/camera/preview
POST /api/camera/quick-analysis
```

### AI

```
POST /api/test-ai
```

## Project Structure

```
backend/
├── services/           # Core services
│   ├── image_processor.py
│   ├── omr_detector.py
│   ├── ai_verifier.py
│   ├── grader.py
│   └── image_annotator.py
├── utils/             # Utilities
│   ├── coordinate_mapper.py
│   └── relative_coordinate_mapper.py
├── camera_preview_api.py
├── config.py
├── main.py
└── requirements.txt
```

## Configuration

See `config.py` for all settings:

- Image processing parameters
- OMR detection thresholds
- Corner detection weights
- CORS origins
- AI settings

## Testing

```bash
# Run tests
python -m pytest

# Test specific file
python test_corner_detection.py
```

## Performance

- OMR Processing: 1.8s per sheet
- AI Verification: 2-3s per answer
- Camera Preview: 5 FPS (200ms)

## Troubleshooting

### Import Errors

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Tesseract Not Found

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows - add to PATH
```

### ZBar Not Found

```bash
# Ubuntu/Debian
sudo apt-get install libzbar0

# macOS
brew install zbar
```

## License

MIT
