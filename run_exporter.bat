@echo off
echo ================================
echo System Resource Monitor Exporter
echo ================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.9+
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
python -m pip install psutil prometheus-client

echo.
echo Starting metrics exporter on http://localhost:9100/metrics
echo Press Ctrl+C to stop
echo.

python src\exporters\metrics_exporter.py

pause
