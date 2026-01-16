@echo off
echo ========================================
echo OMR SYSTEM DEBUG TOOL
echo ========================================
echo.

if "%1"=="" (
    echo Usage: test_debug.bat ^<image_path^>
    echo Example: test_debug.bat test_image.jpg
    echo.
    pause
    exit /b 1
)

echo Testing image: %1
echo.

echo Step 1: Quick Debug (Corner Detection)
echo ----------------------------------------
python quick_debug.py %1
echo.

echo Step 2: Full System Debug
echo ----------------------------------------
python debug_full_system.py %1
echo.

echo ========================================
echo DEBUG COMPLETE
echo ========================================
echo.
echo Check these files:
echo   - quick_debug.jpg (corner detection)
echo   - debug_full_system.jpg (coordinates)
echo.
pause
