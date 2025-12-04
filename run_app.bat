@echo off
echo Starting Text-Mining App...
echo.

REM Set PYTHONPATH to ensure proper imports
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Clear Streamlit cache to avoid import issues
if exist "%USERPROFILE%\.streamlit\cache" (
    echo Clearing Streamlit cache...
    rmdir /s /q "%USERPROFILE%\.streamlit\cache"
)

REM Launch Streamlit
echo Launching app...
streamlit run ui\main.py

pause
