@echo off
echo ========================================
echo  Backend Server - Quick Start
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate venv and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --quiet fastapi uvicorn opencv-python numpy groq python-dotenv pillow scikit-image scipy imutils pandas python-multipart pydantic

echo.
echo ========================================
echo  Starting Backend Server...
echo ========================================
echo  Backend URL: http://localhost:8000
echo  Health Check: http://localhost:8000/health
echo  API Docs: http://localhost:8000/docs
echo ========================================
echo.

REM Start server
python main.py
