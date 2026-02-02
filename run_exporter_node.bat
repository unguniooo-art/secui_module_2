@echo off
echo =========================================
echo System Resource Monitor (Node.js)
echo =========================================
echo.

echo Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo Node.js not found! Please install Node.js
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
call npm install

echo.
echo Starting metrics exporter on http://localhost:9100/metrics
echo.

node src\exporters\metrics_exporter_node.js

pause
